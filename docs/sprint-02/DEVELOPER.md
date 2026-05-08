# Sprint 02 — 개발 사양서

**스프린트:** 02 / 알람 로직  
**기간:** 2026-05-08  
**담당 모듈:** `src/alarm_manager.py`

---

## 구현 목표

`AlarmManager` 클래스를 통해 알람 발화 조건 평가, 사용 시간 계산, 다음 알람 계산을 완성한다.

---

## AlarmManager API

```python
class AlarmEvent(NamedTuple):
    alarm_id: str
    label: str
    alarm_type: str  # "fixed" | "interval"
    sound: str

class AlarmManager:
    def __init__(self, config: ConfigManager, app_start_time: datetime)

    # 스케줄러 스레드에서 1초마다 호출 — UI 함수 직접 호출 금지
    def tick(self, queue: Queue) -> None

    # 메인 스레드에서만 호출 (알람 CRUD 완료 후)
    def reload_from_config(self) -> None

    # 읽기 전용 — 모든 스레드에서 안전
    def get_usage_seconds(self) -> int
    def get_next_alarm_info(self) -> tuple[str, int] | None

    @staticmethod
    def format_duration(seconds: int) -> str
```

---

## 고정 알람 발화 조건

```python
def _check_fixed_alarms(self, now: datetime, queue: Queue):
    if now.second != 0:  # 분당 1회만 평가
        return
    today = now.date().isoformat()
    for alarm in self._fixed_alarms:
        if not alarm.enabled: continue
        if alarm.days and now.weekday() not in alarm.days: continue
        if now.hour == alarm.hour and now.minute == alarm.minute:
            if alarm.last_fired_date != today:        # 당일 중복 방지
                alarm.last_fired_date = today
                self._config.upsert_fixed_alarm(alarm)  # 즉시 영속화
                queue.put(AlarmEvent(...))
```

**핵심 제약:**
- `second == 0`일 때만 평가 → 정확도 ±1초 (sleep 오차 포함 최대 ±2초)
- `last_fired_date` 갱신 즉시 파일 저장 → 앱 재시작 시 중복 방지 유지

---

## 인터벌 알람 발화 조건

```python
def _check_interval_alarms(self, queue: Queue):
    now_epoch = time.time()
    for alarm in self._interval_alarms:
        if not alarm.enabled: continue
        if alarm.next_fire_epoch == 0.0: continue  # 미초기화
        if now_epoch >= alarm.next_fire_epoch:
            alarm.next_fire_epoch = now_epoch + alarm.interval_minutes * 60
            self._config.upsert_interval_alarm(alarm)  # 즉시 영속화
            queue.put(AlarmEvent(...))
```

**초기화 (`_init_interval_alarms`):**
```python
if alarm.next_fire_epoch == 0.0:
    alarm.next_fire_epoch = time.time() + alarm.interval_minutes * 60
```
→ 앱 시작 시 `next_fire_epoch`가 0이면 즉시 발화 없이 `now + interval`로 설정

---

## 사용 시간 계산

```python
def get_usage_seconds(self) -> int:
    if self._config.settings.usage_time_source == "boot":
        return int(time.time() - psutil.boot_time())
    return int((datetime.now() - self._app_start_time).total_seconds())
```

---

## 다음 알람 계산

```python
def get_next_alarm_info(self) -> tuple[str, int] | None:
    candidates = []
    # 고정 알람: 오늘 or 내일 중 가장 빠른 시각 계산
    # 인터벌 알람: next_fire_epoch - now
    candidates.sort(key=lambda x: x[1])
    return candidates[0] if candidates else None
```

---

## 스레드 안전성 원칙

| 메서드 | 호출 스레드 | 이유 |
|--------|------------|------|
| `tick()` | 스케줄러 스레드 | queue.put만 수행 |
| `reload_from_config()` | 메인 스레드만 | 내부 리스트 교체 |
| `get_usage_seconds()` | 모든 스레드 | 읽기 전용 산술 연산 |
| `get_next_alarm_info()` | 모든 스레드 | 읽기 전용 탐색 |

---

## 테스트 (Sprint 02 TC)

파일: `tests/test_sprint2_alarm.py`

| TC ID | 검증 항목 |
|-------|-----------|
| TC-S2-001 | 앱 시작 기준 사용 시간 (2개) |
| TC-S2-002 | 부팅 기준 사용 시간 |
| TC-S2-003 | format_duration (3개) |
| TC-S2-004 | 고정 알람 발화 조건 (2개) |
| TC-S2-005 | 당일 중복 방지 + 익일 발화 (2개) |
| TC-S2-006 | 요일 필터 |
| TC-S2-007 | 비활성 알람 발화 안 함 (2개) |
| TC-S2-008 | 인터벌 발화 + next_fire_epoch 갱신 (2개) |
| TC-S2-009 | 다음 알람 계산 (3개) |

**실행:** `python -m pytest tests/test_sprint2_alarm.py -v`
