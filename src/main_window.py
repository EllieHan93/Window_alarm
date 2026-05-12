import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue
from typing import Optional, Callable

from config_manager import ConfigManager, FixedAlarmConfig, IntervalAlarmConfig
from alarm_manager import AlarmManager
from notification import AlarmNotification
import font_loader
import notifier
import drink_log

_BG = "#ffffff"
_BG2 = "#f3f4f6"
_ACCENT = "#7c3aed"
_FG = "#1f2937"
_FG2 = "#6b7280"
_GREEN = "#059669"
_RED = "#dc2626"

_DAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]
_SOUND_OPTIONS = ["default", "beep", "asterisk"]


def _style_setup(root: tk.Tk) -> None:
    F = font_loader.family()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TButton", background=_ACCENT, foreground="white",
                    font=(F, 9), padding=4)
    style.map("TButton", background=[("active", "#6d28d9")])
    style.configure("Danger.TButton", background=_RED, foreground="white",
                    font=(F, 9), padding=4)
    style.map("Danger.TButton", background=[("active", "#dc2626")])
    style.configure("Treeview", background=_BG2, foreground=_FG,
                    fieldbackground=_BG2, rowheight=26, font=(F, 9))
    style.configure("Treeview.Heading", background=_BG2, foreground=_FG2,
                    font=(F, 9, "bold"))
    style.map("Treeview", background=[("selected", _ACCENT)])
    style.configure("TLabel", background=_BG, foreground=_FG, font=(F, 9))
    style.configure("TFrame", background=_BG)
    style.configure("TCombobox", fieldbackground="white", background="white",
                    foreground=_FG, selectbackground=_ACCENT, font=(F, 9))
    style.configure("TEntry", fieldbackground="white", foreground=_FG,
                    insertcolor=_FG, font=(F, 9))
    style.configure("TCheckbutton", background=_BG, foreground=_FG, font=(F, 9))
    style.configure("TSpinbox", fieldbackground="white", foreground=_FG, font=(F, 9))
    style.configure("TNotebook", background=_BG)
    style.configure("TNotebook.Tab", background=_BG2, foreground=_FG2,
                    padding=[10, 4], font=(F, 9))
    style.map("TNotebook.Tab", background=[("selected", _ACCENT)],
              foreground=[("selected", "white")])


