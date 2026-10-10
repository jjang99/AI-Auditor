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
- **P2-C 4개 전체 구현·활성·전체 회귀**
- **P2-D 6개 전체 구현·활성·전체 회귀**

현재 진행:
- **56개 Freeze 기준 최종 Portable ZIP(EXE) / MSI 재빌드 및 실제 스모크검증**

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

P1 완료:
- 33개 = MVP20 + P1 13

P2 전체 완료 후 현재 Registry:
- **56개 = MVP20 + P1 13 + P2 23**
- **Rule 14 / AI 11 / Hybrid 31**

P2:
- **23 / 23 완료**
- P2-A 7 / 7
- P2-B 6 / 6
- P2-C 4 / 4
- P2-D 6 / 6

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

**P2-A 완료 / Registry 40개 시점 검증 완료**

---

## 5. P2-B — 완료

대상 6개:
- AUD-005 / AUD-021 / REQ-006 / REQ-021 / REQ-027 / REQ-028

**P2-B 완료 / Registry 46개 시점 검증 완료**

---

## 6. P2-C — 완료

대상 4개:
- CHG-008 관련 설계 변경 미반영 — Hybrid
- CHG-010 관련 데이터설계 변경 미반영 — Hybrid
- FP-006 기능 단위 분할·통합 적정성 — AI
- FP-011 FP 변경반영 누락 — Hybrid

검증:
- 전용 + Service 테스트 사용자 PC 정상
- Registry 50 + 선택 UI + 기존 P2-A/B + Catalog/MVP 통합 정상
- 전체 pytest 사용자 PC 정상
- Registry truncation 오류 복구 후 동일 통합/전체 회귀 재검증 정상

**P2-C 완료 / Registry 50개 시점 검증 완료**

---

## 7. P2-D — 완료

대상 6개:
- AI-003 AI 성능·품질 목표 정의 — Hybrid
- AI-008 민감정보 입력·출력 통제 — Hybrid
- AI-013 학습·참조데이터 적정성 — Hybrid
- AI-015 RAG 검색근거 적정성 — AI
- AI-017 AI 평가·테스트 체계 적정성 — Hybrid
- AI-021 AI 로그·추적성 및 운영 모니터링 — Hybrid

핵심 원칙:
- AI/LLM/RAG 관련 근거가 확인된 문서에만 적용
- 특정 목표값·보안기준·정책을 임의 생성하지 않음
- AI-015는 RAG/검색증강 근거가 있을 때만 적용
- AI-021은 일반 애플리케이션 로그만으로 충족 판정하지 않음
- Hybrid 5개는 사전근거가 없으면 AI 호출하지 않음
- 일반 데이터모델 문서의 단순 `모델` 단어는 AI 문서 판별 신호에서 제외

검증:
- P2-D 전용 + Service 테스트 사용자 PC 정상
- P2-D + P2-A/B/C + Registry 56 + 선택 UI + Catalog/MVP 통합 정상
- 최종 `python -m pytest -q` 사용자 PC 정상
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2-D 완료 / P2 23/23 완료 / 실행 Registry 56개 Freeze 확정**

---

## 8. 최종 Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

AI:
`DocumentAIEngine → P2CAIEngine → P2DAIEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine → P2CHybridEngine → P2DHybridEngine`

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 56 → Parser → Rule/AI/Hybrid → 교차문서/종합 후처리 → Issue → Assessment → DB → UI`

---

## 9. Parser / Local AI / Severity 고정

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

## 10. 배포 상태

기존 ZIP/MSI는 P1/P2 확장 전 빌드이므로 최신 제출본이 아니다.

Portable 빌드:
- 스크립트: `scripts/build_portable.ps1`
- Folder: `dist/AI_Auditor/`
- ZIP: `dist/AI_Auditor_Portable.zip`
- SHA256: `dist/AI_Auditor_Portable.zip.sha256.txt`

MSI 빌드:
- 스크립트: `installer/build_msi.ps1`
- 출력: `installer/output/`

---

## 11. 다음 작업

1. 최신 main 로컬 반영
2. Portable ZIP(EXE) 재빌드
3. Portable 실제 실행 / DB / Local AI / 주요 Rule 스모크검증
4. MSI 재빌드
5. MSI 실제 설치 / 모델복사 / DB / Local AI 스모크검증
6. RULE_DESIGN / P2_IMPLEMENTATION_PLAN / README / HACKATHON_SUBMISSION 최종 현행화
7. 최종 Git 상태 확인 및 마무리
