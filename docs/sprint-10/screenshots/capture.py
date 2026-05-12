"""Sprint 10 스크린샷 자동 캡처 (PIN 우회, 직접 모드 전환)."""
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
from notification import AlarmNotification
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


def step1_status():
    window.show()
    root.update_idletasks()
    root.after(400, step2_snap_status)


def step2_snap_status():
    _snap("01_status_view.png", window._win)
    root.after(200, step3_mgmt)


def step3_mgmt():
    window._enter_mgmt_mode()
    root.update_idletasks()
    root.after(400, step4_snap_mgmt)


def step4_snap_mgmt():
    _snap("02_mgmt_fixed.png", window._win)
    root.after(200, step5_interval)


def step5_interval():
    window._mgmt_body.select(window._interval_tab)
    root.update_idletasks()
    root.after(300, step6_snap_interval)


def step6_snap_interval():
    _snap("03_mgmt_interval.png", window._win)
    root.after(200, step7_settings)


def step7_settings():
    window._mgmt_body.select(window._settings_tab)
    root.update_idletasks()
    root.after(300, step8_snap_settings)


def step8_snap_settings():
    _snap("04_mgmt_settings.png", window._win)
    root.after(200, step9_drink)


def step9_drink():
    window._mgmt_body.select(window._drink_log_tab)
    root.update_idletasks()
    root.after(300, step10_snap_drink)


def step10_snap_drink():
    _snap("05_mgmt_drink_log.png", window._win)
    root.after(200, step11_game)


def step11_game():
    window._mgmt_body.select(window._game_log_tab)
    root.update_idletasks()
    root.after(300, step12_snap_game)


def step12_snap_game():
    _snap("06_mgmt_game_log.png", window._win)
    root.after(200, step13_notification)


def step13_notification():
    AlarmNotification.show(
        root, "테스트 알람", "fixed", "default",
        usage_seconds=5400,
        get_usage_fn=lambda: 5400,
    )
    root.update_idletasks()
    root.after(800, step14_snap_notification)


def step14_snap_notification():
    sw = root.winfo_screenwidth()
    img = ImageGrab.grab(bbox=(sw - 400, 0, sw, 280))
    img.save(OUT / "07_notification_fixed.png")
    print("  saved: 07_notification_fixed.png")
    root.after(200, step15_notification2)


def step15_notification2():
    AlarmNotification.show(
        root, "인터벌 테스트", "interval", "default",
        usage_seconds=5400,
        get_usage_fn=lambda: 5400,
    )
    root.update_idletasks()
    root.after(800, step16_snap_notification2)


def step16_snap_notification2():
    sw = root.winfo_screenwidth()
    img = ImageGrab.grab(bbox=(sw - 400, 0, sw, 280))
    img.save(OUT / "08_notification_interval.png")
    print("  saved: 08_notification_interval.png")
    root.after(500, root.quit)


root.after(300, step1_status)
print("캡처 시작...")
root.mainloop()
print("완료.")
