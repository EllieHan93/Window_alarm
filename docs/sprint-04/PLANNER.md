# Sprint 04 — 기획서

**스프린트:** 04 / 빌드 및 배포  
**기간:** 2026-05-08  
**목표:** Python 미설치 환경에서도 실행 가능한 Windows 설치 파일 생성

---

## 스프린트 목표

Sprint 01~03에서 완성된 앱을 일반 사용자가 설치하고 실행할 수 있는 형태로 패키징한다.  
Python 런타임을 포함한 단독 실행 파일과 클릭 한 번으로 설치되는 설치 파일을 제공한다.

---

## 이번 스프린트 범위 (In Scope)

| ID | 기능 | 설명 |
|----|------|------|
| BUILD-01 | PyInstaller 패키징 | Python 런타임 포함 단일 폴더 `.exe` |
| BUILD-02 | 설치 파일 생성 | Inno Setup으로 `TP_Alarm_Setup.exe` 생성 |
| BUILD-03 | 설치 경험 | 클릭 3번 이내 설치 완료 |
| BUILD-04 | 제거 기능 | 프로그램 추가/제거에서 깔끔하게 제거 |
| BUILD-05 | 권한 | 관리자 권한 불필요 (사용자 권한 설치) |

---

## 완료 조건 (Definition of Done)

- [o] `dist\TP_Alarm\TP_Alarm.exe` 실행 시 Python 없이도 앱이 정상 동작한다
- [o] `installer_output\TP_Alarm_Setup.exe` 더블클릭 → 설치 완료
- [o] 설치 후 시작 메뉴에 바로가기 생성된다
- [o] 설치 중 "Windows 시작 시 자동 실행" 옵션이 표시된다
- [o] 제어판 > 앱 > TP Alarm > 제거 동작한다
- [o] 관리자 권한 없는 일반 사용자 계정에서 설치 가능하다

---

## 범위 외 (Out of Scope)

- 코드 서명 (Code Signing Certificate)
- Microsoft Store 배포
- 자동 업데이트 기능
