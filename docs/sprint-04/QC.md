# Sprint 04 — QC 결과

**스프린트:** 04 / 빌드 및 배포  
**테스트 파일:** 자동화 TC 없음 (빌드/설치 검증은 수동)  
**실행일:** 2026-05-08

---

## 자동화 TC 결과

해당 없음.  
빌드 및 설치 파일 생성은 파일시스템/외부 도구(PyInstaller, Inno Setup) 의존성이 있어  
자동화 TC 대신 수동 빌드 검증으로 대체한다.

---

## 빌드 검증

### PyInstaller 빌드

| 항목 | 명령 | 결과 |
|------|------|------|
| 빌드 실행 | `pyinstaller tp_alarm.spec --clean` | ✅ 성공 |
| 산출물 확인 | `dist\TP_Alarm\TP_Alarm.exe` 존재 | ✅ 확인 |
| 크기 확인 | ~5.6 MB | ✅ 확인 |
| Python 없이 실행 | Python 미설치 환경에서 실행 | ✅ 정상 동작 |

### Inno Setup 빌드

| 항목 | 명령 | 결과 |
|------|------|------|
| 빌드 실행 | `ISCC.exe installer.iss` | ✅ 성공 |
| 산출물 확인 | `installer_output\TP_Alarm_Setup.exe` 존재 | ✅ 확인 |
| 크기 확인 | ~21.9 MB | ✅ 확인 |

---

## 수동 검증 항목

| 항목 | 검증 방법 | 결과 |
|------|-----------|------|
| 설치 마법사 한국어 표시 | Setup.exe 실행 후 언어 확인 | ✅ 확인 |
| 관리자 권한 없이 설치 | 일반 사용자 계정에서 설치 실행 | ✅ 확인 |
| 시작 메뉴 바로가기 생성 | 설치 완료 후 시작 메뉴 확인 | ✅ 확인 |
| 제어판 앱 목록 등록 | 설정 > 앱에서 "TP Alarm" 확인 | ✅ 확인 |

---

## 최종 판정

**자동화 TC: 없음**  
**수동 검증: 8항목 전부 확인**  
**→ ✅ Sprint 04 통과**

---

## 비고

- `[Code]` 섹션 `var ResultCode: Integer;` 선언 누락 버그 → 수정 후 빌드 성공
- `.gitignore`에 `dist/`, `build/`, `installer_output/` 추가 완료
- 코드 서명(Code Signing) 미적용 — Windows Defender 경고 발생 가능 (Out of Scope)
