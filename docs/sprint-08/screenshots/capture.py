"""Sprint 08 스크린샷 캡처."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab
import font_loader

OUT = os.path.dirname(os.path.abspath(__file__))


def grab(win, path):
    win.update_idletasks(); win.update(); time.sleep(0.4)
    x, y = win.winfo_rootx(), win.winfo_rooty()
    w, h = win.winfo_width(), win.winfo_height()
    ImageGrab.grab((x, y, x+w, y+h)).save(path)
    print(f"saved: {path}")


def main():
    root = tk.Tk(); root.withdraw()
    font_loader.load()
    F = font_loader.family()

    _ACCENT = "#7c3aed"; _BG = "#ffffff"; _BG2 = "#f3f4f6"
    _FG = "#1f2937"; _FG2 = "#6b7280"; _GREEN = "#059669"

    # ── 1. 상태 뷰 ──────────────────────────────────────────────────────
    w1 = tk.Toplevel(root)
    w1.title("TP Alarm"); w1.geometry("400x240")
    w1.configure(bg=_BG); w1.resizable(False, False)

    hdr = tk.Frame(w1, bg=_ACCENT, height=50)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr, text="⏰  TP Alarm", font=(F, 14, "bold"),
             bg=_ACCENT, fg="white").pack(side="left", padx=16, pady=10)
    # 투명 숨김 버튼
    tk.Button(hdr, text="", bg=_ACCENT, fg=_ACCENT,
              activebackground=_ACCENT, relief="flat",
              bd=0, highlightthickness=0, width=3,
              cursor="arrow").pack(side="right", padx=2, pady=8)

    sp = tk.Frame(w1, bg=_BG2, pady=12)
    sp.pack(fill="x", padx=12, pady=(10,0))
    tk.Label(sp, text="사용 시간",     font=(F, 9),  bg=_BG2, fg=_FG2).grid(row=0,column=0,padx=16,sticky="w")
    tk.Label(sp, text="1시간 23분",    font=(F, 16,"bold"), bg=_BG2, fg=_GREEN).grid(row=1,column=0,padx=16,sticky="w")
    tk.Label(sp, text="다음 알람까지", font=(F, 9),  bg=_BG2, fg=_FG2).grid(row=0,column=1,padx=16,sticky="w")
    tk.Label(sp, text="24분 15초",     font=(F, 16,"bold"), bg=_BG2, fg=_FG).grid( row=1,column=1,padx=16,sticky="w")
    sp.columnconfigure(0, weight=1); sp.columnconfigure(1, weight=1)

    sf = tk.Frame(w1, bg=_BG); sf.pack(fill="x", pady=8)
    br = tk.Frame(sf, bg=_BG); br.pack(pady=10)
    tk.Button(br, text="☕ 커피 마시고싶다", font=(F,10), bg=_ACCENT, fg="white",
              relief="flat", padx=12, pady=6).pack(side="left", padx=(0,8))
    tk.Button(br, text="🍵 차 마시고싶다", font=(F,10), bg="#059669", fg="white",
              relief="flat", padx=12, pady=6).pack(side="left")

    w1.lift()
    root.after(600, lambda: grab(w1, os.path.join(OUT, "01_status_view.png")))

    # ── 2. 설정 탭 (Telegram) ────────────────────────────────────────────
    def show_settings():
        w2 = tk.Toplevel(root); w2.title("TP Alarm - 설정")
        w2.geometry("400x320"); w2.configure(bg=_BG)
        style = ttk.Style(w2); style.theme_use("clam")
        style.configure("TLabel", background=_BG, foreground=_FG, font=(F,9))
        style.configure("TEntry", font=(F,9))
        style.configure("TButton", background=_ACCENT, foreground="white", font=(F,9), padding=4)
        style.map("TButton", background=[("active","#6d28d9")])

        f = tk.Frame(w2, bg=_BG); f.pack(fill="both", expand=True, padx=16, pady=12)
        ttk.Label(f, text="Telegram 알림 설정", font=(F,10,"bold")).pack(anchor="w", pady=(0,4))
        ttk.Label(f, text="봇 토큰 (@BotFather에서 발급)", font=(F,8), foreground=_FG2).pack(anchor="w")
        ttk.Entry(f, width=44).pack(anchor="w", pady=(2,8))
        ttk.Label(f, text="채팅 ID (Chat ID)", font=(F,8), foreground=_FG2).pack(anchor="w")
        ttk.Entry(f, width=24).pack(anchor="w", pady=(2,8))
        ttk.Button(f, text="저장").pack(anchor="w", pady=(0,4))

        tk.Frame(f, bg="#e5e7eb", height=1).pack(fill="x", pady=8)
        ttk.Label(f, text="Telegram 봇 설정 방법", font=(F,9,"bold")).pack(anchor="w")
        ttk.Label(f, text="1. Telegram에서 @BotFather 검색\n2. /newbot 명령으로 봇 생성\n3. 발급된 토큰을 위 입력란에 붙여넣기\n4. 봇에게 메시지 보낸 후 Chat ID 확인",
                  font=(F,8), foreground=_FG2, justify="left").pack(anchor="w")

        w2.lift()
        root.after(600, lambda: grab(w2, os.path.join(OUT, "02_telegram_settings.png")))
        root.after(1400, w2.destroy)

    root.after(1300, show_settings)
    root.after(3000, root.quit)
    root.mainloop()
    print("Done.")


if __name__ == "__main__":
    main()
