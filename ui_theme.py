# -*- coding: utf-8 -*-
"""앱 전역 색상 팔레트와 공통 치수."""
from __future__ import annotations

DARK = {
    "bg": "#0f1115",
    "surface": "#171a21",
    "surface_alt": "#1e222b",
    "surface_hover": "#232834",
    "border": "#2a2f3a",
    "text": "#e6e8ee",
    "muted": "#98a1b2",
    "faint": "#6b7482",
    "accent": "#6d5efc",
    "accent_hover": "#7f73ff",
    "accent_soft": "#211f3d",
    "ok": "#35c77f",
    "ok_soft": "#13301f",
    "warn": "#f0a93b",
    "warn_soft": "#312512",
    "danger": "#f06565",
    "danger_soft": "#331a1c",
    "on_accent": "#ffffff",
}

LIGHT = {
    "bg": "#f4f5f8",
    "surface": "#ffffff",
    "surface_alt": "#f7f8fa",
    "surface_hover": "#eef0f5",
    "border": "#e1e4ea",
    "text": "#141821",
    "muted": "#5f6775",
    "faint": "#8a93a2",
    "accent": "#5b4df0",
    "accent_hover": "#6d60ff",
    "accent_soft": "#eceaff",
    "ok": "#14854c",
    "ok_soft": "#e3f6ec",
    "warn": "#a96a05",
    "warn_soft": "#fdf1dd",
    "danger": "#cf3b3b",
    "danger_soft": "#fdeaea",
    "on_accent": "#ffffff",
}

# CustomTkinter는 (라이트, 다크) 쌍으로 색을 받는다.
KEYS = tuple(DARK)


def pair(name: str) -> tuple[str, str]:
    """색 이름을 (라이트, 다크) 쌍으로 돌려준다."""
    return LIGHT[name], DARK[name]


def colors(dark: bool) -> dict:
    return DARK if dark else LIGHT


# 글꼴
FAMILY = "맑은 고딕"
MONO = "Consolas"

# 공통 치수
RADIUS_CARD = 14
RADIUS_ITEM = 12
RADIUS_CHIP = 9
