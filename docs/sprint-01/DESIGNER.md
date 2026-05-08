# Sprint 01 — 디자인 사양서

**스프린트:** 01 / 기반 레이어  
**기간:** 2026-05-08

---

## 디자인 범위

Sprint 01은 UI가 없는 백엔드 레이어다.  
이 스프린트의 디자인 결정은 **데이터 구조 설계**에 집중한다.

---

## 데이터 구조 설계

### 고정 시각 알람 (FixedAlarmConfig)

| 필드 | 타입 | 표시 예시 | 비고 |
|------|------|-----------|------|
| id | string | — | 사용자에게 노출 안 함 |
| enabled | boolean | ✔ / ✘ | 목록에 아이콘으로 표시 |
| label | string | "오전 업무 시작" | 최대 30자 권장 |
| hour | integer | "09" | 2자리 표시 (`%02d`) |
| minute | integer | "30" | 2자리 표시 |
| days | integer[] | "월화수목금" / "매일" | 빈 배열 = "매일" |
| sound | string | "default" | 드롭다운 선택 |
| last_fired_date | string | 내부용 | UI 비노출 |

### 인터벌 알람 (IntervalAlarmConfig)

| 필드 | 타입 | 표시 예시 | 비고 |
|------|------|-----------|------|
| id | string | — | 사용자에게 노출 안 함 |
| enabled | boolean | ✔ / ✘ | |
| label | string | "휴식 알림" | 최대 30자 권장 |
| interval_minutes | integer | "1시간 30분" | UI에서 시+분 분리 입력 |
| sound | string | "beep" | 드롭다운 선택 |
| next_fire_epoch | float | 내부용 | UI 비노출 |

### 요일 표시 규칙

```
days = []          → "매일"
days = [0,1,2,3,4] → "월화수목금"
days = [5,6]       → "토일"
days = [0]         → "월"
```

### 소리 옵션 레이블

| 값 | 사용자 표시명 | 설명 |
|----|--------------|------|
| default | 기본음 | Windows SystemExclamation |
| beep | 비프음 | 단순 비프 2회 |
| asterisk | 별표음 | Windows SystemAsterisk |

---

## config.json 파일 위치

```
%APPDATA%\TP_alarm\config.json
```

사용자가 직접 편집할 수 있도록 JSON 형식으로 저장 (들여쓰기 2칸).

---

## Sprint 02로 이관될 디자인 사항

- 알람 목록 트리뷰 컬럼 구성
- 알람 추가/수정 다이얼로그 레이아웃
