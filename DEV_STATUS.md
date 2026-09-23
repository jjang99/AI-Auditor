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

## 2026-09-19 EXE 패키징 전 최종 회귀 보정
- PyInstaller onedir/windowed 패키징 및 외부 data DB 경로 분리까지 확인한 뒤 전체 UI 회귀 점검 수행
- Inspection Light Mode 테마 정상화 완료
- Reports Dark/Light Mode 정상화 완료
- Reports 검사보고서 목록은 7건 이상일 때만 세로 스크롤 표시하며, Project Detail Issues와 동일한 얇은 스크롤 기준으로 통일
- Project Detail Issues 스크롤은 Dark/Light 모두 주변 경계선에 맞춘 저대비·얇은 표현으로 확정
- 테마 전환 중 삭제된 CircularScore 참조로 발생하던 `Internal C++ object ... already deleted` 오류 제거
- Inspection 규칙 보기 버튼 재연결 시 발생하던 `Failed to disconnect ... clicked()` RuntimeWarning 제거
- 사용자 최종 확인: Reports Light Mode 정상, Reports/Project Detail 스크롤 정상, 위 터미널 오류/경고 재발 없음
- 위 정상 상태를 새로운 회귀 기준점으로 고정하며, 후속 작업에서 관련 UI/테마/스크롤을 임의 변경하지 않음

## 다음 작업 시작점 — 2026-09-19
1. 현재 GitHub main 정상 기준 유지
2. 최종 기능 회귀 테스트 1회 수행
3. PyInstaller `--onedir --windowed` 최종 EXE 재빌드
4. EXE에서 SQLite/data 경로, 아이콘/리소스, 핵심 E2E 재확인
5. 인터넷 차단/폐쇄망 조건의 독립 실행 검증
6. 이상 없으면 제출용 빌드 및 최종 정리

## 2026-09-19 최종 회귀 미해결 기능 목록
- [x] Projects > + New Project 클릭 무반응 — 수정 및 사용자 확인 PASS
- [x] Projects > 프로젝트 목록 페이지당 5개 페이징 — 6개 이상 목록/이전·다음 페이지 동작 사용자 확인 PASS
- [x] Project Detail > Re-Inspect 모달 내부 기능 무반응 — 파일 선택, 실제 규칙 수 표시, 기존 프로젝트 정보 복원, 동적 예상 검사시간, 재검사 실행까지 사용자 확인 PASS
- [x] Project Detail > New Inspection 클릭 무반응 — 기존 프로젝트 정보 유지 방식까지 수정 및 사용자 확인 PASS
- [x] Project Detail > Export Report 클릭 무반응 — TXT 검사보고서 저장 사용자 확인 PASS
- [x] Project Detail > Issues 정렬 버튼 무반응 — 한글화, 심각도/상태/규칙 정렬, 테마 연동, 프로젝트 전환 시 초기화, 스크롤 기반 목록으로 사용자 확인 PASS
- [x] Reports > 보고서 내보내기 클릭 무반응 — 선택 Inspection 기준 TXT 검사보고서 저장 사용자 확인 PASS
- [x] Inspection > 프로젝트명 미입력 경고 Modal — Dark/Light 테마, 경고 문구/아이콘/OK 버튼 가독성 보정 사용자 확인 PASS
- [x] Administration > 검사 기준 관리 회귀 — ON/OFF 수량 반영, 재진입 상태 유지, 카테고리 아이콘 복구, 중복 Rule Detail 제거, 행 Hover 제거 사용자 확인 PASS
- [ ] Administration > 결과 저장 경로 > 찾아보기 클릭 무반응
- 처리 원칙: 각 항목을 개별 수정 → 사용자 확인 PASS → 체크 완료 후 다음 항목 진행


# 다음 개발 기준선 — 2026-09-19

## 최종 개발 단계
1. 기존 Rule 복원·재분류 — 완료
2. 5대 영역별 전체 검사기준 확정 — 완료 (최종 105개)
3. 실제 구현할 대표 MVP 검사기준 선정 — 완료 (20개)
4. MVP 검사 Engine 구현 — 다음 작업
   - 4-1 문서 Parser 기반 구현
   - 4-2 MVP 20개 검사기준 실제 코드 정의
   - 4-3 Rule 방식 검사 구현
   - 4-4 AI / Hybrid 검사 실행구조 구현
   - 4-5 MVP 20개 통합 및 단위검증
5. Administration·Inspection 통일
6. 데이터 관리 기능 구현
7. 전체 E2E·회귀 검증
8. EXE 최종화
9. 제출 준비·최종 마무리

## 현재 시작점
- 1~3단계 완료.
- 다음 작업은 4단계 MVP 검사 Engine 구현이며, 4-1 문서 Parser 기반 구현부터 시작한다.
- Parser 지원범위: DOCX / XLSX / PDF / PPTX / HWPX. HWP는 PoC 후 안정적 지원범위를 판단한다.
- 형식별 Parser → 표준화된 공통 문서 데이터 → Rule/AI/Hybrid 검사 Engine 구조를 따른다.
- 기존 소스코드 정적분석 Rule은 삭제하지 않고 향후 확장영역으로 보존한다.
- 다음 작업 시작 시 DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → 실제 코드 순서로 현재 상태를 확인한다.

## 2026-09-20 문서 Parser 기반 구현 완료

### 4-1 문서 Parser 기반 구현

- 공통 문서 표준 모델 구현
  - `app/parsers/models.py`
  - `DocumentBlock`
  - `ParsedDocument`
- Parser 공통 인터페이스 구현
  - `app/parsers/base.py`
  - `BaseDocumentParser`
- Parser Factory 및 공통 API 구현
  - `app/parsers/parser_factory.py`
  - `app/parsers/__init__.py`
  - 파일 확장자에 따라 적합한 Parser 자동 선택
- 지원 문서 형식 총 9종
  - DOCX
  - DOC
  - XLSX
  - XLS
  - PDF
  - PPTX
  - PPT
  - HWPX
  - HWP

### 문서 형식별 처리 방식

- DOCX
  - 문단 및 표 텍스트 추출
- DOC
  - `legacy-doc` 기반 Word 97-2003 문서 텍스트 추출
- XLSX
  - 시트별 행 데이터 추출
- XLS
  - `xlrd` 기반 구형 Excel 시트/행 데이터 추출
- PDF
  - 페이지별 텍스트 추출
  - 현재 텍스트 기반 PDF 지원
- PPTX
  - 슬라이드 텍스트 및 표 추출
- PPT
  - `ppt2pptx`를 이용해 임시 PPTX로 변환
  - 기존 `PptxParser`를 재사용하여 내용 추출
  - 변환용 PPTX는 임시 디렉터리에서 처리 후 자동 삭제
- HWPX
  - ZIP/XML 구조의 section XML 기반 문단 텍스트 추출
- HWP
  - `olefile` 기반 HWP 5.x OLE 문서 분석
  - 압축된 BodyText Section을 해제한 뒤 문단 텍스트 추출

### 구형 문서 호환성 PoC 결과

- XLS 실제 샘플 추출 PASS
- HWP 5.x 실제 샘플 추출 PASS
- DOC 실제 샘플 추출 PASS
- PPT 실제 샘플 변환 및 추출 PASS
- 구형 문서 4종 모두 Microsoft Office 또는 한컴오피스 설치 없이 독립 처리 가능성 확인
- 폐쇄망 Windows EXE 적용 방향 유지

### Parser 검증 결과

- 실제 DOCX 문서 텍스트/표 추출 PASS
- 실제 XLSX 다중 시트 데이터 추출 PASS
- 실제 텍스트 기반 PDF 한글 추출 PASS
- 실제 PPTX 슬라이드/표 추출 PASS
- 실제 HWPX 문서 한글 추출 PASS
- 실제 XLS 문서 추출 PASS
- 실제 HWP 5.x 문서 추출 PASS
- 실제 DOC 문서 추출 PASS
- 실제 PPT 문서 변환 및 추출 PASS
- `tests/test_parsers.py` 자동 테스트 총 20개 PASS

### Parser 관련 패키지

- `python-docx==1.2.0`
- `openpyxl==3.1.5`
- `pypdf==6.19.0`
- `python-pptx==1.0.2`
- `xlrd==2.0.2`
- `xlwt==1.3.0`
- `olefile==0.47`
- `legacy-doc==0.2.1`
- `ppt2pptx==0.4.2`
- `pytest==9.1.1`

### 현재 제한사항 및 후속 검토

