import math
import threading
import time
import tkinter as tk
import winsound
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
import font_loader

_SOUNDS = {
    "default": ("SystemExclamation", winsound.SND_ALIAS),
    "beep": None,
    "asterisk": ("SystemAsterisk", winsound.SND_ALIAS),
}

_W, _H       = 360, 260
_CANVAS_H    = 196
_DURATION_MS = 4000
_FRAME_MS    = 33

_FADEIN_STEPS = 10
_FADEIN_MS    = 25

_ACCENT_COLORS = {
    "fixed":    "#E52521",
    "interval": "#049CD8",
}

_TRANSPARENT_COLOR = "#010101"  # chroma key: canvas 배경 → 윈도우 투명 처리

_IMG_PATH = Path(__file__).parent / "source" / "Image.png"


def _play_sound_async(sound: str) -> None:
    def _play():
        entry = _SOUNDS.get(sound, _SOUNDS["default"])
        if entry is None:
            winsound.Beep(880, 400)
            winsound.Beep(1100, 400)
        else:
            try:
                winsound.PlaySound(entry[0], entry[1])
            except Exception:
                winsound.Beep(880, 300)
    threading.Thread(target=_play, daemon=True).start()


def _fmt_usage(secs: int) -> str:
    h, rem = divmod(secs, 3600)
    m, s   = divmod(rem, 60)
    if h > 0:
        return f"{h}시간 {m:02d}분"
    return f"{m}분 {s:02d}초"


