# Sprint 01 — 결과 보고서

**스프린트:** 01 / 기반 레이어  
**완료일:** 2026-05-08  
**상태:** ✅ 완료

---

## 완료된 작업

| 항목 | 결과 |
|------|------|
| `src/config_manager.py` 구현 | ✅ 완료 |
| `FixedAlarmConfig` 데이터클래스 | ✅ 완료 |
| `IntervalAlarmConfig` 데이터클래스 | ✅ 완료 |
| `AppSettings` 데이터클래스 | ✅ 완료 |
| JSON 로드/저장/폴백 | ✅ 완료 |
| Windows 시작 레지스트리 등록/해제 | ✅ 완료 |

---

## 테스트 결과

**파일:** `tests/test_sprint1_config.py`  
**실행 결과:** 12 / 12 PASS  
**실행 시간:** ~0.5s

| TC ID | 테스트명 | 결과 |
|-------|----------|------|
| TC-S1-001 | 최초 실행 시 config.json 자동 생성 | ✅ PASS |
| TC-S1-002 | 기본값 설정 확인 (3개) | ✅ PASS |
| TC-S1-003 | 고정 알람 추가 및 영속성 (2개) | ✅ PASS |
| TC-S1-004 | 인터벌 알람 추가 및 영속성 | ✅ PASS |
| TC-S1-005 | 알람 삭제 (고정/인터벌) | ✅ PASS |
| TC-S1-006 | 설정 영속성 + 레지스트리 오류 처리 (2개) | ✅ PASS |
| TC-S1-007 | 손상된 JSON 폴백 처리 | ✅ PASS |

---

## 산출물

| 파일 | 설명 |
|------|------|
| `src/config_manager.py` | ConfigManager, 데이터클래스 3종 |
| `tests/test_sprint1_config.py` | TC 12개 |

---

## 다음 스프린트 (Sprint 02) 이관 사항

- `ConfigManager`를 `AlarmManager`에서 의존성 주입으로 사용
- `FixedAlarmConfig.last_fired_date` 필드를 발화 로직에서 갱신
- `IntervalAlarmConfig.next_fire_epoch` 필드를 발화 로직에서 갱신

---

## 후속 변경 사항 (Post v1.0)

| 항목 | 변경 내용 |
|------|-----------|
| `start_with_windows` 기본값 | `False` → `True` (PC 켜짐 시 자동 실행 기본 활성화) |
| `load()` 동작 | 설정 로드 후 `_write_startup_registry()` 자동 호출 — 레지스트리와 config.json 동기화 보장 |

**변경 이유:** 알람 앱 특성상 자동 실행이 기본값이어야 한다. 기존에는 설정 탭에서 수동 활성화해야 했으나, 최초 설치 후 재부팅해도 앱이 실행되지 않는 문제가 있었다.
