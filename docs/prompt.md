# TP Alarm — 프롬프트 기록

이 파일은 프로젝트 전반에 걸쳐 사용자가 요청한 주요 프롬프트를 스프린트 단위로 정리한다.

---

## 프로젝트 시작

> 윈도우에 설치될 파일을 만들고싶은데, 사용시간을 알려주기도 하고 특정시간에는 알람이 뜨게 하고싶어

- Python(tkinter) + pystray 기반 Windows 알람 앱 방향 결정
- 사용 시간: 앱 시작 기준 / PC 부팅 기준 두 가지 모드
- 알람 종류: 특정 시각(고정) + 사용 시간 기준(인터벌)

> (질의응답) 개발 언어, 알람 모드, 소리 여부 등 방향 확정

---

## Sprint 01 — 기반 레이어

> TC도 만들어줘 각 단계 스프린트 단위로 하고싶어

- 스프린트 단위로 TC 파일 분리 결정
- `tests/test_sprint1_config.py` 생성 (TC 12개)

> 결과md도 작성해야해

- 각 스프린트마다 `RESULT.md` 생성 규칙 수립

---

## 프로젝트 구조 정리

> /init

- `CLAUDE.md` 생성 (빌드 명령, 아키텍처, 모듈 역할 문서화)

> 이 프로그램 설치 파일도 만들고 싶은데?

- PyInstaller + Inno Setup 방향 결정
- `tp_alarm.spec`, `installer.iss` 생성 → Sprint 04로 편입

> 에이전트를 3개로 나눠서 기획자, 디자이너, 개발자 이렇게

- 스프린트 문서를 기획자(PLANNER) / 디자이너(DESIGNER) / 개발자(DEVELOPER) 3역할로 분리

> 전체적으로 경로 정리를 좀해야할거같아 문서 랑 소스코드랑 등등

- 디렉토리 재구성: `src/`, `tests/`, `docs/`, `assets/`

> 그리고 각 담당 역할에 따른 md 파일들도 역시 스프린트 단위로 버전별 관리가 필요해  
> 각 작업은 전부 스프린트 단위로 문서작성이 있어야하고 스프린트가 끝날때마다  
> 스프린트 결과 산출물도 있어야해 스프린트 단위별로 폴더 관리하는게 좋겠지?

- `docs/sprint-01/` ~ `docs/sprint-04/` 폴더 구조 확정
- 각 폴더에 PLANNER / DESIGNER / DEVELOPER / RESULT 4파일 고정

> 좋은데 planner 완료 체크도 해줘

- PLANNER.md 완료 조건에 체크박스 추가

> 완료 하면 x가 아니라 o 로 하는게 좋을거같아

- 체크 표시: `- [x]` → `- [o]` 로 통일

---

## Sprint 04 — 빌드/배포

> 한번 실행해볼까?

- 앱 구문 검사 및 빌드 확인 진행
- Inno Setup [Code] 섹션 `ResultCode` 변수 선언 누락 버그 수정
- PyInstaller 빌드 성공, Inno Setup 설치 파일 생성 완료

---

## Sprint 05 — UI·UX 개선

> 아 UI가 너무 마음에 안들어 ㅋㅋㅋㅋㅋ 일단, 색을 흰색으로 해줘볼래?  
> 그리고 알람이 울리면 어떻게 울리는지 보여줄수있어?

- `main_window.py` 다크 테마 → 라이트(화이트) 테마 전환
- `notification.py` 색상 라이트 테마 적용
- 헤더에 [🔔 알람 미리보기] 버튼 추가

> 1. 이 프로그램은 참고로 pc가 켜지면 자동 실행이었으면 좋겠어.  
> 2. 알람 팝업은 팝업창이 아니라 모달?없이 사진이나 애니메이션을 창에 띄워서  
>    2-3초 정도 보여주고 자동으로 닫고싶어

- `config_manager.py`: `start_with_windows` 기본값 `True`, 시작 시 레지스트리 동기화
- `notification.py` 완전 재작성: 비모달 토스트 + Canvas 파문/벨 애니메이션 + 3초 자동 닫힘

> 우리 context 프롬프트 모두 스프린트 나눈거에 각각 md 파일로 저장해줘

- `docs/sprint-01/RESULT.md` ~ `docs/sprint-03/RESULT.md` 후속 변경 사항 반영
- `docs/sprint-03/DESIGNER.md`, `DEVELOPER.md` 라이트 테마 및 토스트 설계 업데이트

> 지금부턴 스프린트 5 야

