# AI Auditor 개발 현황

## 기준일
- 2026-10-10

## 현재 전체 상태

기존 완료영역:
- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 해커톤 MVP 대표 Rule 20개 확정 — 완료
- 4단계 MVP 문서 검사 Engine 구현 — 완료
- 5단계 Administration·Inspection·Local AI·Severity·감리 개선판정 통합 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료
- 최종 EXE 안정화 — 완료
- 감리결과서 114개 분석 / 105개 전체 Rule 실무 매핑 — 완료
- MVP20 실제 감리사례 실증검증 — 완료
- 우선 보완 5개 구현 및 전체 회귀검증 — 완료
- 감리분석 보완사항 반영 ZIP(EXE) 재빌드 및 스모크검증 — 완료
- WiX 기반 MSI 설치형 제작 / 실제 설치 / Local AI 검사 검증 — 완료

확장 진행상태:
- 7-0 최소 공통 확장기반 — 완료
- P1 13개 구현기준 확정 — 완료
- P1-A 구조형/결정형 4개 — 완료
- 현재 다음 작업: P1-B 요구사항·시험·추적성 3개

---

## 검사체계

제품 전체 검사체계는 5대 영역 / 총 105개이다.

- 감리 사전점검(AUD): 24개
- 요구사항 정합성(REQ): 28개
- 변경영향도(CHG): 18개
- FP 검증(FP): 12개
- AI 특화 검증(AI): 23개

해커톤 MVP 최초 기준선은 20개이다.

- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4
- 실행방식: Rule 3 / AI 6 / Hybrid 11

현재 GitHub main 실제 실행 가능 Rule은 **24개**이다.

- 기존 MVP20
- AUD-008 계획 대비 산출물 작성상태 점검
- AUD-014 시험계획 완전성 점검
- AUD-016 시험결함 조치상태 점검
- FP-008 상세 산정정보 적정성 점검

현재 실행방식 합계:
- Rule 7
- AI 6
- Hybrid 11

`MVP20`은 최초 해커톤 기준선 명칭으로 유지하고, 현재 실제 실행 가능 Rule 수는 별도로 관리한다.
Full Catalog 105와 실행 가능 Rule 수는 서로 다른 개념이다.

---

## 7-0 최소 공통 확장기반 — 완료

핵심 변경:
- 실제 실행 가능한 Rule을 중앙 Registry에서 관리
- Handler가 없는 Rule의 조기 활성화 방지
- Full Catalog 105 선택상태와 실제 실행 Registry를 분리
- UI Freeze를 유지하면서 실행 Rule 확장 가능하도록 변경

핵심 파일:
- `rules/definitions/document_rule_registry.py`
- `rules/core/document_selection.py`
- `ui/inspection_rule_ui_patch.py`
- `tests/test_document_rule_registry.py`
- `tests/test_document_selection.py`

7-0 완료 직후 사용자 PC 전체 회귀:
- `198 passed, 51 subtests passed`

---

## P1-A — 2026-10-10 완료

완료 Rule:

### AUD-008 계획 대비 산출물 작성상태 점검
- AUD-001과 역할 분리
- AUD-001: 실제 제출 파일의 존재/누락
- AUD-008: 계획표상 현재 대상 산출물의 작성·제출 상태
- 상태 공란 / 미작성 / 작성중 / 미제출 / 미완료 / 진행중 / 보완중 탐지
- 미적용 / 적용제외 / 해당없음 / 시기미도래 / 점검제외는 제외
- 기준자료가 없으면 임의 추정하지 않음

### AUD-014 시험계획 완전성 점검
- 시험항목 / 시험방법·조건 / 예상결과 구조 검증
- 필수 헤더 및 실제 시험행 값 누락 탐지
- 빈 템플릿행 / 합계·요약행 제외

### AUD-016 시험결함 조치상태 점검
- 미조치 / 진행중 / 재검증 필요 등 미종결 상태 탐지
- 완료 상태인데 조치결과 공란인 구조적 불일치 탐지
- 취소 / 해당없음 / 중복 / 제외는 정상 종결로 구분

### FP-008 상세 산정정보 적정성 점검
- `fp_calculator.py` 구조 재사용
- 기능유형 + 보고 FP가 있는 실제 산정행만 대상
- 복잡도 명시 시 허용
- 복잡도 미기재 시 RET/FTR + DET 근거 확인
- 합계/요약행 제외

P1-A 핵심 구현:
- `rules/definitions/document_p1_rules.py`
- `rules/definitions/document_p1_aud008_rule.py`
- `rules/core/p1_rule_checks.py`
- `rules/core/p1_deliverable_status.py`
- `rules/core/p1_document_engine.py`
- `rules/core/inspection_engine.py`
- `rules/definitions/document_rule_registry.py`
- `tests/test_p1_deterministic_rules.py`

