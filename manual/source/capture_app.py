# -*- coding: utf-8 -*-
"""매뉴얼용 앱 화면 캡처. 가짜 기기(가짜 시리얼)만 사용하므로 실제 기기 정보가 나오지 않는다.

    py capture_app.py <프로젝트 폴더> <출력 폴더>
"""
import ctypes
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

PROJECT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))

from PIL import Image  # noqa: E402

import adb_core  # noqa: E402
from adb_core import Device  # noqa: E402

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

FAKE_OK = Device("R3CX00SAMPLE", "device", "SM A175N", "a17ks")
FAKE_NO = Device("R5CY00SAMPLE", "unauthorized", "", "")
devices: list[Device] = []
values: dict[str, str] = {}
adb_core.adb_available = lambda: True
adb_core.list_devices = lambda: list(devices)
adb_core.get_shutter_value = lambda serial: values.get(serial)


def _set(serial, value):
    values[serial] = value


adb_core.set_shutter_value = _set
adb_core.add_routine = lambda serial: None

import ui_main  # noqa: E402
from ui_main import MainWindow  # noqa: E402


class RECT(ctypes.Structure):
    _fields_ = [("l", ctypes.c_long), ("t", ctypes.c_long), ("r", ctypes.c_long), ("b", ctypes.c_long)]


def grab(hwnd: int, name: str) -> None:
    rect = RECT()
    # 그림자 영역을 뺀 실제 창 크기
    if ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect)) != 0:
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
    full = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(full))
    w, h = full.r - full.l, full.b - full.t
    hdc = user32.GetDC(hwnd)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(hwnd, mdc, 2)

    class BMI(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32), ("a", ctypes.c_int32), ("b", ctypes.c_int32),
                    ("c", ctypes.c_uint32), ("d", ctypes.c_uint32)]

    bmi = BMI(ctypes.sizeof(BMI), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).convert("RGB")
    img = img.crop((rect.l - full.l, rect.t - full.t, rect.r - full.l, rect.b - full.t))
    img.save(OUT / f"{name}.png")
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mdc)
    user32.ReleaseDC(hwnd, hdc)
    print("saved", name, img.size)


def frame(win) -> int:
    return int(win.wm_frame(), 16)


def find_dialog(title: str) -> int:
    for _ in range(60):
        hwnd = user32.FindWindowW("#32770", title)
        if hwnd:
            return hwnd
        time.sleep(0.1)
    return 0


def dialog_shot(app, name: str, show) -> None:
    """메시지 상자를 띄워 캡처한 뒤 닫는다."""
    def watcher():
        hwnd = find_dialog(ui_main.appinfo.APP_NAME)
        time.sleep(0.6)
        if hwnd:
            grab(hwnd, name)
            # 예/아니오 상자는 WM_CLOSE 를 무시하므로 [아니오](7)와 [취소/확인](2)을 눌러 닫는다
            user32.PostMessageW(hwnd, 0x0111, 7, 0)
            user32.PostMessageW(hwnd, 0x0111, 2, 0)

    threading.Thread(target=watcher, daemon=True).start()
    show()


def settle(app, sec=0.8):
    end = time.time() + sec
    while time.time() < end:
        app.update()
        time.sleep(0.03)


def main():
    real_info = ui_main.messagebox.showinfo
    ui_main.messagebox.showinfo = lambda *a, **k: None  # 적용 중 상자는 따로 캡처

    app = MainWindow(dark=False)
    app.geometry("660x780+60+40")
    app._auto_scan = lambda: None
    settle(app, 1.5)

    # 1. 기기 없음
    devices.clear()
    app.scan(manual=True)
    settle(app, 1.2)
    grab(frame(app), "app_01_empty")

    # 2. 기기 연결 (정상 1 + 미승인 1)
    devices[:] = [FAKE_OK, FAKE_NO]
    values[FAKE_OK.serial] = "1"
    app._guide_shown = True  # 안내 창 자동 열림 방지
    app.scan(manual=True)
    settle(app, 1.2)
    grab(frame(app), "app_02_devices")

    # 3. 선택 모드
    app._toggle_device(FAKE_OK.serial)
    settle(app, 0.6)
    grab(frame(app), "app_03_select")
    app.only_selected.set(False)
    app.selected.clear()

    # 4. 무음 적용 완료 + 진행 상황
    devices[:] = [FAKE_OK]
    app.scan(manual=True)
    settle(app, 1.0)
    app.log_view.configure(state="normal")
    app.log_view.delete("1.0", "end")
    app.log_view.configure(state="disabled")
    app.apply(adb_core.MUTE_VALUE, "무음 적용")
    settle(app, 2.0)
    if not app.log_open:
        app._toggle_log()
    settle(app, 0.8)
    grab(frame(app), "app_04_muted")

    # 5. 루틴 안내 상자 (실제 앱과 같은 문구)
    ui_main.messagebox.showinfo = real_info
    dialog_shot(app, "app_05_routine_box", lambda: real_info(
        ui_main.appinfo.APP_NAME,
        "휴대폰에 '카메라 무음' 루틴 화면이 열렸습니다.\n\n"
        "화면 아래의 [저장]을 눌러야 루틴이 추가됩니다.\n"
        "(카메라 앱을 켜면 소리 모드가 무음이 되고, 끄면 원래대로 돌아갑니다)",
        parent=app,
    ))
    settle(app, 0.5)

    # 6. adb 내려받기 동의 상자
    dialog_shot(app, "app_06_download_box", lambda: ui_main.messagebox.askyesno(
        ui_main.appinfo.APP_NAME,
        "휴대폰과 통신하려면 Google의 Android SDK Platform-Tools(adb)가 필요합니다.\n\n"
        "Google 공식 서버에서 지금 내려받을까요?\n"
        f"약 10MB · 저장 위치: {Path('C:/GalaxyCameraMute') / 'platform-tools'}",
        parent=app,
    ))
    settle(app, 0.5)

    # 7. 원복 완료
    app.log_view.configure(state="normal")
    app.log_view.delete("1.0", "end")
    app.log_view.configure(state="disabled")
    ui_main.messagebox.showinfo = lambda *a, **k: None
    app.apply(adb_core.UNMUTE_VALUE, "셔터음 원복")
    settle(app, 2.0)
    grab(frame(app), "app_07_unmuted")

    # 8. 설정 방법 창
    app.show_guide(0)
    app.guide.geometry("+760+40")
    settle(app, 1.0)
    grab(frame(app.guide), "app_08_guide_1")
    app.guide.show_step(4)
    settle(app, 0.6)
    grab(frame(app.guide), "app_09_guide_5")
    app.guide.withdraw()

    # 9. 정보 창
    app.show_about()
    settle(app, 1.0)
    grab(frame(app.about), "app_10_about")

    app.destroy()


main()
