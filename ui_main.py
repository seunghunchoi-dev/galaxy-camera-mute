# -*- coding: utf-8 -*-
"""메인 윈도우."""
from __future__ import annotations

import queue
import threading
import tkinter.messagebox as messagebox

import customtkinter as ctk

import adb_core
import appinfo
import ui_theme as T
import ui_widgets as W
from adb_core import AdbError, Device
from ui_about import AboutWindow
from ui_guide import ALLOW_STEP, FIRST_STEP, GuideWindow

AUTO_SCAN_MS = 4000
PUMP_MS = 120


class DeviceCard(ctk.CTkFrame):
    """기기 한 대를 나타내는 카드. 선택 모드에서는 눌러서 고를 수 있다."""

    def __init__(self, master, device: Device, shutter: str, picking: bool, selected: bool, on_click):
        super().__init__(
            master,
            fg_color=T.pair("accent_soft") if selected else T.pair("surface_alt"),
            border_color=T.pair("accent") if selected else T.pair("border"),
            border_width=1,
            corner_radius=T.RADIUS_ITEM,
        )
        self.device = device
        self._on_click = on_click

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=11)

        if picking:
            mark = W.badge(inner, "✓" if selected else "  ", "ok" if selected else "neutral")
            mark.pack(side="left", padx=(0, 10))

        text = ctk.CTkFrame(inner, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True)
        W.label(text, device.name, "device").pack(anchor="w")
        W.label(text, device.serial, "serial").pack(anchor="w")

        if shutter == "무음":
            W.badge(inner, "무음", "ok").pack(side="right")
        elif shutter == "셔터음 켜짐":
            W.badge(inner, "셔터음 켜짐", "warn").pack(side="right")
        elif shutter and shutter != "-":
            W.badge(inner, shutter, "neutral").pack(side="right")

        if device.usable:
            W.badge(inner, "연결됨", "ok").pack(side="right", padx=(0, 6))
        else:
            W.badge(inner, device.state_label, "danger").pack(side="right", padx=(0, 6))

        self._bind_all(self)

    def _bind_all(self, widget) -> None:
        widget.bind("<Button-1>", self._clicked)
        for child in widget.winfo_children():
            self._bind_all(child)

    def _clicked(self, _event=None) -> None:
        self._on_click(self.device.serial)


