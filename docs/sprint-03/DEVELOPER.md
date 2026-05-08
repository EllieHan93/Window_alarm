# Sprint 03 — 개발 사양서

**스프린트:** 03 / UI 및 스레딩 통합  
**기간:** 2026-05-08  
**담당 모듈:** `src/main.py`, `src/tray_app.py`, `src/main_window.py`, `src/notification.py`

---

## 스레딩 아키텍처

```
┌─────────────────────────────────────────────┐
│  MAIN THREAD — tkinter mainloop()            │
│  root.after(200ms) → _process_queue()       │
│    ├─ Command("open_window") → window.show()│
│    ├─ Command("quit")        → root.quit()  │
│    └─ AlarmEvent             → show popup   │
│  MainWindow.after(1000ms) → 사용시간 갱신   │
└──────────────┬──────────────────────────────┘
               │ queue.Queue
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────────┐
│ TRAY THREAD │  │ SCHEDULER THREAD│
│ (daemon)    │  │ (daemon)        │
│ icon.run()  │  │ alarm_mgr.tick()│
│ → q.put()   │  │ every 1 sec     │
└─────────────┘  └─────────────────┘
```

**핵심 규칙:** 트레이/스케줄러 스레드는 `queue.put()`만 호출. tkinter 함수 직접 호출 금지.

---

## main.py 부트스트랩 순서

```python
1. app_start = datetime.now()
2. config = ConfigManager(); config.load()
3. queue = Queue(); stop_event = threading.Event()
4. alarm_mgr = AlarmManager(config, app_start)
5. root = tk.Tk(); root.withdraw()
6. window = MainWindow(root, queue, alarm_mgr, config)
7. tray = TrayApp(queue, alarm_mgr)
8. threading.Thread(target=tray.run, daemon=True).start()
9. threading.Thread(target=_scheduler_loop, daemon=True).start()
10. root.after(200, _process_queue, ...)
11. root.after(300, window.show)   # 시작 시 자동 표시
12. root.mainloop()
13. tray.stop()                    # 정상 종료
```

---

## tray_app.py

```python
class Command(NamedTuple):
    action: str   # "open_window" | "quit"
    payload: dict

class TrayApp:
    def run(self) -> None        # blocking, daemon 스레드
    def stop(self) -> None       # icon.stop()
    def _get_tooltip(self) -> str  # "TP Alarm\n사용 시간: ..."
    def _tooltip_updater(self)   # 30초마다 icon.title 갱신 (별도 daemon)
```

아이콘: `_create_icon_image()` → `PIL.Image` 64×64 RGBA (Pillow으로 런타임 생성)

---

## main_window.py

```python
class MainWindow:
    def show(self)          # deiconify + lift + focus_force + 트리 갱신
    def hide(self)          # withdraw
    def is_visible(self)    # winfo_viewable()

    def _refresh_display(self)      # after(1000ms) 루프 — 사용 시간 갱신
    def _refresh_fixed_tree(self)   # Treeview 재구성
    def _refresh_interval_tree(self)
```

**창 닫기 처리:**
```python
self._win.protocol("WM_DELETE_WINDOW", self.hide)  # destroy 절대 금지
```

**다이얼로그:**
- `FixedAlarmDialog(tk.Toplevel)` — 추가/수정 공용 (alarm=None이면 추가)
- `IntervalAlarmDialog(tk.Toplevel)`
- 저장 시 `on_save(alarm)` 콜백 → `config.upsert` + `alarm_mgr.reload_from_config()`

---

## notification.py

> **v1.1 변경:** 모달 블로킹 팝업 → 비모달 토스트 (3초 자동 닫힘 + Canvas 애니메이션)

```python
_TOAST_W = 340
_TOAST_H = 148
_DURATION_MS = 3000
_FRAME_MS = 33  # ~30fps

class AlarmNotification:
    @staticmethod
    def show(root, label, alarm_type, sound):
        # 1. 비동기 소리 재생 (daemon 스레드)
        # 2. overrideredirect(True) 보더리스 Toplevel 생성
        # 3. animate() — root.after(FRAME_MS) 루프로 캔버스 갱신
        # 4. 3초 경과 시 dialog.destroy() 자동 호출
        # 5. [5분 후 다시] → _schedule_snooze() 즉시 호출 후 닫힘
```

**비모달 핵심:**
```python
dialog.overrideredirect(True)    # 테두리 없는 창
dialog.wm_attributes("-topmost", True)
# grab_set(), wait_window() 없음 — UI 블로킹 안 함
```

**애니메이션 루프:**
```python
def animate():
    elapsed_ms = (time.time() - start_ts) * 1000
    t = min(elapsed_ms / _DURATION_MS, 1.0)

    bar_fill.place(relwidth=max(0, 1.0 - t))   # 프로그레스 바 축소

    # Canvas: ripple 3개 + 벨 흔들기
    for i in range(3):
        phase = (elapsed_ms / 900 + i / 3) % 1.0
        color = _lerp_color("#7c3aed", "#ede9fe", phase)
        # ...create_oval + create_text(🔔)

    if t >= 1.0:
        close(); return
    dialog.after(_FRAME_MS, animate)
```

**스누즈 (비모달):**
```python
def on_snooze():
    close()                                           # 즉시 닫힘
    _schedule_snooze(root, label, alarm_type, sound, 5)  # 예약 분리

def _schedule_snooze(root, label, alarm_type, sound, minutes):
    root.after(minutes * 60 * 1000,
               lambda: AlarmNotification.show(root, label, alarm_type, sound))
```

---

## 테스트 (Sprint 03 TC)

파일: `tests/test_sprint3_integration.py`

| TC ID | 검증 항목 |
|-------|-----------|
| TC-S3-001 | tick()은 UI 없이도 예외 없이 실행 |
| TC-S3-002 | 다중 스레드 동시 tick() 안전성 |
| TC-S3-003 | 스케줄러 루프 — 2초 인터벌 알람 자동 발화 |
| TC-S3-004 | 큐 아이템 타입 검증 (AlarmEvent) |
| TC-S3-005 | 동시 발화 알람 3개 큐에 쌓임 |
| TC-S3-006 | reload_from_config() 후 새 알람 즉시 반영 |

**실행:** `python -m pytest tests/test_sprint3_integration.py -v`
