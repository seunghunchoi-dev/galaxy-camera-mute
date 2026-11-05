# -*- coding: utf-8 -*-
"""capture_app.py 로 찍은 앱 화면에서 저작자 정보(이름·홈페이지·이메일)를 흐리게 가린다.

    py blur_shots.py shots
"""
import sys
from pathlib import Path

from PIL import Image, ImageFilter

for p in sorted(Path(sys.argv[1]).glob("app_*.png")):
    im = Image.open(p)
    if im.size == (662, 812):  # 메인 창: 하단 저작자 줄
        box = (110, 768, 555, 798)
    elif "about" in p.name:  # 정보 창: 저작자 항목
        box = (115, 138, 505, 262)
    else:
        continue
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(9)), box[:2])
    im.save(p)
    print("blurred", p.name)
