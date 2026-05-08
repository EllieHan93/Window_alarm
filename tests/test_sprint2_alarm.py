# Sprint 2: 알람 로직 테스트
# 대상 모듈: alarm_manager.py
# 테스트 범위: 알람 발화 조건, 중복 방지, 사용 시간, 다음 알람 계산

import sys
import time
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from config_manager import ConfigManager, FixedAlarmConfig, IntervalAlarmConfig
from alarm_manager import AlarmManager, AlarmEvent


def _make_manager(tmp_dir: str, start_time: datetime = None) -> tuple[AlarmManager, ConfigManager]:
    cfg = ConfigManager()
    cfg.CONFIG_DIR = Path(tmp_dir) / "TP_alarm"
    cfg.CONFIG_FILE = cfg.CONFIG_DIR / "config.json"
    cfg.load()
    mgr = AlarmManager(cfg, start_time or datetime.now())
    return mgr, cfg


class TC_S2_001_UsageTimeAppStart(unittest.TestCase):
    """TC-S2-001: 앱 시작 기준 사용 시간 계산"""

    def test_usage_time_increases_over_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = datetime.now() - timedelta(seconds=120)
            mgr, _ = _make_manager(tmp, start_time=start)
            secs = mgr.get_usage_seconds()
            self.assertGreaterEqual(secs, 119, "120초 전 시작이면 최소 119초 이상")
            self.assertLess(secs, 130, "너무 크면 안 됨")

    def test_zero_at_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, _ = _make_manager(tmp, start_time=datetime.now())
            self.assertLessEqual(mgr.get_usage_seconds(), 1)


class TC_S2_002_UsageTimeBoot(unittest.TestCase):
    """TC-S2-002: 부팅 기준 사용 시간 계산"""

    def test_boot_time_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            cfg.settings.usage_time_source = "boot"
            secs = mgr.get_usage_seconds()
            self.assertGreater(secs, 0, "부팅 후 경과 시간은 양수여야 함")


class TC_S2_003_FormatDuration(unittest.TestCase):
    """TC-S2-003: 시간 포맷 변환"""

    def test_seconds_only(self):
        result = AlarmManager.format_duration(45)
        self.assertIn("45", result)

    def test_minutes_and_seconds(self):
        result = AlarmManager.format_duration(125)
        self.assertIn("2", result)  # 2분

    def test_hours_and_minutes(self):
        result = AlarmManager.format_duration(3661)
        self.assertIn("1", result)  # 1시간


class TC_S2_004_FixedAlarmFires(unittest.TestCase):
    """TC-S2-004: 고정 시각 알람 발화"""

    def test_fixed_alarm_fires_at_correct_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm_id = ConfigManager.new_id()
            now = datetime.now()
            alarm = FixedAlarmConfig(
                id=alarm_id, enabled=True, label="테스트",
                hour=now.hour, minute=now.minute,
                days=[], sound="default", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            # second=0 인 시각을 시뮬레이션
            trigger_time = now.replace(second=0, microsecond=0)
            mgr._check_fixed_alarms(trigger_time, q)

            self.assertFalse(q.empty(), "알람이 큐에 들어가야 함")
            event = q.get_nowait()
            self.assertIsInstance(event, AlarmEvent)
            self.assertEqual(event.label, "테스트")
            self.assertEqual(event.alarm_type, "fixed")

    def test_fixed_alarm_does_not_fire_wrong_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm = FixedAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="오전9시",
                hour=9, minute=0, days=[], sound="default", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            # 오전 8시 30분
            wrong_time = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
            mgr._check_fixed_alarms(wrong_time, q)
            self.assertTrue(q.empty(), "잘못된 시각에 발화하면 안 됨")


class TC_S2_005_FixedAlarmNoDuplicate(unittest.TestCase):
    """TC-S2-005: 고정 알람 당일 중복 발화 방지"""

    def test_no_duplicate_fire_same_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            today = datetime.now().date().isoformat()
            alarm = FixedAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="중복방지테스트",
                hour=9, minute=0, days=[], sound="default",
                last_fired_date=today,  # 이미 오늘 발화함
            )
            cfg.upsert_fixed_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            trigger = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            mgr._check_fixed_alarms(trigger, q)
            self.assertTrue(q.empty(), "당일 이미 발화했으면 다시 발화하면 안 됨")

    def test_fires_next_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
            alarm = FixedAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="다음날발화",
                hour=9, minute=0, days=[], sound="default",
                last_fired_date=yesterday,
            )
            cfg.upsert_fixed_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            trigger = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            mgr._check_fixed_alarms(trigger, q)
            self.assertFalse(q.empty(), "전날 발화 기록이면 오늘 다시 발화해야 함")