class MainWindow:
    def __init__(self, root: tk.Tk, queue: Queue,
                 alarm_manager: AlarmManager, config: ConfigManager) -> None:
        self._root = root
        self._queue = queue
        self._alarm_mgr = alarm_manager
        self._config = config
        self._authenticated = False

        _style_setup(root)
        self._build_ui()
        self._refresh_display()

    # ------------------------------------------------------------------ #
    #  UI 구성
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        F = font_loader.family()
        self._win = tk.Toplevel(self._root)
        self._win.title("양방구는 게임중")
        self._win.configure(bg=_BG)
        self._win.resizable(False, False)
        self._win.protocol("WM_DELETE_WINDOW", self.hide)
        self._win.withdraw()

        # 헤더 (항상 표시)
        hdr = tk.Frame(self._win, bg=_ACCENT, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🎮  양방구는 게임중", font=(F, 14, "bold"),
                 bg=_ACCENT, fg="white").pack(side="left", padx=16, pady=10)

        # 투명 관리자 버튼 (항상 우측 상단에 숨겨져 있음)
        tk.Button(hdr, text="", bg=_ACCENT, fg=_ACCENT,
                  activebackground=_ACCENT, activeforeground=_ACCENT,
                  relief="flat", bd=0, highlightthickness=0,
                  width=3, cursor="arrow",
                  command=self._on_manage).pack(side="right", padx=2, pady=8)

        # 헤더 버튼 (관리 뷰에서만 pack)
        self._lock_btn = tk.Button(
            hdr, text="🔒", font=(F, 11),
            bg=_ACCENT, fg="white", activebackground="#6d28d9",
            relief="flat", padx=8, cursor="hand2",
            command=self._enter_status_mode)
        self._preview_btn = tk.Button(
            hdr, text="🔔 미리보기", font=(F, 9),
            bg="#6d28d9", fg="white", activebackground="#5b21b6",
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=self._preview_alarm)

        # 상태 패널 (항상 표시)
        sp = tk.Frame(self._win, bg=_BG2, pady=12)
        sp.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(sp, text="사용 시간", font=(F, 9),
                 bg=_BG2, fg=_FG2).grid(row=0, column=0, padx=16, sticky="w")
        self._usage_label = tk.Label(sp, text="--",
                                     font=(F, 16, "bold"),
                                     bg=_BG2, fg=_GREEN)
        self._usage_label.grid(row=1, column=0, padx=16, sticky="w")

        tk.Label(sp, text="다음 알람까지", font=(F, 9),
                 bg=_BG2, fg=_FG2).grid(row=0, column=1, padx=16, sticky="w")
        self._next_label = tk.Label(sp, text="--",
                                    font=(F, 16, "bold"),
                                    bg=_BG2, fg=_FG)
        self._next_label.grid(row=1, column=1, padx=16, sticky="w")
        sp.columnconfigure(0, weight=1)
        sp.columnconfigure(1, weight=1)

        # 상태 뷰 하단 (커피 / 차 버튼)
        self._status_footer = tk.Frame(self._win, bg=_BG)
        btn_row = tk.Frame(self._status_footer, bg=_BG)
        btn_row.pack(pady=10)
        tk.Button(btn_row, text="☕ 커피 마시고싶다",
                  font=(F, 10), bg=_ACCENT, fg="white",
                  activebackground="#6d28d9", relief="flat",
                  padx=12, pady=6, cursor="hand2",
                  command=lambda: self._send_drink("coffee", "☕ 커피 요청이 들어왔어요!")).pack(
                      side="left", padx=(0, 8))
        tk.Button(btn_row, text="🍵 차 마시고싶다",
                  font=(F, 10), bg="#059669", fg="white",
                  activebackground="#047857", relief="flat",
                  padx=12, pady=6, cursor="hand2",
                  command=lambda: self._send_drink("tea", "🍵 차 요청이 들어왔어요!")).pack(
                      side="left")

        # 관리 뷰 본체 (탭)
        self._mgmt_body = ttk.Notebook(self._win)
        self._fixed_tab    = ttk.Frame(self._mgmt_body)
        self._interval_tab = ttk.Frame(self._mgmt_body)
        self._settings_tab = ttk.Frame(self._mgmt_body)
        self._drink_log_tab = ttk.Frame(self._mgmt_body)
        self._mgmt_body.add(self._fixed_tab,    text="  고정 시각 알람  ")
        self._mgmt_body.add(self._interval_tab, text="  인터벌 알람  ")
        self._mgmt_body.add(self._settings_tab, text="  설정  ")
        self._mgmt_body.add(self._drink_log_tab, text="  음료 기록  ")

        self._build_fixed_tab()
        self._build_interval_tab()
        self._build_settings_tab()
        self._build_drink_log_tab()

        # 초기 상태: 상태 뷰
        self._enter_status_mode()

    # ------------------------------------------------------------------ #
    #  모드 전환
    # ------------------------------------------------------------------ #

    def _enter_status_mode(self) -> None:
        self._authenticated = False
        self._mgmt_body.pack_forget()
        self._preview_btn.pack_forget()
        self._lock_btn.pack_forget()
        self._status_footer.pack(fill="x", pady=8)
        self._win.geometry("400x240")

    def _enter_mgmt_mode(self) -> None:
        self._authenticated = True
        self._status_footer.pack_forget()
        self._preview_btn.pack(side="right", padx=12, pady=10)
        self._lock_btn.pack(side="right", padx=4, pady=10)
        self._mgmt_body.pack(fill="both", expand=True, padx=12, pady=10)
        self._win.geometry("520x560")
        self._startup_var.set(self._config.start_with_windows)
        self._refresh_fixed_tree()
        self._refresh_interval_tree()
        self._refresh_drink_log()

    def _on_manage(self) -> None:
        PinDialog(self._win, self._config, on_success=self._enter_mgmt_mode)

    def _send_drink(self, drink_type: str, message: str) -> None:
        from datetime import datetime
        drink_log.record(drink_type)
        text = f"{message}\n{datetime.now().strftime('%Y/%m/%d %H:%M')}"
        notifier.send_telegram(
            self._config.settings.telegram_token,
            self._config.settings.telegram_chat_id,
            text,
        )

    # ------------------------------------------------------------------ #
    #  탭 구성
    # ------------------------------------------------------------------ #

    def _build_fixed_tab(self) -> None:
        f = self._fixed_tab

        btn_frame = tk.Frame(f, bg=_BG)
        btn_frame.pack(fill="x", pady=(8, 4), padx=8)
        ttk.Button(btn_frame, text="+ 추가", command=self._add_fixed).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="✏ 수정", command=self._edit_fixed).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="🗑 삭제", style="Danger.TButton",
                   command=self._delete_fixed).pack(side="left", padx=2)

        cols = ("enabled", "label", "time", "days", "sound")
        self._fixed_tree = ttk.Treeview(f, columns=cols, show="headings", height=10)
        self._fixed_tree.heading("enabled", text="ON")
        self._fixed_tree.heading("label",   text="이름")
        self._fixed_tree.heading("time",    text="시각")
        self._fixed_tree.heading("days",    text="요일")
        self._fixed_tree.heading("sound",   text="소리")
        self._fixed_tree.column("enabled", width=40,  anchor="center")
        self._fixed_tree.column("label",   width=160)
        self._fixed_tree.column("time",    width=70,  anchor="center")
        self._fixed_tree.column("days",    width=100, anchor="center")
        self._fixed_tree.column("sound",   width=80,  anchor="center")
        self._fixed_tree.pack(fill="both", expand=True, padx=8, pady=4)

        ttk.Scrollbar(f, orient="vertical",
                      command=self._fixed_tree.yview).pack(side="right", fill="y")
        self._fixed_tree.configure(
            yscrollcommand=ttk.Scrollbar(f).set)

        self._refresh_fixed_tree()

    def _build_interval_tab(self) -> None:
        f = self._interval_tab

        btn_frame = tk.Frame(f, bg=_BG)
        btn_frame.pack(fill="x", pady=(8, 4), padx=8)
        ttk.Button(btn_frame, text="+ 추가", command=self._add_interval).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="✏ 수정", command=self._edit_interval).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="🗑 삭제", style="Danger.TButton",
                   command=self._delete_interval).pack(side="left", padx=2)

        cols = ("enabled", "label", "interval", "sound")
        self._interval_tree = ttk.Treeview(f, columns=cols, show="headings", height=10)
        self._interval_tree.heading("enabled",  text="ON")
        self._interval_tree.heading("label",    text="이름")
        self._interval_tree.heading("interval", text="간격")
        self._interval_tree.heading("sound",    text="소리")
        self._interval_tree.column("enabled",  width=40,  anchor="center")
        self._interval_tree.column("label",    width=200)
        self._interval_tree.column("interval", width=100, anchor="center")
        self._interval_tree.column("sound",    width=80,  anchor="center")
        self._interval_tree.pack(fill="both", expand=True, padx=8, pady=4)

        self._refresh_interval_tree()

    def _build_settings_tab(self) -> None:
        F = font_loader.family()
        f = self._settings_tab
        pad = {"padx": 16, "pady": 6}

        self._startup_var = tk.BooleanVar(value=self._config.start_with_windows)
        ttk.Checkbutton(f, text="Windows 시작 시 자동 실행",
                        variable=self._startup_var,
                        command=self._on_startup_toggle).pack(anchor="w", **pad)

        self._source_var = tk.StringVar(value=self._config.settings.usage_time_source)
        ttk.Label(f, text="사용 시간 기준").pack(anchor="w", padx=16, pady=(10, 0))
        ttk.Radiobutton(f, text="앱 시작 시간 기준", variable=self._source_var,
                        value="app_start", command=self._on_source_change).pack(anchor="w", padx=24)
        ttk.Radiobutton(f, text="PC 부팅 시간 기준", variable=self._source_var,
                        value="boot", command=self._on_source_change).pack(anchor="w", padx=24)

        # 구분선
        tk.Frame(f, bg="#e5e7eb", height=1).pack(fill="x", padx=16, pady=(12, 4))

        # Telegram 설정
        ttk.Label(f, text="Telegram 알림 설정",
                  font=(F, 9, "bold")).pack(anchor="w", padx=16, pady=(4, 2))
        ttk.Label(f, text="봇 토큰 (@BotFather에서 발급)",
                  font=(F, 8), foreground=_FG2).pack(anchor="w", padx=16)
        self._tg_token_var = tk.StringVar(value=self._config.settings.telegram_token)
        ttk.Entry(f, textvariable=self._tg_token_var, width=44,
                  font=(F, 9)).pack(anchor="w", padx=16, pady=(2, 6))

        ttk.Label(f, text="채팅 ID (Chat ID)",
                  font=(F, 8), foreground=_FG2).pack(anchor="w", padx=16)
        self._tg_chatid_var = tk.StringVar(value=self._config.settings.telegram_chat_id)
        ttk.Entry(f, textvariable=self._tg_chatid_var, width=24,
                  font=(F, 9)).pack(anchor="w", padx=16, pady=(2, 6))

        ttk.Button(f, text="저장", command=self._on_telegram_save).pack(
            anchor="w", padx=16, pady=(0, 4))

    def _build_drink_log_tab(self) -> None:
        F = font_loader.family()
        f = self._drink_log_tab

        btn_frame = tk.Frame(f, bg=_BG)
        btn_frame.pack(fill="x", pady=(8, 4), padx=8)
        ttk.Button(btn_frame, text="🔄 새로고침",
                   command=self._refresh_drink_log).pack(side="left", padx=2)

        cols = ("date", "coffee", "tea", "total")
        self._drink_tree = ttk.Treeview(f, columns=cols, show="headings", height=12)
        self._drink_tree.heading("date",   text="날짜")
        self._drink_tree.heading("coffee", text="☕ 커피")
        self._drink_tree.heading("tea",    text="🍵 차")
        self._drink_tree.heading("total",  text="합계")
        self._drink_tree.column("date",   width=130, anchor="center")
        self._drink_tree.column("coffee", width=80,  anchor="center")
        self._drink_tree.column("tea",    width=80,  anchor="center")
        self._drink_tree.column("total",  width=80,  anchor="center")
        self._drink_tree.pack(fill="both", expand=True, padx=8, pady=4)

        self._refresh_drink_log()

    def _refresh_drink_log(self) -> None:
        self._drink_tree.delete(*self._drink_tree.get_children())
        for date_str, counts in drink_log.get_log().items():
            coffee = counts.get("coffee", 0)
            tea    = counts.get("tea", 0)
            self._drink_tree.insert("", "end", values=(
                date_str, coffee, tea, coffee + tea
            ))

    def _on_startup_toggle(self) -> None:
        self._config.start_with_windows = self._startup_var.get()

    def _on_source_change(self) -> None:
        self._config.settings.usage_time_source = self._source_var.get()
        self._config.save()

    def _on_telegram_save(self) -> None:
        self._config.settings.telegram_token   = self._tg_token_var.get().strip()
        self._config.settings.telegram_chat_id = self._tg_chatid_var.get().strip()
        self._config.save()

    # ------------------------------------------------------------------ #
    #  갱신
    # ------------------------------------------------------------------ #

    def _refresh_fixed_tree(self) -> None:
        self._fixed_tree.delete(*self._fixed_tree.get_children())
        for alarm in self._config.get_fixed_alarms():
            days_str = "매일" if not alarm.days else "".join(_DAYS_KR[d] for d in sorted(alarm.days))
            self._fixed_tree.insert("", "end", iid=alarm.id, values=(
                "✔" if alarm.enabled else "✘",
                alarm.label,
                f"{alarm.hour:02d}:{alarm.minute:02d}",
                days_str,
                alarm.sound,
            ))

    def _refresh_interval_tree(self) -> None:
        self._interval_tree.delete(*self._interval_tree.get_children())
        for alarm in self._config.get_interval_alarms():
            h = alarm.interval_minutes // 60
            m = alarm.interval_minutes % 60
            interval_str = (f"{h}시간 " if h else "") + (f"{m}분" if m else "")
            self._interval_tree.insert("", "end", iid=alarm.id, values=(
                "✔" if alarm.enabled else "✘",
                alarm.label,
                interval_str.strip(),
                alarm.sound,
            ))

    def _refresh_display(self) -> None:
        secs = self._alarm_mgr.get_usage_seconds()
        self._usage_label.config(text=AlarmManager.format_duration(secs))

        next_info = self._alarm_mgr.get_next_alarm_info()
        if next_info:
            label, secs_until = next_info
            self._next_label.config(
                text=f"{AlarmManager.format_duration(secs_until)} ({label})"
            )
        else:
            self._next_label.config(text="없음")

        self._win.after(1000, self._refresh_display)

    # ------------------------------------------------------------------ #
    #  Fixed Alarm CRUD
    # ------------------------------------------------------------------ #

    def _add_fixed(self) -> None:
        FixedAlarmDialog(self._win, None, self._on_save_fixed)

    def _edit_fixed(self) -> None:
        sel = self._fixed_tree.selection()
        if not sel:
            return
        alarm = next((a for a in self._config.get_fixed_alarms() if a.id == sel[0]), None)
        if alarm:
            FixedAlarmDialog(self._win, alarm, self._on_save_fixed)

    def _delete_fixed(self) -> None:
        sel = self._fixed_tree.selection()
        if not sel:
            return
        if messagebox.askyesno("삭제 확인", "선택한 알람을 삭제할까요?", parent=self._win):
            self._config.delete_alarm(sel[0])
            self._alarm_mgr.reload_from_config()
            self._refresh_fixed_tree()

    def _on_save_fixed(self, alarm: FixedAlarmConfig) -> None:
        self._config.upsert_fixed_alarm(alarm)
        self._alarm_mgr.reload_from_config()
        self._refresh_fixed_tree()

    # ------------------------------------------------------------------ #
    #  Interval Alarm CRUD
    # ------------------------------------------------------------------ #

    def _add_interval(self) -> None:
        IntervalAlarmDialog(self._win, None, self._on_save_interval)

    def _edit_interval(self) -> None:
        sel = self._interval_tree.selection()
        if not sel:
            return
        alarm = next((a for a in self._config.get_interval_alarms() if a.id == sel[0]), None)
        if alarm:
            IntervalAlarmDialog(self._win, alarm, self._on_save_interval)

    def _delete_interval(self) -> None:
        sel = self._interval_tree.selection()
        if not sel:
            return
        if messagebox.askyesno("삭제 확인", "선택한 알람을 삭제할까요?", parent=self._win):
            self._config.delete_alarm(sel[0])
            self._alarm_mgr.reload_from_config()
            self._refresh_interval_tree()

    def _on_save_interval(self, alarm: IntervalAlarmConfig) -> None:
        self._config.upsert_interval_alarm(alarm)
        self._alarm_mgr.reload_from_config()
        self._refresh_interval_tree()

    # ------------------------------------------------------------------ #
    #  미리보기 / Show / Hide
    # ------------------------------------------------------------------ #

    def _preview_alarm(self) -> None:
        AlarmNotification.show(
            self._root, "미리보기 알람", "interval", "default",
            usage_seconds=self._alarm_mgr.get_usage_seconds(),
            get_usage_fn=self._alarm_mgr.get_usage_seconds,
        )

    def show(self) -> None:
        self._enter_status_mode()
        self._win.deiconify()
        self._win.lift()
        self._win.focus_force()

    def hide(self) -> None:
        self._win.withdraw()

    def is_visible(self) -> bool:
        return self._win.winfo_viewable()


