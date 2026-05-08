# Sprint 1: 설정 저장/로드 기능 테스트
# 대상 모듈: config_manager.py
# 테스트 범위: JSON 파일 생성, 알람 CRUD, 설정 영속성

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from config_manager import ConfigManager, FixedAlarmConfig, IntervalAlarmConfig, AppSettings


def _make_config(tmp_dir: str) -> ConfigManager:
    cfg = ConfigManager()
    cfg.CONFIG_DIR = Path(tmp_dir) / "TP_alarm"
    cfg.CONFIG_FILE = cfg.CONFIG_DIR / "config.json"
    cfg.load()
    return cfg


class TC_S1_001_FirstRunCreatesFile(unittest.TestCase):
    """TC-S1-001: 최초 실행 시 config.json 자동 생성"""

    def test_config_file_created_on_first_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            self.assertTrue(cfg.CONFIG_FILE.exists(), "config.json 파일이 생성되어야 함")


class TC_S1_002_DefaultSettings(unittest.TestCase):
    """TC-S1-002: 기본값 설정 확인"""

    def test_default_start_with_windows_is_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            self.assertFalse(cfg.settings.start_with_windows)

    def test_default_usage_source_is_app_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            self.assertEqual(cfg.settings.usage_time_source, "app_start")

    def test_default_alarm_lists_are_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            self.assertEqual(cfg.get_fixed_alarms(), [])
            self.assertEqual(cfg.get_interval_alarms(), [])


class TC_S1_003_AddFixedAlarm(unittest.TestCase):
    """TC-S1-003: 고정 시각 알람 추가 및 영속성"""

    def test_add_fixed_alarm_saved_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            alarm = FixedAlarmConfig(
                id=ConfigManager.new_id(),
                enabled=True,
                label="테스트 알람",
                hour=9,
                minute=30,
                days=[],
                sound="default",
                last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)

            # 재로드해서 확인
            cfg2 = _make_config(tmp)
            alarms = cfg2.get_fixed_alarms()
            self.assertEqual(len(alarms), 1)
            self.assertEqual(alarms[0].label, "테스트 알람")
            self.assertEqual(alarms[0].hour, 9)
            self.assertEqual(alarms[0].minute, 30)

    def test_upsert_updates_existing_alarm(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            alarm_id = ConfigManager.new_id()
            alarm = FixedAlarmConfig(
                id=alarm_id, enabled=True, label="원본", hour=8, minute=0,
                days=[], sound="default", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)

            # 수정
            alarm2 = FixedAlarmConfig(
                id=alarm_id, enabled=True, label="수정됨", hour=10, minute=0,
                days=[], sound="beep", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm2)

            alarms = cfg.get_fixed_alarms()
            self.assertEqual(len(alarms), 1)
            self.assertEqual(alarms[0].label, "수정됨")
            self.assertEqual(alarms[0].hour, 10)


class TC_S1_004_AddIntervalAlarm(unittest.TestCase):
    """TC-S1-004: 인터벌 알람 추가 및 영속성"""

    def test_add_interval_alarm_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(),
                enabled=True,
                label="휴식 알림",
                interval_minutes=60,
                sound="beep",
                next_fire_epoch=0.0,
            )
            cfg.upsert_interval_alarm(alarm)

            cfg2 = _make_config(tmp)
            alarms = cfg2.get_interval_alarms()
            self.assertEqual(len(alarms), 1)
            self.assertEqual(alarms[0].interval_minutes, 60)


class TC_S1_005_DeleteAlarm(unittest.TestCase):
    """TC-S1-005: 알람 삭제"""

    def test_delete_fixed_alarm(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            alarm_id = ConfigManager.new_id()
            alarm = FixedAlarmConfig(
                id=alarm_id, enabled=True, label="삭제될 알람",
                hour=7, minute=0, days=[], sound="default", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)
            cfg.delete_alarm(alarm_id)
            self.assertEqual(cfg.get_fixed_alarms(), [])

    def test_delete_interval_alarm(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            alarm_id = ConfigManager.new_id()
            alarm = IntervalAlarmConfig(
                id=alarm_id, enabled=True, label="삭제될 인터벌",
                interval_minutes=30, sound="beep", next_fire_epoch=0.0,
            )
            cfg.upsert_interval_alarm(alarm)
            cfg.delete_alarm(alarm_id)
            self.assertEqual(cfg.get_interval_alarms(), [])


class TC_S1_006_SettingsPersistence(unittest.TestCase):
    """TC-S1-006: 앱 설정 영속성"""

    def test_usage_source_change_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            cfg.settings.usage_time_source = "boot"
            cfg.save()

            cfg2 = _make_config(tmp)
            self.assertEqual(cfg2.settings.usage_time_source, "boot")

    def test_start_with_windows_registry_skipped_on_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _make_config(tmp)
            with patch("config_manager.winreg.OpenKey", side_effect=OSError):
                # 레지스트리 오류여도 예외 없이 처리
                try:
                    cfg.start_with_windows = True
                    cfg.settings.start_with_windows = True
                    cfg.save()
                except Exception as e:
                    self.fail(f"레지스트리 오류가 예외로 전파되면 안 됨: {e}")


class TC_S1_007_CorruptedConfig(unittest.TestCase):
    """TC-S1-007: 손상된 config.json 처리"""

    def test_corrupted_json_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "TP_alarm"
            config_dir.mkdir()
            config_file = config_dir / "config.json"
            config_file.write_text("{invalid json!!!", encoding="utf-8")

            cfg = ConfigManager()
            cfg.CONFIG_DIR = config_dir
            cfg.CONFIG_FILE = config_file
            cfg.load()  # should not raise

            self.assertEqual(cfg.get_fixed_alarms(), [])
            self.assertFalse(cfg.settings.start_with_windows)


if __name__ == "__main__":
    unittest.main(verbosity=2)
