# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발의 **현재 최종 확정 기준(Canonical Decisions)** 을 기록한다.
과거 세부 변경 이력은 Git history에서 확인하며, 본 문서와 충돌하는 과거 문구는 본 문서의 최신 기준으로 대체한다.

---

# 1. 개발 진행 원칙

- 상태를 추측하지 않는다.
- 새 작업 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드 및 installer 관련 파일 → 이전 대화/저장된 결정사항` 순으로 확인한다.
- 이미 완료된 1~6단계를 새 결함 없이 다시 구현하거나 재설계하지 않는다.
- 기존 코드와 실제 동작을 확인한 뒤 수정한다.
- UI Freeze 이후 구조·크기·배치·간격·색상·폰트·버튼 형태를 임의 변경하지 않는다.
- UI 변경은 명시적 결함 또는 현재 기능 구현에 필요한 최소 범위로 제한한다.
- 기능 단위 구현 → targeted test → 전체 회귀 테스트 → 문서 현행화 순서를 유지한다.
- 개발 마감 시 `DEV_STATUS.md`, `DECISIONS.md`, `RULE_DESIGN.md`, `CURRENT_HANDOFF.md`, `README.md`, `HACKATHON_SUBMISSION.md` 등 실제 변경과 관련된 문서를 최신화한다.

## 작업 전 필수 다중 교차검증 원칙

- 어떤 작업이든 시작 전에 GitHub 실제 코드, 프로젝트 구조, 핵심 문서, 기존 테스트 결과, 이전 대화 및 저장된 결정사항을 먼저 확인한다.
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
- 2026-09-18 확정 UI Freeze를 유지한다.

---

# 3. 최종 검사체계 및 현재 실행범위

제품 전체 검사체계:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23
- 합계 105

최초 MVP20 기준선:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

P1 13개는 2026-10-10 전체 구현·활성·회귀검증 완료했다.

현재 실제 실행 Registry:
- **33개 = MVP20 + P1 13개**
- Rule 7 / AI 6 / Hybrid 20

`MVP20`은 최초 기준선 명칭으로 유지한다.
Full Catalog 105와 실제 실행 Registry 수는 별도 개념이다.

---

# 4. Rule / Issue / Severity 역할 분리

- Rule = 무엇을 어떤 방식으로 검사할 것인가
- Issue = 실제 검사에서 무엇이 발견되었는가
- Severity = 발견된 Issue가 얼마나 위험한가
- 감리 개선판정 = 감리 대응 관점에서 어떻게 개선할 것인가

Rule 자체에 고정 최종 Severity를 적용하지 않는다.
검사방식은 Rule / AI / Hybrid이다.

---

# 5. Severity 최종 기준

`Impact × Likelihood → deterministic Severity Matrix`

Impact / Likelihood:
- Low / Medium / High

Severity:
- Low / Medium / High / Critical

Critical은 원칙적으로 `Impact=High AND Likelihood=High`에서만 산정한다.
AI가 최종 Severity를 직접 결정하지 않는다.

---

# 6. Local AI 최종 기준

- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 출력 역할:
- Impact / Impact Reason
- Likelihood / Likelihood Reason

잘못된 JSON / 필수 필드 누락 / 허용되지 않은 값은 정상 판정으로 저장하지 않는다.
`models/`, `runtime/`은 Git 소스관리 대상에서 제외하고 프로그램이 인터넷에서 자동 다운로드하지 않는다.

---

# 7. 감리 개선판정

Severity와 별도 관리한다.
- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -

모든 Issue에 강제로 부여하지 않는다.
CHG-001은 감리 개선판정 비적용(NULL) 정책을 유지한다.

---

# 8. 문서 Parser / Export

Parser 지원 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

제외:
- 스캔 이미지 PDF OCR
- HWPX Report Export

Export 지원:
- DOCX / XLSX / TXT

---

# 9. 실제 검사 실행 흐름

`Inspection`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 필터`
→ `Parser / ParsedDocument`
→ `Rule / AI / Hybrid`
→ `문서별 사전분석 / 교차문서 비교`
→ `Issue 생성`
→ `Impact / Likelihood 평가`
→ `Severity Matrix`
→ `필요 시 감리 개선판정`
→ `DB 저장`
→ `Project Detail / Reports`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않는다.

---

# 10. Inspection 실행 UX 최종 정책

- 검사 전 예상 검사시간 표시
- 검사 진행 중 현재 Rule/단계, 완료 Rule 수, Progress Bar, 예상 남은시간 표시
- Local AI 실행 중 취소 지원
- 취소 시 프로젝트명 / 등록 파일 / 검사기준 선택상태 유지
- 취소된 검사는 DB 미저장
- 취소 후 재검사 가능

---

# 11. Score / Grade

- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

F는 사용하지 않는다.

---

# 12. Administration 데이터 관리