def _load_image(max_w: int, max_h: int):
    """PNG를 로드해 ImageTk.PhotoImage로 반환. 실패 시 None."""
    try:
        from PIL import Image, ImageTk
        img = Image.open(_IMG_PATH).convert("RGBA")
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def _draw_scene(canvas, frame: int, label: str,
                alarm_type: str, accent: str,
                usage_seconds: Optional[int],
                photo) -> None:
    canvas.delete("all")
    W, H = _W, _CANVAS_H

    # 이미지 (하단 중앙 배치)
    if photo:
        img_y = H - photo.height() // 2 - 4
        canvas.create_image(W // 2, img_y, anchor="center", image=photo)

    # 말풍선 위치 (위아래 bobbing)
    bob = int(3 * math.sin(frame * 0.08))

    bw = 190          # 말풍선 너비
    bh = 58           # 말풍선 높이
    bx1 = (W - bw) // 2
    bx2 = bx1 + bw
    by1 = 6 + bob
    by2 = by1 + bh

    # 말풍선 그림자
    canvas.create_rectangle(bx1 + 3, by1 + 3, bx2 + 3, by2 + 3,
                            fill="#e2e8f0", outline="")
    # 말풍선 본체
    canvas.create_rectangle(bx1, by1, bx2, by2,
                            fill="white", outline=accent, width=2)
    # 말풍선 꼬리
    mx = W // 2
    canvas.create_polygon(mx - 8, by2,
                          mx + 8, by2,
                          mx,     by2 + 12,
                          fill="white", outline=accent, width=1)
    canvas.create_line(mx - 6, by2, mx + 6, by2, fill="white", width=3)

    # 말풍선 텍스트
    type_text = "고정 시각 알람" if alarm_type == "fixed" else "인터벌 알람"
    canvas.create_text(W // 2, by1 + 13,
                       text=type_text,
                       font=(font_loader.family(), 7), fill="#555555", anchor="center")
    canvas.create_text(W // 2, by1 + 34,
                       text=label,
                       font=(font_loader.family(), 10, "bold"), fill="#000000",
                       anchor="center", width=bw - 16)


class AlarmNotification:
    @staticmethod
    def show(
        root: tk.Tk,
        label: str,
        alarm_type: str,
        sound: str,
        usage_seconds: Optional[int] = None,
        get_usage_fn: Optional[Callable[[], int]] = None,
    ) -> None:
        _play_sound_async(sound)

        dialog = tk.Toplevel(root)
        dialog.overrideredirect(True)
        dialog.wm_attributes("-topmost", True)
        dialog.wm_attributes("-alpha", 0.0)

        sw = dialog.winfo_screenwidth()
        sh = dialog.winfo_screenheight()
        dialog.geometry(f"{_W}x{_H}+{sw - _W - 20}+20")

        accent = _ACCENT_COLORS.get(alarm_type, _ACCENT_COLORS["fixed"])

        inner = tk.Frame(dialog, bg="#ffffff")
        inner.pack(fill="both", expand=True)

        # 타이틀 바 (드래그 핸들)
        title_bar = tk.Frame(inner, bg=accent, height=22)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="🕹️  양방구는 게임중",
                 font=(font_loader.family(), 8), bg=accent, fg="white").pack(side="left", padx=8)

        # 캔버스 (이미지 + 말풍선)
        canvas = tk.Canvas(inner, width=_W, height=_CANVAS_H,
                           bg=_TRANSPARENT_COLOR, highlightthickness=0)
        dialog.wm_attributes("-transparentcolor", _TRANSPARENT_COLOR)
        canvas.pack()

        # 이미지 로드 (말풍선 아래 공간에 맞게)
        photo = _load_image(_W - 20, _CANVAS_H - 70)
        canvas.photo = photo  # GC 방지

        # 하단 패널
        bottom = tk.Frame(inner, bg="#ffffff")
        bottom.pack(fill="x", padx=14, pady=(5, 4))

        info_frame = tk.Frame(bottom, bg="#ffffff")
        info_frame.pack(anchor="w", pady=(0, 4))

        current_time = datetime.now().strftime("%Y/%m/%d %H:%M")
        tk.Label(info_frame, text=current_time,
                 font=(font_loader.family(), 10, "bold"), fg="#000000",
                 bg="#ffffff").pack(side="left")

        if alarm_type == "interval" and usage_seconds is not None:
            tk.Label(info_frame, text="  |",
                     font=(font_loader.family(), 10), fg="#bbbbbb",
                     bg="#ffffff").pack(side="left")
            tk.Label(info_frame, text=f"  {_fmt_usage(usage_seconds)} 사용",
                     font=(font_loader.family(), 9), fg="#555555",
                     bg="#ffffff").pack(side="left")

        btn_row = tk.Frame(bottom, bg="#ffffff")
        btn_row.pack(anchor="w")

        closed = [False]

        def close():
            if not closed[0] and dialog.winfo_exists():
                closed[0] = True
                dialog.destroy()

        def on_snooze():
            close()
            _schedule_snooze(root, label, alarm_type, sound,
                             minutes=5, get_usage_fn=get_usage_fn)

        tk.Button(btn_row, text="5분 후 다시",
                  font=(font_loader.family(), 8), bg="#e0e0e0", fg="#000000",
                  activebackground="#c8c8c8", relief="flat",
                  padx=6, pady=2, cursor="hand2",
                  command=on_snooze).pack(side="left", padx=(0, 4))
        tk.Button(btn_row, text="닫기",
                  font=(font_loader.family(), 8), bg="#e0e0e0", fg="#000000",
                  activebackground="#c8c8c8", relief="flat",
                  padx=6, pady=2, cursor="hand2",
                  command=close).pack(side="left")

        # 카운트다운 바
        bar_bg = tk.Frame(inner, bg="#e5e7eb", height=4)
        bar_bg.pack(fill="x", side="bottom")
        bar_bg.pack_propagate(False)
        bar_fill = tk.Frame(bar_bg, bg=accent, height=4)
        bar_fill.place(x=0, y=0, relwidth=1.0, height=4)

        # 드래그 이동
        drag = {"x": 0, "y": 0}

        def _drag_start(e):
            drag["x"] = e.x_root - dialog.winfo_x()
            drag["y"] = e.y_root - dialog.winfo_y()

        def _drag_move(e):
            dialog.geometry(f"+{e.x_root - drag['x']}+{e.y_root - drag['y']}")

        for widget in (title_bar, canvas):
            widget.bind("<ButtonPress-1>", _drag_start)
            widget.bind("<B1-Motion>",     _drag_move)

        title_bar.configure(cursor="fleur")
        canvas.configure(cursor="fleur")

        # 애니메이션 + 4초 자동 닫힘
        frame_count = [0]
        start_ts    = [time.time()]

        def animate():
            if closed[0] or not dialog.winfo_exists():
                return

            elapsed_ms = (time.time() - start_ts[0]) * 1000
            t = min(elapsed_ms / _DURATION_MS, 1.0)

            bar_fill.place(x=0, y=0, relwidth=max(0.0, 1.0 - t), height=4)
            _draw_scene(canvas, frame_count[0], label,
                        alarm_type, accent, usage_seconds, photo)
            frame_count[0] += 1

            if t >= 1.0:
                close()
                return

            dialog.after(_FRAME_MS, animate)

        # 페이드인 후 애니메이션 시작
        def start_fadein():
            step = [0]

            def _step():
                if not dialog.winfo_exists():
                    return
                step[0] += 1
                dialog.wm_attributes("-alpha", min(step[0] / _FADEIN_STEPS, 1.0))
                if step[0] < _FADEIN_STEPS:
                    dialog.after(_FADEIN_MS, _step)
                else:
                    start_ts[0] = time.time()
                    dialog.after(10, animate)

            dialog.after(_FADEIN_MS, _step)

        dialog.after(10, start_fadein)
        dialog.lift()


def _schedule_snooze(
    root: tk.Tk,
    label: str,
    alarm_type: str,
    sound: str,
    minutes: int,
    get_usage_fn: Optional[Callable[[], int]] = None,
) -> None:
    def _fire():
        secs = get_usage_fn() if get_usage_fn else None
        AlarmNotification.show(root, label, alarm_type, sound,
                               usage_seconds=secs, get_usage_fn=get_usage_fn)
    root.after(minutes * 60 * 1000, _fire)
