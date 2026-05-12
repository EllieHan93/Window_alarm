# Sprint 07 — 개발 사양서

**스프린트:** 07 / 관리자 잠금 & 트레이 개선  
**기간:** 2026-05-12  
**담당 모듈:** `src/config_manager.py`, `src/alarm_manager.py`, `src/main_window.py`, `src/tray_app.py`

---

## AUTH-01: PIN 저장 (config_manager.py)

`AppSettings` 데이터클래스에 `admin_pin` 추가:
```python
@dataclass
class AppSettings:
    start_with_windows: bool = True
    usage_time_source: str = "app_start"
    admin_pin: str = "0104"
```

`ConfigManager.load()`에서 로드:
```python
admin_pin=s.get("admin_pin", "0104"),
```

검증 메서드:
```python
def check_pin(self, pin: str) -> bool:
    return pin == self.settings.admin_pin
```

---

## alarm_manager.py: 활성 알람 수 조회

```python
def get_active_alarm_count(self) -> int:
    return (sum(1 for a in self._fixed_alarms if a.enabled) +
            sum(1 for a in self._interval_alarms if a.enabled))
```

---

## UI-01/02: 2-모드 메인 창 (main_window.py)

### 상태 관리
```python
self._authenticated = False  # 관리 뷰 진입 여부
```

### 모드 전환
```python
def _enter_status_mode(self):
    self._authenticated = False
    self._mgmt_body.pack_forget()
    self._preview_btn.pack_forget()
    self._lock_btn.pack_forget()
    self._status_footer.pack(fill="x", pady=16)
    self._win.geometry("320x200")

def _enter_mgmt_mode(self):
    self._authenticated = True
    self._status_footer.pack_forget()
    self._preview_btn.pack(side="right", padx=12, pady=10)
    self._lock_btn.pack(side="right", padx=4, pady=10)
    self._mgmt_body.pack(fill="both", expand=True, padx=12, pady=10)
    self._win.geometry("520x560")
    self._startup_var.set(self._config.start_with_windows)
    self._refresh_fixed_tree()
    self._refresh_interval_tree()
```

### show() 동작
```python
def show(self):
    self._enter_status_mode()   # 트레이에서 열면 항상 상태 뷰
    self._win.deiconify()
    self._win.lift()
    self._win.focus_force()
```

---

## AUTH-02: PinDialog (main_window.py)

```python
class PinDialog(tk.Toplevel):
    def __init__(self, parent, config, on_success):
        # grab_set, topmost
        # Entry(show="●"), Enter 바인딩
        # 3회 실패 → 오류 메시지 → 1.5초 후 destroy
        self._attempts = 0

    def _confirm(self):
        if self._config.check_pin(self._pin_var.get()):
            self.destroy(); self._on_success()
        else:
            self._attempts += 1
            self._pin_var.set("")
            remaining = 3 - self._attempts
            if remaining <= 0:
                self._error_label.config(text="인증 실패. 잠시 후 다시 시도하세요.")
                self.after(1500, self.destroy)
            else:
                self._error_label.config(text=f"비밀번호가 틀렸습니다. ({remaining}회 남음)")
```

---

## TRAY-01: 동적 시계 아이콘 (tray_app.py)

```python
def _create_icon_image() -> Image.Image:
    import math
    from datetime import datetime
    now = datetime.now()
    size, cx, cy = 64, 32.0, 32.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, 62, 62], fill=(124, 58, 237), outline=(196, 181, 253), width=2)
    r = 26.0
    for deg in [0, 90, 180, 270]:
        rad = math.radians(deg - 90)
        draw.line([cx+(r-5)*math.cos(rad), cy+(r-5)*math.sin(rad),
                   cx+r*math.cos(rad),     cy+r*math.sin(rad)],
                  fill=(255, 255, 255, 180), width=2)
    h_rad = math.radians((now.hour % 12 + now.minute/60) * 30 - 90)
    draw.line([cx, cy, cx+12*math.cos(h_rad), cy+12*math.sin(h_rad)],
              fill=(200, 200, 255), width=2)
    m_rad = math.radians(now.minute * 6 - 90)
    draw.line([cx, cy, cx+18*math.cos(m_rad), cy+18*math.sin(m_rad)],
              fill="white", width=3)
    draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill="white")
    return img
```

---

## TRAY-02/03: 툴팁 갱신 & 보강 (tray_app.py)

```python
def _get_tooltip(self) -> str:
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%Y/%m/%d (%a)")
    usage = AlarmManager.format_duration(self._alarm_mgr.get_usage_seconds())
    next_info = self._alarm_mgr.get_next_alarm_info()
    next_str = (f"\n다음 알람: {next_info[0]} ({AlarmManager.format_duration(next_info[1])})"
                if next_info else "")
    count = self._alarm_mgr.get_active_alarm_count()
    alarm_str = f"활성 알람: {count}개" if count else "활성 알람 없음"
    return f"TP Alarm\n{date_str}\n사용 시간: {usage}{next_str}\n{alarm_str}"

def _tooltip_updater(self) -> None:
    import time
    while True:
        time.sleep(5)
        if self._icon:
            self._icon.icon  = _create_icon_image()
            self._icon.title = self._get_tooltip()
```

---

## 테스트 계획

자동화 TC 없음. 수동 검증.

| 항목 | 검증 방법 |
|------|-----------|
| 트레이 클릭 → 상태 뷰 (320×200) | 창 크기·내용 확인 |
| [관리자 설정] → PIN 다이얼로그 | 다이얼로그 표시 확인 |
| 올바른 PIN → 관리 뷰 (520×560) | 탭 및 창 크기 확인 |
| 잘못된 PIN 3회 → 자동 닫힘 | 3회 오입력 후 닫힘 확인 |
| [🔒] 클릭 → 상태 뷰 복귀 | 탭 숨김·창 축소 확인 |
| 트레이 아이콘 시침/분침 | 현재 시각과 일치 확인 |
| 툴팁 5초 갱신 | 5초 후 재호버 확인 |
| 툴팁 날짜·알람 수 | 내용 육안 확인 |
