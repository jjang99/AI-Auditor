# AI Auditor 개발 현황

## 기준일
- 2026-09-18

## 현재 개발 단계
- Home, Projects, Inspection, Project Detail, Reports, Administration 기본 화면 구현 상태
- Inspection 실제 동작 연결 완료
- Rule Engine 기본 구조 및 MVP 실행 Rule 20개 구현 완료(보안 6 / 코드 품질 6 / 성능 4 / AI 특화 4)
- Inspection 검사 실행 → 결과 DB 저장 → Project Detail 조회 흐름 연결
- Inspection UI 최종 보정 완료 및 해당 영역 Freeze
- 전체 화면 최종 UI 점검 완료 및 UI Freeze 최종 확정
- MVP 실행 Rule 20개 구현 및 자동 fixture 검증 완료\n- Inspection 규칙 선택/해제 → 실제 Rule Engine 실행 연동 검증 진행 중

## 2026-09-13까지 주요 구현 내용
### Inspection
- 검사 대상 파일 선택/목록 표시/개별 삭제/전체 삭제
- 검사기준 카테고리 선택 및 전체 선택/해제
- 규칙 보기 Modal 및 규칙별 선택 상태 관리
- 검사준비 요약 표시
- QThread 기반 Rule Engine 실행
- 검사 완료 결과 표시 및 DB 저장
- 검사기준 선택 UI, 규칙 Modal, 기존 프로젝트 확인 Modal 시각 보정 완료

### Rule Engine
- `rules/core/models.py`: Rule, RuleIssue, FileInspectionResult, InspectionSummary 모델
- `rules/core/engine.py`: 정규식 기반 deterministic Rule Engine
- `rules/definitions/default_rules.py`: 현재 실행 가능한 기본 Rule 5개
  - SEC-001: 하드코딩 비밀번호 의심
  - SEC-002: SQL 문자열 결합 의심
  - QUAL-001: TODO/FIXME 잔존
  - QUAL-002: 디버그 출력 잔존
  - PERF-001: 무한 반복문 의심
- 현재 AI 특화 검증 실행 Rule은 아직 없음
- 화면의 102개 규칙은 검사기준 체계상의 수량이며, 102개 실행 Rule이 구현된 의미는 아님
- 향후 MVP 목표는 약 20개의 실제 실행 가능한 Rule로 확장

### 데이터/결과 연결
- SQLite 기본 구조 구현
- 프로젝트, 검사, 이슈 저장 구조 구현
- 실제 검사 완료 후 Inspection/Issue 결과 저장
- Project Detail에서 최근 검사 및 이력/이슈 조회 구조 연결

## 2026-09-13 UI 확정 사항
- Inspection 검사기준 선택 행의 체크박스/텍스트 크기 보정 완료
- 체크박스는 선택 변경 후에도 크기와 흰색 체크 표시가 유지되도록 보정
- 규칙 Modal의 카테고리 아이콘 표시 및 크기 보정 완료
- 규칙 Modal의 규칙명/설명/상태 컬럼 정렬 보정 완료
- 기존 프로젝트 확인 Modal 선택 UI를 검사기준 선택과 동일한 사각 체크 방식으로 통일
- 휴지통 아이콘 보정 완료
- 위 Inspection 관련 시각 요소는 사용자 확인 완료 상태로 Freeze

## 현재 정상 구동 기준
- `python main.py` 실행
- Inspection 화면 파일 선택/삭제 정상
- 검사기준 선택/해제 및 규칙 Modal 정상
- Rule Engine 실제 실행 정상
- 검사 완료 결과 DB 저장 정상
- Project Detail 결과 연결 확인

## 2026-09-18 전체 UI 최종 확정
- Home / Projects / Inspection / Project Detail / Reports / Administration 다크·라이트 최종 점검 완료
- 전체 UI Freeze 최종 확정
- 카드 외곽선/내부 네모 요소는 Administration 기준, 텍스트 가독성은 Reports 기준으로 공통화
- Light Mode Soft Light 톤 최종 확정
- Freeze된 UI의 구조·크기·위치·간격·색상·폰트·테두리를 이후 기능 개발에서 임의 변경하지 않음

## 아직 남은 주요 작업
- MVP 실행 Rule 약 20개로 확장 및 AI 특화 Rule 포함
- UI 규칙 목록과 실제 Rule Engine을 하나의 기준 데이터로 연결
- 실제 worker 검사 취소 기능
- 실제 DB 기반 프로젝트 중복 확인/이동 기능 보강
- Score/Grade 산정 로직
- 비정상/이슈 발생 fixture 기반 end-to-end 검증
- 폐쇄망 Windows EXE 패키징 및 최종 테스트

## 다음 작업 시작점
1. GitHub `main` 최신 소스 확인
2. `DEV_STATUS.md`, `DECISIONS.md` 확인
3. 전체 UI는 2026-09-18 최종 Freeze 상태이므로 임의 수정하지 않음
4. MVP 실행 Rule을 약 20개로 확장하고 AI 특화 Rule 포함
5. UI 규칙 목록과 실제 Rule Engine 기준 데이터 통합
6. 검사 취소 / DB 기반 프로젝트 중복 확인 / Score·Grade / E2E 검증 순으로 진행
7. 폐쇄망 Windows EXE 패키징 및 최종 테스트

