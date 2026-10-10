# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-10 KST
- 목적: 새 대화에서도 GitHub 실제 상태를 기준으로 즉시 이어가기 위한 최신 인수인계 기준점

다음 세션 시작 순서:
`GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드/installer → 이전 대화`

작업 원칙:
- 코드 ↔ 문서 ↔ 테스트 ↔ 기존 결정사항을 최소 2~3회 교차검증한다.
- 완료된 기능을 추측으로 다시 만들지 않는다.
- 사용자 로컬 명령은 PowerShell 기준 한 번에 하나씩 안내한다.
- 실제 Handler + targeted/integration + 전체 회귀를 통과한 Rule만 Registry에 활성화한다.
- 2026-09-18 UI Freeze 유지.

---

# 1. 전체 상태

완료 유지:
- 1단계 기존 Rule 복원·재분류
- 2단계 5대 검사영역 / Full Catalog 105개
- 3단계 최초 MVP20 기준선
- 4단계 9종 문서 Parser + Rule/AI/Hybrid Engine
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정
- Inspection UX 보완
- 6단계 Administration 데이터 관리
- EXE 안정화
- 감리자료 114개 분석 / 105개 전체 Rule 매핑
- MVP20 실제 감리사례 검증 및 우선 보완 5개
- 기존 ZIP(EXE) / MSI 제작 및 실제 Local AI 검증
- 7-0 중앙 실행 Registry 기반
- P1 구현기준 13개 확정
- P1-A 4개 / P1-B 3개 / P1-C 2개 / P1-D 3개 / P1-E 1개

**P1 13개 전체 구현·Registry 활성·전체 회귀 완료.**

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
- **33개 = MVP20 + P1 13개**

활성 P1 13개:
- AUD-008 계획 대비 산출물 작성상태
- AUD-010 WBS 완전성·비정상 항목
- AUD-014 시험계획 완전성
- AUD-016 시험결함 조치상태
- AUD-018 품질활동 계획 대비 수행
- AUD-020 인터페이스 정의 완전성
- AUD-022 계약·과업내용 반영 및 이행 증적
- AUD-023 관련 기준·지침 준수
- REQ-007 요구사항 검증가능성·검증방법
- REQ-012 요구사항 시험항목 누락
- REQ-017 요구사항 추적관계 누락
- FP-002 FP 산정대상 중복
- FP-008 상세 산정정보 적정성

현재 실행방식 합계:
- Rule 7
- AI 6
- Hybrid 20

`MVP20`은 최초 기준선 명칭으로만 유지한다. Full Catalog 105와 실제 실행 Registry 33은 별도 개념이다.

---

# 3. P1 완료 요약

## P1-A
- AUD-008 / AUD-014 / AUD-016 / FP-008
- 결정형·구조형 검사 우선 확장

## P1-B
- REQ-007 / REQ-012 / REQ-017
- 요구사항 검증가능성, 요구↔시험 교차검증, 추적링크 누락

## P1-C
- AUD-010 / AUD-018
- WBS 구조검사와 품질활동 계획↔수행근거 교차검증

## P1-D
- AUD-020 / AUD-022 / AUD-023
- 인터페이스 정의, 계약/과업 이행근거, 기준/지침 준수근거
- `P1GovernanceHybridEngine`을 통해 업로드 문서 전체 교차검증 지원

## P1-E
- FP-002 FP 산정대상 중복 점검
- XLS/XLSX 구조형 FP 표에서 기능명/유형/상세근거 후보화
- 동일·유사 기능명 + 동일 FP유형을 후보로 좁히고 AI가 실질 동일 기능인지 판단
- 처리조건·사용자 관점·입출력 차이가 명확한 경우 별도 기능으로 제외
- 합계/소계/요약행 제외
- 단순 문구 차이는 후보를 섣불리 제거하지 않고 AI 판단에 맡김

---

# 4. 최종 Engine 구조

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 33 필터 → Parser → Rule / AI / Hybrid → 문서별 사전분석·교차문서 비교 → Issue → Assessment → DB → UI`

Rule:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine(DocumentRuleEngine)`

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
- AUD-023 적용 기준/지침↔준수·검증근거
- 기존 CHG 비교/종합
- AUD-024 최종 종합

---

# 5. P1 최종 검증

검증 완료:
- P1-E FP-002 전용 테스트 PASS
- FP-002 오탐방지 보강 후 전용 테스트 재PASS
- Registry 33개 + Full Catalog/MVP 통합 테스트 PASS
- 최종 `python -m pytest -q` 사용자 PC 정상 PASS

사용자가 결과를 `정상`으로 확인했으며 정확한 passed/subtests 숫자는 제공되지 않았으므로 임의 기록하지 않는다.

**P1 Release Freeze 기준은 실행 Rule 33개로 확정한다.**

---

# 6. Parser / Local AI / Severity 고정

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

# 7. 배포 상태 — 매우 중요

기존 ZIP(EXE):
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 MSI:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

현재 상태:
- 위 ZIP/MSI는 **P1 확장 전 기존 빌드**이다.
- GitHub main 소스는 **33개 실행 Rule Freeze** 상태다.
- 따라서 기존 ZIP/MSI를 현재 33개 최종 제출본이라고 부르면 안 된다.

다음 작업:
1. 최신 main 로컬 반영 확인
2. 33개 Freeze 소스로 PyInstaller onedir 재빌드
3. ZIP(EXE) 재생성
4. ZIP 실행 및 Local AI 스모크검증
5. 동일 dist 기준 MSI 재빌드
6. MSI 실제 설치/DB 생성/Local AI 스모크검증
7. 성공 후 README / HACKATHON_SUBMISSION의 배포 상태를 최종 완료로 갱신

---

# 8. 이후 확장 우선순위

감리자료 매핑 기준 남은 우선순위:
- P2 23개
- P3 21개
- P4 28개

P1은 더 이상 미구현 대상이 아니다.
새 감리자료가 추가되면 114개를 처음부터 재분석하지 않고 기존 매핑에 증분 반영한다.

신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Full Catalog 105에 추가하지 않는다.

---

# 9. 다음 세션에서 하지 말아야 할 것

- 1~6단계 재구현 금지
- UI Freeze 임의 변경 금지
- 감리자료 114개 처음부터 재분석 금지
- P1 13개 재구현 금지
- 실행 Registry를 다시 MVP20으로 되돌리지 않기
- 기존 ZIP/MSI가 33개 Freeze 소스를 포함한다고 착각하지 않기

다음 실제 작업 시작점은 **33개 Freeze 최신 소스 기준 ZIP(EXE) 재빌드 및 스모크검증**이다.
