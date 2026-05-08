import time
from datetime import datetime
from queue import Queue
from typing import NamedTuple, Optional

import psutil

from config_manager import ConfigManager, FixedAlarmConfig, IntervalAlarmConfig


class AlarmEvent(NamedTuple):
    alarm_id: str
    label: str
    alarm_type: str  # "fixed" or "interval"
    sound: str


class AlarmManager:
    def __init__(self, config: ConfigManager, app_start_time: datetime) -> None:
        self._config = config
        self._app_start_time = app_start_time
        self._fixed_alarms: list[FixedAlarmConfig] = []
        self._interval_alarms: list[IntervalAlarmConfig] = []
        self.reload_from_config()
        self._init_interval_alarms()

    def reload_from_config(self) -> None:
        self._fixed_alarms = self._config.get_fixed_alarms()
        self._interval_alarms = self._config.get_interval_alarms()

    def _init_interval_alarms(self) -> None:
        now_epoch = time.time()
        changed = False
        for alarm in self._interval_alarms:
            if not alarm.enabled:
                continue
            if alarm.next_fire_epoch == 0.0:
                alarm.next_fire_epoch = now_epoch + alarm.interval_minutes * 60
                self._config.upsert_interval_alarm(alarm)
                changed = True

    def tick(self, queue: Queue) -> None:
        now = datetime.now()
        self._check_fixed_alarms(now, queue)
        self._check_interval_alarms(queue)

    def _check_fixed_alarms(self, now: datetime, queue: Queue) -> None:
        if now.second != 0:
            return
        today_str = now.date().isoformat()
        for alarm in self._fixed_alarms:
            if not alarm.enabled:
                continue
            if alarm.days and now.weekday() not in alarm.days:
                continue
            if now.hour == alarm.hour and now.minute == alarm.minute:
                if alarm.last_fired_date != today_str:
                    alarm.last_fired_date = today_str
                    self._config.upsert_fixed_alarm(alarm)
                    queue.put(AlarmEvent(
                        alarm_id=alarm.id,
                        label=alarm.label,
                        alarm_type="fixed",
                        sound=alarm.sound,
                    ))

    def _check_interval_alarms(self, queue: Queue) -> None:
        now_epoch = time.time()
        for alarm in self._interval_alarms:
            if not alarm.enabled:
                continue
            if alarm.next_fire_epoch == 0.0:
                continue
            if now_epoch >= alarm.next_fire_epoch:
                alarm.next_fire_epoch = now_epoch + alarm.interval_minutes * 60
                self._config.upsert_interval_alarm(alarm)
                queue.put(AlarmEvent(
                    alarm_id=alarm.id,
                    label=alarm.label,
                    alarm_type="interval",
                    sound=alarm.sound,
                ))

    def get_usage_seconds(self) -> int:
        source = self._config.settings.usage_time_source
        if source == "boot":
            return int(time.time() - psutil.boot_time())
        return int((datetime.now() - self._app_start_time).total_seconds())

    def get_next_alarm_info(self) -> Optional[tuple[str, int]]:
        now = datetime.now()
        now_epoch = time.time()
        candidates: list[tuple[str, int]] = []

        for alarm in self._fixed_alarms:
            if not alarm.enabled:
                continue
            if alarm.days and now.weekday() not in alarm.days:
                continue
            today = now.replace(hour=alarm.hour, minute=alarm.minute, second=0, microsecond=0)
            if today <= now:
                import datetime as dt
                today = today + dt.timedelta(days=1)
            secs = int((today - now).total_seconds())
            candidates.append((alarm.label, secs))

        for alarm in self._interval_alarms:
            if not alarm.enabled:
                continue
            if alarm.next_fire_epoch > 0:
                secs = max(0, int(alarm.next_fire_epoch - now_epoch))
                candidates.append((alarm.label, secs))

        if not candidates:
            return None
        candidates.sort(key=lambda x: x[1])
        return candidates[0]

    @staticmethod
    def format_duration(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}시간 {m:02d}분"
        return f"{m}분 {s:02d}초"
