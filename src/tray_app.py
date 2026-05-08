import threading
from queue import Queue
from typing import NamedTuple

import pystray
from PIL import Image, ImageDraw, ImageFont

from alarm_manager import AlarmManager


class Command(NamedTuple):
    action: str   # "open_window" | "quit" | "alarm_fired"
    payload: dict


def _create_icon_image(usage_text: str = "") -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 원형 배경
    draw.ellipse([2, 2, size - 2, size - 2], fill=(124, 58, 237), outline=(200, 180, 255), width=2)

    # 시계 눈금 (12, 3, 6, 9시)
    import math
    cx, cy, r = size / 2, size / 2, size / 2 - 6
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle - 90)
        x1 = cx + (r - 4) * math.cos(rad)
        y1 = cy + (r - 4) * math.sin(rad)
        x2 = cx + r * math.cos(rad)
        y2 = cy + r * math.sin(rad)
        draw.line([x1, y1, x2, y2], fill=(255, 255, 255, 200), width=2)

    # 시침 (12시 방향 고정 아이콘)
    draw.line([cx, cy, cx, cy - 14], fill="white", width=3)
    draw.line([cx, cy, cx + 10, cy + 6], fill=(200, 200, 255), width=2)

    # 중심점
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill="white")

    return img


class TrayApp:
    def __init__(self, queue: Queue, alarm_manager: AlarmManager) -> None:
        self._queue = queue
        self._alarm_mgr = alarm_manager
        self._icon: pystray.Icon | None = None

    def run(self) -> None:
        img = _create_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("창 열기", self._on_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("종료", self._on_quit),
        )
        self._icon = pystray.Icon(
            name="TP_Alarm",
            icon=img,
            title=self._get_tooltip(),
            menu=menu,
        )
        # 툴팁 갱신 타이머 (별도 스레드)
        threading.Thread(target=self._tooltip_updater, daemon=True).start()
        self._icon.run()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()

    def _get_tooltip(self) -> str:
        secs = self._alarm_mgr.get_usage_seconds()
        usage = AlarmManager.format_duration(secs)
        next_info = self._alarm_mgr.get_next_alarm_info()
        if next_info:
            label, secs_until = next_info
            next_str = f"\n다음 알람: {label} ({AlarmManager.format_duration(secs_until)})"
        else:
            next_str = ""
        return f"TP Alarm\n사용 시간: {usage}{next_str}"

    def _tooltip_updater(self) -> None:
        import time
        while True:
            time.sleep(30)
            if self._icon:
                self._icon.title = self._get_tooltip()

    def _on_open(self, icon, item) -> None:
        self._queue.put(Command("open_window", {}))

    def _on_quit(self, icon, item) -> None:
        self._queue.put(Command("quit", {}))
