import json
import os
import sys
import uuid
import winreg
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class FixedAlarmConfig:
    id: str
    enabled: bool
    label: str
    hour: int
    minute: int
    days: list  # [] = 매일, [0..6] = 특정 요일 (0=월)
    sound: str
    last_fired_date: str = ""


@dataclass
class IntervalAlarmConfig:
    id: str
    enabled: bool
    label: str
    interval_minutes: int
    sound: str
    next_fire_epoch: float = 0.0


@dataclass
class AppSettings:
    start_with_windows: bool = True
    usage_time_source: str = "app_start"  # "app_start" or "boot"


_DEFAULT_CONFIG = {
    "version": 1,
    "settings": {
        "start_with_windows": True,
        "usage_time_source": "app_start",
    },
    "fixed_alarms": [],
    "interval_alarms": [],
}

_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "TP_Alarm"


class ConfigManager:
    CONFIG_DIR: Path = Path(os.environ.get("APPDATA", ".")) / "TP_alarm"
    CONFIG_FILE: Path = CONFIG_DIR / "config.json"

    def __init__(self) -> None:
        self._data: dict = {}
        self.settings: AppSettings = AppSettings()
        self._fixed_alarms: list[FixedAlarmConfig] = []
        self._interval_alarms: list[IntervalAlarmConfig] = []

    def load(self) -> None:
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = dict(_DEFAULT_CONFIG)
        else:
            self._data = dict(_DEFAULT_CONFIG)
            self._save_raw()

        s = self._data.get("settings", {})
        self.settings = AppSettings(
            start_with_windows=s.get("start_with_windows", True),
            usage_time_source=s.get("usage_time_source", "app_start"),
        )
        self._write_startup_registry(self.settings.start_with_windows)

        self._fixed_alarms = [
            FixedAlarmConfig(**a)
            for a in self._data.get("fixed_alarms", [])
        ]
        self._interval_alarms = [
            IntervalAlarmConfig(**a)
            for a in self._data.get("interval_alarms", [])
        ]

    def save(self) -> None:
        self._data["version"] = 1
        self._data["settings"] = asdict(self.settings)
        self._data["fixed_alarms"] = [asdict(a) for a in self._fixed_alarms]
        self._data["interval_alarms"] = [asdict(a) for a in self._interval_alarms]
        self._save_raw()

    def _save_raw(self) -> None:
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # --- Fixed Alarms ---

    def get_fixed_alarms(self) -> list[FixedAlarmConfig]:
        return list(self._fixed_alarms)

    def upsert_fixed_alarm(self, alarm: FixedAlarmConfig) -> None:
        for i, a in enumerate(self._fixed_alarms):
            if a.id == alarm.id:
                self._fixed_alarms[i] = alarm
                self.save()
                return
        self._fixed_alarms.append(alarm)
        self.save()

    # --- Interval Alarms ---

    def get_interval_alarms(self) -> list[IntervalAlarmConfig]:
        return list(self._interval_alarms)

    def upsert_interval_alarm(self, alarm: IntervalAlarmConfig) -> None:
        for i, a in enumerate(self._interval_alarms):
            if a.id == alarm.id:
                self._interval_alarms[i] = alarm
                self.save()
                return
        self._interval_alarms.append(alarm)
        self.save()

    def delete_alarm(self, alarm_id: str) -> None:
        self._fixed_alarms = [a for a in self._fixed_alarms if a.id != alarm_id]
        self._interval_alarms = [a for a in self._interval_alarms if a.id != alarm_id]
        self.save()

    # --- Startup Registry ---

    @property
    def start_with_windows(self) -> bool:
        return self.settings.start_with_windows

    @start_with_windows.setter
    def start_with_windows(self, value: bool) -> None:
        self.settings.start_with_windows = value
        self._write_startup_registry(value)
        self.save()

    def _write_startup_registry(self, enabled: bool) -> None:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, _REG_PATH, 0, winreg.KEY_SET_VALUE
            )
            if enabled:
                if getattr(sys, "frozen", False):
                    exe_path = sys.executable
                else:
                    exe_path = f'"{sys.executable}" "{Path(__file__).parent / "main.py"}"'
                winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, _APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except OSError:
            pass

    # --- Helpers ---

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex
