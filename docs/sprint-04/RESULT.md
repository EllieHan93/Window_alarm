# Sprint 04 — 결과 보고서

**스프린트:** 04 / 빌드 및 배포  
**완료일:** 2026-05-08  
**상태:** ✅ 완료

---

## 완료된 작업

| 항목 | 결과 |
|------|------|
| `tp_alarm.spec` 작성 | ✅ 완료 |
| `installer.iss` 작성 | ✅ 완료 |
| PyInstaller 빌드 성공 | ✅ 완료 |
| Inno Setup 빌드 성공 | ✅ 완료 |
| `.gitignore` (build/dist/installer_output 제외) | ✅ 완료 |

---

## 빌드 결과

| 산출물 | 경로 | 크기 |
|--------|------|------|
| 앱 실행 파일 | `dist\TP_Alarm\TP_Alarm.exe` | ~5.6 MB |
| 설치 파일 | `installer_output\TP_Alarm_Setup.exe` | ~21.9 MB |

---

## 수동 검증 결과

| 항목 | 결과 |
|------|------|
| PyInstaller 빌드 완료 | ✅ 확인 |
| Inno Setup 빌드 완료 | ✅ 확인 |
| 설치 마법사 한국어 표시 | ✅ 확인 |
| 관리자 권한 없이 설치 | ✅ 확인 |

---

## 산출물

| 파일 | 설명 |
|------|------|
| `tp_alarm.spec` | PyInstaller 빌드 스펙 |
| `installer.iss` | Inno Setup 설치 스크립트 |
| `installer_output\TP_Alarm_Setup.exe` | 최종 배포 파일 |
| `requirements.txt` | 개발 의존성 목록 |

---

## v1.0.0 릴리스 요약

| 스프린트 | 범위 | TC | 상태 |
|----------|------|----|------|
| Sprint 01 | 기반 레이어 (ConfigManager) | 12 | ✅ |
| Sprint 02 | 알람 로직 (AlarmManager) | 18 | ✅ |
| Sprint 03 | UI/스레딩 통합 | 6 | ✅ |
| Sprint 04 | 빌드/배포 | 수동 | ✅ |
| **합계** | | **36** | **✅ 전체 통과** |
