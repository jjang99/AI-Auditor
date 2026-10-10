# AI Auditor 검사기준 설계서

## 1. 문서 목적
AI Auditor의 최종 검사기준 체계, 현재 실제 실행 범위, 검사결과 판정구조, 데이터 관리 원칙을 기록한다.
과거 상세 설계 이력은 Git history에 보존하며, 본 문서는 현재 GitHub main 구현 기준이다.

---

## 2. 최종 5대 검사영역 / Full Catalog 105

| 영역 | ID | 수량 |
|---|---|---:|
| 감리 사전점검 | AUD | 24 |
| 요구사항 정합성 | REQ | 28 |
| 변경영향도 | CHG | 18 |
| FP 검증 | FP | 12 |
| AI 특화 검증 | AI | 23 |
| **합계** |  | **105** |

Full Catalog 105는 제품 전체 검사체계이며 실제 실행 가능한 Rule 수와 동일하지 않다.

---

## 3. 최초 MVP20 기준선

AUD 4:
- AUD-001 / AUD-002 / AUD-007 / AUD-024

REQ 6:
- REQ-001 / REQ-002 / REQ-003 / REQ-004 / REQ-009 / REQ-018

CHG 4:
- CHG-001 / CHG-006 / CHG-012 / CHG-018

FP 2:
- FP-005 / FP-009

AI 4:
- AI-005 / AI-009 / AI-019 / AI-022

최초 실행방식:
- Rule 3
- AI 6
- Hybrid 11

`MVP20`은 최초 기준선 명칭으로 유지한다.

---

## 4. 현재 실제 실행 Rule — 56개

중앙 Registry:
- `rules/definitions/document_rule_registry.py`

현재 실제 실행 가능 Rule:
- **56개 = MVP20 + P1 13 + P2 23**

누적 실행방식:
- **Rule 14**
- **AI 11**
- **Hybrid 31**

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

P2 23개:
- AUD-005 / AUD-015 / AUD-019 / AUD-021
- REQ-006 / REQ-016 / REQ-020 / REQ-021 / REQ-027 / REQ-028
- CHG-005 / CHG-008 / CHG-010
- FP-006 / FP-007 / FP-011
- AI-003 / AI-008 / AI-013 / AI-015 / AI-017 / AI-021 / AI-023

Registry 원칙:
- Full Catalog와 실행 Registry를 분리한다.
- 실제 Handler와 전용/Service/통합/전체 회귀를 통과한 Rule만 활성화한다.
- Registry 미등록 Rule은 UI Full Catalog에 보여도 실제 검사에서는 실행하지 않는다.
- P1 13개와 P2 23개는 모두 검증 후 활성화 완료했다.

---

## 5. 문서 Parser 설계

지원 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

공통 흐름:
`원본 문서 → 형식별 Parser → ParsedDocument / DocumentBlock`

검사 Engine은 원본 형식에 직접 의존하지 않고 표준화 구조를 사용한다.

현재 제외:
- 스캔 이미지 PDF OCR

---

## 6. 최종 문서 검사 실행구조

`Inspection`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 56 필터`
→ `Parser / ParsedDocument`
→ `Rule / AI / Hybrid 라우팅`
→ `문서별 사전분석`
→ `교차문서 비교/후처리`
→ `Issue 생성`
→ `Issue Assessment`
→ `DB 저장`
→ `Project Detail / Reports`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않는다.

Rule 계층:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine(DocumentRuleEngine)`
- `P2DocumentRuleEngine(P1DocumentRuleEngine)`

AI 계층:
- `DocumentAIEngine`
- `P2CAIEngine(DocumentAIEngine)`
- `P2DAIEngine(P2CAIEngine)`