class TC_S2_006_FixedAlarmWeekday(unittest.TestCase):
    """TC-S2-006: 고정 알람 요일 필터"""

    def test_alarm_skipped_on_wrong_weekday(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            now = datetime.now()
            # 오늘 요일을 제외한 요일만 설정
            today_weekday = now.weekday()
            other_days = [d for d in range(7) if d != today_weekday]
            alarm = FixedAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="요일필터",
                hour=now.hour, minute=now.minute,
                days=other_days, sound="default", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            trigger = now.replace(second=0, microsecond=0)
            mgr._check_fixed_alarms(trigger, q)
            self.assertTrue(q.empty(), "오늘이 아닌 요일 알람은 발화하면 안 됨")


class TC_S2_007_DisabledAlarmDoesNotFire(unittest.TestCase):
    """TC-S2-007: 비활성화된 알람은 발화하지 않음"""

    def test_disabled_fixed_alarm_no_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            now = datetime.now()
            alarm = FixedAlarmConfig(
                id=ConfigManager.new_id(), enabled=False, label="비활성",
                hour=now.hour, minute=now.minute,
                days=[], sound="default", last_fired_date="",
            )
            cfg.upsert_fixed_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            trigger = now.replace(second=0, microsecond=0)
            mgr._check_fixed_alarms(trigger, q)
            self.assertTrue(q.empty())

    def test_disabled_interval_alarm_no_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=False, label="비활성인터벌",
                interval_minutes=1, sound="beep",
                next_fire_epoch=time.time() - 10,  # 과거 (발화 조건 충족)
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            mgr._check_interval_alarms(q)
            self.assertTrue(q.empty())


class TC_S2_008_IntervalAlarmFires(unittest.TestCase):
    """TC-S2-008: 인터벌 알람 발화 및 next_fire_epoch 갱신"""

    def test_interval_fires_when_epoch_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="인터벌테스트",
                interval_minutes=60, sound="beep",
                next_fire_epoch=time.time() - 5,  # 5초 전 발화 시각
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            mgr._check_interval_alarms(q)

            self.assertFalse(q.empty(), "만료된 인터벌 알람은 발화해야 함")
            event = q.get_nowait()
            self.assertEqual(event.alarm_type, "interval")

    def test_interval_next_fire_updated_after_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm_id = ConfigManager.new_id()
            alarm = IntervalAlarmConfig(
                id=alarm_id, enabled=True, label="갱신테스트",
                interval_minutes=60, sound="beep",
                next_fire_epoch=time.time() - 5,
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            mgr._check_interval_alarms(q)

            # next_fire_epoch이 미래로 갱신되었는지 확인
            updated = cfg.get_interval_alarms()
            self.assertEqual(len(updated), 1)
            self.assertGreater(updated[0].next_fire_epoch, time.time())


class TC_S2_009_NextAlarmInfo(unittest.TestCase):
    """TC-S2-009: 다음 알람 정보 계산"""

    def test_next_alarm_returns_closest(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            # 30분 뒤 인터벌 알람
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="30분 알람",
                interval_minutes=30, sound="beep",
                next_fire_epoch=time.time() + 1800,
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            result = mgr.get_next_alarm_info()
            self.assertIsNotNone(result)
            label, secs = result
            self.assertEqual(label, "30분 알람")
            self.assertAlmostEqual(secs, 1800, delta=5)

    def test_no_alarms_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, _ = _make_manager(tmp)
            result = mgr.get_next_alarm_info()
            self.assertIsNone(result)

    def test_closest_alarm_selected_among_multiple(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            far = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="먼 알람",
                interval_minutes=120, sound="beep",
                next_fire_epoch=time.time() + 7200,
            )
            close = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="가까운 알람",
                interval_minutes=10, sound="beep",
                next_fire_epoch=time.time() + 600,
            )
            cfg.upsert_interval_alarm(far)
            cfg.upsert_interval_alarm(close)
            mgr.reload_from_config()

            result = mgr.get_next_alarm_info()
            self.assertEqual(result[0], "가까운 알람")


if __name__ == "__main__":
    unittest.main(verbosity=2)
