# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 구조

```
TP_alarm/
├── src/          # Python 소스 코드
├── tests/        # pytest 테스트 (스프린트 단위)
├── docs/         # 스프린트별 사양서 + PROCESS.md + prompt.md
├── assets/       # icon.ico
├── fonts/        # Mona12 픽셀 폰트 (Mona_20260424_2053/ttf/)
├── CLAUDE.md
├── requirements.txt
├── tp_alarm.spec  # PyInstaller 빌드 스펙
└── installer.iss  # Inno Setup 설치 파일 스펙
```

## Commands

```powershell
# 앱 실행
python src/main.py

# 전체 테스트
python -m pytest tests/ -v

# 단일 TC 실행 (예: TC-S2-005)
python -m pytest tests/test_sprint2_alarm.py::TC_S2_005_FixedAlarmNoDuplicate -v

# 패키지 설치
pip install -r requirements.txt

# .exe 빌드 → dist\TP_Alarm\TP_Alarm.exe
pyinstaller tp_alarm.spec --clean

# 설치 파일 빌드 → installer_output\TP_Alarm_Setup.exe
# (PyInstaller 빌드 먼저 실행 필요)
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

## 아키텍처

앱은 3개의 스레드로 구성된다.

```
[MAIN THREAD]  tkinter mainloop()
  └── root.after(200ms) → process_queue()  ← 큐 → UI 디스패치

[TRAY THREAD]  pystray icon.run()  (daemon)
  └── 메뉴 클릭 → queue.put(Command)

[SCHEDULER THREAD]  while True: sleep(1)  (daemon)
  └── alarm_mgr.tick(queue)
```

**핵심 규칙:** `AlarmManager.tick()`과 트레이 콜백은 절대로 tkinter 함수를 직접 호출하지 않는다. 큐(`queue.Queue`)에만 `put`하고, 메인 스레드의 `process_queue()`가 수신해서 UI를 업데이트한다.

## 모듈 역할 (src/)

- **`config_manager.py`** — JSON 설정(`%APPDATA%\TP_alarm\config.json`) 로드/저장, `FixedAlarmConfig` / `IntervalAlarmConfig` / `AppSettings` 데이터클래스, Windows 시작 레지스트리 등록
- **`alarm_manager.py`** — `tick(queue)` (1초마다 스케줄러 스레드에서 호출), 고정 시각·인터벌 알람 발화 조건 평가, `get_usage_seconds()` / `get_next_alarm_info()` 조회
- **`tray_app.py`** — `pystray` 래핑, daemon 스레드에서 `icon.run()` 실행, 메뉴 클릭 → `Command` NamedTuple을 큐에 put
- **`main_window.py`** — tkinter 메인 창(상태 뷰 400×240 ↔ 관리 뷰 520×560), 알람 CRUD + 개별 ON/OFF 토글, 음료 기록·게임 기록 탭, PIN 인증 다이얼로그
- **`notification.py`** — `AlarmNotification.show()` topmost 플로팅 팝업, PNG 이미지+말풍선 Canvas, winsound 비동기 재생, 4초 자동 닫힘, 스누즈 `root.after(ms)` 예약
- **`font_loader.py`** — Mona12 픽셀 폰트 GDI 등록(`AddFontResourceW`), `family()` / `emoji_family()` 제공, 폴백 `"맑은 고딕"`
- **`drink_log.py`** — `%APPDATA%\TP_alarm\drink_log.json` 날짜별 커피/차 횟수 기록, `record()` / `get_log()`
- **`game_log.py`** — `%APPDATA%\TP_alarm\game_log.json` 날짜별 플레이 시간(초) 기록(max 보존), `update()` / `get_log()` / `fmt_duration()`
- **`notifier.py`** — Telegram 봇 비동기 메시지 전송 (`send_telegram()`)
- **`main.py`** — 부트스트랩: 큐 생성 → 스레드 시작 → `root.mainloop()`, 종료 시 `game_log.update()` 호출

## 알람 데이터 모델 핵심

- **고정 알람** `last_fired_date`: 당일 중복 발화 방지용 ISO 날짜 문자열. `second==0`일 때만 평가.
- **인터벌 알람** `next_fire_epoch`: Unix timestamp. `0.0`이면 앱 시작 시 `now + interval`로 초기화. 과거이면 즉시 발화 후 갱신.
- 각 알람의 `enabled` 필드로 개별 활성화 제어. 관리 탭에서 ON/OFF 버튼으로 즉시 토글 가능.

## UI 색상 상수 (main_window.py)

| 상수 | 값 | 용도 |
|------|----|------|
| `_ACCENT` | `#049CD8` | 헤더, 커피 버튼, stats 테두리 |
| `_RED` | `#E52521` | 삭제, 고정알람 팝업 accent |
| `_GREEN` | `#43B047` | 차 버튼, ON 상태 |
| `_YELLOW` | `#FBD000` | 피드백 텍스트 |
| `_BG2` | `#e8f4fd` | stats 패널 배경 |

## 테스트 구조 (tests/)

| 파일 | 스프린트 | 범위 |
|------|---------|------|
| `test_sprint1_config.py` | S1 | ConfigManager CRUD, 파일 영속성 |
| `test_sprint2_alarm.py` | S2 | 알람 발화 조건, 중복 방지, 다음 알람 계산 |
| `test_sprint3_integration.py` | S3 | tick() 스레드 안전성, 큐 통신, 스케줄러 루프 |

모든 테스트는 `tempfile.TemporaryDirectory()`를 사용해 `%APPDATA%`를 격리한다.

## 문서 (docs/)

스프린트 단위 폴더로 관리. 각 폴더에 5개 파일 고정. `docs/PROCESS.md`에 전체 워크플로우 정의, `docs/prompt.md`에 스프린트별 주요 프롬프트 기록.

```
docs/
├── PROCESS.md   전체 워크플로우 & QC 현황
├── prompt.md    스프린트별 주요 프롬프트 기록
├── sprint-01/   기반 레이어 (ConfigManager, 데이터 모델)
├── sprint-02/   알람 로직 (AlarmManager, 발화 조건)
├── sprint-03/   UI/스레딩 통합 (창, 트레이, 팝업)
├── sprint-04/   빌드/배포 (PyInstaller, Inno Setup)
├── sprint-05/   UI·UX 개선 (라이트 테마, 토스트 팝업)
├── sprint-06/   토스트 & 트레이 디자인 개선
├── sprint-07/   관리자 잠금 & 트레이 개선
├── sprint-08/   폰트·UI 정제 & 음료 요청 알림
├── sprint-09/   음료 기록 & 앱 이름 변경
├── sprint-10/   폰트 교체 & 게임 테마 적용
└── sprint-11/   이모티콘 제거 & 알람 개별 ON/OFF 토글
```

각 스프린트 폴더의 파일 구성:

| 파일 | 담당 | 내용 |
|------|------|------|
| `PLANNER.md` | 기획자 | 스프린트 목표, 범위, 완료 조건, 사용자 스토리 |
| `DESIGNER.md` | 디자이너 | 데이터 구조 설계 또는 UI 와이어프레임, 인터랙션 |
| `DEVELOPER.md` | 개발자 | 구현 사양, API, 알고리즘, 테스트 목록 |
| `QC.md` | QC | TC 실행 결과, 수동 검증 항목, 최종 판정 |
| `RESULT.md` | 전체 | 완료 작업, 테스트 결과, 산출물, 다음 스프린트 이관 |

스크린샷: `docs/sprint-XX/screenshots/capture.py` 실행 → `docs/sprint-XX/screenshots/*.png` 저장.
