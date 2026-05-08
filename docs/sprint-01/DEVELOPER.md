# Sprint 01 — 개발 사양서

**스프린트:** 01 / 기반 레이어  
**기간:** 2026-05-08  
**담당 모듈:** `src/config_manager.py`

---

## 구현 목표

`ConfigManager` 클래스를 통해 JSON 파일 기반 설정 영속화 레이어를 완성한다.

---

## 데이터클래스 정의

```python
@dataclass
class FixedAlarmConfig:
    id: str               # uuid4().hex
    enabled: bool
    label: str
    hour: int             # 0–23
    minute: int           # 0–59
    days: list[int]       # [] = 매일, [0..6] (0=월)
    sound: str            # "default" | "beep" | "asterisk"
    last_fired_date: str  # "YYYY-MM-DD" | ""

@dataclass
class IntervalAlarmConfig:
    id: str
    enabled: bool
    label: str
    interval_minutes: int
    sound: str
    next_fire_epoch: float  # Unix timestamp, 0.0 = 미초기화

@dataclass
class AppSettings:
    start_with_windows: bool = False
    usage_time_source: str = "app_start"  # "app_start" | "boot"
```

---

## ConfigManager API

```python
class ConfigManager:
    CONFIG_DIR = Path(os.environ["APPDATA"]) / "TP_alarm"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    # 파일 I/O
    def load(self) -> None          # 없으면 기본값 생성, 파싱 실패 시 폴백
    def save(self) -> None          # 전체 상태 직렬화 후 저장

    # 고정 알람
    def get_fixed_alarms(self) -> list[FixedAlarmConfig]
    def upsert_fixed_alarm(self, alarm: FixedAlarmConfig) -> None

    # 인터벌 알람
    def get_interval_alarms(self) -> list[IntervalAlarmConfig]
    def upsert_interval_alarm(self, alarm: IntervalAlarmConfig) -> None

    # 공통
    def delete_alarm(self, alarm_id: str) -> None  # 양쪽에서 탐색

    # 설정
    @property
    def start_with_windows(self) -> bool
    @start_with_windows.setter  # 레지스트리 자동 갱신

    @staticmethod
    def new_id(self) -> str        # uuid4().hex
```

---

## 레지스트리 등록

```
키: HKCU\Software\Microsoft\Windows\CurrentVersion\Run
값 이름: "TP_Alarm"
값: "<exe 경로>"
```

- `sys.frozen == True` (PyInstaller 패키징) → `sys.executable`
- 일반 실행 → `"{python}" "{main.py 절대 경로}"`
- `OSError` → 무시 (관리 불가 환경 대응, 예외 전파 안 함)

---

## 예외 처리 원칙

| 상황 | 처리 방법 |
|------|-----------|
| `config.json` 미존재 | 기본값으로 파일 신규 생성 |
| JSON 파싱 실패 | `_DEFAULT_CONFIG`로 폴백, 파일 덮어쓰기 |
| 레지스트리 `OSError` | `pass` — 예외 전파 안 함 |
| 알람 ID 중복 | `upsert`: 기존 항목 덮어쓰기 |

---

## 테스트 (Sprint 01 TC)

파일: `tests/test_sprint1_config.py`

| TC ID | 검증 항목 |
|-------|-----------|
| TC-S1-001 | 최초 실행 시 config.json 자동 생성 |
| TC-S1-002 | 기본값 (start_with_windows=False, usage_source=app_start, 알람 목록 empty) |
| TC-S1-003 | 고정 알람 추가 → 파일 저장 → 재로드 → 동일 값 확인 |
| TC-S1-003b | upsert: 동일 ID 알람 수정 시 1개만 유지 |
| TC-S1-004 | 인터벌 알람 추가 영속성 |
| TC-S1-005 | 고정/인터벌 알람 삭제 |
| TC-S1-006 | usage_source 변경 후 재로드 시 유지 |
| TC-S1-006b | 레지스트리 OSError → 예외 없이 처리 |
| TC-S1-007 | 손상된 JSON → 기본값 폴백 |

**실행:** `python -m pytest tests/test_sprint1_config.py -v`