- `docs/sprint-05/` 폴더 생성 (PLANNER / DESIGNER / DEVELOPER / RESULT)
- Sprint 05 = UI·UX 개선 스프린트로 공식화

> 지금까지의 내 프롬프트를 prompt.md 라고해서 정리해줘

- 이 파일 생성

> 좋아, 앞으로의 프롬프트도 항상 이렇게 정리해줘.  
> 그럼 work 프로세스 한번 되짚어볼까?  
> 그리고 각 스프린트단위로 tc생성 및 결과도 QC 에이전트 생성해서 md도 관리하는게 좋겠어.

> 알람 화면엔 현재시간이랑 만약 인터벌 알람이면 사용시간 같이 보이게  
> 고정시각 알람이면 현재시간만 보이게 해줘

- 토스트에 시간 정보 행 추가: 고정 알람 → 현재 시각만, 인터벌 알람 → 현재 시각 + 사용 시간
- `AlarmNotification.show()`에 `usage_seconds`, `get_usage_fn` 파라미터 추가
- `main.py` `_process_queue()`에서 `alarm_mgr.get_usage_seconds()` 전달
- 스누즈 재발화 시에도 `get_usage_fn`으로 최신 사용 시간 사용

> 시간 형식은 yyyy/mm/dd HH:MM 가 나을거같고, 토글 위치 오른쪽 위로 변경하자

- 시간 표시 형식: `"%H:%M"` → `"%Y/%m/%d %H:%M"` (예: `2026/05/08 14:32`)
- 토스트 위치: 화면 우하단 → 화면 우상단 (`+{sw-_TOAST_W-20}+20`)

---

## Sprint 06 — 토스트 & 트레이 디자인 개선

> 스프린트 6이야

- Sprint 06 공식화: 알람 토스트 디자인 + 트레이 아이콘/툴팁 개선
- `docs/sprint-06/` 폴더 생성 (PLANNER / DESIGNER / DEVELOPER / QC / RESULT)

> 그리고 각 md 파일 업데이트

- Sprint 06 전체 문서 초안 작성
- PLANNER: TOAST-01~03, TRAY-01~03 범위 정의
- DESIGNER: 타입별 색상표, 동적 아이콘 설계, 툴팁 형식
- DEVELOPER: 구현 사양 (accent 색상 dict, fade-in 로직, 동적 시계 각도 계산)
- QC: 수동 검증 항목 13개 (구현 후 결과 기입 예정)
- RESULT: 진행 중 상태로 생성

> test sprint는 왜 3에서 멈춘거야?

- Sprint 04(빌드), 05~06(UI/Canvas)는 headless 자동화 불가 → 수동 검증으로 대체
- Sprint 05의 `start_with_windows=True` 기본값 등 로직 변경은 TC 보강 가능 (선택)

> 알람창이 창 형태가 아니라, 고양이가 공 가지고 논다거나 그런 애니메이션? 형태로도 가능해? 고양이에게 말풍성이 나온다거나

- 기존 토스트를 Canvas 기반 고양이 애니메이션 창으로 완전 교체
- 고양이(Canvas shapes): 몸통/머리/귀/눈(깜빡임)/코/입/수염/꼬리(흔들기)/앞발(공 근처서 올라감)
- 공: 좌우+바운스 애니메이션, 타입별 accent 색상
- 말풍선: 알람 타입 + 라벨 표시, 고양이 머리 위 배치
- 하단 패널: 날짜+시간 정보, 버튼, 카운트다운 바
- 페이드인 0.3초 + 4초 자동 닫힘 유지

> 토글창이 아니라 플로팅 창도 가능해?

- 알람 알림을 **드래그 가능한 플로팅 창**으로 변경
- 자동 닫힘 제거 → [닫기]/[5분 후 다시] 버튼으로만 닫힘
- 상단 타이틀 바 드래그로 화면 어디든 이동 가능 (`cursor="fleur"`)
- 고양이 캔버스도 드래그 핸들로 사용 가능
- 카운트다운 바 제거 → 하단 accent 고정 선으로 교체
- 애니메이션 무한 반복 (닫힐 때까지 고양이 계속 놀음)

> 플로팅창은 4초뒤 자동 닫힘 안되나?

- 자동 닫힘 복원: 4초 후 자동 닫힘 + 카운트다운 바 재추가
- 드래그 이동은 유지 (플로팅 + 자동 닫힘 둘 다 적용)

- 토스트에 시간 정보 행 추가: 고정 알람 → 현재 시각만, 인터벌 알람 → 현재 시각 + 사용 시간
- `AlarmNotification.show()`에 `usage_seconds`, `get_usage_fn` 파라미터 추가
- `main.py` `_process_queue()`에서 `alarm_mgr.get_usage_seconds()` 전달
- 스누즈 재발화 시에도 `get_usage_fn`으로 최신 사용 시간 사용

