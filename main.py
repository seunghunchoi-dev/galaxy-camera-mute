# -*- coding: utf-8 -*-
"""갤럭시 카메라 무음 - 엔트리포인트.

Copyright (c) 2026 최승훈 (https://gwchoi.com, gwchoi96@gmail.com)
All rights reserved. 수정·재배포 금지 - 자세한 내용은 LICENSE 파일을 참고하세요.
"""
from __future__ import annotations

import sys


def prefers_dark() -> bool:
    """윈도우의 밝게/어둡게 설정을 따라간다. 알 수 없으면 어둡게."""
    try:
        import darkdetect

        return darkdetect.theme() != "Light"
    except Exception:
        return True


def main() -> int:
    from ui_main import MainWindow

    window = MainWindow(dark=prefers_dark())
    window.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