- 스캔 이미지 기반 PDF의 OCR은 현재 Parser 범위에서 제외
- 현재 PDF는 텍스트 기반 PDF를 우선 지원
- HWP는 현재 HWP 5.x 계열을 대상으로 구현
- 다양한 실제 프로젝트 문서를 이용한 추가 호환성 검증은 후속 통합 테스트에서 계속 수행

### 현재 개발 시작점

- 4-1 문서 Parser 기반 구현 완료
- 지원 문서 형식 총 9종: DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP
- 구형 문서 DOC / XLS / PPT / HWP 실제 샘플 기반 호환성 PoC 완료
- 공통 `ParsedDocument` / `DocumentBlock` 구조 구현 완료
- Parser Factory 및 문서 형식별 자동 Parser 선택 구현 완료
- `InspectionService`에서 9종 문서 형식 허용 및 공통 Parser 호출 연계 완료
- 기존 소스코드/텍스트 기반 Rule Engine 구조는 유지
- `tests/test_parsers.py` Parser 자동 테스트 20개 PASS
- `tests/test_inspection_service.py` Parser 연동 테스트 3개 PASS
- 전체 회귀 테스트 결과 `28 passed, 42 subtests passed`, 실패 0건
- 다음 작업: 4-2 MVP 20개 검사기준 실제 코드 정의

## 2026-09-20 MVP 20개 검사기준 실제 코드 정의 완료
- 4-2 MVP 20개 검사기준 실제 코드 정의 완료
- rules/core/models.py에 RuleExecutionType(Rule / AI / Hybrid) 및 DocumentRule 모델 추가
- 기존 Rule 및 소스코드 정적분석 Rule Engine은 변경하지 않고 유지
- rules/definitions/document_mvp_rules.py에 RULE_DESIGN.md 기준 MVP 20개 정의
- 감리 사전점검 4, 요구사항 정합성 6, 변경영향도 4, FP 검증 2, AI 특화 검증 4
- tests/test_document_mvp_rules.py 추가: 20개 ID/중복, 실행방식, 필수 메타데이터 및 5대 영역 검증
- 기존 Rule Engine 회귀 테스트와 신규 문서 MVP Rule 테스트 PASS
- 전체 pytest 회귀 테스트 실패/오류 0건 확인
- UI Freeze 영역 변경 없음
- 다음 작업: 4-3 Rule 방식 검사 구현


## 2026-09-20 Rule 방식 문서검사 구현 완료
- 4-3 Rule 방식 검사 구현 완료
- `rules/core/models.py`에 문서검사 결과 모델 `DocumentRuleIssue` 추가
- 기존 소스코드 정적분석용 `RuleEngine`은 변경하지 않고 유지
- `rules/core/document_engine.py`에 `DocumentRuleEngine` 구현
- Rule 실행방식으로 확정된 문서 MVP 3개 검사 구현
  - AUD-001: 필수 산출물 누락 점검
  - REQ-001: 요구사항 ID 누락·중복 점검
  - FP-009: FP 산정값 재계산 검증
- AUD-001은 검사 대상 문서 집합의 파일명을 기준으로 필수 산출물 누락 여부를 검사
- REQ-001은 ParsedDocument 블록에서 요구사항 ID 누락 후보와 중복 ID를 검사
- FP-009는 문서에 명시된 FP 합산 산식의 결과값을 재계산하여 산술 불일치를 검사하며, 임의의 FP 분류/가중치 기준은 코드에 고정하지 않음
- `tests/test_document_rule_engine.py` 자동 테스트 8개 PASS
- 전체 pytest 회귀 테스트 PASS 확인
- UI Freeze 영역 변경 없음
- 다음 작업: 4-4 AI / Hybrid 검사 실행구조 구현


## 2026-09-20 AI / Hybrid 검사 실행구조 구현 완료
- 4-4 AI / Hybrid 검사 실행구조 구현 완료
- `rules/core/ai_provider.py`에 AI Provider 공통 인터페이스 및 검사결과 모델 구현
- `rules/core/ai_engine.py`에 AI 방식 Rule 실행 Engine 구현
- AI 방식 MVP Rule 6개 선별 및 실행 구조 검증
- `rules/core/hybrid_engine.py`에 Hybrid 검사 Engine 구현
- Hybrid 방식 MVP Rule 11개 선별 및 실행 구조 검증
- `HybridInspectionContext`를 통해 Rule 기반 사전분석 evidence를 AI Provider로 전달하는 구조 구현
- REQ-003 요구사항 모호성 점검의 Rule 기반 사전분석 구현
  - `적절히`
  - `필요시`
  - `필요 시`
