# -*- coding: utf-8 -*-
"""삼성 갤럭시 카메라 셔터음 무음 처리를 위한 ADB 래퍼.

핵심 명령: adb shell settings put system csc_pref_camera_forced_shuttersound_key 0
(값 0 = 무음, 1 = 셔터음 원복)
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# 셔터음 강제 여부를 담고 있는 삼성 CSC 설정 키
SHUTTER_KEY = "csc_pref_camera_forced_shuttersound_key"
SHUTTER_NAMESPACE = "system"

MUTE_VALUE = "0"      # 무음
UNMUTE_VALUE = "1"    # 원복(셔터음 발생)

# 콘솔 창이 깜빡이지 않도록 하는 Windows 전용 플래그
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


class AdbError(RuntimeError):
    """adb 실행 자체가 불가능하거나 명령이 실패한 경우."""


FROZEN = getattr(sys, "frozen", False) or "__compiled__" in globals()


def app_dir() -> Path:
    """실행 파일(또는 스크립트)이 놓인 폴더. 포터블 모드에서 adb를 여기에 둔다.

    단일 exe는 임시 폴더에 풀려 실행되므로 sys.executable 이 임시 경로를 가리킬 수 있다.
    사용자가 실제로 둔 위치는 argv[0] 이므로 그쪽을 먼저 본다.
    """
    if FROZEN:
        for candidate in (sys.argv[0] if sys.argv else "", sys.executable):
            if not candidate:
                continue
            try:
                path = Path(candidate).resolve()
            except OSError:
                continue
            if path.is_file():
                return path.parent
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_dir() -> Path:
    """프로그램에 함께 묶인 읽기 전용 리소스(guide 이미지 등)가 있는 폴더.

    단일 exe는 실행할 때 임시 폴더에 풀리므로 app_dir() 과 다를 수 있다.
    """
    bundle = getattr(sys, "_MEIPASS", None)      # PyInstaller
    if bundle:
        return Path(bundle)
    return Path(__file__).resolve().parent        # Nuitka onefile / 일반 실행


def data_dir() -> Path:
    """adb를 내려받아 둘 폴더. 실행 폴더에 쓸 수 없으면 사용자 폴더로 물러난다."""
    target = app_dir()
    probe = target / ".write-test"
    try:
        probe.touch()
        probe.unlink()
    except OSError:
        fallback = Path(
            os.environ.get("LOCALAPPDATA") or Path.home()
        ) / "GalaxyCameraMute"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
    return target


# 하위 호환용 별칭
base_dir = app_dir


def find_adb() -> Path:
    """함께 있는 platform-tools → 내려받아 둔 폴더 → PATH 순으로 찾는다."""
    roots = [app_dir(), data_dir()]
    candidates: list[Path] = []
    for root in roots:
        candidates += [
            root / "platform-tools" / "adb.exe",
            root / "platform-tools" / "adb",
            root / "adb.exe",
        ]
    for path in candidates:
        if path.is_file():
            return path

    found = shutil.which("adb")
    if found:
        return Path(found)

    raise AdbError(
        "adb를 찾을 수 없습니다.\n\n"
        f"'{data_dir() / 'platform-tools'}' 폴더에 adb.exe가 있어야 합니다.\n"
        "Android SDK Platform-Tools를 내려받아 해당 경로에 풀어주세요."
    )


@dataclass
class AdbResult:
    returncode: int
    stdout: str
    stderr: str
    command: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def message(self) -> str:
        """사용자에게 보여줄 한 줄 메시지."""
        text = (self.stderr or self.stdout).strip()
        return text.splitlines()[0] if text else ""


def run_adb(args: list[str], serial: str | None = None, timeout: int = 25) -> AdbResult:
    """adb를 한 번 실행한다. serial을 주면 해당 기기로 한정(-s)."""
    adb = find_adb()
    command = [str(adb)]
    if serial:
        command += ["-s", serial]
    command += args

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=_NO_WINDOW,
        )
    except subprocess.TimeoutExpired:
        return AdbResult(-1, "", f"명령이 {timeout}초 안에 끝나지 않았습니다.", command)
    except OSError as exc:
        raise AdbError(f"adb 실행에 실패했습니다: {exc}") from exc

    return AdbResult(proc.returncode, proc.stdout or "", proc.stderr or "", command)


# ----------------------------------------------------------------------------- 기기

STATE_LABELS = {
    "device": "연결됨",
    "unauthorized": "USB 디버깅 미승인",
    "offline": "오프라인",
    "no permissions": "드라이버/권한 문제",
    "recovery": "복구 모드",
    "sideload": "사이드로드 모드",
    "bootloader": "부트로더",
    "authorizing": "승인 대기",
}


@dataclass
class Device:
    serial: str
    state: str
    model: str = ""
    product: str = ""

    @property
    def usable(self) -> bool:
        """설정 변경 명령을 보낼 수 있는 상태인지."""
        return self.state == "device"

    @property
    def state_label(self) -> str:
        return STATE_LABELS.get(self.state, self.state)

    @property
    def name(self) -> str:
        if self.model or self.product:
            return self.model or self.product
        # 인증 전에는 모델명을 읽을 수 없다
        return "알 수 없는 기기" if not self.usable else self.serial

    def hint(self) -> str:
        """사용할 수 없는 상태일 때의 안내 문구."""
        if self.state == "unauthorized":
            return "휴대폰 화면의 'USB 디버깅을 허용하시겠습니까?' 팝업에서 [허용]을 눌러주세요."
        if self.state in ("offline", "authorizing"):
            return "케이블을 다시 꽂거나 USB 연결 모드를 '파일 전송'으로 바꿔보세요."
        if self.state == "no permissions":
            return "USB 드라이버를 확인하고 PC를 재시작해보세요."
        return "설정을 변경할 수 없는 상태입니다."


_DEV_LINE = re.compile(r"^(\S+)\s+(device|unauthorized|offline|authorizing|recovery|sideload|bootloader|no permissions.*?)(\s|$)")


def list_devices() -> list[Device]:
    """adb devices -l 결과를 파싱해 연결된 기기 목록을 돌려준다."""
    result = run_adb(["devices", "-l"])
    if not result.ok and not result.stdout:
        raise AdbError(result.message or "adb devices 실행에 실패했습니다.")

    devices: list[Device] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices") or line.startswith("*"):
            continue
        match = _DEV_LINE.match(line)
        if not match:
            continue
        serial, state = match.group(1), match.group(2).strip()
        model = _extract(line, "model")
        product = _extract(line, "product")
        devices.append(Device(serial, state, model.replace("_", " "), product))
    return devices


def _extract(line: str, key: str) -> str:
    match = re.search(rf"\b{key}:(\S+)", line)
    return match.group(1) if match else ""


# ----------------------------------------------------------------------------- 셔터음

def get_shutter_value(serial: str) -> str | None:
    """현재 설정 값을 읽는다. 값이 없으면 None."""
    result = run_adb(
        ["shell", "settings", "get", SHUTTER_NAMESPACE, SHUTTER_KEY], serial=serial
    )
    if not result.ok:
        raise AdbError(result.message or "설정 값을 읽지 못했습니다.")

    value = result.stdout.strip()
    if not value or value.lower() == "null":
        return None
    return value


def set_shutter_value(serial: str, value: str) -> None:
    """설정 값을 쓰고, 실제로 반영됐는지 되읽어서 확인한다."""
    result = run_adb(
        ["shell", "settings", "put", SHUTTER_NAMESPACE, SHUTTER_KEY, value], serial=serial
    )
    if not result.ok:
        raise AdbError(result.message or "설정 값을 쓰지 못했습니다.")

    applied = get_shutter_value(serial)
    if applied != value:
        raise AdbError(f"값이 반영되지 않았습니다(현재 값: {applied}).")


def mute(serial: str) -> None:
    set_shutter_value(serial, MUTE_VALUE)


def unmute(serial: str) -> None:
    set_shutter_value(serial, UNMUTE_VALUE)


def describe_value(value: str | None) -> str:
    """설정 값을 사람이 읽을 수 있는 상태 문구로 바꾼다."""
    if value is None:
        return "설정 없음(기본값)"
    if value == MUTE_VALUE:
        return "무음"
    if value == UNMUTE_VALUE:
        return "셔터음 켜짐"
    return f"알 수 없음({value})"


# ------------------------------------------------------------------ 빅스비 루틴

# "카메라 앱 실행 시 소리 모드 무음, 종료 시 원래대로" 루틴 (모드 및 루틴 앱에서 내보낸 파일)
ROUTINE_FILE = Path("routine") / "camera_mute.rtn"
ROUTINES_PACKAGE = "com.samsung.android.app.routines"
ROUTINE_ACTIVITY = f"{ROUTINES_PACKAGE}/.ui.share.RoutineFileHandleActivity"
ROUTINE_MIME = "application/vnd.samsung.routines"
ROUTINE_REMOTE = "/sdcard/Download/GalaxyCameraMute.rtn"


def add_routine(serial: str) -> None:
    """루틴 파일을 휴대폰에 넣고 '모드 및 루틴' 앱의 가져오기 화면을 띄운다.

    실제 저장은 휴대폰 화면에서 사용자가 [저장]을 눌러야 끝난다.
    """
    local = resource_dir() / ROUTINE_FILE
    if not local.is_file():
        raise AdbError(f"루틴 파일이 없습니다: {local}")

    installed = run_adb(["shell", "pm", "path", ROUTINES_PACKAGE], serial=serial)
    if "package:" not in installed.stdout:
        raise AdbError("'모드 및 루틴' 앱이 없는 기기입니다.")

    pushed = run_adb(["push", str(local), ROUTINE_REMOTE], serial=serial, timeout=30)
    if not pushed.ok:
        raise AdbError(pushed.message or "루틴 파일을 휴대폰에 복사하지 못했습니다.")

    run_adb(["shell", "input", "keyevent", "KEYCODE_WAKEUP"], serial=serial)
    # 이전에 연 루틴 화면이 남아 있으면 새 화면이 뜨지 않으므로 기존 작업을 비우고 연다
    started = run_adb(
        [
            "shell", "am", "start", "--activity-clear-task",
            "-a", "android.intent.action.VIEW",
            "-d", f"file://{ROUTINE_REMOTE}",
            "-t", ROUTINE_MIME,
            "-n", ROUTINE_ACTIVITY,
        ],
        serial=serial,
    )
    # am start 는 실패해도 종료 코드가 0일 수 있어 출력으로 판단한다
    output = started.stdout + started.stderr
    if not started.ok or "Error" in output:
        raise AdbError(started.message or "루틴 가져오기 화면을 열지 못했습니다.")


def kill_server() -> None:
    """adb 서버를 내린다. 연결이 꼬였을 때 사용."""
    run_adb(["kill-server"], timeout=15)


# ------------------------------------------------------- platform-tools 내려받기

PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"


def adb_available() -> bool:
    try:
        find_adb()
    except AdbError:
        return False
    return True


def download_platform_tools(progress=None) -> Path:
    """Google 공식 서버에서 platform-tools를 받아 프로그램 폴더에 푼다.

    배포본에 adb를 동봉하지 않고 사용자가 직접 Google에서 받도록 하기 위한 경로.
    progress(받은 바이트, 전체 바이트)로 진행률을 알린다. 전체 크기를 모르면 -1.
    """
    import io
    import urllib.request
    import zipfile

    target = data_dir()
    buffer = io.BytesIO()

    request = urllib.request.Request(
        PLATFORM_TOOLS_URL, headers={"User-Agent": "galaxy-camera-mute"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            total = int(response.headers.get("Content-Length") or -1)
            read = 0
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
                read += len(chunk)
                if progress:
                    progress(read, total)
    except OSError as exc:
        raise AdbError(f"다운로드에 실패했습니다: {exc}") from exc

    buffer.seek(0)
    try:
        with zipfile.ZipFile(buffer) as archive:
            archive.extractall(target)
    except (zipfile.BadZipFile, OSError) as exc:
        raise AdbError(f"압축을 푸는 데 실패했습니다: {exc}") from exc

    adb = target / "platform-tools" / "adb.exe"
    if not adb.is_file():
        raise AdbError("받은 파일에서 adb.exe를 찾지 못했습니다.")
    return adb