Hybrid 계층:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine`
- `P1AuditHybridEngine`
- `P1GovernanceHybridEngine`
- `P1FPHybridEngine`
- `P2BHybridEngine`
- `P2CHybridEngine`
- `P2DHybridEngine`

대표 교차문서/후처리:
- REQ-009 요구사항 ↔ 설계
- REQ-012 요구사항 ↔ 시험
- AUD-018 품질활동 계획 ↔ 수행근거
- AUD-021 인터페이스 정의 간 일치
- AUD-022 계약/과업 의무 ↔ 이행근거
- AUD-023 적용 기준/지침 ↔ 준수·검증근거
- REQ-027 출처/상위요구 ↔ 요구사항
- CHG-001 버전쌍 비교
- CHG-008 변경 ↔ 설계
- CHG-010 변경 ↔ 데이터설계
- CHG-012 변경 ↔ 시험
- FP-011 변경 ↔ FP 산정자료
- CHG-006 / CHG-018 종합
- AUD-024 최종 종합

---

## 7. Rule 실행방식

### Rule
결정적 조건으로 판정 가능한 검사.
예: 존재/누락, 정형 값 비교, 산식 재계산, ID 중복.

### AI
문맥·의미·영향 판단이 필요한 검사.
예: 상충 후보, 의미 중복, 영향범위 후보, 종합 위험 후보.

### Hybrid
Rule 기반 구조적 사전분석 + AI 의미판단 조합.
명확한 후보가 없으면 불필요한 AI 호출을 최소화한다.

---

## 8. P1 확장 설계 — 완료

Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개 전체 구현·활성·통합·전체 회귀 완료.
실행 Rule 33개 시점 Freeze 완료.

주요 역할분리/오탐방지:
- AUD-001은 실제 제출 파일 존재, AUD-008은 계획표상 작성/제출 상태
- REQ-012는 시험자료 미업로드 자체를 누락 확정으로 보지 않음
- AUD-018은 계획/수행근거 한쪽만 있을 때 미수행 확정 금지
- FP-002는 동일·유사 기능명 + 동일 FP유형을 후보화하되 합계/소계/요약행 제외

---

## 9. P2 확장 설계 — 완료

Canonical:
- `P2_IMPLEMENTATION_PLAN.md`

P2 23개 전체 구현·활성·통합·전체 회귀 완료.
최종 실행 Rule 56개 Freeze 완료.

### P2-C 핵심
- CHG-008/010/FP-011은 변경자료와 대응문서가 함께 있을 때만 후보 생성
- CHG-010은 데이터/테이블/컬럼 영향이 명시된 변경에 한정
- FP-006은 구조형 FP 후보만 AI에 전달
- 완전 동일 기능명 중복은 FP-002 영역

### P2-D 핵심
- AI/LLM/RAG 맥락이 확인된 문서에만 적용
- 단순 `모델` 단어는 AI 문서 신호로 사용하지 않음
- AI-015는 RAG/검색증강 구조가 명시된 경우만 적용
- AI-021은 단순 애플리케이션 로그만으로 AI 추적성 충족 판정 금지
- Hybrid 5개는 구조적 근거 후보가 없으면 AI 호출하지 않음

---

## 10. Rule과 Issue 분리

Rule:
- 무엇을 검사할지 정의
- 검사방식 정의
- 카테고리 정의
- 활성/비활성 관리

Issue:
- 실제 검사 결과
- 발견 내용과 근거
- Impact / Likelihood / Severity
- 필요 시 감리 개선판정

Rule 자체에 고정 최종 Severity를 적용하지 않는다.

---

## 11. Issue Assessment / Severity

AI 반환:
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

허용값:
- Low / Medium / High

최종 Severity는 deterministic Matrix로 계산한다.

| Impact \ Likelihood | Low | Medium | High |
|---|---|---|---|
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

Critical은 Impact=High && Likelihood=High일 때만 가능하다.

---

## 12. Local AI

기본 모델:
- Qwen3-4B Q4_K_M

Runtime:
- llama.cpp b11312

검증 설정:
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

잘못된 JSON / 허용되지 않은 값 / 빈 근거는 정상 판정으로 저장하지 않는다.

최종 배포검증에서 Portable과 MSI 설치본 모두 실제 모델 로딩과 Local AI 응답을 확인했다.

---

## 13. 감리 개선판정

Severity와 독립 관리한다.

- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -

모든 Issue에 강제하지 않는다.
CHG-001은 감리 개선판정 비적용(NULL) 정책을 유지한다.

---

## 14. REQ-001 구조 오탐 처리

최종 기준:
- 요구사항 정의 문서 범위 중심 검사
- 목차/참조/ID 단독 반복 제외
- 실제 요구사항 정의문장 식별
- 동일 실질 문장 dedup
- 서로 다른 실제 정의문장이 같은 ID를 사용할 때만 중복 후보

실제 HWP 2건 재검증 결과 REQ-001 Issue 0.

---

## 15. 변경영향도 연계구조

`CHG-001 변경 식별`
→ `CHG-006 영향대상 식별`
→ `CHG-008 설계 반영`
→ `CHG-010 데이터설계 반영`
→ `CHG-012 시험 반영`
→ `CHG-018 종합 위험 후보`

구체적 unresolved evidence가 있을 때만 Issue를 만든다.

---

## 16. Inspection Runtime

정상:
`파일/Rule 선택 → 예상시간 → 검사 → 진행률/남은시간 → 정상 완료 → DB 저장`

취소:
`취소 요청 → cancel flag → Local AI runtime 종료 → 검사 중단 → DB 미저장 → 입력상태 유지`

원칙:
- 정상 완료 검사만 DB 저장
- 취소 검사 저장 금지
- UI thread block 금지
- 취소 후 프로젝트/파일/Rule 선택 유지

---

## 17. Score / Grade

- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

F는 사용하지 않는다.

---

## 18. Export

지원:
- DOCX / XLSX / TXT

제외:
- HWPX

---

## 19. Administration 데이터 관리

관계:
`Project → Inspection → Issue`

전체 검사이력 정리:
- Issues → Inspections 삭제
- Project 유지

Project 삭제:
- Issues → Inspections → Project

Repository에서 명시적 transaction/rollback으로 처리하며 Stage 6에서 새 `ON DELETE CASCADE`를 강제하지 않는다.

---

## 20. 감리결과서 기반 Rule 실무검증

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`

