# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-10 KST
- 목적: 다음 대화/새 창에서 상태를 추측하지 않고 바로 이어가기 위한 최신 기준점

다음 세션 시작 순서:
`GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드 및 installer 관련 파일 → 이전 대화/저장된 결정사항`

## 작업 전 필수 다중 교차검증

- GitHub 실제 코드 / 프로젝트 구조 / CURRENT_HANDOFF.md / DECISIONS.md / RULE_DESIGN.md / DEV_STATUS.md / README.md / HACKATHON_SUBMISSION.md / 실제 코드 및 installer 관련 파일 / 기존 테스트 결과 / 이전 대화 / 저장된 결정사항을 먼저 확인한다.
- 한 번 확인한 내용만 믿고 진행하지 않는다. 최소 2~3회 서로 다른 관점으로 재확인한다.
- `코드 ↔ 문서 ↔ 테스트 결과 ↔ 이전 대화/결정사항`을 교차검증한다.
- 충돌 시 최신 GitHub 실제 코드와 실제 동작을 우선 확인하되, 기존 확정 결정사항과의 충돌 여부를 다시 검토한다.
- 충분히 확인되지 않은 상태에서는 추측으로 수정하지 않고, 이미 완료된 기능을 다시 만들지 않는다.
- 사용자가 개발 초보이므로 로컬 명령은 PowerShell 기준으로 한 번에 하나씩 안내한다.
- 가능한 코드/문서 작업은 GitHub에서 직접 수행하고, 사용자에게는 실제 필요한 로컬 검증만 요청한다.

---

# 1. 전체 완료 상태

완료 유지:
- 1단계 기존 Rule 복원·재분류
- 2단계 최종 5대 검사영역 / Full Catalog 105개 확정
- 3단계 해커톤 MVP 대표 Rule 20개 확정
- 4단계 문서 Parser + Rule/AI/Hybrid 검사 Engine
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정
- Inspection 실행 UX 보완
- 6단계 Administration 데이터 관리
- 최종 EXE 안정화
- 감리결과서 114개 실무 분석 / 105개 전체 Rule 매핑
- MVP20 실제 감리사례 실증검증
- 실증검증 우선 보완 5개 수정 및 전체 회귀검증
- ZIP(EXE) 재빌드·스모크검증
- WiX 기반 MSI 설치형 패키지 제작·실설치·Local AI 스모크검증

새 확장 진행:
- 7-0 최소 공통 확장기반 — 완료
- P1 13개 구현기준 확정 — 완료
- P1-A 구조형/결정형 4개 — 완료
- 다음 단계: P1-B 요구사항·시험·추적성 3개 구현

**1~6단계, 감리자료 114개 분석, MVP20 실증검증, 우선 보완 5개, 기존 ZIP/MSI 패키징은 새 결함이 없는 한 다시 구현·재설계·재분석하지 않는다.**

---

# 2. 검사체계 현재 기준

Full Rule Catalog 105개:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23

해커톤 MVP 기준선 20개:
- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4
- 실행방식: Rule 3 / AI 6 / Hybrid 11

현재 GitHub main 실제 실행 가능 Rule:
- **24개 = 기존 MVP20 + P1-A 4개**
- P1-A 활성 Rule:
  - AUD-008 계획 대비 산출물 작성상태 점검
  - AUD-014 시험계획 완전성 점검
  - AUD-016 시험결함 조치상태 점검
  - FP-008 상세 산정정보 적정성 점검
- 현재 실행방식 합계: Rule 7 / AI 6 / Hybrid 11

중요:
- `MVP20`은 최초 해커톤 기준선 명칭으로 유지한다.
- `현재 실제 실행 가능 Rule 수`는 확장 구현으로 24개가 되었다.
- Full Catalog 105개와 실제 실행 가능 Rule 수는 서로 다른 개념이다.

---

# 3. 7-0 최소 공통 확장기반 — 2026-10-10 완료

구현 목적:
- 기존 MVP20에 직접 하드코딩된 실행선택 구조를 확장 가능한 Registry 구조로 전환
- 미구현 Rule이 Full Catalog에 보이더라도 실제 Handler 없이 실행되는 상황 차단
- UI Freeze를 유지하면서 실행 Rule만 안전하게 확장

핵심 파일:
- `rules/definitions/document_rule_registry.py`
- `rules/core/document_selection.py`
- `ui/inspection_rule_ui_patch.py`
- `tests/test_document_rule_registry.py`
- `tests/test_document_selection.py`

