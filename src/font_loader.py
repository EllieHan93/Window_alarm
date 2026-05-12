"""커스텀 폰트를 Windows에 등록하고 폰트 패밀리 이름을 제공한다."""
import ctypes
from pathlib import Path

_FONT_PATH = Path(__file__).parent.parent / "fonts" / "KyoboHandwriting2025lyb.ttf"
_FAMILY = "맑은 고딕"  # fallback


def load() -> str:
    """TTF를 Windows에 등록하고 실제 폰트 패밀리 이름을 반환한다."""
    global _FAMILY
    try:
        ctypes.windll.gdi32.AddFontResourceW(str(_FONT_PATH))
        import tkinter.font as tkfont
        families = tkfont.families()
        for name in families:
            if "kyobo" in name.lower() or "교보" in name:
                _FAMILY = name
                return _FAMILY
        # 등록 직후 목록 갱신 전일 수 있으므로 알려진 이름으로 설정
        _FAMILY = "Kyobo Handwriting 2025"
    except Exception:
        pass
    return _FAMILY


def family() -> str:
    return _FAMILY
