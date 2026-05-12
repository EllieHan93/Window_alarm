"""Telegram 봇 메시지 발송 유틸리티."""
import json
import threading
import urllib.request


def send_telegram(token: str, chat_id: str, text: str) -> None:
    """Telegram 봇으로 메시지를 비동기 발송한다. 실패해도 앱에 영향 없음."""
    if not token or not chat_id:
        return

    def _send():
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass

    threading.Thread(target=_send, daemon=True).start()
