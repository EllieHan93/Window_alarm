# TP Alarm — 개발 프로세스

이 문서는 스프린트마다 반복되는 표준 워크플로우를 정의한다.

---

## 역할 구성 (5 에이전트)

| 역할 | 산출물 | 설명 |
|------|--------|------|
| 기획자 (Planner) | `PLANNER.md` | 목표, 범위, DoD, 사용자 스토리 |
| 디자이너 (Designer) | `DESIGNER.md` | 데이터 구조 설계 or UI 와이어프레임, 인터랙션 |
| 개발자 (Developer) | `DEVELOPER.md` + 코드 | API 사양, 알고리즘, TC 목록 정의, 구현 |
| QC 에이전트 (QC) | `QC.md` + TC 파일 | TC 생성/실행, 결과 기록, Pass/Fail 판정 |
| 결과 취합 (Result) | `RESULT.md` | 완료 항목, 검증 결과, 다음 스프린트 이관 사항 |

> 모든 프롬프트는 스프린트 종료 후 `docs/prompt.md`에 추가 기록한다.

---

## 스프린트 진행 순서

```
Sprint N 시작
    │
    ▼
┌─────────────────────────────┐
│  1. 기획자                  │
│  PLANNER.md 작성             │
│  - 목표 / 범위 / DoD         │
│  - 사용자 스토리             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  2. 디자이너                │
│  DESIGNER.md 작성            │
│  - 데이터 구조 (비UI 스프린트) │
│  - 와이어프레임 (UI 스프린트)  │
│  - 인터랙션 정의             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  3. 개발자                  │
│  DEVELOPER.md 작성           │
│  - API 사양                 │
│  - 알고리즘 설계             │
│  - TC 목록 정의              │
│  ↓                          │
│  코드 구현 (src/)            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  4. QC 에이전트             │  ← 이 단계부터 QC.md 관리
│  TC 파일 생성/갱신           │
│  tests/test_sprintN_*.py     │
│  ↓                          │
│  pytest 실행                │
│  ↓                          │
│  QC.md 결과 기록             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  5. 결과 취합               │
│  RESULT.md 작성              │
│  - 완료 항목                │
│  - TC 결과 요약              │
│  - 다음 스프린트 이관 사항   │
└─────────────────────────────┘
               │
               ▼
         prompt.md 업데이트
```

---

## 폴더 구조

```
docs/
├── PROCESS.md         ← 이 파일 (프로세스 정의)
├── prompt.md          ← 전체 프롬프트 기록 (스프린트별)
└── sprint-XX/
    ├── PLANNER.md     기획자
    ├── DESIGNER.md    디자이너
    ├── DEVELOPER.md   개발자
    ├── QC.md          QC 에이전트  ← 신규
    └── RESULT.md      결과 취합
```

---

## QC 에이전트 워크플로우 상세

### 입력
- `docs/sprint-XX/DEVELOPER.md` — TC 목록, 검증 항목 읽기
- `src/*.py` — 구현된 코드

### 수행 작업

1. **TC 파일 생성/갱신**
   ```
   tests/test_sprint1_config.py      Sprint 01
   tests/test_sprint2_alarm.py       Sprint 02
   tests/test_sprint3_integration.py Sprint 03
   (Sprint 04, 05는 자동화 TC 없음 — 수동 검증만)
   ```

2. **테스트 실행**
   ```powershell
   # 전체
   python -m pytest tests/ -v

   # 스프린트 단위
   python -m pytest tests/test_sprintN_*.py -v

   # 단일 TC
   python -m pytest tests/test_sprintN_*.py::TC_ID -v
   ```

3. **QC.md 기록**
   - 자동화 TC 결과 (Pass/Fail)
   - 수동 검증 항목 결과
   - 최종 판정 (스프린트 통과 여부)
   - Fail 발생 시 버그 내용 및 수정 이력

### QC.md 파일 형식

```markdown
# Sprint XX — QC 결과

**테스트 파일:** tests/test_sprintX_name.py
**실행일:** YYYY-MM-DD
**실행 명령:** python -m pytest tests/test_sprintX_name.py -v

## 자동화 TC

| TC ID | 테스트명 | 결과 |
|-------|----------|------|
| TC-SX-001 | ... | ✅ PASS |

## 수동 검증

| 항목 | 결과 |
|------|------|

## 최종 판정

**전체: N개 / PASS: N개 / FAIL: 0개 → ✅ 스프린트 통과**
```

---

## 스프린트별 QC 현황

| 스프린트 | 주제 | 자동화 TC | 수동 검증 | 판정 |
|----------|------|-----------|-----------|------|
| Sprint 01 | 기반 레이어 (ConfigManager) | 12개 | — | ✅ |
| Sprint 02 | 알람 로직 (AlarmManager) | 8개 | — | ✅ |
| Sprint 03 | UI/스레딩 통합 | 5개 | 5개 | ✅ |
| Sprint 04 | 빌드/배포 | — | 7개 | ✅ |
| Sprint 05 | UI·UX 개선 | — | 8개 | ✅ |
| Sprint 06 | 토스트 & 트레이 디자인 | — | 13개 | ✅ |
| Sprint 07 | 관리자 잠금 & 트레이 개선 | — | 10개 | ✅ |
| Sprint 08 | 폰트·UI 정제 & 음료 요청 알림 | — | 8개 | ✅ |
| Sprint 09 | 음료 기록 & 앱 이름 변경 | — | 7개 | ✅ |
| Sprint 10 | 폰트 교체 & 게임 테마 적용 | — | 7개 | ✅ |
| Sprint 11 | 이모티콘 제거 & 알람 개별 ON/OFF | — | 7개 | ✅ |
