# AI Auditor 개발 현황

## 기준일
- 2026-10-10

---

## 1. 현재 전체 상태

완료:
- 1단계 기존 Rule 복원·재분류
- 2단계 최종 5대 검사영역 / Full Catalog 105개
- 3단계 최초 MVP20 기준선
- 4단계 9종 문서 Parser + Rule/AI/Hybrid 검사 Engine
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정
- Inspection 실행 UX 보완
- 6단계 Administration 데이터 관리
- EXE 안정화
- 감리자료 114개 분석 / 105개 전체 Rule 실무 매핑
- MVP20 실증검증 / 우선 보완 5개
- 7-0 중앙 실행 Registry
- P1 13개 전체 구현·활성·전체 회귀
- **P2-A 7개 전체 구현·활성·전체 회귀**

현재 진행:
- **P2-B 6개 구현 완료 / 전용·Service 검증 대기**

---

## 2. 검사체계

Full Catalog:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23
- 합계 105

최초 MVP20:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

P1 완료 후 기준:
- 33개 = MVP20 + P1 13

P2-A 완료 후 현재 Registry:
- **40개 = MVP20 + P1 13 + P2-A 7**
- Rule 14 / AI 6 / Hybrid 20

P2 전체 완료 목표:
- **56개 = MVP20 + P1 13 + P2 23**
- Rule 14 / AI 11 / Hybrid 31

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
- AUD-015 시험 수행·결과 완전성
- AUD-019 품질지적사항 미조치
- REQ-016 중요 요구사항 시험범위 누락
- REQ-020 잘못된 요구사항 참조
- CHG-005 변경 승인상태
- FP-007 FP 산정방식·적용기준 적정성
- AI-023 AI 자원사용·호출 제한 적정성

구조:
- `rules/definitions/document_p2_a_rules.py`
- `rules/core/p2_a_checks.py`
- `rules/core/p2_document_engine.py`
- `tests/test_p2_a_rules.py`

검증:
- P2-A 전용 테스트 사용자 PC 정상
- P2-A + Registry 40 + 선택 UI + Catalog/MVP 통합 정상
- 전체 `python -m pytest -q` 사용자 PC 정상
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2-A 완료 / 실행 Registry 40개 확정**

---

## 5. P2-B — 구현 완료, 검증 전

대상 6개:
- AUD-005 문서 간 용어 일관성 — AI, 교차문서
- AUD-021 인터페이스 문서정보 일치 — Hybrid, 교차문서
- REQ-006 요구사항 완전성 — AI
- REQ-021 요구사항 상태·승인정보 정합성 — Hybrid
- REQ-027 요구사항 출처·상위요구 및 추가기능 근거 — Hybrid
- REQ-028 요구사항 정합성 종합 위험 후보 — AI, 후처리 종합

구현 파일:
- `rules/definitions/document_p2_b_rules.py`
- `rules/core/p2_b_checks.py`
- `rules/core/p2_b_hybrid_engine.py`
- `rules/core/ai_strategy.py`
- `rules/core/inspection_engine.py`
- `app/services/inspection_service.py`
- `tests/test_p2_b_rules.py`
- `tests/test_p2_b_service.py`

핵심 동작:
- AUD-005: 동일 ID가 여러 문서에서 다른 명칭으로 사용된 구조적 후보만 AI 비교
- AUD-021: 동일 인터페이스 ID의 시스템/방식/주기/데이터 정의 불일치 후보만 AI 판단
- REQ-006: 관련 요구사항 근거가 있을 때 의미상 완전성 AI 판단
- REQ-021: 완료↔미승인, 삭제↔승인 등 명확한 상태/승인 모순 후보
- REQ-027: 출처/상위요구 필드가 실제 존재하는 구조에서 공란 후보, N/A/비대상 제외
- REQ-028: 원문 직접검사가 아니라 실제 REQ 지적사항 종합 후처리

현재 상태:
- **Registry 미등록**
- 전용/Service 테스트 통과 전 활성화 금지

---

## 6. 현재 Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine`

실행 흐름:
`Inspection → Full Catalog 선택 → 실행 Registry → Parser → Rule/AI/Hybrid → 교차문서/종합 후처리 → Issue → Assessment → DB → UI`

주요 교차문서/종합:
- AUD-005 문서 간 용어 비교
- AUD-021 인터페이스 정의 비교
- REQ-009 요구사항↔설계
- REQ-012 요구사항↔시험
- AUD-018 계획↔수행근거
- AUD-022 계약/과업↔이행근거
- AUD-023 기준/지침↔준수근거
- REQ-028 REQ 계열 지적 종합
- CHG 계열 비교/종합
- AUD-024 전체 종합

---

## 7. Parser / Local AI / Severity 고정

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

## 8. 배포 상태

기존 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 MSI:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

중요:
- 기존 배포본은 P1/P2 확장 전 상태
- P2 23개 전체 완료 전 재빌드하지 않음
- P2 전체 완료 후 56개 Freeze 소스로 ZIP/MSI 재빌드 + 실제 스모크검증

---

## 9. 다음 작업

1. 로컬 `git pull --ff-only`
2. `tests/test_p2_b_rules.py` + `tests/test_p2_b_service.py` 실행
3. 정상 시 P2-B 6개 Registry 활성 → 46개
4. 통합검증
5. 전체 pytest
6. P2-B 완료 문서 현행화
7. P2-C 4개 진행
