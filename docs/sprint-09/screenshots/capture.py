"""Sprint 09 스크린샷 자동 캡처 (PIN 우회, 직접 모드 전환)."""
import sys
import time
from pathlib import Path
from datetime import datetime
from queue import Queue

sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

import tkinter as tk
import font_loader
from config_manager import ConfigManager
from alarm_manager import AlarmManager
from main_window import MainWindow
from PIL import ImageGrab

OUT = Path(__file__).parent


def _snap(name: str, win: tk.Toplevel) -> None:
    win.update_idletasks()
    time.sleep(0.3)
    x = win.winfo_rootx()
    y = win.winfo_rooty()
    w = win.winfo_width()
    h = win.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(OUT / name)
    print(f"  saved: {name}  ({w}x{h})")


root = tk.Tk()
root.withdraw()
font_loader.load()

config = ConfigManager()
config.load()
alarm_mgr = AlarmManager(config, datetime.now())
window = MainWindow(root, Queue(), alarm_mgr, config)


def step1():
    window.show()
    root.update_idletasks()
    root.after(400, step2)


def step2():
    _snap("01_status_view.png", window._win)
    root.after(200, step3)


def step3():
    window._enter_mgmt_mode()
    root.update_idletasks()
    root.after(400, step4)


def step4():
    _snap("02_mgmt_view.png", window._win)
    root.after(200, step5)


def step5():
    window._mgmt_body.select(window._drink_log_tab)
    root.update_idletasks()
    root.after(300, step6)


def step6():
    _snap("03_drink_log_tab.png", window._win)
    root.after(200, step7)


def step7():
    window._mgmt_body.select(window._game_log_tab)
    root.update_idletasks()
    root.after(300, step8)


def step8():
    _snap("04_game_log_tab.png", window._win)
    root.after(300, root.quit)


root.after(300, step1)
print("캡처 시작...")
root.mainloop()
print("완료.")
