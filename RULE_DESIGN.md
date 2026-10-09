# AI Auditor 검사기준 설계서

## 1. 문서 목적
AI Auditor의 최종 검사기준 체계, MVP 실행 범위, 검사결과 판정구조, 데이터 관리 원칙을 기록한다.
과거 상세 설계 이력은 Git history에 보존되며, 본 문서는 현재 구현과 일치하는 최신 기준이다.

---

## 2. 최종 5대 검사영역 / 105개

| 영역 | ID | 수량 |
|---|---|---:|
| 감리 사전점검 | AUD | 24 |
| 요구사항 정합성 | REQ | 28 |
| 변경영향도 | CHG | 18 |
| FP 검증 | FP | 12 |
| AI 특화 검증 | AI | 23 |
| **합계** |  | **105** |

105개 Full Catalog는 제품 전체 검사체계이다.
해커톤 MVP에서 실제 실행되는 Rule 전체 수와 동일하지 않다.

---

## 3. MVP 실행 Rule 20개

### 감리 사전점검 4개
- AUD-001
- AUD-002
- AUD-007
- AUD-024

### 요구사항 정합성 6개
- REQ-001
- REQ-002
- REQ-003
- REQ-004
- REQ-009
- REQ-018

### 변경영향도 4개
- CHG-001
- CHG-006
- CHG-012
- CHG-018

### FP 검증 2개
- FP-005
- FP-009

### AI 특화 검증 4개
- AI-005
- AI-009
- AI-019
- AI-022

실행방식:
- Rule: 3
- AI: 6
- Hybrid: 11

---

## 4. 문서 Parser 설계

지원 형식:
- DOCX
- DOC
- XLSX
- XLS
- PDF
- PPTX
- PPT
- HWPX
- HWP

모든 문서는 형식별 Parser를 거쳐 공통 구조로 변환한다.

`원본 문서 → Parser → ParsedDocument / DocumentBlock`

검사 Engine은 원본 형식에 직접 의존하지 않고 표준화 데이터 구조를 사용한다.

현재 제외:
- 스캔 이미지 기반 PDF OCR

---

## 5. 문서 검사 실행구조

`Inspection`
→ `Full Catalog 105 선택상태`
→ `MVP 20 선택 추출`
→ `Parser / ParsedDocument`
→ `Rule / AI / Hybrid 라우팅`
→ `DocumentInspectionEngine`
→ `Issue 생성`
→ `Issue Assessment`
→ `DB 저장`
→ `Project Detail / Reports`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않는다.

---

## 6. Rule 실행방식

### Rule
결정적 조건으로 판정 가능한 검사.

예:
- 존재/누락
- 정형 값 비교
- 산식 재계산
- ID 중복

### AI
문맥·의미·영향 판단이 필요한 검사.

예:
- 상충 후보
- 의미 중복
- 영향범위 후보
- 종합 위험 후보

### Hybrid
Rule 기반 사전분석 + AI 의미판단 조합.

---

## 7. Rule과 Issue 분리

Rule:
- 무엇을 검사할지 정의
- 검사방식 정의
- 카테고리 정의
- 활성/비활성 관리

Issue:
- 실제 검사 결과로 발견된 문제
- 발견 내용과 근거 저장
- Impact / Likelihood / Severity 저장
- 필요한 경우 감리 개선판정 저장

Rule 자체에 고정 Severity를 사용하지 않는다.

---

## 8. Issue Assessment

AI가 반환하는 값:
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

Impact / Likelihood 허용값:
- Low
- Medium
- High

최종 Severity는 AI 출력이 아니라 deterministic Matrix로 계산한다.

---

## 9. Severity Matrix

| Impact \ Likelihood | Low | Medium | High |
|---|---|---|---|
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

Critical:
- Impact = High
- Likelihood = High

두 조건이 모두 만족될 때만 산정한다.

---

## 10. Local AI

현재 기본 모델:
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

출력계약:

```json
{
  "impact": "Low|Medium|High",
  "likelihood": "Low|Medium|High",
  "impact_reason": "한국어 판정근거",
  "likelihood_reason": "한국어 판정근거"
}
```

잘못된 JSON / 허용되지 않은 값 / 빈 근거는 정상 판정으로 저장하지 않는다.

---

## 11. 감리 개선판정

