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
- P1-B 요구사항·시험·추적성 3개 — 완료
- 현재 다음 작업: P1-C 계획·품질 2개 (AUD-010, AUD-018)

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

현재 GitHub main 실제 실행 가능 Rule은 **27개**이다.

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
- AUD-008 계획 대비 산출물 작성상태
- AUD-014 시험계획 완전성
- AUD-016 시험결함 조치상태
- FP-008 상세 산정정보 적정성

검증 이력:
- 첫 3개 Registry 활성화 후 targeted 통합 `30 passed`
- 첫 3개 활성화 후 전체 `209 passed, 51 subtests passed`
- AUD-008 전용 테스트 PASS
- 24개 Registry/통합 targeted PASS
- 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS

---

## P1-B — 2026-10-10 완료

완료 Rule:

### REQ-007 요구사항 검증가능성·검증방법 점검
- 구조형 요구사항 표에서 검증방법 관련 열 식별
- 검증방법 공란 또는 `미정/추후/협의/TBD/예정` 후보 추출
- 단순 숫자 부재만으로 검증불가 판정하지 않음
- 후보가 없으면 AI 호출하지 않음

### REQ-012 요구사항 시험항목 누락 점검
- 단일 문서에서 즉시 누락으로 단정하지 않음
- 개별 Hybrid 실행에서는 skip
- `InspectionService`에서 업로드된 요구사항 문서와 시험문서를 교차비교
- 시험문서가 없는 경우 Issue 후보/AI 호출 안 함
- 시험문서가 존재하고 요구사항 ID 연결이 없을 때만 evidence 생성 후 AI 판단
- N/A / 해당없음 / 비대상 / 시험대상아님 제외

### REQ-017 요구사항 추적관계 누락 점검
- 추적표에 실제 존재하는 후속 링크 열을 구조적으로 검사
- 필요한 추적링크 공란 후보화
- N/A / 해당없음 / 별도시트 참조 제외
- REQ-018 양방향 추적성 검사와 역할 분리

핵심 구현:
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
- P1-B 전용 테스트 PASS
- REQ-012 교차문서 Service 통합 테스트 PASS
- 27개 Registry + P1-B + 기존 Catalog/MVP targeted 통합 PASS
- 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS
- 마지막 전체의 정확한 passed 개수는 사용자가 `정상`으로 확인했으므로 임의 숫자를 기록하지 않음

---

## 현재 문서 검사 Engine

실행 흐름:
`Inspection → Full Catalog 선택상태 → 실행 Registry 필터 → Parser → Rule / AI / Hybrid → 교차문서 후처리 → Issue → Assessment → DB → UI`

Rule 구조:
- 기존 `DocumentRuleEngine` 유지
- `P1DocumentRuleEngine`이 기존 Engine을 상속

Hybrid 구조:
- 기존 `DocumentHybridEngine` 유지
- `P1RequirementHybridEngine(DocumentHybridEngine)`으로 P1-B 사전분석 확장

교차문서 구조:
- REQ-009 요구사항 ↔ 설계
- REQ-012 요구사항 ↔ 시험
- 기존 CHG 비교/후처리 유지

UI Freeze 유지.

---

## 다음 작업 — P1-C

대상:
1. AUD-010 WBS 완전성·비정상 항목 점검
2. AUD-018 품질활동 계획 대비 수행 점검

AUD-010 기준:
- WBS/일정표 구조에서 작업명, 시작일, 종료일, 담당자 등 필수정보 후보 추출
- 종료일 < 시작일 등 명확한 일정역전 후보 추출
- 상위 요약행 / 구분행 / 마일스톤 오탐 방지
- 날짜를 해석할 수 없는 경우 오류로 단정하지 않음

AUD-018 기준:
- 품질보증/검토/점검 계획의 활동·주기·시점과 실제 수행근거 비교
- 시기미도래 제외
- 일부 문서만 업로드된 경우 근거부재만으로 즉시 미수행 확정 금지
- 구조적 후보 + AI 의미판단 Hybrid 유지

P1 전체 13개 중 현재:
- 완료 7개
- 남음 6개

P1-C 완료 후 목표:
- 실제 실행 Rule 29개

P1 전체 완료 목표:
- 실제 실행 Rule 33개

---

## 문서 Parser

지원 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

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
- Impact / Impact 근거
- Likelihood / Likelihood 근거

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

원래 미구현 85개 우선순위:
- P1 13
- P2 23
- P3 21
- P4 28

현재 P1 진행:
- 완료 7
- 남음 6

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
- 위 ZIP/MSI는 P1 확장 전 기존 MVP20 기준 최종 배포본이다.
- 현재 GitHub main 소스는 실행 Rule 27개 기준이다.
- 아직 P1 확장 소스로 ZIP/MSI를 다시 빌드하지 않았다.
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

다음 실제 개발 시작점은 **P1-C AUD-010 → AUD-018**이다.
