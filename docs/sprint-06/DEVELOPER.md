# Sprint 06 — 개발 사양서

**스프린트:** 06 / 토스트 & 트레이 디자인 개선  
**기간:** 2026-05-08  
**담당 모듈:** `src/notification.py`, `src/tray_app.py`

---

## 구현 완료 항목

### TOAST-01: 타입별 Accent 색상 (notification.py) ✓

```python
_ACCENT_COLORS = {
    "fixed":    "#7c3aed",
    "interval": "#2563eb",
}
```

- 타이틀 바 `bg=accent`, 말풍선 `outline=accent`, 카운트다운 바 `bg=accent` 통일 적용

---

### TOAST-03: Fade-in 효과 (notification.py) ✓

```python
_FADEIN_STEPS = 10
_FADEIN_MS    = 25   # 25ms × 10 = 250ms

def start_fadein():
    step = [0]
    def _step():
        step[0] += 1
        dialog.wm_attributes("-alpha", min(step[0] / _FADEIN_STEPS, 1.0))
        if step[0] < _FADEIN_STEPS:
            dialog.after(_FADEIN_MS, _step)
        else:
            start_ts[0] = time.time()
            dialog.after(10, animate)
    dialog.after(_FADEIN_MS, _step)
```

---

### EXTRA-01~02: PNG 이미지 (notification.py) ✓

```python
_IMG_PATH = Path(__file__).parent / "source" / "Image.png"

def _load_image(max_w: int, max_h: int):
    from PIL import Image, ImageTk
    img = Image.open(_IMG_PATH).convert("RGBA")
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# Canvas에 하단 중앙 배치
photo = _load_image(_W - 20, _CANVAS_H - 70)
canvas.photo = photo   # GC 방지
```

---

### EXTRA-03/04: 플로팅 창 + 4초 자동 닫힘 (notification.py) ✓

```python
dialog.overrideredirect(True)
dialog.wm_attributes("-topmost", True)

# 드래그
drag = {"x": 0, "y": 0}
def _drag_start(e): drag["x"] = e.x_root - dialog.winfo_x(); drag["y"] = e.y_root - dialog.winfo_y()
def _drag_move(e):  dialog.geometry(f"+{e.x_root - drag['x']}+{e.y_root - drag['y']}")
for w in (title_bar, canvas):
    w.bind("<ButtonPress-1>", _drag_start)
    w.bind("<B1-Motion>",     _drag_move)

# 4초 카운트다운
_DURATION_MS = 4000
t = min(elapsed_ms / _DURATION_MS, 1.0)
bar_fill.place(relwidth=max(0.0, 1.0 - t))
if t >= 1.0: close()
```

---

### EXTRA-05: 캔버스 투명 배경 (notification.py) ✓

```python
_TRANSPARENT_COLOR = "#010101"

canvas = tk.Canvas(inner, bg=_TRANSPARENT_COLOR, highlightthickness=0)
dialog.wm_attributes("-transparentcolor", _TRANSPARENT_COLOR)
```

- `_draw_scene()` 내 배경 사각형 미사용 (canvas.delete("all") 후 이미지/말풍선만 그림)

---

### EXTRA-06: 창 테두리 제거 (notification.py) ✓

```python
# outer 프레임 제거 (이전: bg="#d1d5db", padx=1, pady=1)
inner = tk.Frame(dialog, bg="#ffffff")
inner.pack(fill="both", expand=True)
```

---

### 말풍선 Bobbing 애니메이션 (notification.py) ✓

```python
bob = int(3 * math.sin(frame * 0.08))
by1 = 6 + bob   # ±3px 상하 진동
```

---

## 미구현 항목 (Sprint 07 이관)

| 항목 | 이유 |
|------|------|
| TOAST-02: 클릭 닫힘 | 드래그와 이벤트 충돌 가능, 버튼 방식 유지 |
| TRAY-01: 동적 시계 아이콘 | 현재 12시 방향 정적 아이콘 (`_create_icon_image()`) |
| TRAY-02: 5초 갱신 | 현재 `time.sleep(30)` |
| TRAY-03: 툴팁 보강 | 현재 사용 시간 + 다음 알람만 표시, 날짜/활성 알람 수 없음 |

---

## 테스트 계획

자동화 TC 없음 (UI/트레이 전용). 수동 검증으로 진행.

| 항목 | 검증 방법 |
|------|-----------|
| 고정 알람 토스트 보라 타이틀 바 | 미리보기 버튼(fixed) |
| 인터벌 알람 토스트 파랑 타이틀 바 | 인터벌 알람 발화 |
| Fade-in 등장 | 토스트 등장 시 육안 확인 |
| 캔버스 투명 | 바탕화면이 이미지 주변으로 보임 |
| 드래그 이동 | 타이틀 바 / 캔버스 드래그 |
| 4초 자동 닫힘 | 카운트다운 바 소진 후 닫힘 확인 |
| 스누즈 5분 후 재발화 | [5분 후 다시] 클릭 후 5분 대기 |
