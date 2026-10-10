# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-10 KST
- 목적: 새 대화에서도 실제 GitHub 기준으로 바로 이어가기 위한 최신 기준점

다음 세션 시작 순서:
`GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드/installer → 이전 대화`

작업 원칙:
- 코드 ↔ 문서 ↔ 테스트 ↔ 기존 결정사항을 최소 2~3회 교차검증한다.
- 완료된 기능을 추측으로 다시 만들지 않는다.
- 사용자가 개발 초보이므로 로컬 명령은 PowerShell 기준 한 번에 하나씩 안내한다.
- 실제 Handler + targeted test + 통합/전체 회귀를 통과한 Rule만 Registry에 활성화한다.
- 2026-09-18 UI Freeze 유지.

---

# 1. 전체 상태

완료 유지:
- 1단계 기존 Rule 복원·재분류
- 2단계 5대 검사영역 / Full Catalog 105개 확정
- 3단계 해커톤 MVP20 확정
- 4단계 9종 문서 Parser + Rule/AI/Hybrid Engine
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정
- Inspection UX 보완
- 6단계 Administration 데이터 관리
- 최종 EXE 안정화
- 감리 관련 114개 파일 분석 / 105개 전체 Rule 매핑
- MVP20 실제 감리사례 검증 및 우선 보완 5개
- 기존 ZIP(EXE) 재빌드/스모크
- WiX MSI 제작/실설치/Local AI 스모크

확장 진행:
- 7-0 중앙 실행 Registry 기반 — 완료
- P1 13개 구현기준 — 완료
- P1-A 4개 — 완료
- P1-B 3개 — 완료
- P1-C 2개 — 완료
- 다음: P1-D 3개 (AUD-020 / AUD-022 / AUD-023)
- 마지막: P1-E 1개 (FP-002)

---

# 2. 현재 검사체계

Full Catalog 105개:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23

최초 MVP 기준선 20개:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

현재 GitHub main 실제 실행 가능 Rule:
- **29개 = MVP20 + P1 9개**

활성 P1 9개:
- AUD-008 계획 대비 산출물 작성상태
- AUD-010 WBS 완전성·비정상 항목
- AUD-014 시험계획 완전성
- AUD-016 시험결함 조치상태
- AUD-018 품질활동 계획 대비 수행
- REQ-007 요구사항 검증가능성·검증방법
- REQ-012 요구사항 시험항목 누락
- REQ-017 요구사항 추적관계 누락
- FP-008 상세 산정정보 적정성

현재 실행방식 합계:
- Rule 7
- AI 6
- Hybrid 16

P1 진행:
- 완료/활성: 9 / 13
- 남음: 4
- P1 전체 완료 목표: 33개 실행 Rule

`MVP20`은 최초 기준선 명칭으로 유지한다. Full Catalog 105와 실제 실행 가능 Rule 수는 별도 개념이다.

---

# 3. P1-A — 완료

완료 Rule:
- AUD-008
- AUD-014
- AUD-016
- FP-008

핵심 역할 분리:
- AUD-001 = 실제 제출 파일 존재/누락
- AUD-008 = 계획표상 작성·제출 상태

검증 이력:
- 첫 3개 활성화 후 targeted 30 passed
- 첫 3개 활성화 후 전체 209 passed, 51 subtests passed
- AUD-008 추가 후 targeted/통합/전체 회귀 PASS

---

# 4. P1-B — 완료

완료 Rule:
- REQ-007: 검증방법 공란/미정/추후/협의/TBD/예정 후보 + AI 판단
- REQ-012: 요구사항↔시험 산출물 교차문서 비교
- REQ-017: 필요한 추적링크 공란 후보, REQ-018과 역할 분리

오탐 방지:
- 숫자 기준 부재만으로 검증불가 단정 금지
- 시험문서가 없으면 REQ-012 누락으로 단정하지 않음
- N/A / 해당없음 / 비대상 / 별도시트 참조 제외

핵심 파일:
- `rules/definitions/document_p1_req_rules.py`
- `rules/core/p1_requirement_checks.py`
- `rules/core/p1_requirement_hybrid_engine.py`
- `tests/test_p1_requirement_rules.py`
- `tests/test_p1_requirement_service.py`

검증:
- 전용 테스트 PASS
- REQ-012 Service 교차문서 통합 PASS
- 27개 Registry 통합 PASS
- 전체 `python -m pytest -q` 사용자 PC PASS

