"""음료 요청 횟수를 날짜별로 기록한다."""
import json
import os
from datetime import date
from pathlib import Path

_LOG_DIR  = Path(os.environ.get("APPDATA", ".")) / "TP_alarm"
_LOG_FILE = _LOG_DIR / "drink_log.json"


def record(drink_type: str) -> None:
    """drink_type: 'coffee' | 'tea'"""
    today = date.today().isoformat()
    data  = _load()
    day   = data.setdefault(today, {"coffee": 0, "tea": 0})
    day[drink_type] = day.get(drink_type, 0) + 1
    _save(data)


def get_log() -> dict:
    """날짜 → {"coffee": N, "tea": N} 딕셔너리 (최신순)."""
    return dict(sorted(_load().items(), reverse=True))


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
