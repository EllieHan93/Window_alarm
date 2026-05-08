# Sprint 06 — 결과 보고서

**스프린트:** 06 / 토스트 & 트레이 디자인 개선  
**완료일:** 2026-05-08  
**상태:** ✅ 완료 (TRAY 항목 Sprint 07 이관)

---

## 완료된 작업

| 항목 | 결과 |
|------|------|
| TOAST-01: 타입별 accent 색상 | ✓ 보라(`#7c3aed`) / 파랑(`#2563eb`) |
| TOAST-02: 클릭 닫힘 | △ 드래그 이동으로 대체 (버튼 닫기 유지) |
| TOAST-03: Fade-in 효과 | ✓ 250ms (25ms × 10스텝) |
| EXTRA-01: Canvas 고양이 애니메이션 | ✓ 구현 후 PNG로 교체 |
| EXTRA-02: PNG 이미지 교체 | ✓ `src/source/Image.png` |
| EXTRA-03: 플로팅 창 + 드래그 | ✓ overrideredirect + B1-Motion |
| EXTRA-04: 4초 자동 닫힘 복원 | ✓ 카운트다운 바 재추가 |
| EXTRA-05: 캔버스 투명 배경 | ✓ `-transparentcolor "#010101"` |
| EXTRA-06: 창 테두리 제거 | ✓ outer 프레임 제거 |
| TRAY-01: 동적 시계 아이콘 | ✗ → Sprint 07 |
| TRAY-02: 툴팁 갱신 5초 | ✗ → Sprint 07 |
| TRAY-03: 툴팁 정보 보강 | ✗ → Sprint 07 |

---

## 수동 검증 결과

→ QC.md 참고  
TOAST/EXTRA 전 항목 통과, TRAY 항목 미구현

---

## 산출물

| 파일 | 변경 내용 |
|------|-----------|
| `src/notification.py` | 전면 재작성: 플로팅 창, PNG, 투명 배경, 테두리 제거, fade-in, accent 색상 |
| `src/tray_app.py` | 미변경 (Sprint 07 예정) |
| `src/source/Image.png` | 사용자 제공 이미지 추가 |

---

## Sprint 06 주요 변경 요약

Sprint 06는 초기 계획(토스트 색상·트레이 개선)에서 출발했으나,  
사용자 요청으로 알람 창이 대폭 리디자인되었다.

1. **Canvas 고양이 도형** 애니메이션 구현
2. **PNG 이미지**로 교체 (사용자 제공 이미지)
3. **플로팅 창** 전환 (드래그 이동, overrideredirect)
4. **투명 배경** 적용 (바탕화면 투과)
5. **테두리 제거** (outer 프레임 삭제)

결과적으로 알람 창이 기존 토스트와 완전히 다른 형태로 진화했다.

---

## 다음 스프린트 이관 사항

| 항목 | 내용 |
|------|------|
| TRAY-01 | 동적 시계 아이콘 (`tray_app.py` `_create_icon_image()` 개선) |
| TRAY-02 | 툴팁 갱신 주기 30초 → 5초 |
| TRAY-03 | 툴팁에 날짜, 활성 알람 수 추가 |
| TOAST-02 검토 | 드래그 유지하면서 클릭 닫힘 병행 가능 여부 |