검증 이력:
- P1-A 첫 3개 전용 테스트 PASS
- 첫 3개 Registry 활성화 후 targeted 통합: `30 passed`
- 첫 3개 활성화 후 전체: `209 passed, 51 subtests passed`
- AUD-008 전용 테스트 PASS
- AUD-008 활성화 후 24개 Registry/통합 targeted PASS
- AUD-008 활성화 후 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS
- 마지막 전체 실행의 정확한 passed 개수는 사용자가 `정상`으로 확인했으므로 별도 숫자를 임의 기록하지 않음

---

## 현재 문서 검사 Engine

실행 흐름:
`Inspection → Full Catalog 선택상태 → 실행 Registry 필터 → Parser → Rule / AI / Hybrid → DocumentInspectionEngine → Issue → DB → UI`

Rule 구조:
- 기존 `DocumentRuleEngine` 유지
- `P1DocumentRuleEngine`이 기존 Engine을 상속
- P1 결정형 Handler를 추가
- `DocumentInspectionEngine`은 현재 `P1DocumentRuleEngine` 사용

기존 AI / Hybrid Engine은 유지한다.

---

## 다음 작업 — P1-B

대상:
1. REQ-007 요구사항 검증가능성·검증방법 점검
2. REQ-012 요구사항 시험항목 누락 점검
3. REQ-017 요구사항 추적관계 누락 점검

재사용 대상:
- REQ-003 모호성 후보 구조
- REQ-009 요구사항↔설계 교차문서 구조
- REQ-018 추적성 구조

역할 분리:
- REQ-007: 요구사항 자체가 검증 가능한지 / 검증방법이 있는지
- REQ-012: 요구사항에 대응하는 시험항목이 빠졌는지
- REQ-017: 필요한 추적 링크가 빠졌는지
- REQ-018: 전체 양방향 추적 가능성

P1 전체 13개 중 현재:
- 완료 4개
- 남음 9개

P1 전체 완료 목표:
- 실제 실행 Rule 33개

---

## 문서 Parser

지원 9종:
- DOCX
- DOC
- XLSX
- XLS
- PDF
- PPTX
- PPT
- HWPX
- HWP

공통 구조:
`원본 문서 → 형식별 Parser → ParsedDocument / DocumentBlock`

스캔 이미지 PDF OCR은 현재 범위에서 제외한다.

---

## Local AI / Severity

기본 Local AI:
- Qwen3-4B Q4_K_M
- llama.cpp b11312
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 역할:
- Impact
- Impact 근거
- Likelihood
- Likelihood 근거

최종 Severity:
`Impact × Likelihood → deterministic Severity Matrix`

AI가 최종 Severity를 직접 결정하지 않는다.
감리 개선판정은 Severity와 별도 관리한다.

---

## 감리결과서 기반 실무검증

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`
- `P1_IMPLEMENTATION_PLAN.md`

분석 원본:
- 114개
- PDF 94 / DOCX 19 / XLSX 1
- 2019~2025 독립 감리보고서
- 일부 2025 보고서에 2026 후속일정 포함

원래 미구현 85개 우선순위:
- P1 13
- P2 23
- P3 21
- P4 28

현재 P1 진행:
- 완료 4
- 남음 9

감리자료 114개는 이후 Rule 구현 때 처음부터 다시 분석하지 않는다.
새 자료가 들어올 때만 증분 반영한다.

신규 Rule 후보:
- 9개 + 조건부 1개 유지
- Full Catalog 105에는 아직 추가하지 않음
- 사용자 승인 전 임의 추가 금지

---

## 배포 상태 주의

기존 최종 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 최종 MSI 설치형:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

중요:
- 위 ZIP/MSI는 P1-A 확장 전, 기존 MVP20 기준 최종 배포본이다.
- 현재 GitHub main 소스는 실행 Rule 24개 기준이다.
- 아직 P1-A 확장 소스로 ZIP/MSI를 다시 빌드하지 않았다.
- README / HACKATHON_SUBMISSION의 기존 배포검증 문구는 현재 기존 배포본 기준으로 유지한다.
- P1 확장 범위를 동결한 뒤 최신 소스로 ZIP/MSI를 다시 빌드·스모크검증하고 제출문서를 최종 현행화한다.

---

## 고정사항

- 2026-09-18 UI Freeze 유지
- HWPX Export 제외
- Grade A/B/C/D/E
- Severity = Impact × Likelihood Matrix
- Qwen3-4B Q4_K_M 유지
- Inspection 취소 시 DB 미저장 + 입력상태 유지
- Administration 데이터 삭제 정책 유지
- 작업 전 코드↔문서↔테스트↔이전 결정사항 2~3회 교차검증
- 검증되지 않은 Rule의 Registry 선등록 금지

다음 실제 개발 시작점은 **P1-B REQ-007 → REQ-012 → REQ-017**이다.
