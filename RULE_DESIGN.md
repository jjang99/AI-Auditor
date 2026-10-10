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

## 4. 현재 실제 실행 Rule — 29개

중앙 Registry:
- `rules/definitions/document_rule_registry.py`

현재 실제 실행 가능 Rule:
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

Registry 원칙:
- Full Catalog와 실행 Registry를 분리한다.
- 실제 Handler와 targeted regression을 통과한 Rule만 활성화한다.
- Registry 미등록 Rule은 UI Full Catalog에 보여도 실제 검사에서는 실행하지 않는다.
- P1-D/P1-E는 검증 전 선등록하지 않는다.

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

## 6. 현재 문서 검사 실행구조

`Inspection`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 필터`
→ `Parser / ParsedDocument`
→ `Rule / AI / Hybrid 라우팅`
→ `문서별 사전분석`
→ `교차문서 후처리`
→ `Issue 생성`
→ `Issue Assessment`
→ `DB 저장`
→ `Project Detail / Reports`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않는다.

Rule 계층:
- `DocumentRuleEngine`
- `P1DocumentRuleEngine(DocumentRuleEngine)`

Hybrid 계층:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine(DocumentHybridEngine)`
- `P1AuditHybridEngine(P1RequirementHybridEngine)`

교차문서/후처리:
- REQ-009 요구사항 ↔ 설계
- REQ-012 요구사항 ↔ 시험
- AUD-018 품질활동 계획 ↔ 수행근거
- CHG-001 버전쌍 비교
- CHG-012 변경 ↔ 시험
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

## 8. P1 확장 설계

Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

현재:
- P1-A 4개 완료
- P1-B 3개 완료
- P1-C 2개 완료
- P1-D 3개 다음
- P1-E 1개 마지막

P1 전체 완료 목표:
- 33개 실행 Rule

### P1-A 역할 분리
- AUD-001: 실제 제출 파일 존재/누락
- AUD-008: 계획표상 현재 대상 산출물의 작성·제출 상태

### P1-B 오탐 방지
- REQ-007: 숫자 기준 부재만으로 검증불가 단정 금지
- REQ-012: 시험문서 미업로드만으로 누락 확정 금지
- REQ-017: N/A/별도시트 참조 인정, REQ-018과 역할 분리

### P1-C 오탐 방지
- AUD-010: 합계/구분/마일스톤 제외, 날짜 해석 불가 시 오류 확정 금지
- AUD-018: 계획/수행근거 한쪽만 업로드되면 미수행 확정 금지, 시기미도래 제외

---

## 9. Rule과 Issue 분리

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

## 10. Issue Assessment / Severity

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

## 11. Local AI

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

---

## 12. 감리 개선판정

Severity와 독립 관리한다.

- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -

모든 Issue에 강제하지 않는다.
CHG-001은 감리 개선판정 비적용(NULL) 정책을 유지한다.

---

## 13. REQ-001 구조 오탐 처리

최종 기준:
- 요구사항 정의 문서 범위 중심 검사
- 목차/참조/ID 단독 반복 제외
- 실제 요구사항 정의문장 식별
- 동일 실질 문장 dedup
- 서로 다른 실제 정의문장이 같은 ID를 사용할 때만 중복 후보

실제 HWP 2건 재검증 결과 REQ-001 Issue 0.

---

## 14. 변경영향도 연계구조

`CHG-001 변경 식별`
→ `CHG-006 영향대상 식별`
→ `CHG-012 시험 변경 미반영`
→ `CHG-018 종합 위험 후보`

CHG-012/CHG-018은 구체적 unresolved evidence가 있을 때만 Issue를 만든다.

---

## 15. Inspection Runtime

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

## 16. Score / Grade

- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

F는 사용하지 않는다.

---

## 17. Export

지원:
- DOCX / XLSX / TXT

제외:
- HWPX

---

## 18. Administration 데이터 관리

관계:
`Project → Inspection → Issue`

전체 검사이력 정리:
- Issues → Inspections 삭제
- Project 유지

Project 삭제:
- Issues → Inspections → Project

Repository에서 명시적 transaction/rollback으로 처리하며 Stage 6에서 새 `ON DELETE CASCADE`를 강제하지 않는다.

핵심 Repository API:
- `get_data_management_summary()`
- `get_projects_with_delete_impact()`
- `get_project_delete_impact(project_id)`
- `delete_all_inspection_history()`
- `delete_project_with_history(project_id)`

기존 실제 삭제검증과 자동테스트는 완료 상태로 유지한다.

---

## 19. 감리결과서 기반 Rule 실무검증

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`

분석대상:
- 감리 관련 파일 114개
- PDF 94 / DOCX 19 / XLSX 1
- 105개 Full Catalog 전체 매핑

미구현 85개 원래 우선순위:
- P1 13
- P2 23
- P3 21
- P4 28

감리자료는 각 Priority 구현 시 처음부터 재분석하지 않고 기존 매핑을 재사용한다.

신규 Rule 후보:
- NEW-PM-01 프로젝트 진척·지연 및 만회계획
- NEW-PM-02 위험·이슈·Action Item 사후관리
- NEW-DATA-01 데이터 모델·물리DB 구조·무결성
- NEW-DATA-02 데이터 품질진단·이관·전환 정합성
- NEW-ARCH-01 아키텍처·인프라 구성 및 자원 적정성
- NEW-PERF-01 성능·용량·부하·튜닝
- NEW-SEC-01 일반 보안취약점·개발보안
- NEW-UX-01 UI/UX 사용성·편의성
- NEW-OPS-01 운영절차·백업복구·서비스관리 준비도
- NEW-REL-01 교육·인수인계·전환·하자보수 준비도 — 조건부

사용자 승인 전 Full Catalog 105에 임의 추가하지 않는다.

---

## 20. 현재 완료 상태

1~6단계와 기존 배포 안정화는 완료 유지.
P1-A/B/C 9개도 완료 및 Registry 활성 상태.

현재 다음 구현:
- **P1-D AUD-020 → AUD-022 → AUD-023**

P1-D 완료 후:
- 실행 Rule 32개
- 남은 P1-E FP-002 1개

P1 전체 완료 후:
- 실행 Rule 33개
- 최신 소스로 ZIP/MSI 재빌드·스모크검증
- README / HACKATHON_SUBMISSION 최종 현행화
