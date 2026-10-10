# AI Auditor 개발 현황

## 기준일
- 2026-10-10

## 현재 전체 상태

기존 완료영역:
- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 해커톤 MVP 대표 Rule 20개 확정 — 완료
- 4단계 9종 문서 Parser + Rule/AI/Hybrid 검사 Engine — 완료
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료
- 최종 EXE 안정화 — 완료
- 감리결과서 114개 분석 / 105개 전체 Rule 실무 매핑 — 완료
- MVP20 실제 감리사례 실증검증 — 완료
- 우선 보완 5개 구현 및 전체 회귀검증 — 완료
- 기존 ZIP(EXE) 재빌드 및 스모크검증 — 완료
- WiX MSI 제작 / 실제 설치 / Local AI 검사 검증 — 완료

확장 진행상태:
- 7-0 최소 공통 확장기반 — 완료
- P1 13개 구현기준 확정 — 완료
- P1-A 4개 — 완료
- P1-B 3개 — 완료
- P1-C 2개 — 완료
- 현재 다음 작업: P1-D 3개 (AUD-020 / AUD-022 / AUD-023)
- 이후 P1-E: FP-002

---

## 검사체계

제품 전체 검사체계:
- 감리 사전점검(AUD): 24
- 요구사항 정합성(REQ): 28
- 변경영향도(CHG): 18
- FP 검증(FP): 12
- AI 특화 검증(AI): 23
- 합계: 105

최초 MVP 기준선:
- 20개
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

현재 GitHub main 실제 실행 가능 Rule:
- **29개 = MVP20 + P1 9개**

P1 활성 9개:
- AUD-008 계획 대비 산출물 작성상태 점검
- AUD-010 WBS 완전성·비정상 항목 점검
- AUD-014 시험계획 완전성 점검
- AUD-016 시험결함 조치상태 점검
- AUD-018 품질활동 계획 대비 수행 점검
- REQ-007 요구사항 검증가능성·검증방법 점검
- REQ-012 요구사항 시험항목 누락 점검
- REQ-017 요구사항 추적관계 누락 점검
- FP-008 상세 산정정보 적정성 점검

현재 실행방식 합계:
- Rule 7
- AI 6
- Hybrid 16

`MVP20`은 최초 기준선 명칭으로 유지한다.
Full Catalog 105와 실행 가능 Rule 수는 서로 다른 개념이다.

---

## 7-0 최소 공통 확장기반 — 완료

핵심:
- 중앙 `document_rule_registry.py`에서 실제 실행 가능한 Rule만 관리
- Handler 없는 Rule 조기 활성화 방지
- Full Catalog 105와 실제 실행 Registry 분리
- UI Freeze 유지

7-0 직후 전체 회귀:
- `198 passed, 51 subtests passed`

---

## P1-A — 완료

완료:
- AUD-008
- AUD-014
- AUD-016
- FP-008

검증:
- 첫 3개 Registry 활성화 후 targeted `30 passed`
- 첫 3개 활성화 후 전체 `209 passed, 51 subtests passed`
- AUD-008 전용/통합/전체 회귀 PASS

---

## P1-B — 완료

완료:
- REQ-007 요구사항 검증가능성·검증방법
- REQ-012 요구사항 시험항목 누락
- REQ-017 요구사항 추적관계 누락

구조:
- `P1RequirementHybridEngine(DocumentHybridEngine)`
- REQ-012는 `InspectionService`에서 요구사항↔시험 교차문서 비교

오탐 방지:
- 검증방법의 숫자 부재만으로 검증불가 단정 금지
- 시험문서 미업로드 시 REQ-012 누락 확정 금지
- N/A / 해당없음 / 비대상 / 별도시트 참조 제외

검증:
- P1-B 전용 PASS
- REQ-012 Service 통합 PASS
- 27개 Registry 통합 PASS
- 전체 `python -m pytest -q` 사용자 PC PASS

---

## P1-C — 2026-10-10 완료

### AUD-010 WBS 완전성·비정상 항목 점검
- Hybrid
- WBS 표에서 작업명/시작일/종료일/담당자 구조 식별
- 시작일/종료일/담당자 누락 후보
- 종료일 < 시작일 일정 역전 후보
- 합계/소계/구분/마일스톤 제외
- 해석 불가능한 날짜는 오류로 단정하지 않음

