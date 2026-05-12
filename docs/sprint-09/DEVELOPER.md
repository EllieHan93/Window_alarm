# Sprint 09 — DEVELOPER

**스프린트:** 09 / 음료 기록 & 앱 이름 변경

---

## 신규 파일

### `src/drink_log.py`
- `record(drink_type: str)` — 오늘 날짜 카운트 +1, `drink_log.json`에 저장
- `get_log() -> dict` — 전체 로그를 날짜 내림차순으로 반환
- `_load() / _save()` — JSON 파일 I/O, 디렉토리 자동 생성

---

## 변경 파일

### `src/main_window.py`
- `import drink_log` 추가
- `_send_drink(drink_type, message)` — `drink_type` 파라미터 추가, `drink_log.record(drink_type)` 호출
- `_build_ui()` — `self._drink_log_tab` (4번째 탭) 추가
- `_enter_mgmt_mode()` — `_refresh_drink_log()` 호출 추가
- `_build_drink_log_tab()` — Treeview (날짜·커피·차·합계) + 새로고침 버튼
- `_refresh_drink_log()` — `drink_log.get_log()`로 트리뷰 갱신

### `src/notification.py`
- 타이틀바 Label `"⏰  TP Alarm"` → `"🎮  양방구는 게임중"`

### `src/tray_app.py`
- `_get_tooltip()` 첫 줄 `"TP Alarm"` → `"양방구는 게임중"`

---

## 테스트 목록

| TC | 내용 | 방법 |
|----|------|------|
| TC-S9-01 | 커피 버튼 클릭 → `drink_log.json`에 coffee +1 | 수동 |
| TC-S9-02 | 차 버튼 클릭 → tea +1 | 수동 |
| TC-S9-03 | 날짜 변경 시 새 키 생성 (코드 검토) | 코드 검토 |
| TC-S9-04 | 음료 기록 탭 날짜 내림차순 표시 | 수동 |
| TC-S9-05 | 새로고침 버튼 → 최신 데이터 반영 | 수동 |
| TC-S9-06 | 알람 팝업 타이틀바 "양방구는 게임중" | 수동 |
| TC-S9-07 | 트레이 툴팁 "양방구는 게임중" | 수동 |
