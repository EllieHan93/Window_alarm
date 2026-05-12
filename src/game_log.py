"""일별 게임(앱 사용) 시간을 기록한다."""
import json
import os
from datetime import date
from pathlib import Path

_LOG_DIR  = Path(os.environ.get("APPDATA", ".")) / "TP_alarm"
_LOG_FILE = _LOG_DIR / "game_log.json"


def update(seconds: int) -> None:
    """오늘 기록을 갱신한다. 같은 날 여러 세션이 있으면 가장 긴 값을 유지."""
    today = date.today().isoformat()
    data  = _load()
    data[today] = max(data.get(today, 0), seconds)
    _save(data)


def get_log() -> dict:
    """날짜 → 초(int) 딕셔너리 (최신순)."""
    return dict(sorted(_load().items(), reverse=True))


def fmt_duration(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, _   = divmod(rem, 60)
    if h > 0:
        return f"{h}시간 {m:02d}분"
    return f"{m}분"


def _load() -> dict:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    if _LOG_FILE.exists():
        try:
            with open(_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(data: dict) -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
