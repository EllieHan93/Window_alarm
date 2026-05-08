# Sprint 01 — QC 결과

**스프린트:** 01 / 기반 레이어  
**테스트 파일:** `tests/test_sprint1_config.py`  
**실행일:** 2026-05-08  
**실행 명령:** `python -m pytest tests/test_sprint1_config.py -v`

---

## 자동화 TC 결과

| TC ID | 테스트명 | 검증 항목 | 결과 |
|-------|----------|-----------|------|
| TC-S1-001 | test_config_file_created | 최초 실행 시 config.json 자동 생성 | ✅ PASS |
| TC-S1-002a | test_default_settings | 기본 설정값 확인 (start_with_windows=True) | ✅ PASS |
| TC-S1-002b | test_default_usage_source | 기본 usage_time_source="app_start" | ✅ PASS |
| TC-S1-002c | test_default_alarms_empty | 초기 알람 목록 빈 배열 | ✅ PASS |
| TC-S1-003a | test_add_fixed_alarm | 고정 알람 추가 후 저장 | ✅ PASS |
| TC-S1-003b | test_fixed_alarm_persistence | 앱 재시작 후 고정 알람 복원 | ✅ PASS |
| TC-S1-004 | test_add_interval_alarm | 인터벌 알람 추가 및 영속성 | ✅ PASS |
| TC-S1-005a | test_delete_fixed_alarm | 고정 알람 삭제 | ✅ PASS |
| TC-S1-005b | test_delete_interval_alarm | 인터벌 알람 삭제 | ✅ PASS |
| TC-S1-006a | test_settings_persistence | 설정값 변경 후 재시작 유지 | ✅ PASS |
| TC-S1-006b | test_registry_error_handling | 레지스트리 접근 실패 시 예외 없음 | ✅ PASS |
| TC-S1-007 | test_corrupted_json_fallback | 손상된 JSON → 기본값으로 폴백 | ✅ PASS |

---

## 수동 검증 항목

해당 없음 (Sprint 01은 UI 없는 백엔드 레이어)

---

## 최종 판정

**전체: 12개 / PASS: 12개 / FAIL: 0개**  
**→ ✅ Sprint 01 통과**

---

## 비고

- 모든 테스트는 `tempfile.TemporaryDirectory()`로 `%APPDATA%` 격리
- `ConfigManager.CONFIG_DIR` 오버라이드 방식으로 실제 파일시스템 오염 없음
- Sprint 05에서 `start_with_windows` 기본값이 `False` → `True`로 변경됨 → TC-S1-002a 기대값 업데이트 필요 시 확인
