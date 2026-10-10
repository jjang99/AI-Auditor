# AI Auditor 개발 현황

## 기준일
- 2026-10-10

## 현재 전체 상태

기존 완료영역:
- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 최초 MVP20 기준선 확정 — 완료
- 4단계 9종 문서 Parser + Rule/AI/Hybrid 검사 Engine — 완료
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료
- EXE 안정화 — 완료
- 감리자료 114개 분석 / 105개 전체 Rule 실무 매핑 — 완료
- MVP20 실제 감리사례 실증검증 — 완료
- 우선 보완 5개 구현 및 전체 회귀검증 — 완료
- 기존 ZIP(EXE) / MSI 제작 및 실제 Local AI 검증 — 완료

확장 완료:
- 7-0 중앙 실행 Registry 기반 — 완료
- P1 13개 구현기준 확정 — 완료
- P1-A 4개 — 완료
- P1-B 3개 — 완료
- P1-C 2개 — 완료
- P1-D 3개 — 완료
- P1-E FP-002 — 완료

**P1 13개 전체 구현·Registry 활성·전체 회귀 완료.**

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
- **33개 = MVP20 + P1 13개**

P1 활성 13개:
- AUD-008 계획 대비 산출물 작성상태 점검
- AUD-010 WBS 완전성·비정상 항목 점검
- AUD-014 시험계획 완전성 점검
- AUD-016 시험결함 조치상태 점검
- AUD-018 품질활동 계획 대비 수행 점검
- AUD-020 인터페이스 정의 완전성 점검
- AUD-022 계약·과업내용 반영 및 이행 증적 점검
- AUD-023 관련 기준·지침 준수 점검
- REQ-007 요구사항 검증가능성·검증방법 점검
- REQ-012 요구사항 시험항목 누락 점검
- REQ-017 요구사항 추적관계 누락 점검
- FP-002 FP 산정대상 중복 점검
- FP-008 상세 산정정보 적정성 점검

현재 실행방식 합계:
- Rule 7
- AI 6
- Hybrid 20

`MVP20`은 최초 기준선 명칭으로 유지한다.
Full Catalog 105와 실행 Registry 33은 서로 다른 개념이다.

---

## 7-0 중앙 실행 Registry — 완료

핵심:
- `rules/definitions/document_rule_registry.py`에서 실제 실행 가능한 Rule 관리
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
- targeted / 통합 / 전체 회귀 PASS

---

## P1-B — 완료

완료:
- REQ-007 요구사항 검증가능성·검증방법
- REQ-012 요구사항 시험항목 누락
- REQ-017 요구사항 추적관계 누락

구조:
- `P1RequirementHybridEngine(DocumentHybridEngine)`
- REQ-012는 요구사항↔시험 교차문서 비교

오탐 방지:
- 숫자 기준 부재만으로 검증불가 단정 금지
- 시험문서 미업로드 시 REQ-012 누락 확정 금지
- N/A / 해당없음 / 비대상 / 별도시트 참조 제외

검증:
- 전용 / Service 통합 / Registry / 전체 회귀 PASS

---

## P1-C — 완료

### AUD-010 WBS 완전성·비정상 항목 점검
- Hybrid
- WBS 작업명/시작일/종료일/담당자 구조 식별
- 필수정보 누락 및 일정 역전 후보 추출
- 합계/소계/구분/마일스톤 제외
- 해석 불가능 날짜는 오류 확정 금지

### AUD-018 품질활동 계획 대비 수행 점검
- Hybrid + 교차문서 비교
- 품질계획과 수행근거 비교
- 한쪽만 업로드되면 미수행 확정 금지
- 시기미도래/향후/예정/해당없음/N/A 제외

검증:
- 전용 / Service 교차문서 / Registry / 전체 회귀 PASS

---

## P1-D — 완료

완료:
- AUD-020 인터페이스 정의 완전성
- AUD-022 계약·과업내용 반영 및 이행 증적
- AUD-023 관련 기준·지침 준수