- AI / Hybrid 검사 결과에 실행방식 및 Provider 정보를 기록하도록 확장
- `rules/core/inspection_engine.py`에 Rule / AI / Hybrid 통합 실행 Engine 구현
- `tests/test_ai_provider.py`에 AI / Hybrid / 통합 실행구조 자동 테스트 추가
- 4-4 전용 테스트 7개 PASS
- 전체 pytest 회귀 테스트 `46 passed, 42 subtests passed`
- 기존 `RuleEngine` 및 `DocumentRuleEngine` 변경 없음
- UI Freeze 영역 변경 없음
- 다음 작업: 4-5 MVP 20개 통합 및 단위검증


## 2026-09-20 MVP 20개 통합 및 단위검증 완료

### 4-5 MVP 20개 통합 및 단위검증
- `tests/test_document_mvp_integration.py` 추가.
- MVP 대표 Rule 20개 전체 구성 검증 완료.
- 실행방식별 분류 검증 완료: Rule 3 / AI 6 / Hybrid 11.
- 5대 검사영역별 구성 검증 완료: 감리 사전점검 4 / 요구사항 정합성 6 / 변경영향도 4 / FP 검증 2 / AI 특화 검증 4.
- `DocumentAIEngine` 및 `DocumentHybridEngine` 실제 라우팅 검증 완료.
- `DocumentInspectionEngine`을 통한 AI 6개 + Hybrid 11개 실제 Provider 호출 검증 완료.
- Rule 방식 3개(AUD-001 / REQ-001 / FP-009)는 기존 `tests/test_document_rule_engine.py` 단위검증과 함께 통합 확인 완료.
- 기존 4-4 통합 실행 테스트 재확인 PASS.
- 전체 pytest 회귀 테스트 결과: `50 passed, 42 subtests passed`, 실패 0건.
- 기존 `RuleEngine`, `DocumentRuleEngine` 및 UI Freeze 영역 변경 없음.

### 4단계 완료 상태
- 4-1 문서 Parser 기반 구현 — 완료
- 4-2 MVP 20개 검사기준 실제 코드 정의 — 완료
- 4-3 Rule 방식 검사 구현 — 완료
- 4-4 AI / Hybrid 검사 실행구조 구현 — 완료
- 4-5 MVP 20개 통합 및 단위검증 — 완료
- 따라서 MVP 검사 Engine 구현 4단계 전체 완료.

### 다음 개발 시작점
1. GitHub main 최신 코드와 DECISIONS.md / RULE_DESIGN.md / DEV_STATUS.md를 먼저 확인한다.
2. UI Freeze 상태와 기존 RuleEngine / DocumentRuleEngine 정상 구조를 유지한다.
3. 5단계 Administration·Inspection 통일을 시작한다.
4. Administration 및 Inspection의 검사기준 표시/선택 기준을 최종 5대 검사영역과 MVP 20개 정의에 맞춘다.
5. 기존 소스코드 정적분석 Rule은 삭제하지 않고 향후 확장영역으로 보존한다.
6. 기능 단위 구현 → 자동 테스트 → 전체 회귀 테스트 순서를 유지한다.

---

## 2026-09-23 5단계 Administration·Inspection 통일 시작

### 현재 완료 상태
- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 5대 영역별 전체 검사기준 확정 — 완료
  - 최종 5대 검사영역 / 총 105개
- 3단계 대표 MVP 검사기준 선정 — 완료
  - 총 20개
- 4단계 MVP 검사 Engine 구현 — 전체 완료
  - 4-1 문서 Parser 기반 구현 완료
  - 4-2 MVP 20개 검사기준 실제 코드 정의 완료
  - 4-3 Rule 방식 문서검사 구현 완료
  - 4-4 AI / Hybrid 검사 실행구조 구현 완료
  - 4-5 MVP 20개 통합 및 단위검증 완료
- 4단계 최종 회귀 테스트
  - `50 passed, 42 subtests passed`
  - 실패 0건
- 4단계 완료 기준 GitHub main 커밋: `4b0f512`

