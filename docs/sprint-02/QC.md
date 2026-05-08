# Sprint 02 — QC 결과

**스프린트:** 02 / 알람 로직  
**테스트 파일:** `tests/test_sprint2_alarm.py`  
**실행일:** 2026-05-08  
**실행 명령:** `python -m pytest tests/test_sprint2_alarm.py -v`

---

## 자동화 TC 결과

| TC ID | 테스트명 | 검증 항목 | 결과 |
|-------|----------|-----------|------|
| TC-S2-001a | test_usage_time_app_start | 앱 시작 기준 사용 시간 계산 | ✅ PASS |
| TC-S2-001b | test_usage_time_app_start_elapsed | 경과 시간 정확도 | ✅ PASS |
| TC-S2-002 | test_usage_time_boot | psutil 부팅 기준 사용 시간 | ✅ PASS |
| TC-S2-003a | test_format_duration_seconds | format_duration — 59초 이하 | ✅ PASS |
| TC-S2-003b | test_format_duration_minutes | format_duration — 1분~59분 | ✅ PASS |
| TC-S2-003c | test_format_duration_hours | format_duration — 1시간 이상 | ✅ PASS |
| TC-S2-004a | test_fixed_alarm_fires | 고정 알람 발화 조건 충족 | ✅ PASS |
| TC-S2-004b | test_fixed_alarm_wrong_time | 다른 시각 — 발화 안 함 | ✅ PASS |
| TC-S2-005a | test_fixed_alarm_no_duplicate | 당일 중복 방지 | ✅ PASS |
| TC-S2-005b | test_fixed_alarm_next_day | 익일 재발화 | ✅ PASS |
| TC-S2-006 | test_fixed_alarm_day_filter | 요일 필터 — 해당 요일에만 발화 | ✅ PASS |
| TC-S2-007a | test_disabled_fixed_alarm | 비활성 고정 알람 발화 안 함 | ✅ PASS |
| TC-S2-007b | test_disabled_interval_alarm | 비활성 인터벌 알람 발화 안 함 | ✅ PASS |
| TC-S2-008a | test_interval_alarm_fires | next_fire_epoch 경과 시 발화 | ✅ PASS |
| TC-S2-008b | test_interval_epoch_updated | 발화 후 next_fire_epoch 갱신 | ✅ PASS |
| TC-S2-009a | test_next_alarm_fixed | 다음 고정 알람 계산 | ✅ PASS |
| TC-S2-009b | test_next_alarm_interval | 다음 인터벌 알람 계산 | ✅ PASS |
| TC-S2-009c | test_next_alarm_none | 알람 없을 때 None 반환 | ✅ PASS |

---

## 수동 검증 항목

해당 없음 (Sprint 02는 UI 없는 비즈니스 로직)

---

## 최종 판정

**전체: 18개 / PASS: 18개 / FAIL: 0개**  
**→ ✅ Sprint 02 통과**

---

## 비고

- `tick()`이 UI 함수를 직접 호출하지 않음 (큐에만 put) — 설계 원칙 충족
- `next_fire_epoch = 0.0` 초기값 시 앱 시작 즉시 `now + interval`로 설정되는 동작 확인
- 고정 알람 `second == 0` 게이트: 분 경계에서만 평가하므로 테스트에서 `now.second = 0` 목 설정 필요