Severity와 독립적으로 관리한다.

- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -

모든 Issue에 강제하지 않는다.
CHG-001은 감리 개선판정 비적용(NULL) 정책이다.

---

## 12. REQ-001 구조 오탐 처리

실제 HWP 요구사항 문서에서 목차·참조·반복 구조 때문에 동일 ID가 여러 번 등장하는 문제를 확인했다.

최종 처리기준:
- 요구사항 정의 문서 범위 중심 검사
- 목차/참조/ID 단독 반복 제외
- 실제 요구사항 정의문장 식별
- 동일 실질 문장 dedup
- 서로 다른 실제 요구사항 정의문장이 동일 ID를 사용하는 경우만 중복 후보

실제 HWP 2건 재검증 결과 REQ-001 Issue 0.

---

## 13. 변경영향도 연계구조

MVP 변경영향도 흐름:

`CHG-001 변경 식별`
→ `CHG-006 영향대상 식별`
→ `CHG-012 시험 변경 미반영`
→ `CHG-018 종합 위험 후보`

CHG-012:
- 구체적 unresolved evidence가 있을 때만 Issue 생성
- 최종 실문서 검증 0 Issue PASS

CHG-018:
- 위반 없음 / 근거 없음 결과를 Issue로 저장하지 않음
- unresolved evidence gate 적용
- 최종 실문서 검증 0 Issue PASS

---

## 14. Inspection 실행 Runtime

정상 흐름:
`파일/Rule 선택 → 예상시간 계산 → 검사 실행 → Rule/진행률/남은시간 표시 → 정상 완료 → DB 저장`

취소 흐름:
`취소 요청 → cancel flag → Local AI runtime 비동기 종료 → 검사 중단 → DB 미저장 → 입력상태 유지`

원칙:
- 정상 완료 검사만 DB 저장
- 취소된 검사 저장 금지
- UI thread block 금지
- 취소 후 프로젝트/파일/Rule 선택 유지

---

## 15. Score / Grade

최종 Grade:
- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

F는 사용하지 않는다.

---

## 16. Export

지원:
- DOCX
- XLSX
- TXT

제외:
- HWPX

HWPX는 직접 생성 파일 손상 및 COM Type Library 문제로 MVP 제외한다.

---

# 17. Administration 데이터 관리 설계 — Stage 6

## 17.1 목적
사용자가 검사결과와 프로젝트 데이터를 안전하게 정리할 수 있도록 한다.

Administration 구성:
1. 검사 기준 관리
2. 환경 설정
3. 데이터 관리

---

## 17.2 데이터 관계

기본 관계:

`Project → Inspection → Issue`

DB FK는 기존 구조를 유지하며 Stage 6에서 `ON DELETE CASCADE`를 새로 강제하지 않는다.
삭제는 Repository에서 명시적으로 수행한다.

---

## 17.3 전체 검사 이력 정리

삭제 대상:
- 모든 Issue
- 모든 Inspection

유지 대상:
- Project

삭제순서:
`Issues → Inspections`

사용자 표시:
- 프로젝트 정보: N개 (유지)
- 검사 이력: N건 (삭제)
- 이슈: N건 (삭제)

삭제는 하나의 transaction으로 처리하며 실패 시 rollback한다.

---

## 17.4 프로젝트 삭제

선택한 Project 삭제 시 함께 삭제:
- 해당 Project의 Issues
- 해당 Project의 Inspections
- 해당 Project

삭제순서:
`Issues → Inspections → Project`

다른 Project의 데이터는 보존해야 한다.

---

## 17.5 Repository API

`app/database/repositories/data_management_repository.py`

주요 함수:
- `get_data_management_summary()`
- `get_projects_with_delete_impact()`
- `get_project_delete_impact(project_id)`
- `delete_all_inspection_history()`
- `delete_project_with_history(project_id)`

---

## 17.6 UI

`ui/administration_page.py`
- 데이터 관리 카드
- 전체 데이터 요약
- 전체 검사 이력 정리 진입
- 프로젝트 관리 진입

`ui/data_management_dialogs.py`
- `DeleteConfirmDialog`
- `ProjectManagementDialog`

---

## 17.7 Danger Action 계층

진입과 최종 실행의 위험 수준을 시각적으로 구분한다.