핵심 원칙:
- Full Catalog 105는 그대로 유지
- 실제 Handler + targeted test를 통과한 Rule만 Registry에 등록
- Registry 미등록 Rule은 UI Catalog에 존재해도 실제 검사에서는 실행하지 않음
- 기존 호환 API `get_selected_document_mvp_rules()`는 유지하되 내부적으로 현재 Registry 기준을 반환

7-0 직후 사용자 PC 검증:
- targeted regression 정상
- 전체 `python -m pytest -q`: `198 passed, 51 subtests passed`

---

# 4. P1 구현 계획

Canonical 기준:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개:
- AUD-008
- AUD-010
- AUD-014
- AUD-016
- AUD-018
- AUD-020
- AUD-022
- AUD-023
- REQ-007
- REQ-012
- REQ-017
- FP-002
- FP-008

구현 순서:

P1-A — 구조형/결정형
1. AUD-014
2. AUD-016
3. FP-008
4. AUD-008

P1-B — 요구사항·시험·추적성
5. REQ-007
6. REQ-012
7. REQ-017

P1-C — 계획·품질
8. AUD-010
9. AUD-018

P1-D — 인터페이스·계약·기준
10. AUD-020
11. AUD-022
12. AUD-023

P1-E — FP 의미중복
13. FP-002

P1 전체 완료 시 목표 실제 실행 Rule 수:
- 33개 = MVP20 + P1 13개

---

# 5. P1-A 4개 — 2026-10-10 완료

## AUD-014 시험계획 완전성
- 시험항목 / 시험방법·조건 / 예상결과 구조 점검
- 실제 시험행의 필수값 누락 탐지
- 빈 템플릿행, 합계·요약행 오탐 방지

## AUD-016 시험결함 조치상태
- 미조치 / 진행중 / 재검증 필요 등 미종결 상태 탐지
- 완료 상태인데 조치결과가 비어 있는 구조적 불일치 탐지
- 취소 / 해당없음 / 중복 / 제외 상태는 정상 종결로 구분

## FP-008 상세 산정정보 적정성
- 기존 `fp_calculator.py` 구조 재사용
- 기능유형 + 보고 FP가 있는 실제 산정행만 대상
- 복잡도 명시 시 허용
- 복잡도가 없으면 RET/FTR + DET 근거 확인
- 합계/요약행 제외

## AUD-008 계획 대비 산출물 작성상태
AUD-001과 역할 분리:
- AUD-001 = 실제 제출 파일 존재/누락
- AUD-008 = 계획표상 현재 대상 산출물의 작성·제출 상태 관리

탐지:
- 상태 공란
- 미작성
- 작성중
- 미제출
- 미완료
- 진행중/보완중

제외:
- 미적용
- 적용제외
- 해당없음
- 시기미도래
- 점검제외
- 기준자료 자체가 없는 경우 임의 추정 금지

P1-A 핵심 파일:
- `rules/definitions/document_p1_rules.py`
- `rules/definitions/document_p1_aud008_rule.py`
- `rules/core/p1_rule_checks.py`
- `rules/core/p1_deliverable_status.py`
- `rules/core/p1_document_engine.py`
- `rules/core/inspection_engine.py`
- `rules/definitions/document_rule_registry.py`
- `tests/test_p1_deterministic_rules.py`
- `tests/test_document_rule_registry.py`
- `tests/test_document_selection.py`

검증:
- P1-A 첫 3개 전용 테스트 PASS
- 첫 3개 활성화 후 통합 targeted: `30 passed`
- 첫 3개 활성화 후 전체: `209 passed, 51 subtests passed`
- AUD-008 전용 테스트 PASS
- AUD-008 활성화 후 24개 Registry/통합 targeted PASS
- AUD-008 활성화 후 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS
  - 사용자가 최종 결과를 `정상`으로 확인했으며 정확한 passed 개수는 별도 기록하지 않음

---