---

# 5. P1-C — 2026-10-10 완료

완료 Rule:

## AUD-010 WBS 완전성·비정상 항목 점검
- Hybrid
- 구조형 WBS에서 작업명/시작일/종료일/담당자 헤더 식별
- 시작일/종료일/담당자 누락 후보 추출
- 종료일 < 시작일인 명확한 일정 역전 후보 추출
- 합계/소계/구분/마일스톤 행 제외
- 날짜를 해석하지 못하면 오류로 단정하지 않음

## AUD-018 품질활동 계획 대비 수행 점검
- Hybrid + 교차문서 후처리
- 품질보증/품질관리/품질계획 문서와 품질활동/점검/검토결과/회의록 등 수행근거 문서를 함께 비교
- 계획 또는 수행근거 문서 한쪽만 있으면 Issue 후보/AI 호출 안 함
- 시기미도래/향후/예정/해당없음/N/A 제외
- 계획활동이 수행근거에서 확인되지 않을 때만 evidence 생성 후 AI 판단

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
- P1-C 사전분석 전용 테스트 PASS
- AUD-018 Service 교차문서 통합 테스트 PASS
- 29개 Registry + P1-A/B/C + 기존 Catalog/MVP targeted 통합 PASS
- 최종 전체 `python -m pytest -q` 사용자 PC 정상 PASS
- 사용자가 결과를 `정상`으로 확인했으며 정확한 passed/subtests 숫자는 임의 기록하지 않음

---

# 6. 현재 Engine 구조

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 필터 → Parser → Rule / AI / Hybrid → 교차문서 후처리 → Issue → Assessment → DB → UI`

Rule:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine(DocumentRuleEngine)`

Hybrid 상속:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine`
- `P1AuditHybridEngine`

교차문서/후처리:
- REQ-009 요구사항↔설계
- REQ-012 요구사항↔시험
- AUD-018 품질활동 계획↔수행근거
- 기존 CHG 비교/종합
- AUD-024 최종 종합

---

# 7. 다음 작업 — P1-D

대상:
1. AUD-020 인터페이스 정의 완전성 점검
2. AUD-022 계약·과업내용 반영 및 이행 증적 점검
3. AUD-023 관련 기준·지침 준수 점검

구현 원칙:
- 세 Rule 모두 Hybrid 유지
- 명확한 구조적 후보를 Rule 단계에서 먼저 좁히고 AI는 의미판단에만 사용
- 일부 문서 미업로드만으로 미이행/미준수를 확정하지 않음
- 기존 AUD/REQ/CHG Rule과 동일 Issue 중복 방지
- P1-D 3개가 targeted + 통합 + 전체 회귀를 모두 통과한 뒤 Registry 활성화

P1-D 완료 시 목표:
- 실행 Rule 32개
- P1 완료 12 / 13
- 남은 P1-E: FP-002 1개

---

# 8. Parser / Local AI / Severity 고정

Parser 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

제외:
- 스캔 이미지 PDF OCR
- HWPX Report Export

Local AI:
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- reasoning off
- temperature 0.7 / top-p 0.8 / top-k 20 / min-p 0 / seed 42

Severity:
`Impact × Likelihood → deterministic Severity Matrix`
AI가 최종 Severity를 직접 결정하지 않는다.

---

# 9. 배포 상태 주의

기존 최종 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 최종 MSI:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

중요:
- 위 ZIP/MSI는 P1 확장 전 MVP20 기준 기존 배포본이다.
- 현재 GitHub main 소스는 29개 실행 Rule 기준이다.
- 아직 P1 확장 소스로 ZIP/MSI를 다시 빌드하지 않았다.
- README / HACKATHON_SUBMISSION의 기존 배포검증 문구는 기존 배포본 기준으로 유지한다.
- P1 확장 범위를 동결한 뒤 최신 소스로 재빌드/스모크검증 후 제출문서를 최종 현행화한다.

---

# 10. 다음 세션에서 하지 말아야 할 것

- 1~6단계 재구현 금지
- UI Freeze 임의 변경 금지
- 감리자료 114개 처음부터 재분석 금지
- P1-A/B/C 9개 재구현 금지
- 검증 전 P1-D/E Registry 선등록 금지
- 기존 ZIP/MSI가 현재 29개 소스를 포함한다고 착각하지 않기

다음 실제 개발 시작점은 **P1-D AUD-020 → AUD-022 → AUD-023**이다.
