# Sprint 04 — 개발 사양서

**스프린트:** 04 / 빌드 및 배포  
**기간:** 2026-05-08  
**담당 파일:** `tp_alarm.spec`, `installer.iss`

---

## 빌드 순서

```powershell
# Step 1: PyInstaller → dist\TP_Alarm\
pyinstaller tp_alarm.spec --clean

# Step 2: Inno Setup → installer_output\TP_Alarm_Setup.exe
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

---

## tp_alarm.spec 핵심 설정

```python
a = Analysis(
    ['src/main.py'],        # 진입점
    pathex=['src'],         # 모듈 탐색 경로
    datas=[('assets', 'assets')],  # icon.ico 포함
    hiddenimports=[
        'pystray._win32',          # Windows 트레이 백엔드
        'PIL._tkinter_finder',     # Pillow-tkinter 연동
    ],
)

exe = EXE(..., console=False, icon='assets/icon.ico')  # 콘솔 창 없음

coll = COLLECT(...)  # --onedir (폴더 방식)
```

**`--onedir` 선택 이유:** `--onefile` 대비 시작 시간 2~3초 단축 (트레이 상주 앱에 중요).

---

## installer.iss 핵심 설정

```ini
[Setup]
DefaultDirName={localappdata}\TP Alarm   ; 사용자 권한 설치
PrivilegesRequired=lowest                ; 관리자 불필요
OutputBaseFilename=TP_Alarm_Setup

[Tasks]
; 선택 옵션: 바탕화면 바로가기, Windows 시작 자동 실행
Name: "desktopicon"; Flags: unchecked
Name: "startuprun"; Description: "Windows 시작 시 자동 실행"

[Files]
Source: "dist\TP_Alarm\TP_Alarm.exe"
Source: "dist\TP_Alarm\_internal\*"; Flags: recursesubdirs
Source: "assets\icon.ico"

[Code]
; 설치 전 실행 중인 앱 자동 종료
procedure CurStepChanged(CurStep: TSetupStep);
var ResultCode: Integer;
begin
  if CurStep = ssInstall then
    Exec('taskkill.exe', '/f /im TP_Alarm.exe', '', SW_HIDE,
         ewWaitUntilTerminated, ResultCode);
end;
```

---

## PyInstaller 주의사항

| 항목 | 내용 |
|------|------|
| `pystray._win32` | hidden import 필수 — 자동 감지 안 됨 |
| `PIL._tkinter_finder` | hidden import 필수 |
| assets 경로 | 런타임에서 `sys._MEIPASS / "assets"` 로 접근 |
| 콘솔 창 | `console=False` 필수 — 트레이 앱에서 콘솔 노출 금지 |

---

## 수동 검증 체크리스트

| 항목 | 방법 | 기대 결과 |
|------|------|-----------|
| Python 없는 환경 실행 | Python 제거 후 `.exe` 실행 | 앱 정상 동작 |
| 설치 → 실행 | `TP_Alarm_Setup.exe` 더블클릭 | 설치 완료, 앱 자동 시작 |
| 관리자 권한 없이 설치 | 일반 계정에서 실행 | UAC 없이 설치 완료 |
| 제거 | 제어판 > 앱 > TP Alarm > 제거 | 파일 삭제, 시작 메뉴 제거 |
| 재설치 (기존 앱 실행 중) | 실행 중 상태에서 setup 재실행 | 기존 프로세스 종료 후 설치 |
| 바탕화면 바로가기 | 설치 시 옵션 체크 | 바탕화면에 아이콘 생성 |
| Windows 시작 프로그램 | 설치 시 옵션 체크 → 재부팅 | 자동 실행 확인 |
