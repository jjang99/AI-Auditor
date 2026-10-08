# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발의 **현재 최종 확정 기준(Canonical Decisions)** 을 기록한다.
과거 세부 변경 이력은 Git history에서 확인하며, 본 문서와 충돌하는 과거 문구는 본 문서의 최신 기준으로 대체한다.

---

# 1. 개발 진행 원칙

- 상태를 추측하지 않는다.
- 새 작업 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → 실제 코드 → 이전 대화/저장된 결정사항` 순으로 확인한다.
- 이미 완료된 1~6단계를 새 결함 없이 다시 구현하거나 재설계하지 않는다.
- 기존 코드와 실제 동작을 확인한 뒤 수정한다.
- UI Freeze 이후 구조·크기·배치·간격·색상·폰트·버튼 형태를 임의 변경하지 않는다.
- UI 변경은 명시적 결함 또는 현재 기능 구현에 필요한 최소 범위로 제한한다.
- 기능 단위 구현 → targeted test → 전체 회귀 테스트 → 문서 현행화 순서를 유지한다.
- 개발 마감 시 `DEV_STATUS.md`, `DECISIONS.md`, `RULE_DESIGN.md`, `CURRENT_HANDOFF.md`를 최신화한다.

## 작업 전 필수 다중 교차검증 원칙

- 어떤 작업이든 시작 전에 GitHub 실제 코드, 프로젝트 구조, `CURRENT_HANDOFF.md`, `DECISIONS.md`, `RULE_DESIGN.md`, `DEV_STATUS.md`, 기존 테스트 결과, 이전 대화 및 저장된 결정사항을 먼저 확인한다.
- 한 번 확인한 내용만 믿고 바로 작업하지 않는다. 동일 상태를 최소 2~3회, 서로 다른 관점에서 재확인한다.
- `코드 ↔ 문서 ↔ 테스트 결과 ↔ 이전 대화/결정사항`이 서로 일치하는지 교차검증한 뒤 작업을 시작한다.
- 내용이 충돌하면 최신 GitHub 실제 코드와 실제 동작을 우선 기준으로 삼되, 기존 확정 결정사항과 충돌하는지 다시 확인한다.
- 충분히 검증되지 않은 상태에서는 추측으로 수정하거나 이미 완료된 기능을 다시 만들지 않는다.
- 검증이 끝난 뒤 현재 구조를 가장 적게 흔들면서도 안전하고 효율적인 방안을 선택한다.
- 사용자가 개발자가 아니므로, 가능한 작업은 먼저 GitHub 코드와 자료를 직접 확인·수정하고, 사용자에게는 실제로 필요한 로컬 명령과 확인사항만 단계별로 안내한다.

---

# 2. 전체 UI 공통 기준

- 기본 화면은 기존 Home 기준 창 크기를 유지한다.
- Dark / Light Mode를 제공하며 기본은 Dark Mode이다.
- 공통 메뉴: Home / Projects / Inspection / Reports / Administration
- 클릭 가능한 카드·행·버튼만 Hover 피드백을 적용한다.
- 카드 외곽선/내부 정보영역 표현은 Administration에서 확정한 기준을 유지한다.
- 텍스트 가독성 및 정보 위계는 Reports에서 확정한 수준을 유지한다.
- Light Mode는 Soft Light 계열의 옅은 블루그레이 배경 + 흰 카드 톤을 유지한다.

---

# 3. 최종 검사체계

AI Auditor의 제품 전체 검사체계는 5대 영역 / 총 105개 Rule이다.

- 감리 사전점검(AUD): 24개
- 요구사항 정합성(REQ): 28개
- 변경영향도(CHG): 18개
- FP 검증(FP): 12개
- AI 특화 검증(AI): 23개

해커톤 MVP 실제 실행 대상은 20개이다.

- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4

MVP 20개 실행방식:
- Rule 3
- AI 6
- Hybrid 11

Full Catalog 105개와 MVP 실제 실행 20개는 서로 다른 개념으로 관리한다.

---

# 4. Rule / Issue / Severity 역할 분리

- Rule = 무엇을 어떤 방식으로 검사할 것인가
- Issue = 실제 검사에서 무엇이 발견되었는가
- Severity = 발견된 Issue가 얼마나 위험한가
- 감리 개선판정 = 감리 대응 관점에서 어떻게 개선할 것인가

Rule 자체에 고정 Severity를 사용하지 않는다.
Administration의 Rule 정보는 `Code / 규칙 제목 / 설명 / 검사방식 / 상태`를 기준으로 한다.
검사방식은 Rule / AI / Hybrid이다.

---

# 5. Severity 최종 기준

Severity는 실제 Issue의 Impact와 Likelihood로 계산한다.

`Impact × Likelihood → Severity`

Impact / Likelihood:
- Low
- Medium
- High

Severity:
- Low
- Medium
- High
- Critical

Matrix:

| Impact \ Likelihood | Low | Medium | High |
|---|---|---|---|
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

Critical은 원칙적으로 `Impact=High AND Likelihood=High`에서만 산정한다.
AI가 최종 Severity를 직접 결정하지 않는다.

---

# 6. Local AI 최종 기준

현재 기본 Local AI:
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행 기준 검증

생성 설정:
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 출력 역할:
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

AI 출력은 JSON 계약과 허용값을 검증한다.
잘못된 JSON / 필수 필드 누락 / 허용되지 않은 값은 정상 판정으로 저장하지 않는다.

`models/`, `runtime/`은 대용량 실행자산으로 Git 소스관리 대상에서 제외한다.
프로그램이 인터넷에서 모델을 자동 다운로드하지 않는다.

---

# 7. 감리 개선판정

Severity와 별도 관리한다.

- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -

모든 Issue에 강제로 부여하지 않는다.
CHG-001은 변경사항 식별 근거 데이터 역할이므로 감리 개선판정 비적용(NULL)으로 한다.
별도 `audit_reason` 필드는 현재 MVP 확정범위에 추가하지 않는다.

---

# 8. 문서 Parser 최종 지원범위

지원 형식 9종:
- DOCX
- DOC
- XLSX
- XLS
- PDF
- PPTX
- PPT
- HWPX
- HWP

모든 Parser는 원본 형식을 공통 `ParsedDocument / DocumentBlock` 구조로 표준화한다.
스캔 이미지 기반 PDF OCR은 현재 MVP에서 제외한다.

---

# 9. 실제 검사 실행 흐름

`Inspection`
→ `Full Catalog 105 선택상태`
→ `MVP 20 선택 추출`
→ `Parser / ParsedDocument`
→ `Rule / AI / Hybrid`
→ `DocumentInspectionEngine`
→ `Issue 생성`
→ `Impact / Likelihood 평가`
→ `Severity Matrix`
→ `필요 시 감리 개선판정`
→ `DB 저장`
→ `Project Detail / Reports`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않고 향후 확장영역으로 보존한다.

---

# 10. Inspection 실행 UX 최종 정책

- 검사 전 예상 검사시간을 표시한다.
- 검사 진행 중 현재 Rule/단계, 완료 Rule 수, Progress Bar, 예상 남은시간을 표시한다.
- Local AI 실행 중 취소를 지원한다.
- 취소는 UI thread를 차단하지 않는다.
- 취소 시 프로젝트명 / 등록 파일 / 검사기준 선택상태를 유지한다.
- 취소된 검사는 DB에 저장하지 않는다.
- 취소 후 다시 검사할 수 있다.

위 Inspection 동작은 사용자 화면 검증 완료 상태로 고정한다.

---

# 11. Score / Grade

Grade는 A / B / C / D / E만 사용한다.

- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

과거 F 표기는 사용하지 않는다.

---

# 12. Export Report

MVP 지원 형식:
- DOCX
- XLSX
- TXT

HWPX는 MVP에서 제외한다.
사유:
- 직접 생성 HWPX가 한/글에서 손상 파일로 확인됨
- pyhwpx 사용 시 사용자 환경의 한글 COM Type Library 미등록 문제 확인
- HWPX 하나를 위해 COM 등록을 제품 필수조건으로 만들지 않음

HWPX를 다시 임의 복원하거나 재실험하지 않는다.

---

# 13. Project Detail 최종 UI

- Issue 행은 Header(Severity / Rule ID / 상태) + Body(실제 Issue 내용) 구조를 사용한다.
- 긴 Issue 내용은 전체 폭을 사용하고 높이를 자동 확장한다.
- Issue 정렬 UI는 기존 QComboBox 방식을 유지한다.
- 감리 개선판정 결과 배지의 확정 색상 규칙을 유지한다.
- `판정 없음`은 Dark / Light 테마별 중립 표현을 사용한다.
- 새로운 명시적 결함이 없는 한 다시 재설계하지 않는다.

---

# 14. Administration 최종 구성

Administration은 다음 3개 섹션으로 구성한다.

1. 검사 기준 관리
2. 환경 설정
3. 데이터 관리

환경 설정:
- 로컬 AI 모델 선택 구조
- 로그 저장

과거 `결과 저장 경로`, `검사 결과 자동 저장`은 사용하지 않는다.
보고서 파일 저장은 Export 기능으로 일원화한다.

---

# 15. 데이터 관리 최종 정책 — 2026-10-08

## 전체 검사 이력 정리
- 모든 Inspection 삭제
- 모든 Issue 삭제
- Project 정보 유지
- 실행 전 영향범위 표시
- 복구 불가 경고 Modal 표시

표시 문구는 `프로젝트 정보: N개 (유지)`를 사용한다.

## 프로젝트 관리
- Project 목록을 표시한다.
- 프로젝트명 / 부서 / 검사 이력 수 / 이슈 수를 표시한다.
- 선택 Project 삭제 시 해당 Project의 Inspection / Issue를 함께 삭제한다.
- 실행 전 영향범위와 복구 불가 경고를 표시한다.

## 삭제 순서
DB FK에 CASCADE를 새로 강제하지 않고 Repository에서 명시적으로 처리한다.

Project 삭제:
`Issues → Inspections → Project`

전체 검사 이력 정리:
`Issues → Inspections`

삭제는 transaction으로 처리하고 오류 시 rollback한다.

---

# 16. 데이터 관리 Danger UI 계층

모든 관련 버튼을 같은 빨강으로 채우지 않는다.

- Administration `정리`: 위험 작업 진입을 알리는 낮은 강조 Danger
- Administration `관리`: 관리 화면 진입이므로 기본 버튼
- 프로젝트 목록 `삭제`: 빨간 테두리 Danger
- 최종 확인 Modal의 `정리 실행 / 프로젝트 삭제`: Filled Danger

즉 실제 비가역 삭제를 실행하는 최종 단계가 가장 강한 시각 강조를 가진다.

---

# 17. 데이터 관리 실제 검증 완료

실제 DB에서 검증하였다.

프로젝트 삭제:
- 테스트 Project 삭제
- 연결 Inspection 삭제
- 연결 Issue 삭제
- orphan Inspection 0
- orphan Issue 0

전체 검사 이력 정리:
- 실제 DB 백업 후 실행
- Project 수 유지
- Inspection 0
- Issue 0
- 검증 후 원본 DB 복원 완료

전용 자동테스트:
- `tests/test_data_management_repository.py`
- 6 passed

최신 전체 회귀테스트:
- `python -m pytest -q`
- 사용자 PC에서 실패 0건 확인

---

# 18. 최종 실제 검사 기준점

Project: `tawga`
- Inspection ID: 40
- Score: 95
- Grade: A
- Issues: 7
- Critical 0 / High 0 / Medium 4 / Low 3

REQ-001 구조 오탐 수정 이후 결과이며, 새로운 명시적 결함이 없으면 재검사하지 않는다.

---

# 19. 현재 완료 범위

1단계부터 6단계까지 완료 상태로 확정한다.

- 1단계 Rule 복원·재분류
- 2단계 5대 영역 / 105개 확정
- 3단계 MVP 20개 확정
- 4단계 MVP 검사 Engine
- 5단계 제품 통합 / Local AI / Severity / 감리판정
- Inspection 실행 UX 보완
- 6단계 Administration 데이터 관리

새 결함이 없는 한 위 완료 범위를 다시 뜯지 않는다.

---

# 20. 다음 단계

최종 EXE 안정화는 완료되었다.
다음은 감리결과서 기반 실무 검증이다.

- 감리결과서 지적사항 추출
- 유사 지적 통합 / 중복 제거 / 일반화
- Full Rule Catalog 105개 전체와 매핑
- MVP 20개 / 미구현 85개 / 신규 Rule 후보로 분류
- 실제 감리 사례로 현재 MVP 20개 검증
- 해커톤 최종 문서화·제출
- 제출 후 85개 Rule을 감리 매핑 결과의 우선순위에 따라 순차 구현

감리결과서는 MVP 20개만을 위한 자료가 아니다.
한 번 분석한 결과를 105개 전체 검증과 향후 85개 구현에 재사용하며, 나중에 처음부터 다시 분석하지 않는다.