### 현재 검사기준
- 최종 제품 검사체계: 5대 영역 / 105개
  - 감리 사전점검(AUD): 24개
  - 요구사항 정합성(REQ): 28개
  - 변경영향도(CHG): 18개
  - FP 검증(FP): 12개
  - AI 특화 검증(AI): 23개
- 현재 MVP 실제 실행 Rule: 20개
  - AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- 실행방식
  - Rule: 3개
  - AI: 6개
  - Hybrid: 11개
- 전체 105개 검사체계와 현재 실제 실행 가능한 MVP 20개를 구분하여 관리한다.

### 5단계 시작 전 확인된 기존 UI 데이터 불일치
- Administration에는 과거 100개 검사기준 체계가 남아 있음.
- Inspection에는 과거 102개 검사기준 체계가 남아 있음.
- Administration Rule 목록에는 실제 최종 검사기준이 아닌 샘플 Rule 표시 구조가 남아 있음.
- 위 데이터/기능 연결을 최종 5대 검사영역 기준으로 통일해야 함.
- 기존 소스코드 정적분석 Rule은 삭제하지 않고 향후 확장영역으로 보존함.

### 5단계 작업계획
1. 최종 105개 검사체계와 MVP 20개 실행체계의 공통 데이터 기준 정리
2. Administration을 최종 5대 검사영역 / 105개 기준으로 통일
3. Inspection을 최종 5대 검사영역 기준으로 통일
4. Inspection의 MVP 20개 선택과 기존 문서검사 Engine 실행 연결
5. Administration 활성/비활성과 Inspection 개별 선택 상태 정합성 점검
6. 통합 테스트 및 전체 회귀 테스트
7. 개발 문서 최종 업데이트 및 Git commit / push

### 개발 시 유지사항
- 2026-09-18 UI Freeze 상태를 유지한다.
- UI 구조·배치·크기·간격·색상·폰트·버튼/팝업 형태를 임의 변경하지 않는다.
- 기존 `RuleEngine`과 `DocumentRuleEngine`은 실제 결함이 확인되지 않는 한 임의 수정하지 않는다.
- Administration의 활성/비활성과 Rule의 구현/미구현 상태를 같은 개념으로 처리하지 않는다.
- 기능 단위로 수정 → 확인 → 자동 테스트 → 전체 회귀 테스트 순서로 진행한다.

### 현재 개발 시작점
- 다음 작업: **5-1 최종 검사체계와 MVP 실행체계의 공통 데이터 기준 정리**
- 코드 수정 전 실제 관련 파일과 데이터 흐름을 확인한 뒤 변경 대상을 확정한다.

---

## 2026-09-23 5-1 공통 검사기준 데이터 정리 완료

- 최종 5대 검사영역 / 105개 전체 검사체계와 MVP 20개 실행체계의 공통 기준정보를 `rules/definitions/document_rule_catalog.py`에 정의함.
- 영역별 기준:
  - 감리 사전점검(AUD): 전체 24 / MVP 4
  - 요구사항 정합성(REQ): 전체 28 / MVP 6
  - 변경영향도(CHG): 전체 18 / MVP 4
  - FP 검증(FP): 전체 12 / MVP 2
  - AI 특화 검증(AI): 전체 23 / MVP 4
- 전체 검사체계 105개와 MVP 실행 대상 20개를 별도 개념으로 유지함.
- MVP 상세 Rule 정의는 기존 `document_mvp_rules.py`를 그대로 기준으로 사용하며 중복 정의하지 않음.
- 기존 소스코드 정적분석 Rule 및 기존 Engine은 변경하지 않음.
- Administration / Inspection UI 및 UI Freeze 영역 변경 없음.
- `tests/test_document_rule_catalog.py` 추가:
  - 5대 영역 / 전체 105개 / MVP 20개 검증
  - 실제 MVP 20개 코드와 영역별 `4 / 6 / 4 / 2 / 4` 구성 일치 여부 검증
- 전체 회귀 테스트 결과: `52 passed, 42 subtests passed`, 실패 0건.

### 다음 작업
- **5-2 Administration을 최종 5대 검사영역 / 105개 기준으로 통일**

---

## 2026-09-23 5단계 진행상태 최신화

### 1. 현재 전체 개발단계

- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 5대 검사영역별 전체 검사기준 확정 — 완료
- 3단계 대표 MVP 검사기준 20개 선정 — 완료
- 4단계 MVP 검사 Engine 구현 — 전체 완료
  - 4-1 문서 Parser 기반 구현 — 완료
  - 4-2 MVP 20개 검사기준 실제 코드 정의 — 완료
  - 4-3 Rule 방식 문서검사 구현 — 완료
  - 4-4 AI / Hybrid 검사 실행구조 구현 — 완료
  - 4-5 MVP 20개 통합 및 단위검증 — 완료
- 5단계 최종 검사체계의 실제 제품 통합 — 진행 중

---

### 2. 최종 검사체계 현재 기준

최종 제품의 검사체계는 다음 5대 검사영역 / 총 105개 Rule을 기준으로 한다.

- 감리 사전점검(AUD): 24개
- 요구사항 정합성(REQ): 28개
- 변경영향도(CHG): 18개
- FP 검증(FP): 12개
- AI 특화 검증(AI): 23개

총계:

`24 + 28 + 18 + 12 + 23 = 105개`

현재 실제 실행 대상 MVP Rule은 총 20개이다.

- AUD: 4개
- REQ: 6개
- CHG: 4개
- FP: 2개
- AI: 4개

실행방식 기준:

- Rule: 3개
- AI: 6개
- Hybrid: 11개

전체 105개 검사체계와 실제 실행 가능한 MVP 20개는 서로 다른 개념으로 관리한다.

---

### 3. 105개 Full Rule Catalog 구현 완료

기존 5-1에서 정의한 5대 영역별 수량 및 MVP 연결정보를 확장하여,
최종 105개 Rule 전체를 실제 Catalog 데이터로 정의하였다.

주요 반영내용:

- `rules/definitions/document_rule_catalog.py`
  - 최종 5대 검사영역 전체 105개 Rule Catalog 구성
  - AUD 24 / REQ 28 / CHG 18 / FP 12 / AI 23
  - 각 Rule의 코드, 제목, 설명 등 실제 기준정보 구성
  - MVP 20개와 전체 105개 체계를 구분하여 관리

- `tests/test_document_full_rule_catalog.py`
  - 전체 Rule 수 검증
  - 영역별 Rule 수 검증
  - Rule ID 중복 여부 검증
  - Rule 누락 여부 검증
  - Rule ID 연속성 검증
  - MVP 20개와 전체 Catalog 정합성 검증

- `tools/build_document_rule_catalog.py`
  - Full Rule Catalog 생성·관리 보조 도구
  - 향후 Rule Catalog 수정 또는 재생성 시 재현 가능한 개발도구로 보존

최종 전체 회귀 테스트:

`57 passed, 42 subtests passed`

실패 0건.

Full Rule Catalog 완료 GitHub main 커밋:

`7f3c591`

---

### 4. 검사결과 판정체계 최종 확정

2026-09-23 검사결과 Severity 및 감리 개선판정 구조를 최종 확정하였다.

기존 방식처럼 Rule 자체에
`Critical / High / Medium / Low`를 고정하지 않는다.

역할을 다음과 같이 분리한다.

`Rule`
= 무엇을 어떤 방식으로 검사할 것인가

`Issue`
= 실제 검사 결과 무엇이 발견되었는가

`Severity`
= 발견된 문제가 얼마나 위험한가

`감리 개선판정`
= 감리 대응 관점에서 발견된 문제를 어떻게 개선할 것인가

---

### 5. Rule 관리방식 변경

Administration의 기존 Rule Detail 구조:

`Code / 규칙 제목 / 설명 / 심각도 / 상태`

변경 구조:

`Code / 규칙 제목 / 설명 / 검사방식 / 상태`

검사방식:

- Rule
- AI
- Hybrid

따라서 Rule 자체에 고정 Severity를 저장하여
실제 Issue Severity로 사용하는 방식은 폐기한다.

2026-09-18 UI Freeze 중 Administration의
Rule Detail `심각도` 표시 관련 결정은
2026-09-23 판정체계 결정으로 해당 부분만 대체한다.

그 외 UI 구조·레이아웃·크기·간격·색상·폰트 등의
Freeze 사항은 가능한 한 유지한다.

---

### 6. Issue Severity 산정방식 확정

실제 발견된 Issue의 Severity는 다음 방식으로 산정한다.

`Impact × Likelihood → Severity`

Impact:

발견된 Issue를 조치하지 않았을 때
사업·업무·기능·품질·데이터·보안 등에 미칠
부정적 영향의 크기.

