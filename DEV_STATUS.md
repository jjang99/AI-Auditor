# AI Auditor 개발 현황

## 기준일
- 2026-09-13

## 현재 개발 단계
- Home, Projects, Inspection, Project Detail, Reports, Administration 기본 화면 구현 상태
- Inspection 실제 동작 연결 완료
- Rule Engine 기본 구조 및 기본 실행 Rule 5개 구현 완료
- Inspection 검사 실행 → 결과 DB 저장 → Project Detail 조회 흐름 연결
- Inspection UI 최종 보정 완료 및 해당 영역 Freeze
- 다음 작업: Project Detail부터 전체 화면 최종 UI 점검 계속 진행 → 전체 UI Freeze

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

## 아직 남은 주요 작업
- 전체 화면 최종 UI 점검 완료 및 UI Freeze
- Project Detail 최종 가독성/UI 점검
- Reports / Administration 최종 UI 점검
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
3. Inspection은 확정 상태이므로 임의 수정하지 않음
4. Project Detail 화면 최종 UI 점검부터 재개
5. Project Detail → Reports → Administration → 공통 UI/화면 이동 점검
6. 전체 UI Freeze 확정 후 MVP Rule 20개 구현 단계로 이동

## 개발 진행 원칙
- 기존 파일과 실제 코드를 먼저 확인한 후 수정한다.
- 이미 만들어진 파일을 임의로 다시 만들거나 덮어쓰지 않는다.
- 확정된 UI 구조·기능·메뉴·동작을 임의로 변경하지 않는다.
- 코드 상태와 대화에서 확정한 내용을 모두 개발 기준으로 사용한다.
- 코드와 결정사항이 충돌하면 임의 판단하지 않고 차이를 확인한다.
- 개발 종료 시 코드, `DEV_STATUS.md`, `DECISIONS.md`를 함께 최신화한다.
