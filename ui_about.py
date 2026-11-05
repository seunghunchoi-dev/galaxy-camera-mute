# -*- coding: utf-8 -*-
"""정보 · 라이선스 창."""
from __future__ import annotations

import webbrowser

import customtkinter as ctk

import adb_core
import appinfo
import ui_theme as T
import ui_widgets as W


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, master, dark: bool) -> None:
        super().__init__(master, fg_color=T.pair("bg"))
        self.title(f"{appinfo.APP_NAME} 정보")
        self.geometry("540x780")
        self.resizable(False, False)

        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=22, pady=18)

        # 하단 버튼 줄을 먼저 배치해야 내용이 길어져도 밀려나지 않는다
        bottom = ctk.CTkFrame(root, fg_color="transparent")
        bottom.pack(fill="x", side="bottom", pady=(14, 0))
        W.chip(bottom, "라이선스 전문 보기", self.show_licenses, width=150).pack(side="left")
        W.chip(bottom, "닫기", self.withdraw, width=70).pack(side="right")

        W.label(root, f"{appinfo.APP_NAME}  v{appinfo.VERSION}", "title").pack(anchor="w")
        W.label(root, appinfo.APP_TAGLINE, "subtitle").pack(anchor="w", pady=(2, 14))

        card = W.card(root)
        card.pack(fill="x")
        self._row(card, "저작자", appinfo.AUTHOR, first=True)
        self._row(card, "홈페이지", appinfo.HOMEPAGE, link=appinfo.HOMEPAGE)
        self._row(card, "이메일", appinfo.EMAIL, link=f"mailto:{appinfo.EMAIL}")
        self._row(card, "라이선스", f"{appinfo.LICENSE_NAME} · {appinfo.COPYRIGHT}", last=True)

        W.label(root, "사용한 오픈소스", "section").pack(anchor="w", pady=(16, 6))
        oss = W.card(root)
        oss.pack(fill="x")
        for i, (name, license_name, url, _note) in enumerate(appinfo.THIRD_PARTY):
            block = ctk.CTkFrame(oss, fg_color="transparent")
            block.pack(
                fill="x",
                padx=16,
                pady=(14 if i == 0 else 8, 14 if i == len(appinfo.THIRD_PARTY) - 1 else 0),
            )
            W.label(block, name, "device").pack(anchor="w")
            line = W.label(block, f"{license_name} · {url}", "footer")
            line.pack(anchor="w")
            self._as_link(line, url)

        W.label(
            root,
            "이 프로그램은 본인 소유 기기에 사용하세요. "
            "타인의 동의 없는 촬영에 사용해 발생하는 문제에 대해 저작자는 책임지지 않습니다.",
            "footer",
            wraplength=460,
        ).pack(anchor="w", pady=(16, 0))

        self.licenses: LicenseWindow | None = None
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda _e: self.withdraw())

    def show_licenses(self) -> None:
        if self.licenses is None or not self.licenses.winfo_exists():
            self.licenses = LicenseWindow(self)
        self.licenses.deiconify()
        self.licenses.lift()
        self.licenses.focus_force()

    def _row(self, card, key: str, value: str, link: str | None = None,
             first: bool = False, last: bool = False) -> None:
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(14 if first else 5, 14 if last else 0))
        W.label(row, key, "section", width=90).pack(side="left", anchor="w")
        value_label = W.label(row, value, "hint")
        value_label.pack(side="left", fill="x", expand=True)
        if link:
            self._as_link(value_label, link)

    @staticmethod
    def _as_link(widget: ctk.CTkLabel, url: str) -> None:
        widget.configure(text_color=T.pair("accent"), cursor="hand2")
        widget.bind("<Button-1>", lambda _e: webbrowser.open(url))


class LicenseWindow(ctk.CTkToplevel):
    """프로그램에 함께 들어 있는 라이선스 전문을 보여준다.

    MIT·BSD는 배포물에 저작권 고지와 라이선스 전문을 포함하도록 요구한다.
    파일 하나로 배포하기 위해 전문을 exe 안에 넣고 여기서 읽어 보여준다.
    """

    def __init__(self, master) -> None:
        super().__init__(master, fg_color=T.pair("bg"))
        self.title("라이선스 전문")
        self.geometry("720x620")

        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=18, pady=16)

        self.files = sorted((adb_core.resource_dir() / "licenses").glob("*.txt"))

        bar = ctk.CTkFrame(root, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 10))
        self.buttons: list[ctk.CTkButton] = []
        for index, path in enumerate(self.files):
            name = self._short(path.stem)
            button = W.chip(bar, name, lambda i=index: self.show(i), width=len(name) * 9 + 22)
            button.pack(side="left", padx=(0, 5))
            self.buttons.append(button)

        self.view = ctk.CTkTextbox(
            root,
            fg_color=T.pair("surface_alt"),
            border_color=T.pair("border"),
            border_width=1,
            corner_radius=10,
            font=W.font(11, mono=True),
            text_color=T.pair("muted"),
            wrap="word",
        )
        self.view.pack(fill="both", expand=True)

        W.chip(root, "닫기", self.withdraw, width=70).pack(side="bottom", anchor="e", pady=(12, 0))
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda _e: self.withdraw())

        if self.files:
            self.show(0)
        else:
            self._set_text("라이선스 파일을 찾을 수 없습니다.")

    @staticmethod
    def _short(stem: str) -> str:
        """버튼에 쓸 짧은 이름."""
        if stem.startswith("GalaxyCameraMute"):
            return "이 프로그램"
        return stem.split("-")[0]

    def _set_text(self, text: str) -> None:
        self.view.configure(state="normal")
        self.view.delete("1.0", "end")
        self.view.insert("1.0", text)
        self.view.configure(state="disabled")

    def show(self, index: int) -> None:
        try:
            text = self.files[index].read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            text = f"파일을 읽지 못했습니다: {exc}"
        self._set_text(text)
        for i, button in enumerate(self.buttons):
            chosen = i == index
            button.configure(
                fg_color=T.pair("accent_soft") if chosen else "transparent",
                border_color=T.pair("accent") if chosen else T.pair("border"),
                text_color=T.pair("accent") if chosen else T.pair("muted"),
            )