Likelihood:

발견된 Issue를 조치하지 않고 그대로 진행할 경우
그 Issue로 인한 부정적 영향이 실제로 현실화될 가능성.

주의:

Likelihood는 Issue 자체가 존재할 가능성이 아니다.
이미 발견된 Issue를 방치했을 때
부정적인 결과가 현실화될 가능성을 의미한다.

Impact와 Likelihood는 각각 다음 3단계로 판정한다.

- LOW
- MEDIUM
- HIGH

Severity는 다음 Matrix를 사용한다.

| Impact \ Likelihood | LOW | MEDIUM | HIGH |
|---|---|---|---|
| HIGH | MEDIUM | HIGH | CRITICAL |
| MEDIUM | LOW | MEDIUM | HIGH |
| LOW | LOW | LOW | MEDIUM |

Critical은 원칙적으로 다음 조건에서만 산정한다.

`Impact == HIGH AND Likelihood == HIGH`

Rule Code, Rule Category, 보안/AI/감리 영역이라는 이유만으로
Critical을 사전 지정하지 않는다.

---

### 7. Severity 판정근거 관리

최종적으로 Severity 값만 저장하는 구조를 지향하지 않는다.

가능한 범위에서 다음 정보를 함께 관리한다.

- Impact
- Impact 판정근거
- Likelihood
- Likelihood 판정근거
- Severity
- Severity 판정근거

목표는 사용자가 다음을 확인할 수 있도록 하는 것이다.

`왜 이 Issue가 High인가?`

즉 검사결과의 설명가능성을 확보한다.

---

### 8. 감리 개선판정 분리

Severity와 감리 개선판정은 서로 다른 개념으로 관리한다.

Severity:

- Critical
- High
- Medium
- Low

감리 관점의 판정이 필요한 Issue에는 별도로 다음 정보를 관리한다.

개선권고유형:

- 필수
- 협의
- 권고

개선시점:

- 단기
- 장기

중요 여부:

- O
- -

모든 Issue에 감리 개선판정을 강제로 부여하지 않는다.

감리 관점의 판정이 의미 있는 Issue에 적용한다.

Severity와 감리 개선판정은 서로 대체하지 않는다.

---

### 9. 관련 기준 검토 우선순위

감리 관련 Rule·판정·검사기준 검토 시
다음 자료 우선순위를 적용한다.

1순위: 현행 정보시스템 감리기준

2순위: NIA 정보시스템 감리 수행 가이드

3순위: NIA 지능정보기술 감리 실무 가이드 및 분야별 감리 가이드

4순위: 실제 감리에서 사용하는 지적사항·개선권고 등의 판정/조치 체계

보조:

- NIST
- OWASP
- CVSS 등

국내 정보시스템 감리와 직접 관련된 판단은
국내 감리기준과 NIA 자료를 우선한다.

NIST / OWASP / CVSS 등은
위험도·보안·AI 관련 판단 및 공통 Severity 체계를
보완하기 위한 자료로 사용한다.

상세 결정 및 설계기준은
`DECISIONS.md`와 `RULE_DESIGN.md`를 기준으로 한다.

판정체계 문서 확정 GitHub main 커밋:

`a88b609`

---

## 10. 5단계 최신 작업구조

기존 5단계의 목적은 유지한다.

목표:

`최종 5대 검사영역 / 105개 Rule`
+
`MVP 20개 실제 실행 Engine`
+
`Administration / Inspection / 검사결과 / DB`

를 하나의 제품 흐름으로 통합한다.

오늘 확정한 Severity 및 감리 개선판정 체계를 반영하여
5단계의 남은 작업을 다음과 같이 세분화한다.

### 5-1. 공통 검사기준 데이터 정리
상태: 완료

- 5대 영역 공통 기준정보 정의
- 전체 105개와 MVP 20개 분리
- Full Rule Catalog 105개 구성 완료
- 전체 Catalog 검증 완료

---

### 5-2. Administration 최종 통일
상태: 진행 중

목표:

Administration을 최종
5대 검사영역 / 105개 Rule 기준으로 통일한다.

주요 작업:

- 105개 실제 Rule Catalog 연결
- 기존 샘플/과거 Rule 데이터 제거 또는 대체
- 5대 검사영역별 Rule 표시
- MVP 여부 표시 및 데이터 정합성 확인
- Rule 활성/비활성 상태 연결
- 기존 `심각도` 표시를 `검사방식`으로 변경
- Rule / AI / Hybrid 표시
- Rule Detail 실제 데이터 연결
- 기존 UI Freeze 최대한 유지