> 일단, png를 줄게 고양이 그림은 다 없애고 이 사진으로 대체 해보자  
> D:\Project\Study\TP_alarm\src\source\Image.png

- Canvas 고양이/공 도형 애니메이션 전체 제거
- `_load_image()`로 PNG 로드 → `_draw_scene()`에서 캔버스 하단 중앙에 표시
- 말풍선 + 페이드인 + 4초 자동 닫힘 + 드래그 유지

> 배경화면은 없었으면 좋겠어

- `_draw_scene()` 배경 직사각형(`#f8fafc`) 제거
- Canvas `bg` 를 `#f8fafc` → `#ffffff` (창 배경과 통일)

> 흰배경도 필요없다면? translate로 투명하게

- `_TRANSPARENT_COLOR = "#010101"` 상수 추가 (chroma key)
- Canvas `bg` → `_TRANSPARENT_COLOR`
- `dialog.wm_attributes("-transparentcolor", _TRANSPARENT_COLOR)` 적용
- 캔버스 영역(이미지+말풍선 외 공간)이 완전 투명 → 바탕화면이 보임
- 타이틀 바·하단 패널은 `#010101`을 사용하지 않아 불투명 유지

> 창 테두리도 아예 없애줘

- `outer` 프레임(`bg="#d1d5db"`, padx=1, pady=1) 제거
- `inner` 프레임을 `dialog`에 직접 pack

> 여기까지 스프린트 정리해보자
> 아 그리고 스프린트가 하나 끝나면 모든 화면의 스크린샷 찍어서 기록해줄래?

- 스프린트 종료 시 앱 실행 → 화면 스크린샷 촬영 → `docs/sprint-XX/screenshots/` 에 저장하는 규칙 수립

---

## Sprint 07 — 관리자 잠금 & 트레이 개선

> 이제 스프린트 7 을 진행해보자, 새로운 기능을 넣을건데,  
> 알람설정에 관련된 기능은 관리자만 볼수있게하고싶어 비밀번호는 0104  
> UI 자체를 숨기고싶고, 트레이에서 프로그램을 실행시켰을땐,  
> 사용시간만 보였으면 좋겟어, 나머지는 버튼을 들어가야 관리창이 나오게.

- `AppSettings.admin_pin = "0104"` 추가, `ConfigManager.check_pin()` 구현
- `AlarmManager.get_active_alarm_count()` 추가
- `MainWindow` 2-모드 구조: 상태 뷰(320×200) ↔ 관리 뷰(520×560)
- `PinDialog`: 4자리 PIN 입력, 3회 실패 자동 닫힘
- 트레이에서 창 열면 항상 상태 뷰(사용 시간 + [관리자 설정] 버튼)
- [🔒 잠금] 버튼으로 관리 뷰 → 상태 뷰 복귀
- TRAY-01: 동적 시계 아이콘 (`_create_icon_image()` 현재 시각 반영)
- TRAY-02: 툴팁 갱신 30초 → 5초
- TRAY-03: 툴팁에 날짜, 활성 알람 수 추가

> 여기까지 스프린트 정리해보자

- Sprint 06 전체 문서 최종 업데이트 (PLANNER / DESIGNER / DEVELOPER / QC / RESULT)
- 완료: TOAST-01(accent 색상), TOAST-03(fade-in), EXTRA(PNG·플로팅·투명·테두리 제거)
- 미완료 → Sprint 07 이관: TRAY-01(동적 아이콘), TRAY-02(5초 갱신), TRAY-03(툴팁 보강)

---

> 좋아, 앞으로의 프롬프트도 항상 이렇게 정리해줘.  
> 그럼 work 프로세스 한번 되짚어볼까?  
> 그리고 각 스프린트단위로 tc생성 및 결과도 QC 에이전트 생성해서 md도 관리하는게 좋겠어.

- 역할 5개로 확장: 기획자 / 디자이너 / 개발자 / **QC 에이전트** / 결과 취합
- `docs/PROCESS.md` 생성 — 전체 워크플로우, QC 에이전트 역할 및 파일 형식 정의
- `docs/sprint-01/QC.md` ~ `docs/sprint-05/QC.md` 생성 (TC 결과 + 수동 검증 항목)
- 각 스프린트 문서 구조: PLANNER / DESIGNER / DEVELOPER / **QC** / RESULT (5파일)
- prompt.md는 매 스프린트 종료 시 반드시 업데이트하는 규칙 수립
