# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-10 KST
- 목적: 새 대화에서도 GitHub 실제 상태를 기준으로 즉시 이어가기 위한 최신 인수인계 기준점

다음 세션 시작 순서:
`GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → P2_IMPLEMENTATION_PLAN.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드/installer → 이전 대화`

작업 원칙:
- 코드 ↔ 문서 ↔ 테스트 ↔ 기존 결정사항을 최소 2~3회 교차검증한다.
- 완료된 기능을 추측으로 다시 만들지 않는다.
- 사용자 로컬 명령은 PowerShell 기준 한 번에 하나씩 안내한다.
- 실제 Handler + targeted/integration + 전체 회귀를 통과한 Rule만 Registry에 활성화한다.
- 2026-09-18 UI Freeze 유지.

---

# 1. 현재 기준선

완료:
- 1~6단계
- 9종 Parser / Rule·AI·Hybrid Engine
- Local AI / Severity / 감리 개선판정
- UI Freeze / Administration 데이터 관리 / EXE 안정화
- 감리자료 114개 분석 / Full Catalog 105 매핑
- MVP20 실증검증 및 우선 보완 5개
- 7-0 중앙 실행 Registry
- P1 13개 전체 구현·활성·전체 회귀
- **P2-A 7개 구현·활성·전체 회귀**
- **P2-B 6개 구현·활성·전체 회귀**

현재 GitHub main 실제 실행 Registry:
- **46개 = MVP20 + P1 13 + P2-A 7 + P2-B 6**
- 누적 실행방식: **Rule 14 / AI 9 / Hybrid 23**

P2 진행:
- **13 / 23 완료**
- P2-A 7 / 7 완료
- P2-B 6 / 6 완료
- P2-C 0 / 4 현재 시작
- P2-D 0 / 6

---

# 2. P2-A 완료

활성 7개:
- AUD-015 시험 수행·결과 완전성
- AUD-019 품질지적사항 미조치
- REQ-016 중요 요구사항 시험범위 누락
- REQ-020 잘못된 요구사항 참조
- CHG-005 변경 승인상태
- FP-007 FP 산정방식·적용기준 적정성
- AI-023 AI 자원사용·호출 제한 적정성

검증:
- 전용 테스트 PASS
- Registry 40개 + 선택 UI + Catalog/MVP/P1 통합 PASS
- 전체 `python -m pytest -q` 사용자 PC 정상 PASS

---

# 3. P2-B 완료

활성 6개:
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

핵심 동작:
- AUD-005: 동일 ID가 여러 문서에서 다른 명칭으로 사용된 경우만 교차문서 AI 후보
- AUD-021: 동일 인터페이스 ID의 시스템/방식/주기/데이터 정의가 문서 간 불일치할 때만 후보
- REQ-006: 관련 요구사항 근거가 있을 때 의미상 완전성 판단
- REQ-021: 상태/승인정보의 구조적 모순 후보
- REQ-027: 출처/상위요구 필드가 실제 있는 구조에서 근거 공란 후보, N/A 제외
- REQ-028: 원문 직접검사가 아니라 실제 REQ 지적사항이 있을 때만 종합 후처리

검증:
- `tests/test_p2_b_rules.py` + `tests/test_p2_b_service.py` 사용자 PC 정상
- P2-B + P2-A + Registry 46 + 선택 UI + Catalog/MVP 통합 정상
- 최종 `python -m pytest -q` 사용자 PC 정상
- 사용자가 정확한 passed 숫자를 보내지 않았으므로 임의 기록하지 않는다.

**P2-B 완료 / 실행 Registry 46개 확정.**

---

# 4. Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine`

주요 교차문서/후처리:
- AUD-005 문서 간 용어 비교
- AUD-021 인터페이스 정의 비교
- REQ-009 요구사항↔설계
- REQ-012 요구사항↔시험
- AUD-018 품질활동 계획↔수행근거
- AUD-022 계약/과업 의무↔이행근거
- AUD-023 기준/지침↔준수근거
- REQ-028 REQ 계열 실제 지적 종합
- CHG 계열 비교/종합
- AUD-024 전체 최종 종합

---

# 5. P2-C 현재 시작점

대상 4개:
- CHG-008 관련 설계 변경 미반영 — Hybrid
- CHG-010 관련 데이터설계 변경 미반영 — Hybrid
- FP-006 기능 단위 분할·통합 적정성 — AI
- FP-011 FP 변경반영 누락 — Hybrid

Canonical 경계:
- CHG-008: 확인된 변경 + 관련 설계 산출물이 함께 있을 때 최신 반영 여부를 교차검증
- CHG-010: 데이터/테이블/컬럼 영향 근거가 있는 변경에 한정해 데이터설계 반영 여부 검증
- FP-006: 구조형 FP 행의 기능명/유형/상세근거를 이용해 과도 분할·이질 기능 통합 후보를 AI 판단
- FP-011: 확인된 요구/기능 변경 + FP 산정자료가 함께 있을 때 갱신 누락 후보 검증

오탐 방지:
- 교차문서 Rule은 필요한 문서 한쪽만 업로드된 상태를 자동 실패로 판정하지 않는다.
- CHG-008/010은 실제 변경 근거 없이 일반 설계문서가 오래됐다고 추정하지 않는다.
- FP-006은 FP-002 중복산정과 역할을 분리한다.
- FP-011은 변경자료 또는 FP 자료 한쪽만 있는 경우 미반영으로 확정하지 않는다.

P2-C는 Registry에 미리 올리지 않는다.

---

# 6. Full Catalog / 목표

Full Catalog 105:
- AUD 24 / REQ 28 / CHG 18 / FP 12 / AI 23

P2 전체 23:
- Rule 7 / AI 5 / Hybrid 11

P2 전체 완료 목표:
- **56개 = MVP20 + P1 13 + P2 23**
- **Rule 14 / AI 11 / Hybrid 31**

남은 P2:
- P2-C 4개
- P2-D 6개

---

# 7. 배포 정책

기존 ZIP/MSI는 P1/P2 확장 전 빌드다.

최신 결정:
- P2 전체 23개 완료 전 재빌드하지 않는다.
- P2 23개 전체 검증 후 **56개 Freeze** 소스로 ZIP(EXE) + MSI를 한 번 재빌드한다.
- ZIP 실제 실행 / Local AI / DB / 주요 Rule 스모크 후 동일 dist 기준 MSI를 재빌드·실설치 검증한다.

---

# 8. 다음 실제 작업

1. P2-C 4개 정의/사전분석 구현
2. Hybrid/AI 실행경로 연결
3. 전용 + Service 테스트
4. 로컬 검증 정상 시 Registry 활성 → 목표 50개
5. 통합 회귀
6. 전체 pytest
7. P2-C 문서 현행화 후 P2-D 진행

하지 말아야 할 것:
- P1/P2-A/P2-B 재구현 금지
- UI Freeze 임의 변경 금지
- 감리자료 114개 전체 재분석 금지
- P2-C 전용검증 전 Registry 활성 금지
- P2 전체 완료 전 ZIP/MSI 최신 제출본 재생성 금지