# 6. 현재 Engine 구조

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 필터 → Parser → Rule / AI / Hybrid → DocumentInspectionEngine → Issue → Assessment → DB → UI`

Rule 계층:
- 기존 `DocumentRuleEngine`은 유지
- `P1DocumentRuleEngine(DocumentRuleEngine)`이 검증 완료된 P1 결정형 Handler를 추가
- `DocumentInspectionEngine`의 Rule 엔진은 현재 `P1DocumentRuleEngine` 사용
- AI/Hybrid 엔진은 기존 구조를 유지

이 구조는 기존 MVP20 동작을 보존하면서 P1 Rule만 점진적으로 추가하기 위한 것이다.

---

# 7. 다음 작업 — P1-B

다음 구현 대상:
1. REQ-007 요구사항 검증가능성·검증방법 점검
2. REQ-012 요구사항 시험항목 누락 점검
3. REQ-017 요구사항 추적관계 누락 점검

재사용 기준:
- REQ-003 모호성 후보 추출 구조
- REQ-009 요구사항 ↔ 설계 교차문서 구조
- REQ-018 추적성 구조

역할 분리:
- REQ-007: 요구사항이 실제로 검증 가능한가 / 검증방법이 있는가
- REQ-012: 요구사항에 대응하는 시험항목이 누락됐는가
- REQ-017: 필요한 추적 연결 자체가 누락됐는가
- REQ-018: 전체 양방향 추적 가능성

오탐 방지:
- 모든 요구사항에 숫자 기준을 강제하지 않음
- N/A / 해당없음 / 별도시트 참조 인정
- 비기능 요구사항에 기능 산출물 링크를 일률적으로 강제하지 않음
- REQ-003 / REQ-018과 동일 Issue를 중복 생성하지 않도록 역할을 분리

---

# 8. 감리자료 / Rule 근거

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`

분석 기준:
- 114개 감리 관련 파일
- PDF 94 / DOCX 19 / XLSX 1
- 2019~2025 독립 보고서
- 일부 2025 보고서에 2026 후속일정 포함

미구현 우선순위 원래 분류:
- P1 13
- P2 23
- P3 21
- P4 28

현재 P1 진행상태:
- 완료/활성 4개
- 남음 9개

감리자료 114개는 P1~P4 구현 때 처음부터 다시 분석하지 않는다.
새 자료가 추가될 때만 증분 반영한다.

신규 Rule 후보:
- 9개 + 조건부 1개 유지
- 현재 Full Catalog 105에는 추가하지 않음
- 사용자 승인 전 임의 추가 금지

---

# 9. Parser / Local AI / Severity 고정 기준

Parser 지원 9종:
- DOCX
- DOC
- XLSX
- XLS
- PDF
- PPTX
- PPT
- HWPX
- HWP

제외:
- 스캔 이미지 PDF OCR
- HWPX Report Export

Local AI:
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 역할:
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

Final Severity:
`Impact × Likelihood → deterministic Severity Matrix`

AI가 Severity를 직접 결정하지 않는다.
감리 개선판정은 Severity와 별도 관리한다.

---

# 10. UI / 데이터 / 배포 고정 기준

UI:
- 2026-09-18 UI Freeze 유지
- Dark 기본 / Light 지원
- 임의 레이아웃·폰트·간격·색상 재설계 금지

Administration 데이터 관리:
- 전체 검사이력 정리: `Issues → Inspections`, Project 유지
- Project 삭제: `Issues → Inspections → Project`
- transaction / rollback 유지

현재 기존 최종 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

현재 기존 최종 MSI 설치형:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

중요:
- 위 ZIP/MSI는 P1-A 확장 전 최종 배포본이다.
- 현재 GitHub main 소스는 24개 Rule 기준이지만 ZIP/MSI를 아직 다시 빌드하지 않았다.
- 따라서 README / HACKATHON_SUBMISSION의 기존 배포검증 문구를 24개 기준으로 성급히 바꾸지 않는다.
- P1 확장 범위를 동결한 뒤 최신 소스로 ZIP/MSI를 재빌드·스모크검증하고 제출문서를 최종 현행화한다.

---

# 11. 다음 세션에서 하지 말아야 할 것

- 1~6단계를 다시 구현하지 않는다.
- UI Freeze를 깨지 않는다.
- 감리자료 114개를 처음부터 다시 분석하지 않는다.
- MVP20 보완 5개를 다시 작업하지 않는다.
- 검증되지 않은 P1 Rule을 Registry에 미리 등록하지 않는다.
- P1-A 4개를 다시 구현하지 않는다.
- 기존 최종 ZIP/MSI가 현재 24개 소스를 포함한다고 착각하지 않는다.

다음 시작점은 **P1-B REQ-007 → REQ-012 → REQ-017 구현**이다.