삭제 정책:
- 전체 검사 이력 정리: Issues → Inspections, Project 유지
- Project 삭제: Issues → Inspections → Project
- Repository transaction 사용, 오류 시 rollback
- 새 ON DELETE CASCADE를 강제하지 않음

기존 실제 삭제검증과 자동테스트는 완료 상태로 유지한다.

---

# 13. 감리결과서 기반 실무검증 결정

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`

확정사항:
- 감리자료 114개 분석 결과를 재사용한다.
- Full Catalog 105를 감리 결과 때문에 임의 변경하지 않는다.
- 원래 미구현 85개 우선순위: P1 13 / P2 23 / P3 21 / P4 28
- P1 13개는 완료됐으므로 현재 확장 우선순위는 P2 → P3 → P4다.
- 새 감리자료는 전체 재분석 대신 증분 반영한다.
- 신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Catalog나 코드에 추가하지 않는다.

---

# 14. MVP20 / P1 확정

MVP20 실증검증 Canonical:
- `MVP20_AUDIT_VALIDATION.md`

실증 보완 완료:
- AUD-001 / REQ-002 / REQ-003 / REQ-009 / FP-009

P1 Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

P1 13개는 전용 테스트, Registry 33개 통합검증, 전체 `python -m pytest -q` 사용자 PC PASS 후 **33개 소스 Freeze**로 확정한다.

---

# 15. P2 구현 결정 — 2026-10-10

P2 Canonical:
- `P2_IMPLEMENTATION_PLAN.md`

P2 확정 대상은 `AUDIT_EVIDENCE_MAPPING.md`의 23개다.

구성:
- AUD 4 / REQ 6 / CHG 3 / FP 3 / AI 7
- Rule 7 / AI 5 / Hybrid 11

Batch:
- P2-A 7개: 구조형/결정형
- P2-B 6개: 감리·요구사항 의미/교차문서
- P2-C 4개: 변경영향·FP
- P2-D 6개: AI/RAG 품질·보안·운영

구현 원칙:
- P1 33개 Freeze를 기준선으로 보존한다.
- 각 Batch는 구현 → 전용 테스트 → Registry 활성 → 통합 회귀 → 전체 회귀 순서로 독립 완료한다.
- 미완성 Batch를 완료로 표기하지 않는다.
- P2 23개 완료 목표는 **56개 실행 Rule**이다.
- P2 완료 시 누적 실행방식은 Rule 14 / AI 11 / Hybrid 31이다.

---

# 16. 배포 패키징 결정

배포형태:
- ZIP(EXE)
- MSI 설치형

기존 검증 배포본:
- ZIP: `C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`
- MSI: `C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

기존 패키징 정책:
- PyInstaller onedir
- 개발 DB 미포함, 첫 실행 시 `data/ai_auditor.db` 자동생성
- MSI per-user 설치
- 설치 위치 `%LOCALAPPDATA%\Programs\AI Auditor`
- Qwen GGUF는 2GB 초과로 MSI File table에 직접 포함하지 않음
- `AI_Auditor_Install.cmd`가 MSI 설치 후 모델 복사/크기검증 수행
- MSIX는 현재 배포범위 제외

**2026-10-10 최신 결정:**
- P1 33개 상태에서 ZIP/MSI 재빌드는 하지 않는다.
- 기존 ZIP/MSI는 현재 소스보다 오래된 배포본이므로 최종 제출본으로 간주하지 않는다.
- 먼저 P2 23개 전체를 구현·Registry 활성·전체 회귀하여 **56개 실행 Rule Freeze**를 만든다.
- 그 후 56개 최신 main 소스로 ZIP(EXE)를 재빌드하고 실제 실행 + Local AI + DB + 주요 Rule 스모크검증을 한다.
- 같은 최신 dist를 기준으로 MSI를 재빌드하고 실제 설치 + 모델 복사 + DB 생성 + Local AI 스모크검증을 한다.
- 위 검증 성공 후 README / HACKATHON_SUBMISSION의 배포 상태를 최종 완료로 갱신한다.

---

# 17. 현재 완료 범위와 다음 단계

완료:
- 1~6단계
- UI Freeze
- Local AI / Severity / 감리판정
- Administration 데이터 관리
- 감리자료 114개 분석 / 105개 매핑
- MVP20 실증검증 및 5개 보완
- P1 13개 구현·Registry 활성·전체 회귀
- 소스 기준 실행 Rule 33개 Freeze
- P2 23개 Canonical 구현계획 확정

현재 다음 단계:
- **P2-A 7개 구현 시작**
- P2-A 완료 후 P2-B → P2-C → P2-D
- P2 전체 완료 후 56개 최신 소스로 ZIP/MSI 재빌드·실제 스모크검증

새 결함이 없는 한 완료된 범위를 다시 뜯지 않는다.