class MainWindow(ctk.CTk):
    def __init__(self, dark: bool = True) -> None:
        super().__init__(fg_color=T.pair("bg"))
        self.dark = dark
        ctk.set_appearance_mode("dark" if dark else "light")

        self.ui_queue: queue.Queue = queue.Queue()
        self.devices: list[Device] = []
        self.shutter_values: dict[str, str] = {}
        self.selected: set[str] = set()
        self.scanning = False
        self.applying = False
        self._signature: tuple | None = None
        self._status_kind = "muted"
        self._guide_shown = False
        self.guide: GuideWindow | None = None
        self.about: AboutWindow | None = None

        self.title(appinfo.APP_NAME)
        self.geometry("660x780")
        self.minsize(580, 660)
        self._set_icon()

        self._build()
        self._pump()
        self.after(80, self._startup)
        self.after(AUTO_SCAN_MS, self._auto_scan)

    def _set_icon(self) -> None:
        path = adb_core.resource_dir() / "app.ico"
        if path.is_file():
            try:
                self.iconbitmap(str(path))
            except Exception:
                pass

    # ------------------------------------------------------------- 화면 구성
    def _build(self) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=20, pady=(18, 14))

        self._build_header(root)
        self._build_status(root)
        self._build_devices(root)
        self._build_actions(root)
        self._build_log(root)
        self._build_footer(root)

    def _build_header(self, root) -> None:
        row = ctk.CTkFrame(root, fg_color="transparent")
        row.pack(fill="x", pady=(0, 14))

        text = ctk.CTkFrame(row, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True)
        W.label(text, appinfo.APP_NAME, "title").pack(anchor="w")
        W.label(text, appinfo.APP_TAGLINE, "subtitle").pack(anchor="w", pady=(2, 0))

        W.chip(row, "정보", self.show_about, width=56).pack(side="right", anchor="n")
        self.theme_btn = W.chip(row, "라이트" if self.dark else "다크", self.toggle_theme, width=62)
        self.theme_btn.pack(side="right", anchor="n", padx=(0, 6))
        W.chip(row, "설정 방법", lambda: self.show_guide(FIRST_STEP), width=86).pack(
            side="right", anchor="n", padx=(0, 6)
        )

    def _build_status(self, root) -> None:
        card = W.card(root)
        card.pack(fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        self.status_dot = ctk.CTkLabel(
            inner, text="●", font=W.font(15), text_color=T.pair("muted"), width=14
        )
        self.status_dot.pack(side="left", padx=(0, 10))
        self.status_label = W.label(inner, "기기를 확인하는 중…", "hint")
        self.status_label.pack(side="left", fill="x", expand=True)
        self.refresh_btn = W.chip(inner, "새로고침", lambda: self.scan(manual=True), width=76)
        self.refresh_btn.pack(side="right")

    def _build_devices(self, root) -> None:
        head = ctk.CTkFrame(root, fg_color="transparent")
        head.pack(fill="x", pady=(16, 6))
        W.label(head, "연결된 기기", "section").pack(side="left")

        self.only_selected = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            head,
            text="선택한 기기에만 적용",
            variable=self.only_selected,
            command=self._render_devices,
            font=W.font(12),
            text_color=T.pair("muted"),
            fg_color=T.pair("accent"),
            hover_color=T.pair("accent_hover"),
            border_color=T.pair("border"),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            border_width=2,
        ).pack(side="right")

        self.device_host = ctk.CTkScrollableFrame(
            root,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=T.pair("border"),
            scrollbar_button_hover_color=T.pair("faint"),
        )
        self.device_host.pack(fill="both", expand=True)

    def _build_actions(self, root) -> None:
        row = ctk.CTkFrame(root, fg_color="transparent")
        row.pack(fill="x", pady=(14, 0))
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        self.mute_btn = W.primary(
            row, "카메라 무음 적용", lambda: self.apply(adb_core.MUTE_VALUE, "무음 적용")
        )
        self.mute_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.unmute_btn = W.secondary(
            row, "셔터음 원복", lambda: self.apply(adb_core.UNMUTE_VALUE, "셔터음 원복")
        )
        self.unmute_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.with_routine = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            root,
            text="무음 적용 시 빅스비 루틴도 추가 (카메라를 켜면 소리 모드 무음)",
            variable=self.with_routine,
            font=W.font(12),
            text_color=T.pair("muted"),
            fg_color=T.pair("accent"),
            hover_color=T.pair("accent_hover"),
            border_color=T.pair("border"),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            border_width=2,
        ).pack(anchor="w", pady=(10, 0))

    def _build_log(self, root) -> None:
        box = ctk.CTkFrame(root, fg_color="transparent")
        box.pack(fill="x", pady=(12, 0))

        self.log_open = False
        self.log_btn = ctk.CTkButton(
            box,
            text="진행 상황 보기  ▾",
            command=self._toggle_log,
            fg_color="transparent",
            hover_color=T.pair("surface_hover"),
            text_color=T.pair("muted"),
            font=W.font(12),
            width=120,
            height=26,
            corner_radius=T.RADIUS_CHIP,
        )
        self.log_btn.pack(anchor="w")

        self.log_view = ctk.CTkTextbox(
            box,
            height=150,
            fg_color=T.pair("surface_alt"),
            border_color=T.pair("border"),
            border_width=1,
            corner_radius=10,
            font=W.font(11, mono=True),
            text_color=T.pair("muted"),
            wrap="word",
        )
        for kind in ("ok", "warn", "danger", "muted"):
            try:
                self.log_view.tag_config(kind, foreground=T.colors(self.dark)[kind])
            except Exception:
                pass
        self.log_view.configure(state="disabled")

    def _build_footer(self, root) -> None:
        self.footer = W.label(
            root,
            f"{appinfo.COPYRIGHT} · {appinfo.HOMEPAGE.replace('https://', '')} · {appinfo.EMAIL}",
            "footer",
            anchor="center",
        )
        self.footer.pack(fill="x", pady=(10, 0))

    # ------------------------------------------------------------------ 테마
    def toggle_theme(self) -> None:
        self.dark = not self.dark
        ctk.set_appearance_mode("dark" if self.dark else "light")
        self.theme_btn.configure(text="라이트" if self.dark else "다크")
        self._paint_dot()
        for kind in ("ok", "warn", "danger", "muted"):
            try:
                self.log_view.tag_config(kind, foreground=T.colors(self.dark)[kind])
            except Exception:
                pass
        if self.guide is not None and self.guide.alive():
            self.guide.refresh_theme(self.dark)

    # ------------------------------------------------------------- 상태/로그
    def _paint_dot(self, kind: str | None = None) -> None:
        if kind is not None:
            self._status_kind = kind
        self.status_dot.configure(text_color=T.pair(self._status_kind))

    def set_status(self, text: str, kind: str = "muted") -> None:
        self.status_label.configure(text=text)
        self._paint_dot(kind)

    def log(self, message: str, kind: str = "muted") -> None:
        self.log_view.configure(state="normal")
        self.log_view.insert("end", message + "\n", kind)
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def _toggle_log(self) -> None:
        self.log_open = not self.log_open
        if self.log_open:
            self.log_view.pack(fill="x", pady=(6, 0))
            self.log_btn.configure(text="진행 상황 숨기기  ▴")
        else:
            self.log_view.pack_forget()
            self.log_btn.configure(text="진행 상황 보기  ▾")

    def _update_buttons(self) -> None:
        state = "disabled" if self.applying else "normal"
        self.mute_btn.configure(state=state)
        self.unmute_btn.configure(state=state)
        self.refresh_btn.configure(state=state)

    # --------------------------------------------------------- 백그라운드 작업
    def post(self, func, *args) -> None:
        self.ui_queue.put((func, args))

    def _pump(self) -> None:
        while True:
            try:
                func, args = self.ui_queue.get_nowait()
            except queue.Empty:
                break
            try:
                func(*args)
            except Exception as exc:  # UI 갱신 실패가 앱을 멈추지 않도록
                self.log(f"화면 갱신 오류: {exc}", "danger")
        self.after(PUMP_MS, self._pump)

    def run_bg(self, fn, *args, on_done=None, on_failed=None) -> None:
        def worker() -> None:
            try:
                result = fn(*args)
            except Exception as exc:
                if on_failed:
                    self.post(on_failed, str(exc))
            else:
                if on_done:
                    self.post(on_done, result)

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------ 시작
    def _startup(self) -> None:
        if adb_core.adb_available():
            self.scan(manual=True)
            return

        agreed = messagebox.askyesno(
            appinfo.APP_NAME,
            "휴대폰과 통신하려면 Google의 Android SDK Platform-Tools(adb)가 필요합니다.\n\n"
            "Google 공식 서버에서 지금 내려받을까요?\n"
            f"약 10MB · 저장 위치: {adb_core.data_dir() / 'platform-tools'}",
            parent=self,
        )
        if not agreed:
            self.set_status("adb가 없어 기기를 확인할 수 없습니다.", "danger")
            return

        self.set_status("Platform-Tools를 내려받는 중…", "accent")
        self.log("Google 공식 서버에서 Platform-Tools를 내려받습니다.")
        self.run_bg(
            adb_core.download_platform_tools,
            self._download_progress,
            on_done=self._download_done,
            on_failed=self._download_failed,
        )

    def _download_progress(self, read: int, total: int) -> None:
        if total > 0:
            self.post(self.set_status, f"Platform-Tools 내려받는 중… {read * 100 // total}%", "accent")

    def _download_done(self, _path) -> None:
        self.log("Platform-Tools 설치 완료", "ok")
        self.scan(manual=True)

    def _download_failed(self, message: str) -> None:
        self.set_status("adb를 준비하지 못했습니다.", "danger")
        self.log(message, "danger")
        messagebox.showwarning(
            appinfo.APP_NAME,
            f"Platform-Tools를 내려받지 못했습니다.\n\n{message}\n\n"
            "직접 받으려면 아래 주소에서 내려받아 프로그램과 같은 폴더에 "
            "'platform-tools' 로 풀어주세요.\n"
            f"{adb_core.PLATFORM_TOOLS_URL}",
            parent=self,
        )

    # ------------------------------------------------------------------ 스캔
    def _auto_scan(self) -> None:
        if not (self.scanning or self.applying):
            self.scan(manual=False)
        self.after(AUTO_SCAN_MS, self._auto_scan)

    def scan(self, manual: bool = False, keep_status: bool = False) -> None:
        if self.scanning or self.applying or not adb_core.adb_available():
            return
        self.scanning = True
        if manual and not keep_status:
            self.set_status("기기를 확인하는 중…")
        self.run_bg(
            self._scan_work,
            manual,
            on_done=lambda payload: self._scan_done(payload, keep_status),
            on_failed=self._scan_failed,
        )

    def _scan_work(self, manual: bool):
        devices = adb_core.list_devices()
        signature = tuple((d.serial, d.state) for d in devices)
        if not manual and signature == self._signature:
            return None
        self._signature = signature

        values: dict[str, str] = {}
        for device in devices:
            if not device.usable:
                continue
            try:
                values[device.serial] = adb_core.describe_value(
                    adb_core.get_shutter_value(device.serial)
                )
            except AdbError as exc:
                values[device.serial] = f"조회 실패({exc})"
        return devices, values

    def _scan_failed(self, message: str) -> None:
        self.scanning = False
        self.set_status("adb를 실행할 수 없습니다.", "danger")
        self.log(message, "danger")

    def _scan_done(self, payload, keep_status: bool) -> None:
        self.scanning = False
        if payload is None:
            return

        devices, values = payload
        had_devices = bool(self.devices)
        self.devices = devices
        self.shutter_values = values
        self.selected &= {d.serial for d in devices}
        self._render_devices()

        usable = [d for d in devices if d.usable]
        if not keep_status:
            if not devices:
                self.set_status("연결된 기기가 없습니다. 케이블과 USB 디버깅을 확인해주세요.", "warn")
                if had_devices:
                    self.log("기기 연결이 끊겼습니다.", "warn")
            elif usable:
                self.set_status(f"기기 {len(devices)}대 연결됨 (사용 가능 {len(usable)}대)", "ok")
            else:
                self.set_status("기기를 찾았지만 USB 디버깅 승인이 필요합니다.", "warn")

            for device in devices:
                if device.usable:
                    self.log(f"{device.name} ({device.serial}) 연결됨")
                else:
                    self.log(f"{device.name} ({device.serial}) · {device.state_label}", "warn")

        self._maybe_guide(devices)

    def _render_devices(self) -> None:
        for child in self.device_host.winfo_children():
            child.destroy()

        if not self.devices:
            self._empty_state()
            return

        picking = self.only_selected.get()
        for device in self.devices:
            DeviceCard(
                self.device_host,
                device,
                self.shutter_values.get(device.serial, "-"),
                picking,
                picking and device.serial in self.selected,
                self._toggle_device,
            ).pack(fill="x", pady=(0, 8))

    def _empty_state(self) -> None:
        card = W.card(self.device_host)
        card.pack(fill="x", pady=(0, 8))
        W.label(card, "연결된 기기가 없습니다", "device", anchor="center").pack(
            fill="x", padx=20, pady=(26, 4)
        )
        W.label(
            card,
            "USB 케이블을 연결하고 휴대폰에서 USB 디버깅을 켜주세요.",
            "hint",
            anchor="center",
        ).pack(fill="x", padx=20)
        W.chip(card, "설정 방법 보기", lambda: self.show_guide(FIRST_STEP), width=120).pack(
            pady=(12, 26)
        )

    def _toggle_device(self, serial: str) -> None:
        if not self.only_selected.get():
            self.only_selected.set(True)
            self.selected = {serial}
        elif serial in self.selected:
            self.selected.discard(serial)
        else:
            self.selected.add(serial)
        self._render_devices()

    # ------------------------------------------------------------------ 적용
    def targets(self) -> list[Device]:
        if self.only_selected.get():
            return [d for d in self.devices if d.serial in self.selected]
        return list(self.devices)

    def apply(self, value: str, label: str) -> None:
        if self.applying:
            return
        if self.scanning:
            # 자동 스캔과 겹친 클릭을 버리지 않고 스캔 직후 이어서 실행한다
            self.after(150, lambda: self.apply(value, label))
            return

        targets = self.targets()
        if not targets:
            if self.only_selected.get() and self.devices:
                messagebox.showinfo(appinfo.APP_NAME, "목록에서 적용할 기기를 선택해주세요.", parent=self)
            else:
                self.show_guide(FIRST_STEP)
            return

        usable = [d for d in targets if d.usable]
        for device in (d for d in targets if not d.usable):
            self.log(f"건너뜀: {device.name} · {device.hint()}", "warn")
        if not usable:
            self.show_guide(ALLOW_STEP)
            return

        self.applying = True
        self._update_buttons()
        self.set_status(f"{label} 중…", "accent")
        self.log(f"[{label}] 대상 {len(usable)}대 · {adb_core.SHUTTER_KEY} = {value}")
        routine = value == adb_core.MUTE_VALUE and self.with_routine.get()
        self.run_bg(
            self._apply_work,
            usable,
            value,
            routine,
            on_done=lambda result: self._apply_done(result, label),
            on_failed=lambda message: self._apply_done(([], [message], [], []), label),
        )

    @staticmethod
    def _apply_work(devices: list[Device], value: str, routine: bool):
        ok, errors = [], []
        routine_ok, routine_errors = [], []
        for device in devices:
            name = f"{device.name} ({device.serial})"
            try:
                adb_core.set_shutter_value(device.serial, value)
            except AdbError as exc:
                errors.append(f"{name} · {exc}")
                continue
            ok.append(name)
            if not routine:
                continue
            try:
                adb_core.add_routine(device.serial)
            except AdbError as exc:
                routine_errors.append(f"{name} · {exc}")
            else:
                routine_ok.append(name)
        return ok, errors, routine_ok, routine_errors

    def _apply_done(self, result, label: str) -> None:
        ok, errors, routine_ok, routine_errors = result
        self.applying = False
        self._update_buttons()

        for line in ok:
            self.log(f"완료: {line} → {label}", "ok")
        for line in errors:
            self.log(f"실패: {line}", "danger")

        total = len(ok) + len(errors)
        if errors and not ok:
            self.set_status(f"{label} 실패", "danger")
            messagebox.showerror(
                appinfo.APP_NAME, f"{label}에 실패했습니다.\n\n" + "\n".join(errors), parent=self
            )
        elif errors:
            self.set_status(f"{label} 일부 성공 ({len(ok)}/{total})", "warn")
        else:
            self.set_status(f"{label} 완료 ({len(ok)}대)", "ok")
            if label == "무음 적용":
                self.log("카메라 앱을 완전히 종료 후 다시 열어 촬영해 확인하세요.")
                self.log("One UI 업데이트 후에는 설정이 돌아갈 수 있습니다.")

        for line in routine_ok:
            self.log(f"루틴 가져오기 화면 열림: {line}", "ok")
        for line in routine_errors:
            self.log(f"루틴 추가 실패: {line}", "warn")
        if routine_ok:
            messagebox.showinfo(
                appinfo.APP_NAME,
                "휴대폰에 '카메라 무음' 루틴 화면이 열렸습니다.\n\n"
                "화면 아래의 [저장]을 눌러야 루틴이 추가됩니다.\n"
                "(카메라 앱을 켜면 소리 모드가 무음이 되고, 끄면 원래대로 돌아갑니다)",
                parent=self,
            )
        if label == "셔터음 원복" and not errors:
            self.log("빅스비 루틴을 추가했었다면 '모드 및 루틴' 앱에서 직접 삭제해주세요.")

        self._signature = None
        self.scan(keep_status=True)

    # ------------------------------------------------------------------ 창들
    def show_guide(self, index: int = FIRST_STEP) -> None:
        if self.guide is None or not self.guide.alive():
            self.guide = GuideWindow(self, self.dark)
        self.guide.show_step(index)
        self.guide.deiconify()
        self.guide.lift()
        self.guide.focus_force()

    def _maybe_guide(self, devices: list[Device]) -> None:
        blocked = [d for d in devices if d.state in ("unauthorized", "authorizing")]
        if not blocked:
            if any(d.usable for d in devices):
                self._guide_shown = False
            return
        if self._guide_shown:
            return
        self._guide_shown = True
        self.log("인증되지 않은 기기가 있어 설정 방법을 엽니다.", "warn")
        self.show_guide(ALLOW_STEP)

    def show_about(self) -> None:
        if self.about is None or not self.about.winfo_exists():
            self.about = AboutWindow(self, self.dark)
        self.about.deiconify()
        self.about.lift()
        self.about.focus_force()
