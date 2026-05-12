# Sprint 10 — DEVELOPER

**스프린트:** 10 / 폰트 교체 & 게임 테마 적용

---

## 변경 파일

### `src/font_loader.py`
- `_FONT_MAIN`: `KyoboHandwriting2025lyb.ttf` → `Mona12.ttf`
- `_FONT_KR`: `Mona12TextKR.ttf` 추가 등록
- 패밀리 감지: `"mona" in name.lower()` → 감지된 이름 `"Mona12"`
- 폴백: `"Mona12"` (하드코딩)

### `src/main_window.py`
- 색상 상수 전면 교체 (`_ACCENT`, `_BG2`, `_FG`, `_GREEN`, `_RED`, `_YELLOW` 추가)
- `_style_setup()`: TButton active `#0277b8`, Danger active `#c41e1b`
- 헤더 버튼 active 색상 업데이트
- `_build_ui()`: stats 패널에 `_ACCENT` 2px 래퍼 Frame 추가
- `_build_ui()`: 음료 버튼 영역에 `_YELLOW` 2px 래퍼 Frame 추가
- 🎮 → 🕹️ 이모티콘 변경

### `src/notification.py`
- `_ACCENT_COLORS`: `"fixed"` → `#E52521`, `"interval"` → `#049CD8`
- `inner` Frame에 `highlightthickness=2, highlightbackground=accent` 추가
- 텍스트 색상 `#1f2937` → `#000000`, `#6b7280` → `#555555`
- 버튼 배경 `#f3f4f6` → `#e0e0e0`
- 🕹️ 이모티콘 변경

### `src/tray_app.py`
- 아이콘 원: `fill=(124,58,237)` → `(4,156,216)` (파랑)
- 아이콘 테두리: `outline=(196,181,253)` → `(251,208,0)` (노랑)
- 툴팁 `"TP Alarm"` → `"양방구는 게임중"`

---

## 테스트 목록

| TC | 내용 | 방법 |
|----|------|------|
| TC-S10-01 | Mona12 폰트 정상 렌더링 | 수동 |
| TC-S10-02 | 헤더 파랑, 버튼 파랑/초록 표시 | 수동 |
| TC-S10-03 | stats 패널 파란 픽셀 테두리 | 수동 |
| TC-S10-04 | 음료 버튼 영역 노란 픽셀 테두리 | 수동 |
| TC-S10-05 | 고정알람 팝업 빨간 테두리 | 수동 |
| TC-S10-06 | 인터벌알람 팝업 파란 테두리 | 수동 |
| TC-S10-07 | 트레이 아이콘 파랑+노랑 | 수동 |
