# -*- coding: utf-8 -*-
"""공통 위젯 조각."""
from __future__ import annotations

import customtkinter as ctk

import ui_theme as T


def font(size: int = 13, weight: str = "normal", mono: bool = False) -> ctk.CTkFont:
    return ctk.CTkFont(family=T.MONO if mono else T.FAMILY, size=size, weight=weight)


def card(master, **kwargs) -> ctk.CTkFrame:
    """테두리가 있는 카드 프레임."""
    options = dict(
        fg_color=T.pair("surface"),
        border_color=T.pair("border"),
        border_width=1,
        corner_radius=T.RADIUS_CARD,
    )
    options.update(kwargs)
    return ctk.CTkFrame(master, **options)


def badge(master, text: str, kind: str = "neutral") -> ctk.CTkLabel:
    """상태를 나타내는 알약 모양 라벨."""
    palette = {
        "neutral": ("surface_hover", "muted"),
        "ok": ("ok_soft", "ok"),
        "warn": ("warn_soft", "warn"),
        "danger": ("danger_soft", "danger"),
    }[kind]
    return ctk.CTkLabel(
        master,
        text=f"  {text}  ",
        fg_color=T.pair(palette[0]),
        text_color=T.pair(palette[1]),
        corner_radius=T.RADIUS_CHIP,
        font=font(11, "bold"),
        height=24,
    )


def chip(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """테두리만 있는 작은 보조 버튼."""
    options = dict(
        text=text,
        command=command,
        fg_color="transparent",
        hover_color=T.pair("surface_hover"),
        text_color=T.pair("muted"),
        border_color=T.pair("border"),
        border_width=1,
        corner_radius=T.RADIUS_CHIP,
        font=font(12),
        height=30,
    )
    options.update(kwargs)
    return ctk.CTkButton(master, **options)


def primary(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    options = dict(
        text=text,
        command=command,
        fg_color=T.pair("accent"),
        hover_color=T.pair("accent_hover"),
        text_color=T.DARK["on_accent"],
        corner_radius=T.RADIUS_ITEM,
        font=font(15, "bold"),
        height=50,
    )
    options.update(kwargs)
    return ctk.CTkButton(master, **options)


def secondary(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    options = dict(
        text=text,
        command=command,
        fg_color=T.pair("surface_alt"),
        hover_color=T.pair("surface_hover"),
        text_color=T.pair("text"),
        border_color=T.pair("border"),
        border_width=1,
        corner_radius=T.RADIUS_ITEM,
        font=font(15, "bold"),
        height=50,
    )
    options.update(kwargs)
    return ctk.CTkButton(master, **options)


def label(master, text: str, role: str = "body", **kwargs) -> ctk.CTkLabel:
    roles = {
        "title": (font(22, "bold"), "text"),
        "subtitle": (font(12), "muted"),
        "section": (font(12, "bold"), "muted"),
        "body": (font(13), "text"),
        "hint": (font(12), "muted"),
        "footer": (font(11), "faint"),
        "device": (font(15, "bold"), "text"),
        "serial": (font(11, mono=True), "faint"),
    }
    typeface, color = roles[role]
    options = dict(text=text, font=typeface, text_color=T.pair(color), anchor="w", justify="left")
    options.update(kwargs)
    return ctk.CTkLabel(master, **options)
