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

확장 진행:
- 7-0 최소 공통 확장기반 — 완료
- P1 13개 구현기준 확정 — 완료
- P1-A 구조형/결정형 4개 — 완료
- P1-B 요구사항·시험·추적성 3개 — 완료
- 다음 단계: P1-C 계획·품질 2개 (AUD-010, AUD-018)

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
- **27개 = 기존 MVP20 + P1 7개**

P1 활성 7개:
- AUD-008 계획 대비 산출물 작성상태 점검
- AUD-014 시험계획 완전성 점검
- AUD-016 시험결함 조치상태 점검
- REQ-007 요구사항 검증가능성·검증방법 점검
- REQ-012 요구사항 시험항목 누락 점검
- REQ-017 요구사항 추적관계 누락 점검
- FP-008 상세 산정정보 적정성 점검

현재 실행방식 합계:
- Rule 7
- AI 6
- Hybrid 14

중요:
- `MVP20`은 최초 해커톤 기준선 명칭으로 유지한다.
- `현재 실제 실행 가능 Rule 수`는 확장 구현으로 27개가 되었다.
- Full Catalog 105개와 실제 실행 가능 Rule 수는 서로 다른 개념이다.

---

# 3. 7-0 최소 공통 확장기반 — 완료

구현 목적:
- 기존 MVP20 직접 하드코딩 구조를 확장 가능한 중앙 Registry 구조로 전환
- Handler가 없는 Rule의 조기 활성화 차단
- UI Freeze를 유지하면서 실제 실행 Rule만 점진 확장

핵심 파일:
- `rules/definitions/document_rule_registry.py`
- `rules/core/document_selection.py`
- `ui/inspection_rule_ui_patch.py`
- `tests/test_document_rule_registry.py`
- `tests/test_document_selection.py`

원칙:
- Full Catalog 105는 유지
- 실제 Handler + targeted test를 통과한 Rule만 Registry 등록
- Registry 미등록 Rule은 UI Catalog에 존재해도 실제 검사에서는 실행하지 않음

7-0 직후 사용자 PC 전체 회귀:
- `198 passed, 51 subtests passed`

---

# 4. P1 구현 계획

Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

구현 묶음:
- P1-A: AUD-014 / AUD-016 / FP-008 / AUD-008 — 완료
- P1-B: REQ-007 / REQ-012 / REQ-017 — 완료
- P1-C: AUD-010 / AUD-018 — 다음
- P1-D: AUD-020 / AUD-022 / AUD-023
- P1-E: FP-002

P1 전체 완료 시 목표:
- 실제 실행 Rule 33개 = MVP20 + P1 13개

현재 P1:
- 완료/활성 7개
- 남음 6개

---

# 5. P1-A — 완료

완료 Rule:
- AUD-008 계획 대비 산출물 작성상태
- AUD-014 시험계획 완전성
- AUD-016 시험결함 조치상태
- FP-008 상세 산정정보 적정성

핵심 역할 분리:
- AUD-001 = 실제 제출 파일 존재/누락
- AUD-008 = 계획표상 현재 대상 산출물의 작성·제출 상태

검증:
- 첫 3개 활성화 후 targeted `30 passed`
- 첫 3개 활성화 후 전체 `209 passed, 51 subtests passed`
- AUD-008 추가 후 targeted PASS
- 24개 Registry 통합 PASS
- 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS

---

# 6. P1-B — 2026-10-10 완료

## REQ-007 요구사항 검증가능성·검증방법 점검

구현:
- Hybrid
- 구조형 요구사항 표에서 `요구사항 ID + 검증방법/확인방법/시험방법/수용기준` 열을 식별
- 검증방법 공란 또는 `미정/추후/협의/TBD/예정` 후보를 사전추출
- 숫자가 없다는 이유만으로 기능 요구사항 전체를 검증불가로 판정하지 않음
- 후보가 없으면 AI 호출하지 않음

## REQ-012 요구사항 시험항목 누락 점검

구현:
- Hybrid
- 단일 문서만 보고 누락으로 단정하지 않음
- 개별문서 Hybrid 실행에서는 건너뜀
- `InspectionService` 후처리에서 업로드된 요구사항 문서와 시험문서를 함께 비교
- 시험문서가 하나도 없으면 업로드 불완전 가능성이 있으므로 Issue 후보 생성/AI 호출 안 함
- 시험문서가 존재하고 요구사항 ID 연결이 확인되지 않을 때만 교차문서 evidence 생성 후 AI 최종판단
- `N/A/해당없음/비대상/시험대상아님` 제외

## REQ-017 요구사항 추적관계 누락 점검

구현:
- Hybrid
- 추적표에 실제 존재하는 후속 산출물 열 중 최소 2개 이상이 정의된 구조를 대상으로 함
- 필요한 추적링크 공란을 후보화
- N/A / 해당없음 / 별도시트 참조 제외
- REQ-018의 전체 양방향 추적성 검사와 역할 분리