# ====================================================================== #
#  PIN 다이얼로그
# ====================================================================== #

class PinDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config: ConfigManager,
                 on_success: Callable) -> None:
        super().__init__(parent)
        self.title("관리자 인증")
        self.resizable(False, False)
        self.configure(bg=_BG)
        self.wm_attributes("-topmost", True)
        self.grab_set()
        self._config = config
        self._on_success = on_success
        self._attempts = 0
        self._build()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self) -> None:
        tk.Label(self, text="🔐  관리자 비밀번호",
                 font=(font_loader.family(), 11, "bold"),
                 bg=_BG, fg=_FG).pack(pady=(20, 8), padx=24)

        self._pin_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self._pin_var,
                          show="●", width=12, justify="center",
                          font=(font_loader.family(), 14))
        entry.pack(pady=4, padx=24)
        entry.bind("<Return>", lambda e: self._confirm())
        entry.focus_set()

        self._error_label = tk.Label(self, text="",
                                     font=(font_loader.family(), 9),
                                     bg=_BG, fg=_RED)
        self._error_label.pack(pady=(2, 0))

        btn_frame = tk.Frame(self, bg=_BG)
        btn_frame.pack(pady=(8, 20))
        ttk.Button(btn_frame, text="확인", command=self._confirm).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="취소", command=self.destroy).pack(side="left", padx=6)

    def _confirm(self) -> None:
        pin = self._pin_var.get().strip()
        if self._config.check_pin(pin):
            self.destroy()
            self._on_success()
        else:
            self._attempts += 1
            self._pin_var.set("")
            remaining = 3 - self._attempts
            if remaining <= 0:
                self._error_label.config(text="인증 실패. 잠시 후 다시 시도하세요.")
                self.after(1500, self.destroy)
            else:
                self._error_label.config(
                    text=f"비밀번호가 틀렸습니다. ({remaining}회 남음)")


