# AI Auditor 개발 현황

## 기준일
- 2026-10-10

---

## 1. 현재 전체 상태

완료:
- 1~6단계 기존 기능
- 9종 문서 Parser / Rule·AI·Hybrid Engine
- Local AI / Severity / 감리 개선판정
- UI Freeze / Administration 데이터 관리 / EXE 안정화
- 감리자료 114개 분석 / Full Catalog 105 매핑
- MVP20 실증검증 및 우선 보완 5개
- 7-0 중앙 실행 Registry
- P1 13개 전체 구현·활성·전체 회귀
- **P2-A 7개 전체 구현·활성·전체 회귀**
- **P2-B 6개 전체 구현·활성·전체 회귀**

현재 진행:
- **P2-C 4개 구현 완료 / 전용·Service 검증 대기**

---

## 2. 검사체계

Full Catalog 105:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23

최초 MVP20:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

P1 완료 기준:
- 33개 = MVP20 + P1 13

P2-A 완료 기준:
- 40개 = MVP20 + P1 13 + P2-A 7

P2-B 완료 후 현재 Registry:
- **46개 = MVP20 + P1 13 + P2-A 7 + P2-B 6**
- **Rule 14 / AI 9 / Hybrid 23**

P2 진행:
- **13 / 23 완료**

P2 전체 완료 목표:
- **56개 = MVP20 + P1 13 + P2 23**
- **Rule 14 / AI 11 / Hybrid 31**

---

## 3. P1 — 완료/Freeze

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

검증:
- 각 Batch 전용 테스트 PASS
- Registry 33개 통합 PASS
- 전체 pytest 사용자 PC PASS

**P1 Freeze = 실행 Rule 33개**

---

## 4. P2-A — 완료

대상 7개:
- AUD-015 / AUD-019 / REQ-016 / REQ-020 / CHG-005 / FP-007 / AI-023

검증:
- 전용 테스트 사용자 PC 정상
- Registry 40 + 선택 UI + Catalog/MVP/P1 통합 정상
- 전체 `python -m pytest -q` 사용자 PC 정상

**P2-A 완료 / 실행 Registry 40개**

---

## 5. P2-B — 완료

대상 6개:
- AUD-005 문서 간 용어 일관성 — AI, 교차문서
- AUD-021 인터페이스 문서정보 일치 — Hybrid, 교차문서
- REQ-006 요구사항 완전성 — AI
- REQ-021 요구사항 상태·승인정보 정합성 — Hybrid
- REQ-027 요구사항 출처·상위요구 및 추가기능 근거 — Hybrid
- REQ-028 요구사항 정합성 종합 위험 후보 — AI, 후처리 종합

구현:
- `rules/definitions/document_p2_b_rules.py`
- `rules/core/p2_b_checks.py`
- `rules/core/p2_b_hybrid_engine.py`
- `rules/core/ai_strategy.py`
- `rules/core/inspection_engine.py`
- `app/services/inspection_service.py`
- `tests/test_p2_b_rules.py`
- `tests/test_p2_b_service.py`

검증:
- P2-B 전용 + Service 테스트 사용자 PC 정상
- P2-B + P2-A + Registry 46 + 선택 UI + Catalog/MVP 통합 정상
- 최종 `python -m pytest -q` 사용자 PC 정상
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2-B 완료 / 실행 Registry 46개**

---

## 6. P2-C — 구현 완료, 검증 전

대상 4개:
- CHG-008 관련 설계 변경 미반영 — Hybrid
- CHG-010 관련 데이터설계 변경 미반영 — Hybrid
- FP-006 기능 단위 분할·통합 적정성 — AI
- FP-011 FP 변경반영 누락 — Hybrid

구현 파일:
- `rules/definitions/document_p2_c_rules.py`
- `rules/core/p2_c_checks.py`
- `rules/core/p2_c_hybrid_engine.py`
- `rules/core/p2_c_ai_engine.py`
- `rules/core/ai_strategy.py`
- `rules/core/inspection_engine.py`
- `tests/test_p2_c_rules.py`
- `tests/test_p2_c_service.py`

핵심 동작:
- CHG-008: 명시적 변경관리 행 + 일반 설계 산출물이 함께 있을 때만 교차문서 후보
- CHG-010: 데이터/테이블/컬럼 영향이 명시된 변경 + 데이터설계 문서가 함께 있을 때만 후보
- FP-006: 구조형 FP 행에서 과도 분할/부적절 통합 후보만 사전추출 후 AI 판단; 완전 동일 기능명은 FP-002 책임영역으로 제외
- FP-011: 기능/요구 변경 + FP 산정자료가 함께 있을 때만 변경반영 후보

오탐 방지:
- 필요한 문서 한쪽만 업로드된 경우 AI 호출하지 않음
- 일반 설계문서의 오래됨을 임의 추정하지 않음
- FP-006과 FP-002 역할 분리

현재 상태:
- **Registry 미등록**
- 전용/Service 테스트 정상 확인 전 활성화 금지

---

## 7. 현재 Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

AI:
`DocumentAIEngine → P2CAIEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine → P2CHybridEngine`

실행 흐름:
`Inspection → Full Catalog 선택 → 실행 Registry → Parser → Rule/AI/Hybrid → 교차문서/종합 후처리 → Issue → Assessment → DB → UI`

---

## 8. Parser / Local AI / Severity 고정

Parser 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

Local AI:
- Qwen3-4B Q4_K_M
- llama.cpp b11312
- reasoning off
- temperature 0.7 / top-p 0.8 / top-k 20 / min-p 0 / seed 42

Severity:
`Impact × Likelihood → deterministic Severity Matrix`

제외:
- 스캔 PDF OCR
- HWPX Report Export

---

## 9. 배포 상태

기존 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 MSI:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

정책:
- 기존 배포본은 P1/P2 확장 전 상태
- P2 23개 전체 완료 전 재빌드하지 않음
- P2 전체 완료 후 56개 Freeze 소스로 ZIP/MSI 재빌드 + 실제 스모크검증

---

## 10. 다음 작업

1. 로컬 `git pull --ff-only`
2. `tests/test_p2_c_rules.py` + `tests/test_p2_c_service.py` 실행
3. 실패 시 수정
4. 정상 시 P2-C 4개 Registry 활성 → 목표 50개
5. 통합검증
6. 전체 pytest
7. P2-C 완료 문서 현행화
8. P2-D 6개 진행