구조:
- `P1GovernanceHybridEngine(P1AuditHybridEngine)`
- 검사 시작 시 업로드 문서 전체를 P1-D 엔진에 전달
- AUD-020은 문서 단위 구조형 후보 추출
- AUD-022/AUD-023은 업로드 문서 전체 교차검증

오탐 방지:
- 단순 외부기관 언급을 인터페이스로 간주하지 않음
- 계약/RFP 일반 설명문을 의무사항으로 간주하지 않음
- 계약/과업 문서 단독 업로드만으로 미이행 확정 금지
- 비적용/해당없음/N/A 기준은 준수대상에서 제외
- 기준 자체를 법적으로 재해석해 위반 판정하지 않음

검증:
- 구조 사전분석 / 교차문서 / Service / Registry 32개 / 전체 회귀 PASS

---

## P1-E — 2026-10-10 완료

### FP-002 FP 산정대상 중복 점검
- Hybrid
- XLS/XLSX 구조형 FP 표에서 기능명/FP유형/상세근거를 추출
- 동일·유사 기능명 + 동일 FP유형인 행을 중복 후보화
- 상세 설명/처리조건/입출력 정보가 명확히 다른 경우 별도 기능으로 제외
- 단순 표현 차이는 후보에서 제거하지 않고 AI가 실질 동일 기능 여부를 판단
- 합계/소계/요약행 제외

구조:
- `rules/definitions/document_p1_fp_rules.py`
- `rules/core/p1_fp_checks.py`
- `rules/core/p1_fp_hybrid_engine.py`
- `P1FPHybridEngine(P1GovernanceHybridEngine)`
- `tests/test_p1_fp_rules.py`

검증:
- FP-002 전용 테스트 PASS
- 오탐방지 보강 후 전용 테스트 재PASS
- Registry 33개 + Full Catalog/MVP 통합 PASS
- 최종 `python -m pytest -q` 사용자 PC 정상 PASS
- 사용자가 결과를 `정상`으로 확인했으며 정확한 passed/subtests 숫자는 제공되지 않아 임의 기록하지 않음

**P1 Release Freeze = 실행 Rule 33개.**

---

## 현재 문서 검사 Engine

실행 흐름:
`Inspection → Full Catalog 선택상태 → 실행 Registry 33 필터 → Parser → Rule / AI / Hybrid → 교차문서 후처리 → Issue → Assessment → DB → UI`

Rule:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine`

Hybrid 상속:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine`
- `P1AuditHybridEngine`
- `P1GovernanceHybridEngine`
- `P1FPHybridEngine`

주요 교차문서/후처리:
- REQ-009 요구사항↔설계
- REQ-012 요구사항↔시험
- AUD-018 품질활동 계획↔수행근거
- AUD-022 계약/과업 의무↔이행근거
- AUD-023 적용기준↔준수근거
- 기존 CHG 후처리
- AUD-024 최종 종합

---

## Parser / Local AI / Severity

Parser 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

제외:
- 스캔 이미지 PDF OCR
- HWPX Report Export

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

원래 미구현 85개 우선순위:
- P1 13 / P2 23 / P3 21 / P4 28

현재 P1 13개는 모두 구현 완료되었으므로 이후 확장 우선순위는:
- P2 23
- P3 21
- P4 28

감리자료는 처음부터 재분석하지 않고 기존 매핑을 재사용한다.

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
- 위 배포본은 P1 확장 전 기존 빌드이다.
- 현재 GitHub main은 33개 실행 Rule Freeze 기준이다.
- 아직 33개 소스로 ZIP/MSI를 재빌드하지 않았다.

다음 작업:
1. 33개 Freeze 소스로 ZIP(EXE) 재빌드
2. ZIP 실행 + Local AI 스모크검증
3. 동일 dist 기준 MSI 재빌드
4. MSI 실제 설치 + DB 자동생성 + Local AI 스모크검증
5. 성공 후 README / HACKATHON_SUBMISSION 배포 상태 최종 현행화

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

다음 실제 작업 시작점은 **33개 Freeze 최신 소스 기준 ZIP(EXE) 재빌드 및 스모크검증**이다.