## 개발 진행 원칙
- 기존 파일과 실제 코드를 먼저 확인한 후 수정한다.
- 이미 만들어진 파일을 임의로 다시 만들거나 덮어쓰지 않는다.
- 확정된 UI 구조·기능·메뉴·동작을 임의로 변경하지 않는다.
- 코드 상태와 대화에서 확정한 내용을 모두 개발 기준으로 사용한다.
- 코드와 결정사항이 충돌하면 임의 판단하지 않고 차이를 확인한다.
- 개발 종료 시 코드, `DEV_STATUS.md`, `DECISIONS.md`를 함께 최신화한다.


## 2026-09-18 작업 마감
- 오늘 작업 주제: 전체 화면 최종 UI 점검 및 UI Freeze 확정
- Home / Projects / Inspection / Project Detail / Reports / Administration 전체 화면 최종 확인 완료
- 공통 시각 기준 최종 반영: Administration 기준 카드/내부 박스, Reports 기준 텍스트 가독성
- 다크/라이트 모드 전체 PASS 및 UI Freeze
- DECISIONS.md에 최종 Freeze 기준 기록 완료
- 다음 개발 시작점: MVP 실제 실행 Rule 약 20개 선정 및 구현
- 다음 세션에서는 UI를 다시 수정하지 않고 최신 GitHub 코드, DECISIONS.md, DEV_STATUS.md 확인 후 Rule 단계부터 재개


## 2026-09-18 MVP Rule 및 Inspection 연동 진행
- MVP 실제 실행 Rule 20개 구현 완료
  - 보안 취약점 6개
  - 코드 품질 6개
  - 성능 및 효율성 4개
  - AI 특화 검증 4개
- `tests/test_mvp_rules.py` 자동 fixture 검증을 사용자 PC에서 실행하여 4개 테스트 메서드 모두 PASS
- Rule 공통 모델에 UI 선택 위치 메타데이터(`selection_index`)를 추가하고, Inspection의 별도 하드코딩 매핑을 제거하여 Rule 정의 데이터를 사용하도록 연결
- 공통 데이터 연결 변경 후 자동 테스트 재실행 PASS
- 실제 GUI 연동 검증:
  - SEC-002 ON 상태에서 테스트 파일의 SQL 문자열 직접 조합 이슈 검출 확인
  - SEC-002 OFF 상태에서 동일 파일 재검사 시 SEC-002 미검출 확인
  - 따라서 Inspection 개별 규칙 선택/해제가 실제 Rule Engine 실행 여부에 반영됨을 확인
- 검사 완료 후 Project Detail 이동 뒤 Inspection 메뉴로 재진입하면 완료 카드가 남아 새 검사를 시작할 수 없던 상태관리 문제 발견
- Inspection 재진입 시 검사 준비 상태로 복원하도록 수정하고 사용자 화면에서 `검사 시작` 버튼 재표시 확인
- UI Freeze의 구조/크기/스타일은 변경하지 않았으며 기능 상태 및 데이터 연동만 수정
- 현재 다음 작업: 20개 Rule 공통 데이터 연결의 남은 부분 점검 및 Inspection 표시 수량(개념상 102개 / 실제 실행 20개) 정합성 검토


## 2026-09-18 MVP 기능 및 E2E 검증 추가 완료
- Inspection 적용 규칙 표시를 실제 실행 Rule 기준 20 / 20개로 연결하고 사용자 화면 확인 PASS
- 실제 검사 취소 기능 구현: QThread Worker → InspectionService → Rule Engine cooperative cancellation 연결
- 검사 취소 시 완료 결과를 저장하지 않고 검사 준비 상태로 복귀하도록 처리, 사용자 화면 확인 PASS
- 미지원 파일(PDF/DOCX 등)은 검사 등록 단계에서 제외하고 경고 안내하도록 처리
- DB 기반 동일 프로젝트명 확인 연결: 동일 이름 존재 시 기존 프로젝트 확인 Modal에 실제 DB 프로젝트 표시, 사용자 확인 PASS
- 신규 검사 완료 시 MVP Score/Grade 산정 및 DB 저장 연결, Project Detail 표시 사용자 확인 PASS
- E2E 검증 PASS:
  - 신규 프로젝트 → 파일 등록 → 20개 Rule → 검사 실행 → Issue 검출 → Score/Grade → DB 저장
  - 검사 결과 보기 → Project Detail → Issue Detail → Projects → Reports 결과 반영까지 전체 흐름 확인
- 현재 MVP 핵심 기능 흐름은 E2E 기준 정상 동작 확인

## 다음 작업 시작점
1. 최신 GitHub 코드 및 본 문서/DECISIONS.md 확인
2. UI Freeze 상태 유지
3. 폐쇄망 Windows EXE 패키징 준비
4. EXE 실행 및 SQLite/리소스/경로 동작 점검
5. 최종 회귀 테스트 및 제출 준비
