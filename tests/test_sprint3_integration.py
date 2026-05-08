# Sprint 3: 스레딩 통합 테스트
# 대상 모듈: alarm_manager.py + config_manager.py (통합)
# 테스트 범위: tick()의 스레드 안전성, 큐 통신, 알람 연속 발화 방지

import sys
import time
import tempfile
import threading
import unittest
from datetime import datetime
from pathlib import Path
from queue import Queue

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


class TC_S3_001_TickOnlyPutsToQueue(unittest.TestCase):
    """TC-S3-001: tick()은 큐에만 put하고 UI 함수 호출 없음"""

    def test_tick_does_not_raise_without_ui(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, _ = _make_manager(tmp)
            q = Queue()
            # UI가 없어도 예외 없이 실행되어야 함
            try:
                mgr.tick(q)
            except Exception as e:
                self.fail(f"tick()이 예외를 발생시키면 안 됨: {e}")


class TC_S3_002_ConcurrentTickSafe(unittest.TestCase):
    """TC-S3-002: 다중 스레드에서 tick() 동시 호출 안전성"""

    def test_concurrent_tick_no_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="동시성테스트",
                interval_minutes=1, sound="beep",
                next_fire_epoch=time.time() + 60,
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            errors = []

            def run_tick():
                try:
                    for _ in range(10):
                        mgr.tick(q)
                        time.sleep(0.01)
                except Exception as e:
                    errors.append(str(e))

            threads = [threading.Thread(target=run_tick) for _ in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=5)

            self.assertEqual(errors, [], f"동시 tick 오류: {errors}")


class TC_S3_003_SchedulerLoopIntegration(unittest.TestCase):
    """TC-S3-003: 스케줄러 루프 - 인터벌 알람 자동 발화"""

    def test_interval_alarm_fires_in_scheduler(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="자동발화",
                interval_minutes=1, sound="beep",
                next_fire_epoch=time.time() + 2,  # 2초 뒤 발화
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            stop = threading.Event()

            def scheduler():
                while not stop.is_set():
                    mgr.tick(q)
                    time.sleep(0.5)

            t = threading.Thread(target=scheduler, daemon=True)
            t.start()

            # 5초 안에 발화 기대
            fired = False
            for _ in range(10):
                time.sleep(0.5)
                if not q.empty():
                    fired = True
                    break

            stop.set()
            self.assertTrue(fired, "5초 안에 인터벌 알람이 발화해야 함")


class TC_S3_004_QueueCommandRouting(unittest.TestCase):
    """TC-S3-004: Command/AlarmEvent 큐 라우팅 타입 검증"""

    def test_alarm_event_type_is_correct(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="타입테스트",
                interval_minutes=60, sound="beep",
                next_fire_epoch=time.time() - 1,
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            mgr._check_interval_alarms(q)

            self.assertFalse(q.empty())
            item = q.get_nowait()
            self.assertIsInstance(item, AlarmEvent)
            self.assertEqual(item.alarm_type, "interval")
            self.assertEqual(item.label, "타입테스트")


class TC_S3_005_MultipleAlarmsInQueue(unittest.TestCase):
    """TC-S3-005: 동시 발화 알람 여러 개 큐에 쌓임"""

    def test_multiple_alarms_enqueued(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)
            for i in range(3):
                alarm = IntervalAlarmConfig(
                    id=ConfigManager.new_id(), enabled=True, label=f"알람{i}",
                    interval_minutes=60, sound="beep",
                    next_fire_epoch=time.time() - 1,
                )
                cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            q = Queue()
            mgr._check_interval_alarms(q)

            count = 0
            while not q.empty():
                q.get_nowait()
                count += 1
            self.assertEqual(count, 3, "3개 알람 모두 큐에 들어가야 함")


class TC_S3_006_ReloadFromConfig(unittest.TestCase):
    """TC-S3-006: reload_from_config() 후 새 알람 즉시 반영"""

    def test_new_alarm_reflected_after_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr, cfg = _make_manager(tmp)

            # 처음엔 알람 없음
            q = Queue()
            mgr._check_interval_alarms(q)
            self.assertTrue(q.empty())

            # 알람 추가 후 reload
            alarm = IntervalAlarmConfig(
                id=ConfigManager.new_id(), enabled=True, label="추가됨",
                interval_minutes=60, sound="beep",
                next_fire_epoch=time.time() - 1,
            )
            cfg.upsert_interval_alarm(alarm)
            mgr.reload_from_config()

            mgr._check_interval_alarms(q)
            self.assertFalse(q.empty(), "reload 후 새 알람이 발화해야 함")


if __name__ == "__main__":
    unittest.main(verbosity=2)
