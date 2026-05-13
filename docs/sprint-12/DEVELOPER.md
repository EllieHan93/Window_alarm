# Sprint 12 — DEVELOPER

**스프린트:** 12 / 알림 팝업 UI 정리 & 음료 피드백 개선

---

## 변경 파일

### `src/notification.py`

**`_draw_scene()` 말풍선 텍스트 수정**

```python
# Before
type_text = "고정 시각 알람" if alarm_type == "fixed" else "인터벌 알람"
canvas.create_text(W // 2, by1 + 13, text=type_text, ...)
canvas.create_text(W // 2, by1 + 34, text=label, ...)

# After
canvas.create_text(W // 2, by1 + bh // 2, text=label, ...)
```

**`AlarmNotification.show()` 버튼 제거**

- `btn_row` 프레임 및 "5분 후 다시", "닫기" 버튼 위젯 제거
- `close()` 함수는 유지 (4초 자동 닫힘용)
- `on_snooze()` 함수 및 `_schedule_snooze()` 호출 제거

### `src/main_window.py`

**`_flash_drink()` 피드백 개선**

```python
# Before
self._drink_feedback.config(text=label_text, fg=orig)
self._win.after(700, restore)

# After
self._drink_feedback.config(text=label_text, fg=_RED)
self._win.after(1500, restore)
```

### `tp_alarm.spec`

**`src/source/Image.png` 빌드 포함 추가**

```python
# Before
datas=[('assets', 'assets')],

# After
datas=[('assets', 'assets'), ('src/source', 'source')],
```