분석대상:
- 감리 관련 파일 114개
- PDF 94 / DOCX 19 / XLSX 1
- Full Catalog 105 전체 매핑

원래 미구현 85개 우선순위:
- P1 13 — 완료
- P2 23 — 완료
- P3 21 — 미구현
- P4 28 — 미구현

신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Full Catalog 105에 추가하지 않는다.

---

## 21. 최종 배포 상태

Portable:
- `dist/AI_Auditor_Portable.zip`
- ZIP 약 2.35 GB
- SHA256 `A53BB20BD7CA531EB27F67C6D60371DF5C6E4BDC68410688A4F331B80A054672`
- EXE / DB / llama.cpp / Qwen3-4B / Local AI 응답 스모크 PASS

MSI:
- `installer/output/`
- `AI_Auditor_Setup.msi` + external CAB + 모델 + `AI_Auditor_Install.cmd`
- 실제 설치 / EXE / DB / 모델 로딩 / Local AI 응답 PASS
- 설치 Launcher 오류코드 처리 보완 후 최종 재빌드·동작 확인 PASS

---

## 22. 현재 완료 상태

현재 소스 Freeze:
- Full Catalog 105
- 실제 실행 Registry 56
- P1 13/13 완료
- P2 23/23 완료

현재 배포 상태:
- **56개 Freeze Portable 최종 검증 완료**
- **56개 Freeze MSI 최종 검증 완료**

핵심 개발 및 P2 확장, 최종 배포검증은 완료 상태다.
