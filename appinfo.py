# -*- coding: utf-8 -*-
"""앱 이름·버전·저작자 등 한곳에 모아둔 메타 정보."""
from __future__ import annotations

APP_NAME = "갤럭시 카메라 무음"
APP_TAGLINE = "ADB로 셔터음 강제 설정을 해제합니다"
VERSION = "1.0.1"

AUTHOR = "최승훈"
HOMEPAGE = "https://gwchoi.com"
EMAIL = "gwchoi96@gmail.com"
COPYRIGHT_YEAR = "2026"

COPYRIGHT = f"© {COPYRIGHT_YEAR} {AUTHOR}"
CONTACT_LINE = f"{COPYRIGHT} · {HOMEPAGE.replace('https://', '')} · {EMAIL}"

LICENSE_NAME = "All rights reserved (수정·재배포 금지)"

THIRD_PARTY = [
    (
        "CustomTkinter",
        "MIT License",
        "https://github.com/TomSchimansky/CustomTkinter",
        "GUI 툴킷. 수정하지 않고 그대로 사용합니다.",
    ),
    (
        "Pillow",
        "MIT-CMU License",
        "https://python-pillow.org",
        "안내 이미지 표시에 사용합니다.",
    ),
    (
        "darkdetect",
        "BSD 3-Clause",
        "https://github.com/albertosottile/darkdetect",
        "윈도우의 밝게/어둡게 설정을 읽습니다.",
    ),
    (
        "Android SDK Platform-Tools (adb)",
        "Apache License 2.0",
        "https://developer.android.com/tools/releases/platform-tools",
        "동봉하지 않고 사용자가 Google 공식 서버에서 직접 내려받습니다.",
    ),
    (
        "Python / Tcl-Tk",
        "PSF License · Tcl-Tk License",
        "https://docs.python.org/3/license.html",
        "실행 환경과 기본 GUI 라이브러리.",
    ),
    (
        "Zstandard (zstd)",
        "BSD 3-Clause",
        "https://github.com/facebook/zstd",
        "단일 exe의 압축 해제에 쓰입니다 (Nuitka 포함).",
    ),
]