# ====================================================================== #
#  알람 다이얼로그
# ====================================================================== #

class FixedAlarmDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, alarm: Optional[FixedAlarmConfig],
                 on_save: Callable) -> None:
        super().__init__(parent)
        self._on_save = on_save
        self._alarm = alarm
        self.title("고정 시각 알람 " + ("수정" if alarm else "추가"))
        self.resizable(False, False)
        self.configure(bg=_BG)
        self.wm_attributes("-topmost", True)
        self.grab_set()
        self._build()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self) -> None:
        p = {"padx": 12, "pady": 6}
        a = self._alarm

        tk.Label(self, text="알람 이름", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=0, column=0, sticky="w", **p)
        self._label_var = tk.StringVar(value=a.label if a else "")
        ttk.Entry(self, textvariable=self._label_var, width=24).grid(
            row=0, column=1, columnspan=3, sticky="ew", **p)

        tk.Label(self, text="시각 (HH:MM)", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=1, column=0, sticky="w", **p)
        self._hour_var = tk.StringVar(value=str(a.hour)   if a else "9")
        self._min_var  = tk.StringVar(value=str(a.minute) if a else "0")
        ttk.Spinbox(self, from_=0, to=23, textvariable=self._hour_var,
                    width=5, format="%02.0f").grid(row=1, column=1, **p)
        tk.Label(self, text=":", bg=_BG, fg=_FG).grid(row=1, column=2)
        ttk.Spinbox(self, from_=0, to=59, textvariable=self._min_var,
                    width=5, format="%02.0f").grid(row=1, column=3, **p)

        tk.Label(self, text="요일 (빈칸=매일)", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=2, column=0, sticky="w", **p)
        self._day_vars = []
        day_frame = tk.Frame(self, bg=_BG)
        day_frame.grid(row=2, column=1, columnspan=3, sticky="w", **p)
        existing_days = a.days if a else []
        for i, name in enumerate(_DAYS_KR):
            var = tk.BooleanVar(value=(i in existing_days))
            self._day_vars.append(var)
            ttk.Checkbutton(day_frame, text=name, variable=var).pack(side="left")

        tk.Label(self, text="소리", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=3, column=0, sticky="w", **p)
        self._sound_var = tk.StringVar(value=a.sound if a else "default")
        ttk.Combobox(self, textvariable=self._sound_var,
                     values=_SOUND_OPTIONS, state="readonly",
                     width=12).grid(row=3, column=1, columnspan=2, sticky="w", **p)

        self._enabled_var = tk.BooleanVar(value=a.enabled if a else True)
        ttk.Checkbutton(self, text="활성화", variable=self._enabled_var).grid(
            row=4, column=0, columnspan=2, sticky="w", **p)

        btn_frame = tk.Frame(self, bg=_BG)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="저장",  command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="취소",  command=self.destroy).pack(side="left", padx=6)

    def _save(self) -> None:
        label = self._label_var.get().strip()
        if not label:
            messagebox.showwarning("입력 오류", "알람 이름을 입력하세요.", parent=self)
            return
        try:
            hour   = int(self._hour_var.get())
            minute = int(self._min_var.get())
            assert 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AssertionError):
            messagebox.showwarning("입력 오류", "올바른 시각을 입력하세요.", parent=self)
            return

        days = [i for i, v in enumerate(self._day_vars) if v.get()]
        alarm = FixedAlarmConfig(
            id=self._alarm.id if self._alarm else ConfigManager.new_id(),
            enabled=self._enabled_var.get(),
            label=label, hour=hour, minute=minute, days=days,
            sound=self._sound_var.get(),
            last_fired_date=self._alarm.last_fired_date if self._alarm else "",
        )
        self._on_save(alarm)
        self.destroy()


class IntervalAlarmDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, alarm: Optional[IntervalAlarmConfig],
                 on_save: Callable) -> None:
        super().__init__(parent)
        self._on_save = on_save
        self._alarm = alarm
        self.title("인터벌 알람 " + ("수정" if alarm else "추가"))
        self.resizable(False, False)
        self.configure(bg=_BG)
        self.wm_attributes("-topmost", True)
        self.grab_set()
        self._build()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self) -> None:
        p = {"padx": 12, "pady": 6}
        a = self._alarm

        tk.Label(self, text="알람 이름", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=0, column=0, sticky="w", **p)
        self._label_var = tk.StringVar(value=a.label if a else "")
        ttk.Entry(self, textvariable=self._label_var, width=24).grid(
            row=0, column=1, columnspan=2, sticky="ew", **p)

        tk.Label(self, text="간격 (시간)", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=1, column=0, sticky="w", **p)
        existing_h = (a.interval_minutes // 60) if a else 1
        existing_m = (a.interval_minutes % 60)  if a else 0
        self._hour_var = tk.StringVar(value=str(existing_h))
        self._min_var  = tk.StringVar(value=str(existing_m))
        hf = tk.Frame(self, bg=_BG)
        hf.grid(row=1, column=1, columnspan=2, sticky="w", **p)
        ttk.Spinbox(hf, from_=0, to=23, textvariable=self._hour_var, width=5).pack(side="left")
        tk.Label(hf, text="시간", bg=_BG, fg=_FG).pack(side="left", padx=4)
        ttk.Spinbox(hf, from_=0, to=59, textvariable=self._min_var, width=5).pack(side="left")
        tk.Label(hf, text="분",   bg=_BG, fg=_FG).pack(side="left", padx=4)

        tk.Label(self, text="소리", bg=_BG, fg=_FG2,
                 font=(font_loader.family(), 9)).grid(row=2, column=0, sticky="w", **p)
        self._sound_var = tk.StringVar(value=a.sound if a else "beep")
        ttk.Combobox(self, textvariable=self._sound_var,
                     values=_SOUND_OPTIONS, state="readonly",
                     width=12).grid(row=2, column=1, sticky="w", **p)

        self._enabled_var = tk.BooleanVar(value=a.enabled if a else True)
        ttk.Checkbutton(self, text="활성화", variable=self._enabled_var).grid(
            row=3, column=0, columnspan=2, sticky="w", **p)

        btn_frame = tk.Frame(self, bg=_BG)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="저장",  command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="취소",  command=self.destroy).pack(side="left", padx=6)

    def _save(self) -> None:
        label = self._label_var.get().strip()
        if not label:
            messagebox.showwarning("입력 오류", "알람 이름을 입력하세요.", parent=self)
            return
        try:
            h = int(self._hour_var.get())
            m = int(self._min_var.get())
            assert h * 60 + m > 0
        except (ValueError, AssertionError):
            messagebox.showwarning("입력 오류", "간격은 1분 이상이어야 합니다.", parent=self)
            return

        import time
        alarm = IntervalAlarmConfig(
            id=self._alarm.id if self._alarm else ConfigManager.new_id(),
            enabled=self._enabled_var.get(),
            label=label,
            interval_minutes=h * 60 + m,
            sound=self._sound_var.get(),
            next_fire_epoch=(self._alarm.next_fire_epoch if self._alarm
                             else time.time() + (h * 60 + m) * 60),
        )
        self._on_save(alarm)
        self.destroy()
