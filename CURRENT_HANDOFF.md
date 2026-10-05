# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-05 19:34 KST 기준
- 목적: 다음 대화/새 창에서 상태를 추측하지 않고 바로 이어가기 위한 최신 인계 기준점
- 이 파일은 다음 세션 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → 실제 코드` 순으로 반드시 확인한다.

---

## 1. 사용자가 최종 확인한 현재 상태

### Project Detail UI
2026-10-05 사용자 최종 확인: **수정 완료**

최종 확인된 보정사항:
- Issues 목록 행 구조를 `첫 줄: Severity | Rule ID | 상태`, `둘째 줄 이하: 실제 Issue 내용` 구조로 변경
- CHG-001 등 긴 내용은 아래 전체 폭을 사용하고 내용 길이에 따라 행 높이를 자동 확장
- `미조치` 상태가 잘리지 않도록 독립 상태칸 유지
- 감리 개선판정 결과 배지 가독성 강화
  - 배지 높이 24px
  - 글자 12px / Bold
  - 실제 결과 색상 규칙과 도움말 색상 규칙 일치
- 감리 개선판정 색상 기준
  - 필수: 빨강
  - 협의: 주황
  - 권고: 보라
  - 단기: 보라
  - 장기: 청록
  - O: 빨강
  - -: 회색
- `판정 없음`은 다크/라이트 테마별 중립 색상으로 분리
- 개선권고유형 / 개선시점 / 중요 여부 제목과 배지 사이 간격 확대
- Issues의 Rule ID/실제 내용은 widget-local style을 사용하여 기존 QSS에 덮이지 않도록 가독성 강화
- 사용자 최종 답변: `수정 완료. 너무 오래 걸렸어요.`

따라서 위 Project Detail UI는 **확정 완료**로 취급한다. 새로운 명시적 결함이 나오기 전에는 다시 임의 변경하지 않는다.

### 가장 최근 Project Detail UI 관련 자동테스트
사용자 PC에서 다음 두 테스트 묶음 최종 PASS:
- `tests/test_project_detail_audit_badges.py`
- `tests/test_project_detail_issue_status_layout.py`
- 결과: **4 passed in 0.43s**

주의: 이 결과는 targeted UI 테스트이며 전체 `pytest` 최종 결과는 아님.

---

## 2. 1~4단계 확정 상태

### 1단계
- 기존 Rule 복원·재분류 완료

### 2단계
- 최종 5대 검사영역 / 총 105개 확정
  - AUD 24
  - REQ 28
  - CHG 18
  - FP 12
  - AI 23

### 3단계
- MVP 대표 Rule 20개 확정
  - AUD 4
  - REQ 6
  - CHG 4
  - FP 2
  - AI 4

### 4단계
- 4-1 Parser 기반 구현 완료
- 4-2 MVP 20개 코드 정의 완료
- 4-3 Rule 방식 문서검사 완료
- 4-4 AI / Hybrid 실행구조 완료
- 4-5 MVP 20개 통합 및 단위검증 완료
- 4단계는 전체 완료 상태로 유지

---

## 3. 5단계 실제 최신 상태

### 5-1 공통 검사기준 데이터 정리
- **확정 완료**
- Full Rule Catalog 105개와 MVP 20개 분리 관리

### 5-2 Administration 최종 통일
- **확정 완료**
- 최종 5대 영역 / 105개 Catalog 연결
- Rule / AI / Hybrid 검사방식 표시
- Rule 활성/비활성 관리 연결

### 5-3 Inspection 최종 통일
- **확정 완료**
- Administration과 동일한 5대 영역 / 105개 기준 사용
- 실제 실행은 MVP 20개로 명확히 분리

### 5-4 MVP 20개 ↔ 문서검사 Engine 실제 연결
- **확정 완료**
- `Full Catalog 선택 → MVP 20 추출 → Parser → Rule/AI/Hybrid → DocumentInspectionEngine → Issue/DB → UI` 연결 완료

### 5-5 Issue Severity + 감리 개선판정 + Local AI
- 기능 핵심은 **사실상 완료 상태**
- 데이터 모델 / DB / UI / 실행 흐름 구현됨
- Impact / Likelihood 3단계
- Impact × Likelihood Severity Matrix
- Final Severity는 AI가 아니라 deterministic Matrix로 산정
- 감리 개선판정은 Severity와 독립
  - 개선권고유형: 필수 / 협의 / 권고
  - 개선시점: 단기 / 장기
  - 중요 여부: O / -
- Qwen3-4B Q4_K_M + llama.cpp b11312 연동
- reasoning off
- temp 0.7 / top-p 0.8 / top-k 20 / min-p 0 / seed 42
- Local AI가 Impact/Likelihood 및 근거 판정
- CHG-001은 감리 개선판정 비적용 정책

### 5-6 제품 전체 데이터/UI 정합성
- 문서에는 미완료로 남아 있으나 실제 구현은 상당부분 완료
- Engine → Issue → DB → Project Detail → Severity → 감리판정 → Reports 흐름은 이미 구현·검증됨
- **단, 5단계 종료 전에 최신 실제 검사결과 DB 진단으로 최종 확인 필요**

### 5-7 통합 및 전체 회귀테스트
- **미완료**
- 최근 UI/Engine 변경 이후 전체 `pytest`를 다시 수행해야 함
- 과거 전체 PASS 수치는 최신 변경 이전이므로 최종 기준으로 사용하지 않음

### 5-8 최종 문서화 및 Git 기준점
- **미완료**
- 아래 문서 현행화 필요
  - `DEV_STATUS.md`
  - `DECISIONS.md`
  - `RULE_DESIGN.md`
- 5단계 학습자료 작성 필요
- 최종 Git status / commit / push / working tree clean 확인 필요

---

## 4. 실문서/Engine 최신 검증 기준

### HWP Parser
- 실제 문서 검증 완료

### REQ-003
- PASS

### REQ-004
- 완료

### REQ-018
- 완료

### REQ-001
- 과거 구조 반복으로 28건 오탐 발생
- 요구사항 문서 scope 제한 + 실제 정의 문장 판정 + 구조 반복 제거 로직으로 수정
- 실제 요구사항 HWP 2건 재검증 결과 각각 REQ-001 issues 0
- targeted 자동테스트 12 passed
- **확정 완료. 새 결함 없으면 재수정/재실행하지 않음**

### CHG-001
- PASS
- 여러 실제 변경사항을 별도 Issue로 생성 가능
- Project Detail에서 같은 Rule ID라도 실제 내용이 구분되어 보이도록 UI 보정 완료
- 감리 개선판정은 None 정책

### CHG-006
- PASS

### CHG-012
- 최종 실제 검증 PASS
- `[CHG-012 ISSUES] 0`
- 전체 targeted 테스트 17 passed 당시 확인
- **확정 완료. 새 결함 없으면 재실행하지 않음**

### CHG-018
- 최종 실제 검증 PASS
- `[CHG-018 ISSUES] 0`
- deterministic unresolved-evidence gate
- **확정 완료. 새 결함 없으면 재실행하지 않음**

### Impact / Likelihood 실제 배치
- PASS

### 감리 개선판정 실제 Qwen 검증
- REQ-018: 필수 / 단기 / O
- AUD-005: 판정 없음
- PASS

---

## 5. 최신 실제 Re-Inspect 기준

프로젝트: `tawga`
가장 최근 확인된 실제 검사:
- 2026-10-05 16:24
- Score 95
- Issues 7
- Grade A
- Distribution: Critical 0 / High 0 / Medium 4 / Low 3

이 결과는 REQ-001 구조 오탐 수정 이후의 실제 결과이다.

5단계 종료 전 아래 진단 필요:
- 최신 inspection이 DB에서도 7 Issues / 95 / A인지 확인
- REQ-001 구조 오탐이 0인지 확인
- CHG-001 감리판정이 NULL/판정 없음인지 확인
- 각 Issue의 Severity / Impact / Likelihood / 감리판정이 UI와 DB에서 일치하는지 확인

진단도구:
- `python -m tools.diagnose_latest_inspection`

**Re-Inspect는 다시 할 필요 없음.**

---

## 6. Export Report 확정

MVP 최종 지원:
- DOCX
- XLSX
- TXT

제외:
- HWPX

사유:
- 직접 생성 HWPX는 한/글에서 손상 파일로 확인됨
- pyhwpx 0.47은 사용자 PC에서 한글 COM Type Library 미등록으로 사용 불가
- HWPX 하나를 위해 COM 등록을 제품 필수조건으로 만들지 않음

**HWPX를 다시 복원하거나 재실험하지 않는다.**

---

## 7. 5단계 종료 전 정확한 남은 작업 순서

1. **최신 실제 검사결과 DB 최종 진단**
   - `tools.diagnose_latest_inspection`
   - Re-Inspect 없음

2. **감리 개선판정 '판정근거' 범위 최종 확인**
   - Impact/Likelihood 근거는 구현됨
   - `필수/협의/권고`, `단기/장기`, `O/-` 자체의 별도 근거까지 MVP 필수로 확정했는지 과거 결정사항을 다시 확인
   - 과거 확정이 없으면 새 기능을 임의 추가하지 않음

3. **전체 자동 회귀테스트**
   - 최신 코드 기준 `pytest` 전체 1회
   - 실패 0건 확인

4. **로컬 변경사항 확인**
   - 특히 `tools/validate_change_synthesis.py`
   - 과거 CHG-012 stale fixture 한 줄 삭제 diff가 로컬에 남아 있었음
   - 최종 `git status`, `git diff`로 확인 후 GitHub와 동기화

5. **문서 3종 현행화**
   - `DEV_STATUS.md`
   - `DECISIONS.md`
   - `RULE_DESIGN.md`

6. **5단계 상세 학습자료 작성**
   - 사용자 혼자 추후 공부할 수 있도록 작성
   - 반드시 포함:
     - 5단계 구현기능
     - Architecture / 데이터 흐름
     - Severity Matrix
     - Qwen Local AI
     - 감리 개선판정
     - DB/UI 흐름
     - 실문서 검증
     - REQ-001 오탐 사례와 해결
     - Grade A~E 불일치 해결
     - Project Detail runtime/QSS/UI 문제와 해결
     - 테스트 방법

7. **5단계 최종 Git 마감**
   - git status
   - commit / push
   - working tree clean
   - 위까지 완료 후에만 `5단계 확정 완료` 선언

---

## 8. 5단계 이후 남은 프로젝트 작업

### 6단계: Administration 데이터 관리
**실제로 아직 구현하지 않은 기능**

기존 확정사항:
- Administration에 `3. 데이터 관리`
- 전체 검사 이력 정리
- 프로젝트 관리
- 전체 검사 이력 삭제 시 Project 정보는 유지
- Project 삭제 시 해당 Project의 Inspection + Issues 함께 삭제
- 삭제 전 범위 및 되돌릴 수 없음을 알리는 확인 Modal

현재 `administration_page.py`에는:
- 1. 검사 기준 관리
- 2. 환경 설정
까지만 구현되어 있으며 `3. 데이터 관리`는 없음.

따라서 6단계는 실제 개발 필요.

### 최종 배포/제출 마감
6단계 이후 별도 최종 마감 작업:
- 최신 코드 전체 회귀
- PyInstaller EXE 재빌드
- SQLite/data 경로 확인
- 아이콘/리소스 포함 확인
- Qwen3-4B + llama.cpp 포함/연동 확인
- 인터넷 차단/폐쇄망 독립 실행 검증
- 실제 Inspection 1회
- 결과 DB 저장/조회
- Export 확인
- 제출용 폴더/산출물 정리

과거 EXE 빌드 성공 이력은 있으나 Local AI 추가 이후 최신 빌드는 다시 확인해야 함.

---

## 9. 남은 예상 시간

### 5단계 최종 마감
- 약 1~1.5시간

### 6단계 Administration 데이터 관리
- 약 1.5~2.5시간

### 최종 EXE / 폐쇄망 / 제출 검증
- 약 1.5~3시간

### 전체
- 약 4~7시간
- 현실적 예상: 약 5~6시간

사용자 작업 패턴상:
- 안정적으로 작업일 2회
- 잘 풀리면 긴 작업일 1회 + 짧은 마감 1회 가능

---

## 10. 절대 다시 되돌리지 말아야 할 확정사항

- 2026-09-18 UI Freeze 전체 방향 유지
- Project Detail 정렬 컨트롤은 현재 QComboBox 기준 확정. 다시 건드리지 않음
- HWPX MVP 제외 확정
- CHG-012 final 0 확정. 새 결함 없으면 재실행하지 않음
- CHG-018 final 0 확정. 새 결함 없으면 재실행하지 않음
- REQ-001 실제 HWP 오탐 0 검증 완료. 새 결함 없으면 재수정하지 않음
- Grade는 A/B/C/D/E 체계. 0~59 = E. F를 다시 사용하지 않음
- CHG-001은 감리 개선판정 비적용 정책
- Severity와 감리 개선판정은 별개
- Final Severity는 AI가 아니라 Matrix 계산
- Local AI 기본 모델은 Qwen3-4B Q4_K_M
- 이미지 생성이 아니라 실제 코드 수정 중심
- 문서 업데이트와 학습자료를 개발 마감 시 반드시 수행

---

## 11. 다음 세션 개발 원칙

사용자가 특히 요구한 원칙:
- 빠르게 대충 하지 말고 `확인 → 재확인 → 교차확인 → 수정`
- 이미 완료된 사항을 다시 뜯지 말 것
- 상태를 추측하지 말고 GitHub 실제 코드를 먼저 확인할 것
- 사용자가 코드/파일을 다시 붙여 넣게 하기 전에 GitHub/문서/이전 기록부터 확인할 것
- 수정 후 `확정 완료 / 문서가 뒤처짐 / 확인 필요 / 미완료`로 상태를 명확히 말할 것
- UI 수정은 사용자가 명시적으로 지적한 결함 범위에서만 수행
- 테스트가 PASS해도 실제 화면 확인 전에는 UI 정상이라고 단정하지 않음
- 전체 pytest 결과가 최신이 아니면 과거 pass 수치를 현재 최종 결과처럼 말하지 않음

다음 세션은 반드시 이 파일을 읽은 후 작업을 시작한다.

---

## 12. 최신 GitHub 기준점

2026-10-05 19:32 KST 전후 확인된 main 최신 커밋:
- `503203c88677f5f101408ba6c530a4843475d3a7`
- message: `test: cover theme-aware audit badge polish`

이 `CURRENT_HANDOFF.md` 생성 커밋 이후에는 main SHA가 달라지므로, 다음 세션에서는 main 최신 SHA를 다시 조회한다.
