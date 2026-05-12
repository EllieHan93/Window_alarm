# Sprint 08 — 개발 사양서

**스프린트:** 08 / 폰트·UI 정제 & 음료 요청 알림  
**기간:** 2026-05-12

---

## FONT-01/02: font_loader.py

```python
# src/font_loader.py
import ctypes
from pathlib import Path

_FONT_PATH = Path(__file__).parent.parent / "fonts" / "KyoboHandwriting2025lyb.ttf"
_FAMILY = "맑은 고딕"

def load() -> str:
    global _FAMILY
    ctypes.windll.gdi32.AddFontResourceW(str(_FONT_PATH))
    # tkfont.families() 검색 후 매칭, 폴백은 "Kyobo Handwriting 2025"
    ...
    return _FAMILY

def family() -> str:
    return _FAMILY
```

- `main.py`에서 `root = tk.Tk()` 이후 `font_loader.load()` 호출
- `main_window.py`, `notification.py`에서 `font_loader.family()` 사용

---

## UI-02: 투명 관리자 버튼

```python
tk.Button(hdr, text="", bg=_ACCENT, fg=_ACCENT,
          activebackground=_ACCENT, activeforeground=_ACCENT,
          relief="flat", bd=0, highlightthickness=0,
          width=3, cursor="arrow",
          command=self._on_manage).pack(side="right", padx=2, pady=8)
```

---

## UI-03: 커피/차 버튼 + _send_drink()

```python
def _send_drink(self, message: str) -> None:
    from datetime import datetime
    text = f"{message}\n{datetime.now().strftime('%Y/%m/%d %H:%M')}"
    notifier.send_telegram(
        self._config.settings.telegram_token,
        self._config.settings.telegram_chat_id,
        text,
    )
```

---

## NOTIF-01: notifier.py

```python
import json, threading, urllib.request

def send_telegram(token, chat_id, text):
    if not token or not chat_id: return
    def _send():
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": text}).encode()
        req = urllib.request.Request(url, data=data,
              headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    threading.Thread(target=_send, daemon=True).start()
```

- 추가 의존성 없음 (stdlib `urllib` 사용)
- 토큰/채팅ID 미설정 시 즉시 반환 (앱 오류 없음)

---

## NOTIF-02: 설정 탭 Telegram UI

- `AppSettings.telegram_token: str = ""`
- `AppSettings.telegram_chat_id: str = ""`
- `_on_telegram_save()`: 두 값을 config에 저장
- 설정 탭 하단에 입력 필드 + [저장] 버튼 + 안내 텍스트