P1-B 핵심 파일:
- `rules/definitions/document_p1_req_rules.py`
- `rules/core/p1_requirement_checks.py`
- `rules/core/p1_requirement_hybrid_engine.py`
- `rules/core/inspection_engine.py`
- `app/services/inspection_service.py`
- `tests/test_p1_requirement_rules.py`
- `tests/test_p1_requirement_service.py`
- `rules/definitions/document_rule_registry.py`
- `tests/test_document_rule_registry.py`
- `tests/test_document_selection.py`

검증:
- P1-B Rule 전용 테스트 PASS
- REQ-012 교차문서 Service 통합 테스트 PASS
- 27개 Registry + P1-B + 기존 Full Catalog/MVP 통합 targeted PASS
- 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS
- 마지막 실행의 정확한 passed 개수는 사용자가 `정상`으로 확인했으므로 숫자를 임의 기록하지 않음

---

# 7. 현재 Engine 구조

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 필터 → Parser → Rule / AI / Hybrid → 교차문서 후처리 → Issue → Assessment → DB → UI`

Rule:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine(DocumentRuleEngine)`

Hybrid:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine(DocumentHybridEngine)`
- 기존 Hybrid Rule 동작을 보존하면서 P1-B 사전분석 확장

교차문서:
- REQ-009 요구사항↔설계 비교
- REQ-012 요구사항↔시험 비교
- CHG 계열 기존 비교/후처리

UI Freeze는 유지한다.

---

# 8. 다음 작업 — P1-C

대상:
1. AUD-010 WBS 완전성·비정상 항목 점검
2. AUD-018 품질활동 계획 대비 수행 점검

AUD-010 구현기준:
- WBS/일정표 구조의 작업명, 시작일, 종료일, 담당자 필수정보 후보 추출
- 종료일 < 시작일 같은 명확한 일정역전 후보 추출
- 상위 요약행 / 구분행 / 마일스톤 오탐 방지
- 날짜를 해석할 수 없으면 오류로 단정하지 않음

AUD-018 구현기준:
- 품질보증/검토/점검 계획의 활동·주기·시점과 실제 수행근거 비교
- 시기미도래 제외
- 일부 문서만 업로드된 경우 근거부재만으로 즉시 미수행 확정 금지
- 구조적 후보 + AI 의미판단 Hybrid 유지

P1-C가 모두 검증·활성화되면 실행 Rule 목표:
- 29개

---

# 9. 감리자료 / Rule 근거

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`
- `P1_IMPLEMENTATION_PLAN.md`

감리자료:
- 114개
- PDF 94 / DOCX 19 / XLSX 1
- 2019~2025 독립 보고서

감리자료는 P1~P4 구현 때 처음부터 다시 분석하지 않는다.
새 자료가 들어올 때만 증분 반영한다.

신규 Rule 후보:
- 9개 + 조건부 1개 유지
- Full Catalog 105에는 아직 추가하지 않음
- 사용자 승인 전 임의 추가 금지

---

# 10. Parser / Local AI / Severity 고정 기준

Parser 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

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

Final Severity:
`Impact × Likelihood → deterministic Severity Matrix`

AI가 Severity를 직접 결정하지 않는다.
감리 개선판정은 Severity와 별도 관리한다.

---

# 11. UI / 데이터 / 배포 고정 기준

UI:
- 2026-09-18 UI Freeze 유지
- Dark 기본 / Light 지원
- 임의 재설계 금지

Administration 데이터 관리:
- 전체 검사이력 정리: `Issues → Inspections`, Project 유지
- Project 삭제: `Issues → Inspections → Project`
- transaction / rollback 유지

기존 최종 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 최종 MSI 설치형:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

중요:
- 위 ZIP/MSI는 P1 확장 전 기존 MVP20 기준 최종 배포본이다.
- 현재 GitHub main 소스는 27개 Rule 기준이다.
- P1 확장 소스로 ZIP/MSI를 아직 다시 빌드하지 않았다.
- README / HACKATHON_SUBMISSION의 기존 배포검증 문구는 기존 배포본 기준으로 유지한다.
- P1 확장 범위를 동결한 뒤 최신 소스로 ZIP/MSI를 재빌드·스모크검증하고 제출문서를 최종 현행화한다.

---

# 12. 다음 세션에서 하지 말아야 할 것

- 1~6단계를 다시 구현하지 않는다.
- UI Freeze를 깨지 않는다.
- 감리자료 114개를 처음부터 다시 분석하지 않는다.
- MVP20 보완 5개를 다시 작업하지 않는다.
- P1-A/P1-B 7개를 다시 구현하지 않는다.
- 검증되지 않은 P1 Rule을 Registry에 미리 등록하지 않는다.
- 기존 ZIP/MSI가 현재 27개 소스를 포함한다고 착각하지 않는다.

다음 실제 개발 시작점은 **P1-C AUD-010 → AUD-018**이다.
