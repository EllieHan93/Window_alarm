# Sprint 02 — 결과 보고서

**스프린트:** 02 / 알람 로직  
**완료일:** 2026-05-08  
**상태:** ✅ 완료

---

## 완료된 작업

| 항목 | 결과 |
|------|------|
| `src/alarm_manager.py` 구현 | ✅ 완료 |
| 고정 알람 발화 로직 (`_check_fixed_alarms`) | ✅ 완료 |
| 당일 중복 발화 방지 (`last_fired_date`) | ✅ 완료 |
| 요일 필터 | ✅ 완료 |
| 인터벌 알람 발화 로직 (`_check_interval_alarms`) | ✅ 완료 |
| `next_fire_epoch` 발화 후 즉시 갱신 및 파일 저장 | ✅ 완료 |
| 사용 시간 계산 (앱 시작 / 부팅 기준) | ✅ 완료 |
| 다음 알람 계산 (`get_next_alarm_info`) | ✅ 완료 |
| `format_duration` 포맷터 | ✅ 완료 |

---

## 테스트 결과

**파일:** `tests/test_sprint2_alarm.py`  
**실행 결과:** 18 / 18 PASS  
**실행 시간:** ~0.8s

| TC ID | 테스트명 | 결과 |
|-------|----------|------|
| TC-S2-001 | 앱 시작 기준 사용 시간 (2개) | ✅ PASS |
| TC-S2-002 | 부팅 기준 사용 시간 | ✅ PASS |
| TC-S2-003 | format_duration (3개) | ✅ PASS |
| TC-S2-004 | 고정 알람 발화 조건 (2개) | ✅ PASS |
| TC-S2-005 | 당일 중복 방지 + 익일 발화 (2개) | ✅ PASS |
| TC-S2-006 | 요일 필터 | ✅ PASS |
| TC-S2-007 | 비활성 알람 발화 안 함 (2개) | ✅ PASS |
| TC-S2-008 | 인터벌 발화 + epoch 갱신 (2개) | ✅ PASS |
| TC-S2-009 | 다음 알람 계산 (3개) | ✅ PASS |

---

## 산출물

| 파일 | 설명 |
|------|------|
| `src/alarm_manager.py` | AlarmManager, AlarmEvent |
| `tests/test_sprint2_alarm.py` | TC 18개 |

---

## 다음 스프린트 (Sprint 03) 이관 사항

- `AlarmEvent` → 큐에서 꺼내 `AlarmNotification.show()` 호출
- `get_usage_seconds()` → 메인 창 1초 갱신 루프에 연결
- `get_next_alarm_info()` → 메인 창 다음 알람 표시에 연결
- `tick()` → 스케줄러 스레드에서 1초마다 호출
