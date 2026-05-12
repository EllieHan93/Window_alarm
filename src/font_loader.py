"""커스텀 폰트를 Windows에 등록하고 폰트 패밀리 이름을 제공한다."""
import ctypes
from pathlib import Path

_FONT_DIR   = Path(__file__).parent.parent / "fonts" / "Mona_20260424_2053" / "ttf"
_FONT_MAIN  = _FONT_DIR / "01_Main"  / "Mona12.ttf"
_FONT_KR    = _FONT_DIR / "03_Text"  / "Mona12TextKR.ttf"
_FONT_EMOJI = _FONT_DIR / "02_Emoji" / "Mona12ColorEmoji.ttf"

_FAMILY = "맑은 고딕"  # fallback


def load() -> str:
    global _FAMILY
    try:
        ctypes.windll.gdi32.AddFontResourceW(str(_FONT_MAIN))
        ctypes.windll.gdi32.AddFontResourceW(str(_FONT_KR))
        ctypes.windll.gdi32.AddFontResourceW(str(_FONT_EMOJI))
        import tkinter.font as tkfont
        for name in tkfont.families():
            if "mona" in name.lower():
                _FAMILY = name
                return _FAMILY
        _FAMILY = "Mona12"
    except Exception:
        pass
    return _FAMILY


def family() -> str:
    return _FAMILY


def emoji_family() -> str:
    """이모티콘 포함 위젯용 폰트."""
    return "Segoe UI"
