"""Sprint 09 스크린샷 캡처 스크립트."""
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).parent

def _save(name: str, x: int, y: int, w: int, h: int) -> None:
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(OUT / name)
        print(f"  saved: {name}")
    except Exception as e:
        print(f"  FAIL {name}: {e}")

def main():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.destroy()

    print("앱을 실행하고 5초 기다립니다...")
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).parents[3] / "src" / "main.py")]
    )
    time.sleep(5)

    # 01 — 상태 뷰 (앱 시작 시 자동 표시, 400×240 위치 오른쪽 상단 추정)
    _save("01_status_view.png", sw - 440, 0, 440, 300)

    # 02 — 음료 기록 탭 (관리 뷰, 520×560)
    # 캡처 전 수동 진입 필요 — 여기서는 위치만 저장
    print("\n관리 뷰의 '음료 기록' 탭을 열어주세요. 5초 후 캡처합니다...")
    time.sleep(5)
    _save("02_drink_log_tab.png", sw // 2 - 270, sh // 2 - 290, 540, 580)

    proc.terminate()
    print("완료.")

if __name__ == "__main__":
    main()
