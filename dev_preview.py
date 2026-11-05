# -*- coding: utf-8 -*-
"""개발용: 실기기 없이 가상 기기로 화면을 확인한다.

    py dev_preview.py          가상 기기 2대 (정상 1 + USB 디버깅 미승인 1)
    py dev_preview.py --empty  연결된 기기가 없는 상태
    py dev_preview.py --light  라이트 테마로 시작

실제 adb를 호출하지 않으므로 설정이 바뀌지 않는다.
"""
from __future__ import annotations

import sys

import adb_core
from adb_core import Device

EMPTY = "--empty" in sys.argv
LIGHT = "--light" in sys.argv

FAKE = [] if EMPTY else [
    Device("R3CX00SAMPLE", "device", "SM A175N", "a17ks"),
    Device("R5CY00SAMPLE", "unauthorized", "", ""),
]
_values = {"R3CX00SAMPLE": "1"}

adb_core.adb_available = lambda: True
adb_core.list_devices = lambda: list(FAKE)
adb_core.get_shutter_value = lambda serial: _values.get(serial)


def _set(serial: str, value: str) -> None:
    print(f"[가상] {serial} ← {value}")
    _values[serial] = value


adb_core.set_shutter_value = _set
adb_core.add_routine = lambda serial: print(f"[가상] {serial} ← 빅스비 루틴")

from ui_main import MainWindow  # noqa: E402  (가짜 adb를 먼저 심어야 한다)

if __name__ == "__main__":
    MainWindow(dark=not LIGHT).mainloop()