### AUD-018 품질활동 계획 대비 수행 점검
- Hybrid + 교차문서 후처리
- 품질계획 문서와 수행근거 문서를 함께 비교
- 한쪽만 업로드되면 Issue 후보/AI 호출 안 함
- 시기미도래/향후/예정/해당없음/N/A 제외
- 수행근거가 확인되지 않는 계획활동만 evidence 생성 후 AI 판단

핵심 파일:
- `rules/definitions/document_p1_audit_rules.py`
- `rules/core/p1_audit_checks.py`
- `rules/core/p1_audit_hybrid_engine.py`
- `rules/core/inspection_engine.py`
- `app/services/inspection_service.py`
- `tests/test_p1_audit_rules.py`
- `tests/test_p1_audit_service.py`
- `rules/definitions/document_rule_registry.py`
- `tests/test_document_rule_registry.py`
- `tests/test_document_selection.py`

검증:
- P1-C 사전분석 전용 PASS
- AUD-018 Service 교차문서 통합 PASS
- 29개 Registry + P1-A/B/C + 기존 Catalog/MVP targeted 통합 PASS
- 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS
- 사용자가 `정상`으로 확인했으므로 정확한 passed/subtests 숫자는 임의 기록하지 않음

---

## 현재 문서 검사 Engine

실행 흐름:
`Inspection → Full Catalog 선택상태 → 실행 Registry 필터 → Parser → Rule / AI / Hybrid → 교차문서 후처리 → Issue → Assessment → DB → UI`

Rule:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine`

Hybrid 상속:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine`
- `P1AuditHybridEngine`

교차문서/후처리:
- REQ-009 요구사항↔설계
- REQ-012 요구사항↔시험
- AUD-018 품질활동 계획↔수행근거
- 기존 CHG 후처리
- AUD-024 최종 종합

---

## 다음 작업 — P1-D

대상:
1. AUD-020 인터페이스 정의 완전성 점검
2. AUD-022 계약·과업내용 반영 및 이행 증적 점검
3. AUD-023 관련 기준·지침 준수 점검

구현 원칙:
- 모두 Hybrid
- 구조적 후보를 먼저 추출하고 AI는 문맥 판단에 사용
- 일부 문서 미업로드를 곧바로 미이행/미준수로 판정하지 않음
- 기존 Rule과 중복 Issue 최소화
- targeted + 통합 + 전체 회귀 후 Registry 활성화

P1 현재:
- 완료 9 / 13
- 남음 4

P1-D 완료 목표:
- 실행 Rule 32개
- P1 완료 12 / 13
- 남은 P1-E FP-002 1개

P1 전체 완료 목표:
- 실행 Rule 33개

---

## Parser / Local AI / Severity

Parser 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

제외:
- 스캔 이미지 PDF OCR
- HWPX Export

Local AI:
- Qwen3-4B Q4_K_M
- llama.cpp b11312
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

Severity:
`Impact × Likelihood → deterministic Severity Matrix`

---

## 감리자료 기반 근거

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`
- `P1_IMPLEMENTATION_PLAN.md`

감리 원본:
- 114개
- PDF 94 / DOCX 19 / XLSX 1
- 2019~2025 독립 감리보고서

미구현 85개 원래 우선순위:
- P1 13 / P2 23 / P3 21 / P4 28

감리자료는 이후 구현 때 처음부터 재분석하지 않는다. 새 자료만 증분 반영한다.

신규 Rule 후보:
- 9개 + 조건부 1개 유지
- 사용자 승인 전 Full Catalog 105에 추가 금지

---

## 배포 상태 주의

기존 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 MSI:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

중요:
- 위 배포본은 P1 확장 전 MVP20 기준이다.
- 현재 GitHub main은 29개 실행 Rule 기준이다.
- 아직 P1 확장 소스로 ZIP/MSI를 재빌드하지 않았다.
- README / HACKATHON_SUBMISSION의 기존 배포검증 문구는 기존 배포본 기준으로 유지한다.
- P1 확장 동결 후 최신 소스로 재빌드/스모크하고 제출문서를 최종 현행화한다.

---

## 고정사항

- UI Freeze 유지
- Grade A/B/C/D/E
- Severity = Impact × Likelihood Matrix
- Qwen3-4B Q4_K_M 유지
- Inspection 취소 시 DB 미저장 + 입력상태 유지
- Administration 삭제 정책 유지
- 작업 전 코드↔문서↔테스트↔결정사항 교차검증
- 검증되지 않은 Rule Registry 선등록 금지

다음 실제 개발 시작점은 **P1-D AUD-020 → AUD-022 → AUD-023**이다.
