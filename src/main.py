import sys
import threading
import time
from datetime import datetime
from queue import Queue, Empty

import tkinter as tk

from config_manager import ConfigManager
from alarm_manager import AlarmManager, AlarmEvent
from main_window import MainWindow
from tray_app import TrayApp, Command
from notification import AlarmNotification
import font_loader
import game_log


def _scheduler_loop(alarm_mgr: AlarmManager, queue: Queue, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        alarm_mgr.tick(queue)
        time.sleep(1)


def _process_queue(root: tk.Tk, window: MainWindow, tray: TrayApp,
                   queue: Queue, stop_event: threading.Event,
                   alarm_mgr: AlarmManager = None) -> None:
    try:
        while True:
            item = queue.get_nowait()
            if isinstance(item, Command):
                if item.action == "open_window":
                    window.show()
                elif item.action == "quit":
                    if alarm_mgr:
                        game_log.update(alarm_mgr.get_usage_seconds())
                    stop_event.set()
                    tray.stop()
                    root.quit()
                    return
            elif isinstance(item, AlarmEvent):
                AlarmNotification.show(
                    root,
                    label=item.label,
                    alarm_type=item.alarm_type,
                    sound=item.sound,
                    usage_seconds=alarm_mgr.get_usage_seconds() if alarm_mgr else None,
                    get_usage_fn=alarm_mgr.get_usage_seconds if alarm_mgr else None,
                )
    except Empty:
        pass

    if not stop_event.is_set():
        root.after(200, _process_queue, root, window, tray, queue, stop_event, alarm_mgr)


def main() -> None:
    app_start = datetime.now()

    config = ConfigManager()
    config.load()

    queue: Queue = Queue()
    stop_event = threading.Event()

    alarm_mgr = AlarmManager(config, app_start)

    root = tk.Tk()
    root.withdraw()
    root.title("양방구는 게임중")

    font_loader.load()  # Tk 생성 후 커스텀 폰트 등록

    window = MainWindow(root, queue, alarm_mgr, config)
    tray = TrayApp(queue, alarm_mgr)

    tray_thread = threading.Thread(target=tray.run, daemon=True, name="TrayThread")
    sched_thread = threading.Thread(
        target=_scheduler_loop, args=(alarm_mgr, queue, stop_event),
        daemon=True, name="SchedulerThread"
    )

    tray_thread.start()
    sched_thread.start()

    root.after(200, _process_queue, root, window, tray, queue, stop_event, alarm_mgr)

    # 시작 시 메인 창 자동 표시
    root.after(300, window.show)

    root.mainloop()


if __name__ == "__main__":
    main()
