# Sprint 05 — 개발 사양서

**스프린트:** 05 / UI·UX 개선  
**기간:** 2026-05-08  
**담당 모듈:** `src/main_window.py`, `src/notification.py`, `src/config_manager.py`

---

## UI-01: 라이트 테마 전환 (main_window.py)

### 색상 상수 변경

```python
# 변경 전 (다크)       →  변경 후 (라이트)
_BG    = "#1e1e2e"    →  _BG    = "#ffffff"
_BG2   = "#2a2a3e"    →  _BG2   = "#f3f4f6"
_ACCENT= "#7c3aed"    →  _ACCENT= "#7c3aed"  # 유지
_FG    = "#e2e8f0"    →  _FG    = "#1f2937"
_FG2   = "#94a3b8"    →  _FG2   = "#6b7280"
_GREEN = "#10b981"    →  _GREEN = "#059669"
_RED   = "#ef4444"    →  _RED   = "#dc2626"
```

### ttk 스타일 변경 사항

```python
# 입력 위젯: 흰 배경으로 고정 (라이트 테마에서 fieldbackground 명시)
style.configure("TCombobox", fieldbackground="white", ...)
style.configure("TEntry",    fieldbackground="white", ...)
style.configure("TSpinbox",  fieldbackground="white", ...)
# Treeview 헤더: _BG → _BG2 (흰 배경에서 구분 목적)
style.configure("Treeview.Heading", background=_BG2, ...)
```

---

## UI-02: 비모달 토스트 알림 (notification.py)

### 핵심 변경: 모달 → 비모달

```python
# 제거됨
dialog.grab_set()
dialog.wait_window()

# 추가됨
dialog.overrideredirect(True)   # 보더리스
# 3초 후 자동 닫힘 → animate() 루프에서 t >= 1.0 시 close() 호출
```

### 자동 닫힘 + 애니메이션 루프

```python
_DURATION_MS = 3000
_FRAME_MS    = 33     # ~30fps

start_ts = time.time()
closed = [False]

def close():
    if not closed[0] and dialog.winfo_exists():
        closed[0] = True
        dialog.destroy()

def animate():
    if closed[0] or not dialog.winfo_exists():
        return
    elapsed_ms = (time.time() - start_ts) * 1000
    t = min(elapsed_ms / _DURATION_MS, 1.0)

    bar_fill.place(relwidth=max(0.0, 1.0 - t))  # 프로그레스 바

    canvas.delete("all")
    for i in range(3):                           # 파문 3개
        phase = (elapsed_ms / 900 + i / 3) % 1.0
        r = int(6 + phase * 26)
        color = _lerp_color("#7c3aed", "#ede9fe", phase)
        width = max(1, int(2.5 * (1 - phase)))
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color, width=width)

    swing = math.sin(elapsed_ms / 180) * 2      # 벨 흔들기
    canvas.create_text(cx, cy + int(swing), text="🔔",
                       font=("맑은 고딕", 20), fill="#7c3aed")

    if t >= 1.0:
        close(); return
    dialog.after(_FRAME_MS, animate)

dialog.after(10, animate)
```

### 색상 보간 헬퍼

```python
def _lerp_color(c1: str, c2: str, t: float) -> str:
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02x}{g:02x}{b:02x}"
```

### 스누즈 (비모달 방식)

```python
def on_snooze():
    close()                                              # 즉시 닫힘
    _schedule_snooze(root, label, alarm_type, sound, 5) # 별도 예약

def _schedule_snooze(root, label, alarm_type, sound, minutes):
    ms = minutes * 60 * 1000
    root.after(ms, lambda: AlarmNotification.show(root, label, alarm_type, sound))
```

---

## UI-03: 알람 미리보기 버튼 (main_window.py)

### 헤더에 버튼 추가

```python
# _build_ui() 내 헤더 프레임에 추가
tk.Button(hdr, text="🔔 알람 미리보기",
          font=("맑은 고딕", 9), bg="#6d28d9", fg="white",
          relief="flat", padx=10, pady=4, cursor="hand2",
          command=self._preview_alarm).pack(side="right", padx=12, pady=10)
```

### 미리보기 메서드

```python
def _preview_alarm(self) -> None:
    AlarmNotification.show(self._root, "미리보기 알람", "fixed", "default")
```

import 추가: `from notification import AlarmNotification`

---

## UI-04: 자동 실행 기본 활성화 (config_manager.py)

### 기본값 변경

```python
# AppSettings 데이터클래스
start_with_windows: bool = True   # False → True

# _DEFAULT_CONFIG
"start_with_windows": True        # False → True

# load() 내 폴백
s.get("start_with_windows", True) # False → True
```

### 시작 시 레지스트리 동기화

```python
def load(self) -> None:
    ...
    self.settings = AppSettings(
        start_with_windows=s.get("start_with_windows", True),
        ...
    )
    self._write_startup_registry(self.settings.start_with_windows)  # 추가
```

**효과:** 앱 시작 시 config.json 값과 레지스트리가 항상 일치하도록 보장.  
수동으로 레지스트리 키를 삭제해도 앱 재시작 시 복구된다.

---

## 테스트 계획

Sprint 05는 UI 변경 위주이므로 자동화 TC 추가 없이 수동 검증으로 진행한다.

| 항목 | 검증 방법 |
|------|-----------|
| 라이트 테마 적용 | 앱 실행 후 창 배경 흰색 확인 |
| 토스트 자동 닫힘 | 알람 발화 후 3초 내 닫힘 확인 |
| 토스트 애니메이션 | 파문 + 벨 흔들기 육안 확인 |
| 미리보기 버튼 | 버튼 클릭 → 토스트 즉시 표시 |
| 자동 실행 등록 | 최초 실행 후 regedit에서 TP_Alarm 키 확인 |
| 기존 TC | `python -m pytest tests/ -v` 전체 통과 확인 |