- Administration `정리`: 낮은 강조 Danger
- Administration `관리`: 기본 버튼
- Project 목록 `삭제`: Outline Danger
- 최종 실행 `정리 실행 / 프로젝트 삭제`: Filled Danger

최종 비가역 실행 단계가 가장 강한 강조를 가진다.

---

## 17.8 프로젝트 관리 목록 UI

표시정보:
- 프로젝트명
- 부서
- 검사 이력 수
- 이슈 수

설계원칙:
- 프로젝트명과 메타정보는 충분한 시인성 확보
- 불필요하게 큰 카드 높이는 사용하지 않음
- 카드 간격은 리스트 밀도를 해치지 않는 수준으로 유지
- Dark / Light 모두 삭제 버튼 식별 가능

---

## 17.9 실제 삭제 검증

Project 삭제 검증:
- 임시 Project / Inspection / Issue 생성
- UI 삭제 실행
- Project 삭제 확인
- 연결 Inspection 삭제 확인
- 연결 Issue 삭제 확인
- orphan Inspection 0
- orphan Issue 0

전체 검사 이력 정리 검증:
- DB 백업
- 실제 전체 정리 실행
- Project 수 유지 확인
- Inspection 0
- Issue 0
- 원본 DB 복원

---

## 17.10 자동테스트

`tests/test_data_management_repository.py`

검증:
- summary count
- project impact list
- clear history preserves projects
- project delete impact
- selected project tree delete
- missing project safe handling

결과:
- 6 passed

최신 전체 회귀:
- `python -m pytest -q`
- 실패 0건

---

## 18. 완료 상태

1~6단계는 완료 상태로 유지한다.
최종 EXE 안정화도 완료 상태이다.
새 결함이 없는 한 기존 완료영역을 다시 재설계하지 않는다.

---

## 19. 감리결과서 기반 Rule 실무검증 설계 기준 — 2026-10-09

감리결과서 분석 결과의 Canonical 기준은 `AUDIT_EVIDENCE_MAPPING.md`로 관리한다.

분석대상:
- 감리 관련 파일 114개
- 105개 Full Catalog 전체와 매핑
- MVP 20개만을 대상으로 하지 않음

분석방법:
1. 파일/버전/중복 식별
2. 개선권고·지적사항 추출
3. 유사 지적 통합 및 중복 제거
4. 일반화된 지적유형 도출
5. 105개 기존 Rule 매핑
6. 요약 지적표 재검증
7. 상세본문 재검증
8. FP / AI-RAG / 보안 / 데이터 / UI-UX 전문분야·별첨 교차검증

미구현 85개 구현 기본 우선순위:
- P1 13개
- P2 23개
- P3 21개
- P4 28개

P1:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

근거등급:
- 강함: 다수 보고서/연도 반복 또는 전문점검에서 반복 직접 확인
- 보통: 복수 직접 사례 또는 최근 전문점검 중요 직접 근거
- 제한: 직접 사례는 있으나 빈도·범위 제한
- 간접: 하위 결과를 종합하는 메타 Rule
- 미확인: 현재 114개 자료에서 직접 1:1 감리지적 근거 미확인

`미확인`은 Rule 삭제나 무효화를 뜻하지 않는다. 예방/전략 Rule로 유지한다.

105개 밖 반복·중요 지적유형은 신규 Rule 후보로만 관리한다.
사용자 승인 전 `document_rule_catalog.py`에 추가하지 않는다.

현재 후보:
- NEW-PM-01 프로젝트 진척·지연 및 만회계획 점검
- NEW-PM-02 위험·이슈·Action Item 사후관리 점검
- NEW-DATA-01 데이터 모델·물리DB 구조·무결성 적정성 점검
- NEW-DATA-02 데이터 품질진단·이관·전환 정합성 점검
- NEW-ARCH-01 아키텍처·인프라 구성 및 자원 적정성 점검
- NEW-PERF-01 성능·용량·부하·튜닝 적정성 점검
- NEW-SEC-01 일반 보안취약점·개발보안 진단 및 조치 점검
- NEW-UX-01 UI/UX 사용성·편의성 적정성 점검
- NEW-OPS-01 운영절차·백업복구·서비스관리 준비도 점검
- NEW-REL-01 교육·인수인계·시스템전환·하자보수 준비도 점검 — 조건부 통합 검토

