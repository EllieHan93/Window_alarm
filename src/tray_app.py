import math
import threading
import time
from datetime import datetime
from queue import Queue
from typing import NamedTuple

import pystray
from PIL import Image, ImageDraw

from alarm_manager import AlarmManager


class Command(NamedTuple):
    action: str   # "open_window" | "quit" | "alarm_fired"
    payload: dict


def _create_icon_image() -> Image.Image:
    now = datetime.now()
    size = 64
    cx = cy = size / 2

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([2, 2, size - 2, size - 2],
                 fill=(4, 156, 216), outline=(251, 208, 0), width=2)

    r = size / 2 - 6
    for deg in [0, 90, 180, 270]:
        rad = math.radians(deg - 90)
        x1 = cx + (r - 5) * math.cos(rad)
        y1 = cy + (r - 5) * math.sin(rad)
        x2 = cx + r * math.cos(rad)
        y2 = cy + r * math.sin(rad)
        draw.line([x1, y1, x2, y2], fill=(255, 255, 255, 180), width=2)

    h_rad = math.radians((now.hour % 12 + now.minute / 60) * 30 - 90)
    draw.line([cx, cy,
               cx + 12 * math.cos(h_rad),
               cy + 12 * math.sin(h_rad)],
              fill=(200, 200, 255), width=2)

    m_rad = math.radians(now.minute * 6 - 90)
    draw.line([cx, cy,
               cx + 18 * math.cos(m_rad),
               cy + 18 * math.sin(m_rad)],
              fill="white", width=3)

    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill="white")
    return img


class TrayApp:
    def __init__(self, queue: Queue, alarm_manager: AlarmManager) -> None:
        self._queue = queue
        self._alarm_mgr = alarm_manager
        self._icon: pystray.Icon | None = None

    def run(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("창 열기", self._on_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("종료", self._on_quit),
        )
        self._icon = pystray.Icon(
            name="TP_Alarm",
            icon=_create_icon_image(),
            title=self._get_tooltip(),
            menu=menu,
        )
        threading.Thread(target=self._tooltip_updater, daemon=True).start()
        self._icon.run()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()

    def _get_tooltip(self) -> str:
        now = datetime.now()
        date_str = now.strftime("%Y/%m/%d (%a)")
        usage = AlarmManager.format_duration(self._alarm_mgr.get_usage_seconds())
        next_info = self._alarm_mgr.get_next_alarm_info()
        next_str = (
            f"\n다음 알람: {next_info[0]} ({AlarmManager.format_duration(next_info[1])})"
            if next_info else ""
        )
        count = self._alarm_mgr.get_active_alarm_count()
        alarm_str = f"활성 알람: {count}개" if count else "활성 알람 없음"
        return f"양방구는 게임중\n{date_str}\n사용 시간: {usage}{next_str}\n{alarm_str}"

    def _tooltip_updater(self) -> None:
        while True:
            time.sleep(5)
            if self._icon:
                self._icon.icon  = _create_icon_image()
                self._icon.title = self._get_tooltip()

    def _on_open(self, icon, item) -> None:
        self._queue.put(Command("open_window", {}))

    def _on_quit(self, icon, item) -> None:
        self._queue.put(Command("quit", {}))