---

### 5-3. Inspection 최종 통일
상태: 미완료

목표:

Inspection의 검사기준 표시 및 선택구조를
최종 5대 검사영역 기준으로 통일한다.

주요 작업:

- 기존 과거 검사기준 수량/하드코딩 제거
- 최종 5대 영역 표시
- 전체 105개와 MVP 20개 관계 정리
- Inspection에서 실제 실행 가능한 MVP Rule 명확화
- 기존 UI Freeze 유지

---

### 5-4. MVP 20개와 문서검사 Engine 실제 연결
상태: 미완료

목표:

Inspection에서 선택한 MVP Rule이
4단계에서 구현한 문서검사 Engine으로 실제 전달되도록 연결한다.

실행 흐름:

`Inspection`
→ `MVP Rule 선택`
→ `Rule / AI / Hybrid 라우팅`
→ `DocumentInspectionEngine`
→ `Issue 생성`

기존 4단계 Engine 구조는 실제 결함이 없는 한 임의 변경하지 않는다.

---

### 5-5. Issue Severity 및 감리 개선판정 구현
상태: 미완료

목표:

2026-09-23 확정한 검사결과 판정체계를
실제 코드와 데이터 구조에 적용한다.

주요 작업:

- Issue Impact 저장구조
- Impact 판정근거
- Issue Likelihood 저장구조
- Likelihood 판정근거
- Severity Matrix 구현
- 최종 Severity 저장
- Severity 판정근거 저장
- 필요한 Issue의 감리 개선판정 구조
- 개선권고유형
- 개선시점
- 중요 여부

Severity는 Rule의 고정값을 그대로 복사하지 않는다.

---

### 5-6. 제품 전체 데이터·UI 정합성 연결
상태: 미완료

주요 작업:

- Administration 활성/비활성
  ↔ Inspection 선택상태 정합성

- 검사 Engine
  ↔ Issue 저장

- Issue
  ↔ Project Detail

- Severity
  ↔ Issue Distribution

- 검사결과
  ↔ Reports

- 신규 판정정보
  ↔ DB 저장/조회

- Issue Detail에 필요한 판정정보 연결

UI 세부 표현은 실제 구현 화면을 확인하면서 보정하되
기존 UI Freeze의 전체 디자인 방향은 유지한다.

---

### 5-7. 5단계 통합 및 전체 회귀 테스트
상태: 미완료

검증대상:

- 5대 검사영역
- Full Rule Catalog 105개
- MVP Rule 20개
- Rule / AI / Hybrid 실행
- Administration
- Inspection
- Issue 생성
- Impact / Likelihood
- Severity Matrix
- 감리 개선판정
- DB 저장/조회
- Project Detail
- Reports
- 기존 기능 회귀

기능 단위 테스트 후
전체 `pytest` 회귀 테스트를 수행한다.

---

### 5-8. 5단계 최종 문서화 및 Git 기준점 확정
상태: 미완료

5단계 구현 완료 후 다음 문서를 실제 구현상태와 일치하도록 갱신한다.

- `DECISIONS.md`
- `RULE_DESIGN.md`
- `DEV_STATUS.md`

이후:

- 전체 테스트 확인
- Git status 확인
- commit
- GitHub main push
- working tree clean 확인

까지 완료하여 5단계 기준점을 확정한다.

---

## 11. 현재 정확한 다음 작업

현재 다음 개발 작업은:

**5-2 Administration 최종 통일**

이다.

시작 시 반드시 다음 순서를 따른다.

1. GitHub main 최신 상태 확인
2. Administration 관련 실제 코드 확인
3. 현재 Administration 데이터 흐름 확인
4. 105개 Full Rule Catalog와 기존 UI 연결구조 비교
5. 변경 대상 확정
6. 기능 단위로 구현
7. 화면 확인
8. 자동 테스트
9. 전체 회귀 테스트

기존 UI를 임의로 다시 설계하지 않는다.

오늘 확정한 Severity 체계 때문에
5단계 자체를 별도의 새로운 개발단계로 변경하지 않는다.

Severity 및 감리 개선판정 구현은
5단계 내부 세부작업으로 처리한다.