# Sprint 11 — DEVELOPER

**스프린트:** 11 / UI 이모티콘 제거 & 알람 개별 ON/OFF 토글

---

## 변경 파일

### `src/main_window.py`

**이모티콘 제거**
- `_build_ui()`: 헤더 타이틀, 잠금/미리보기 버튼 텍스트
- `_build_ui()`: 커피/차 버튼 텍스트 및 `_send_drink()` 호출 인자 메시지
- `_flash_drink()`: 피드백 레이블 텍스트 `"☕  +1"` → `"커피 +1"`, `"🍵  +1"` → `"차 +1"`
- `_build_fixed_tab()`: 수정/삭제 버튼 텍스트
- `_build_interval_tab()`: 수정/삭제 버튼 텍스트
- `_build_drink_log_tab()`: 새로고침 버튼, 커피/차 컬럼 헤딩
- `_build_game_log_tab()`: 새로고침 버튼, 플레이 시간 컬럼 헤딩
- `PinDialog._build()`: 타이틀 레이블

**ON/OFF 토글 버튼**
- `_build_fixed_tab()`: `ttk.Button(text="ON/OFF", command=self._toggle_fixed)` 추가
- `_build_interval_tab()`: `ttk.Button(text="ON/OFF", command=self._toggle_interval)` 추가
- `_toggle_fixed()` 신규 메서드:
  ```python
  def _toggle_fixed(self) -> None:
      sel = self._fixed_tree.selection()
      if not sel: return
      alarm = next((a for a in self._config.get_fixed_alarms() if a.id == sel[0]), None)
      if alarm:
          alarm.enabled = not alarm.enabled
          self._config.upsert_fixed_alarm(alarm)
          self._alarm_mgr.reload_from_config()
          self._refresh_fixed_tree()
          self._fixed_tree.selection_set(sel[0])
  ```
- `_toggle_interval()`: 동일 패턴, `get_interval_alarms()` / `upsert_interval_alarm()` 사용

### `src/notification.py`

- `AlarmNotification.show()` 타이틀 바 레이블: `"🕹️  양방구는 게임중"` → `"양방구는 게임중"`

---

## 테스트 목록

| TC | 내용 | 방법 |
|----|------|------|
| TC-S11-01 | UI 전체 이모티콘 미표시 확인 | 수동 |
| TC-S11-02 | 알람 팝업 타이틀 이모티콘 미표시 | 수동 |
| TC-S11-03 | 고정알람 선택 후 ON/OFF → ✔↔✘ 전환 | 수동 |
| TC-S11-04 | 인터벌알람 선택 후 ON/OFF → ✔↔✘ 전환 | 수동 |
| TC-S11-05 | 토글 후 앱 재시작 → 상태 유지 (config 저장 확인) | 수동 |
| TC-S11-06 | 선택 없이 ON/OFF 클릭 → 오류 없이 무시 | 수동 |
| TC-S11-07 | 커피/차 버튼 피드백 텍스트 정상 표시 | 수동 |
