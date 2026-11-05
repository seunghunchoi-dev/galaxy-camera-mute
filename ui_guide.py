# -*- coding: utf-8 -*-
"""USB 디버깅 설정 방법을 실제 휴대폰 화면으로 보여주는 안내 창."""
from __future__ import annotations

import customtkinter as ctk
from PIL import Image

import ui_theme as T
import ui_widgets as W
from adb_core import resource_dir
from guide_steps import ALLOW_STEP, FIRST_STEP, IMAGE_DIR, STEPS, TITLE

__all__ = ["GuideWindow", "FIRST_STEP", "ALLOW_STEP"]


class GuideWindow(ctk.CTkToplevel):
    def __init__(self, master, dark: bool) -> None:
        super().__init__(master, fg_color=T.pair("bg"))
        self.title(TITLE)
        self.geometry("560x740")
        self.resizable(False, False)
        self.index = 0
        self._images: dict[str, ctk.CTkImage | None] = {}

        self._build()
        self.show_step(0)
        self.bind("<Left>", lambda _e: self.show_step(self.index - 1))
        self.bind("<Right>", lambda _e: self.show_step(self.index + 1))
        self.bind("<Escape>", lambda _e: self.withdraw())
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    # ------------------------------------------------------------- 화면 구성
    def _build(self) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=20, pady=16)

        # 아래쪽 버튼 줄을 먼저 배치해 내용에 밀려 잘리지 않게 한다
        nav = ctk.CTkFrame(root, fg_color="transparent")
        nav.pack(fill="x", side="bottom", pady=(14, 0))
        self.prev_btn = W.chip(nav, "←  이전", lambda: self.show_step(self.index - 1), width=76)
        self.prev_btn.pack(side="left")
        self.next_btn = W.chip(nav, "다음  →", lambda: self.show_step(self.index + 1), width=76)
        self.next_btn.pack(side="left", padx=(6, 0))
        W.chip(nav, "닫기", self.withdraw, width=64).pack(side="right")

        head = ctk.CTkFrame(root, fg_color="transparent")
        head.pack(fill="x")
        self.heading = W.label(head, "", "title")
        self.heading.pack(side="left")
        self.counter = W.label(head, "", "subtitle", anchor="e")
        self.counter.pack(side="right")

        rail = ctk.CTkFrame(root, fg_color="transparent")
        rail.pack(fill="x", pady=(10, 12))
        self.chips: list[ctk.CTkButton] = []
        for i in range(len(STEPS)):
            chip = W.chip(rail, str(i + 1), lambda n=i: self.show_step(n), width=32)
            chip.pack(side="left", padx=(0, 4))
            self.chips.append(chip)

        card = W.card(root)
        card.pack(fill="x")
        self.image_label = ctk.CTkLabel(card, text="")
        self.image_label.pack(padx=14, pady=(14, 6))
        self.caption = W.label(card, "", "footer", anchor="center")
        self.caption.pack(fill="x", padx=14, pady=(0, 12))

        self.body = W.label(root, "", "hint", wraplength=500, justify="left")
        self.body.pack(fill="x", pady=(14, 0))


    # ------------------------------------------------------------------ 표시
    def refresh_theme(self, dark: bool) -> None:
        # 색은 (라이트, 다크) 쌍으로 지정해 뒀으므로 appearance mode만 바뀌면 따라온다.
        self.configure(fg_color=T.pair("bg"))

    def _image(self, name: str) -> ctk.CTkImage | None:
        if name not in self._images:
            path = resource_dir() / IMAGE_DIR / name
            try:
                picture = Image.open(path)
                width = 460
                height = round(picture.height * width / picture.width)
                self._images[name] = ctk.CTkImage(
                    light_image=picture, dark_image=picture, size=(width, height)
                )
            except Exception:
                self._images[name] = None
        return self._images[name]

    def show_step(self, index: int) -> None:
        self.index = max(0, min(index, len(STEPS) - 1))
        step = STEPS[self.index]

        self.heading.configure(text=step["heading"])
        self.counter.configure(text=f"{self.index + 1} / {len(STEPS)}")
        self.body.configure(text=step["body"])

        image = self._image(step["image"])
        if image is None:
            self.image_label.configure(image=None, text="(가이드 이미지를 찾을 수 없습니다)")
            self.caption.configure(text="")
        else:
            self.image_label.configure(image=image, text="")
            self.caption.configure(text=step["caption"])

        for i, chip in enumerate(self.chips):
            selected = i == self.index
            chip.configure(
                fg_color=T.pair("accent_soft") if selected else "transparent",
                border_color=T.pair("accent") if selected else T.pair("border"),
                text_color=T.pair("accent") if selected else T.pair("muted"),
            )
        self.prev_btn.configure(state="normal" if self.index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.index < len(STEPS) - 1 else "disabled")