기존 105에 흡수하는 대표 유형:
- 웹접근성·웹표준·가이드 준수 → AUD-023
- 인터페이스 정의 누락/문서 불일치 → AUD-020/AUD-021
- 변경 후 설계/화면/데이터/시험/문서 미현행화 → CHG-008~013
- 단순 산출물 미작성/시기미도래 → AUD-001/AUD-008/AUD-022

재사용 원칙:
- 향후 85개 구현 시 114개 감리자료를 처음부터 다시 분석하지 않는다.
- `AUDIT_EVIDENCE_MAPPING.md`의 P1 → P2 → P3 → P4를 기본 우선순위로 사용한다.
- 새 감리자료만 기존 분석에 증분 반영한다.

---

## 20. MVP20 감리사례 실증검증 설계 기준 — 2026-10-09

Canonical 기준:
- `MVP20_AUDIT_VALIDATION.md`

실증검증 결과 실제 감리사례보다 탐지범위가 좁아 즉시 보완한 5개:
- AUD-001
- REQ-002
- REQ-003
- REQ-009
- FP-009

### AUD-001

설계 기준:
`산출물목록 → 테일러링 적용/제외 확인 → 현재 제출대상 확정 → 실제 업로드 파일과 비교`

- 산출물목록을 우선 기준으로 사용한다.
- 테일러링 `미적용/제외`는 현재 제출대상에서 제외한다.
- `시기미도래/해당없음`은 누락으로 판정하지 않는다.
- 산출물목록이 없고 테일러링만 있는 경우 명시적 적용항목만 사용한다.
- 기준자료가 없으면 표준 산출물목록을 임의 생성하지 않는다.
- UI Freeze를 변경하지 않고 업로드된 기준문서 자체에서 자동 도출한다.

구현:
- `rules/core/deliverable_baseline.py`
- `rules/core/document_engine.py`

### REQ-002

- 완전 동일문구만 비교하지 않는다.
- 요구사항명/의미가 유사한 후보를 AI 비교단계로 넘긴다.
- 무관한 요구사항끼리는 후보쌍으로 만들지 않는다.

### REQ-003

- `적절히/필요시` 같은 직접 모호표현뿐 아니라 정량목표·횟수·조건·범위의 값 누락을 후보화한다.
- `협의 후 확정`과 같은 미확정 표현을 포함한다.
- 명시적 수치/단위가 있는 정상 문장은 오탐하지 않는다.

### REQ-009

개별 문서 Hybrid Loop가 아니라 복수 산출물 교차검증 경로를 사용한다.

`요구사항정의/기술/추적 → 요구사항 ID/내용 추출 → 화면/인터페이스/테이블/데이터/프로그램/아키텍처 등 설계근거 연결 → AI 정합성 판단`

- 요구사항 ID 직접 연결을 최우선으로 한다.
- ID가 없으면 충분한 핵심어가 겹치는 경우만 후보화한다.
- 연결근거가 전혀 없다는 사실만으로 REQ-009 미반영을 단정하지 않는다.
- Local AI 입력은 제한된 배치로 구성한다.

구현:
- `rules/core/requirement_design_alignment.py`
- `app/services/inspection_service.py`

### FP-009

- 기존 텍스트 한 줄 산식 검사를 유지한다.
- XLS/XLSX 구조형 FP 행을 추가 검증한다.
- 기능유형: ILF / EIF / EI / EO / EQ
- 명시 복잡도가 있으면 표준 가중치로 계산한다.
- 복잡도가 없으면 RET/FTR + DET가 모두 있을 때 표준 복잡도 행렬로 계산한다.
- 기능개수 열이 있으면 `기능개수 × 가중치`를 적용한다.
- 계산 근거가 충분하지 않으면 추정하지 않는다.

구현:
- `rules/core/fp_calculator.py`
- `rules/core/document_engine.py`

### 검증 정책

각 보완은 실제 감리사례 형태의 회귀 fixture를 추가한 뒤 targeted regression을 수행한다.
최종적으로 전체 `python -m pytest -q`를 수행하며, 2026-10-09 사용자 PC에서 실패 0건을 확인했다.

남은 부분적합/실무사례 제한 Rule은 해커톤 제출 차단 결함이 아니라 후속 정밀확장 대상으로 관리한다.
