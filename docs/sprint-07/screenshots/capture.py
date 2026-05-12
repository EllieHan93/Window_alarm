"""Sprint 07 스크린샷 캡처 스크립트."""
import sys, os, time, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab

OUT = os.path.dirname(os.path.abspath(__file__))


def grab_window(win, path):
    win.update_idletasks()
    win.update()
    time.sleep(0.3)
    x = win.winfo_rootx()
    y = win.winfo_rooty()
    w = win.winfo_width()
    h = win.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(path)
    print(f"saved: {path}")


def main():
    root = tk.Tk()
    root.withdraw()

    _ACCENT = "#7c3aed"
    _BG = "#ffffff"
    _BG2 = "#f3f4f6"
    _FG = "#1f2937"
    _FG2 = "#6b7280"
    _GREEN = "#059669"
    _RED = "#dc2626"

    # ── 1. 상태 뷰 ──────────────────────────────────────────────────────
    w1 = tk.Toplevel(root)
    w1.title("TP Alarm")
    w1.geometry("320x200")
    w1.configure(bg=_BG)
    w1.resizable(False, False)

    hdr = tk.Frame(w1, bg=_ACCENT, height=50)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr, text="⏰  TP Alarm", font=("맑은 고딕", 14, "bold"),
             bg=_ACCENT, fg="white").pack(side="left", padx=16, pady=10)

    sp = tk.Frame(w1, bg=_BG2, pady=12)
    sp.pack(fill="x", padx=12, pady=(10, 0))
    tk.Label(sp, text="사용 시간",     font=("맑은 고딕", 9),  bg=_BG2, fg=_FG2).grid(row=0, column=0, padx=16, sticky="w")
    tk.Label(sp, text="1시간 23분",    font=("맑은 고딕", 18, "bold"), bg=_BG2, fg=_GREEN).grid(row=1, column=0, padx=16, sticky="w")
    tk.Label(sp, text="다음 알람까지", font=("맑은 고딕", 9),  bg=_BG2, fg=_FG2).grid(row=0, column=1, padx=16, sticky="w")
    tk.Label(sp, text="24분 15초",     font=("맑은 고딕", 18, "bold"), bg=_BG2, fg=_FG).grid( row=1, column=1, padx=16, sticky="w")
    sp.columnconfigure(0, weight=1); sp.columnconfigure(1, weight=1)

    sf = tk.Frame(w1, bg=_BG)
    sf.pack(fill="x", pady=16)
    tk.Button(sf, text="관리자 설정", font=("맑은 고딕", 10),
              bg=_ACCENT, fg="white", relief="flat", padx=16, pady=6).pack()

    w1.lift()
    root.after(600, lambda: grab_window(w1, os.path.join(OUT, "01_status_view.png")))

    # ── 2. PIN 다이얼로그 ────────────────────────────────────────────────
    def show_pin():
        w2 = tk.Toplevel(root)
        w2.title("관리자 인증")
        w2.resizable(False, False)
        w2.configure(bg=_BG)
        w2.wm_attributes("-topmost", True)

        tk.Label(w2, text="🔐  관리자 비밀번호",
                 font=("맑은 고딕", 11, "bold"), bg=_BG, fg=_FG).pack(pady=(20, 8), padx=24)
        pin_var = tk.StringVar()
        e = ttk.Entry(w2, textvariable=pin_var, show="●", width=12,
                      justify="center", font=("맑은 고딕", 14))
        e.pack(pady=4, padx=24)
        tk.Label(w2, text="비밀번호가 틀렸습니다. (2회 남음)",
                 font=("맑은 고딕", 9), bg=_BG, fg=_RED).pack(pady=(2, 0))
        bf = tk.Frame(w2, bg=_BG); bf.pack(pady=(8, 20))
        style = ttk.Style(root)
        style.theme_use("clam")
        ttk.Button(bf, text="확인").pack(side="left", padx=6)
        ttk.Button(bf, text="취소").pack(side="left", padx=6)

        w2.update_idletasks()
        x = w1.winfo_rootx() + (w1.winfo_width()  - w2.winfo_reqwidth())  // 2
        y = w1.winfo_rooty() + (w1.winfo_height() - w2.winfo_reqheight()) // 2
        w2.geometry(f"+{x}+{y}")
        w2.lift()
        root.after(600, lambda: grab_window(w2, os.path.join(OUT, "02_pin_dialog.png")))
        root.after(1400, w2.destroy)

    root.after(1300, show_pin)

    # ── 3. 관리 뷰 ──────────────────────────────────────────────────────
    def show_mgmt():
        w3 = tk.Toplevel(root)
        w3.title("TP Alarm")
        w3.geometry("520x560")
        w3.configure(bg=_BG)

        style = ttk.Style(w3)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", background=_BG2, foreground=_FG2, padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", _ACCENT)], foreground=[("selected", "white")])
        style.configure("Treeview", background=_BG2, foreground=_FG, fieldbackground=_BG2, rowheight=26, font=("맑은 고딕", 9))
        style.configure("Treeview.Heading", background=_BG2, foreground=_FG2, font=("맑은 고딕", 9, "bold"))
        style.map("Treeview", background=[("selected", _ACCENT)])

        hdr3 = tk.Frame(w3, bg=_ACCENT, height=50)
        hdr3.pack(fill="x"); hdr3.pack_propagate(False)
        tk.Label(hdr3, text="⏰  TP Alarm", font=("맑은 고딕", 14, "bold"),
                 bg=_ACCENT, fg="white").pack(side="left", padx=16, pady=10)
        tk.Button(hdr3, text="🔒", font=("맑은 고딕", 11),
                  bg=_ACCENT, fg="white", relief="flat", padx=8).pack(side="right", padx=4, pady=10)
        tk.Button(hdr3, text="🔔 미리보기", font=("맑은 고딕", 9),
                  bg="#6d28d9", fg="white", relief="flat", padx=10, pady=4).pack(side="right", padx=12, pady=10)

        sp3 = tk.Frame(w3, bg=_BG2, pady=12)
        sp3.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(sp3, text="사용 시간",     font=("맑은 고딕", 9),  bg=_BG2, fg=_FG2).grid(row=0, column=0, padx=16, sticky="w")
        tk.Label(sp3, text="1시간 23분",    font=("맑은 고딕", 18, "bold"), bg=_BG2, fg=_GREEN).grid(row=1, column=0, padx=16, sticky="w")
        tk.Label(sp3, text="다음 알람까지", font=("맑은 고딕", 9),  bg=_BG2, fg=_FG2).grid(row=0, column=1, padx=16, sticky="w")
        tk.Label(sp3, text="24분 15초",     font=("맑은 고딕", 18, "bold"), bg=_BG2, fg=_FG).grid(row=1, column=1, padx=16, sticky="w")
        sp3.columnconfigure(0, weight=1); sp3.columnconfigure(1, weight=1)

        nb = ttk.Notebook(w3)
        nb.pack(fill="both", expand=True, padx=12, pady=10)
        ft = ttk.Frame(nb); it = ttk.Frame(nb); st = ttk.Frame(nb)
        nb.add(ft, text="  고정 시각 알람  ")
        nb.add(it, text="  인터벌 알람  ")
        nb.add(st, text="  설정  ")

        bf2 = tk.Frame(ft, bg=_BG); bf2.pack(fill="x", pady=(8,4), padx=8)
        style.configure("TButton", background=_ACCENT, foreground="white", font=("맑은 고딕", 9), padding=4)
        style.map("TButton", background=[("active", "#6d28d9")])
        ttk.Button(bf2, text="+ 추가").pack(side="left", padx=2)
        ttk.Button(bf2, text="✏ 수정").pack(side="left", padx=2)

        cols = ("enabled", "label", "time", "days", "sound")
        tree = ttk.Treeview(ft, columns=cols, show="headings", height=8)
        for col, txt, w in [("enabled","ON",40),("label","이름",160),("time","시각",70),("days","요일",100),("sound","소리",80)]:
            tree.heading(col, text=txt); tree.column(col, width=w, anchor="center" if col!="label" else "w")
        tree.insert("", "end", values=("✔","오전 업무 시작","09:00","매일","default"))
        tree.insert("", "end", values=("✔","점심 시간","12:00","월화수목금","beep"))
        tree.pack(fill="both", expand=True, padx=8, pady=4)

        w3.lift()
        root.after(600, lambda: grab_window(w3, os.path.join(OUT, "03_mgmt_view.png")))
        root.after(1400, w3.destroy)

    root.after(2500, show_mgmt)
    root.after(4200, root.quit)
    root.mainloop()
    print("All screenshots captured.")


if __name__ == "__main__":
    main()
