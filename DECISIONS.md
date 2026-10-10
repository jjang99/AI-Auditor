# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발의 **현재 최종 확정 기준(Canonical Decisions)** 을 기록한다.
과거 세부 변경 이력은 Git history에서 확인하며, 본 문서와 충돌하는 과거 문구는 본 문서의 최신 기준으로 대체한다.

---

# 1. 개발 진행 원칙

- 상태를 추측하지 않는다.
- 새 작업 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드 및 installer 관련 파일 → 이전 대화/저장된 결정사항` 순으로 확인한다.
- 이미 완료된 기능을 새 결함 없이 다시 구현하거나 재설계하지 않는다.
- 기존 코드와 실제 동작을 확인한 뒤 수정한다.
- UI Freeze 이후 구조·크기·배치·간격·색상·폰트·버튼 형태를 임의 변경하지 않는다.
- 기능 단위 구현 → targeted/integration test → 전체 회귀 → 문서 현행화 순서를 유지한다.
- 사용자가 개발자가 아니므로 로컬 명령은 PowerShell 기준 한 번에 하나씩 안내한다.

## 작업 전 필수 다중 교차검증 원칙

- GitHub 실제 코드, 프로젝트 구조, 핵심 문서, 테스트 결과, 이전 결정사항을 최소 2~3회 다른 관점에서 교차확인한다.
- 내용이 충돌하면 최신 GitHub 실제 코드와 실제 동작을 우선 기준으로 하되 기존 확정 결정사항과의 충돌 여부도 다시 확인한다.
- 충분히 검증되지 않은 상태에서는 추측으로 수정하거나 Registry에 선등록하지 않는다.

---

# 2. 전체 UI 공통 기준

- Dark Mode 기본 / Light Mode 지원
- 공통 메뉴: Home / Projects / Inspection / Reports / Administration
- 클릭 가능한 카드·행·버튼만 Hover 피드백 적용
- Administration 카드 기준, Reports 정보 위계 기준 유지
- 2026-09-18 UI Freeze 유지
- 새로운 명시적 결함이 없는 한 임의 재설계 금지

---

# 3. 최종 검사체계

제품 전체 검사체계는 5대 영역 / 총 105개 Rule이다.

- AUD 감리 사전점검: 24
- REQ 요구사항 정합성: 28
- CHG 변경영향도: 18
- FP 검증: 12
- AI 특화 검증: 23

최초 해커톤 MVP 기준선은 20개이다.

- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4

최초 MVP20 실행방식:
- Rule 3
- AI 6
- Hybrid 11

**2026-10-10 P1 확장 완료 후 실제 실행 Registry는 33개로 확정한다.**

- 33개 = MVP20 + P1 13개
- Rule 7
- AI 6
- Hybrid 20

`MVP20`은 최초 기준선 명칭으로 유지하며, 현재 실제 실행 가능 범위를 뜻하지 않는다.
Full Catalog 105와 실행 Registry 33은 별도 개념이다.

---

# 4. P1 13개 Release Freeze 결정 — 2026-10-10

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

배치:
- P1-A 4개 완료
- P1-B 3개 완료
- P1-C 2개 완료
- P1-D 3개 완료
- P1-E 1개 완료

완료조건:
- Rule별 Handler/사전분석 구현
- targeted/integration test
- Registry 활성
- 기존 MVP/Catalog 통합 회귀
- 최종 `python -m pytest -q` 사용자 PC 정상

위 조건을 모두 통과했으므로 **P1 Release Freeze = 실행 Rule 33개**로 확정한다.

새 결함이 없는 한 P1 13개를 다시 미구현 상태로 되돌리거나 재구현하지 않는다.

---

# 5. P1 주요 역할·오탐방지 확정

- AUD-001은 실제 제출 파일 존재/누락, AUD-008은 계획표상 작성·제출 상태를 담당한다.
- REQ-007은 숫자 부재만으로 검증불가를 단정하지 않는다.
- REQ-012는 시험문서 미업로드만으로 시험항목 누락을 확정하지 않는다.
- REQ-017은 N/A/해당없음/별도시트 참조를 인정하며 REQ-018과 역할을 분리한다.
- AUD-010은 합계/소계/구분/마일스톤을 일반 작업행으로 보지 않는다.
- AUD-018은 계획/수행근거 한쪽만 업로드된 경우 미수행을 확정하지 않는다.
- AUD-020은 단순 외부기관 언급을 인터페이스 정의로 간주하지 않는다.
- AUD-022는 일반 설명문을 계약 의무로 간주하지 않고, 증적 미업로드만으로 미이행을 단정하지 않는다.
- AUD-023은 문서에 적용대상으로 명시된 기준만 확인하며 AI가 법적 위반을 새로 해석하지 않는다.
- FP-002는 동일·유사 기능명 + 동일 FP유형을 후보화하고, 처리조건·사용자 관점·입출력 차이가 명확한 경우만 별도 기능으로 제외한다.
- FP-002의 단순 설명문구 차이는 자동 제외하지 않고 AI가 실질 동일 기능 여부를 판단한다.

---

# 6. Rule / Issue / Severity 역할 분리

- Rule = 무엇을 어떤 방식으로 검사할 것인가
- Issue = 실제 검사에서 무엇이 발견되었는가
- Severity = 발견된 Issue가 얼마나 위험한가
- 감리 개선판정 = 감리 대응 관점에서 어떻게 개선할 것인가

Rule 자체에 고정 최종 Severity를 사용하지 않는다.
검사방식은 Rule / AI / Hybrid이다.

---

# 7. Severity 최종 기준

AI는 다음을 판단한다.
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

Impact / Likelihood:
- Low / Medium / High

최종 Severity는 deterministic Matrix로 계산한다.

| Impact \ Likelihood | Low | Medium | High |
|---|---|---|---|
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

Critical은 원칙적으로 `Impact=High AND Likelihood=High`에서만 산정한다.
AI가 최종 Severity를 직접 결정하지 않는다.

---

# 8. Local AI 최종 기준

- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

잘못된 JSON / 필수 필드 누락 / 허용되지 않은 값은 정상 판정으로 저장하지 않는다.
`models/`, `runtime/`은 대용량 실행자산으로 Git 소스관리 대상에서 제외한다.
프로그램이 인터넷에서 모델을 자동 다운로드하지 않는다.

---

# 9. 실제 검사 실행 흐름

`Inspection`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 33 필터`
→ `Parser / ParsedDocument`
→ `Rule / AI / Hybrid`
→ `문서별 사전분석 / 교차문서 비교`
→ `Issue 생성`
→ `Impact / Likelihood 평가`
→ `Severity Matrix`
→ `필요 시 감리 개선판정`
→ `DB 저장`
→ `Project Detail / Reports`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않고 향후 확장영역으로 보존한다.

Hybrid 상속 구조:
- `DocumentHybridEngine`
- `P1RequirementHybridEngine`
- `P1AuditHybridEngine`
- `P1GovernanceHybridEngine`
- `P1FPHybridEngine`

---

# 10. 문서 Parser 최종 지원범위

지원 형식 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

모든 Parser는 원본 형식을 공통 `ParsedDocument / DocumentBlock` 구조로 표준화한다.
스캔 이미지 기반 PDF OCR은 현재 범위에서 제외한다.

---

# 11. Inspection 실행 UX 최종 정책

- 검사 전 예상시간 표시
- 검사 진행 중 현재 Rule/단계, 완료 Rule 수, Progress Bar, 예상 남은시간 표시
- Local AI 실행 중 취소 지원
- 취소 시 프로젝트명 / 파일 / Rule 선택상태 유지
- 취소 검사는 DB에 저장하지 않음
- 취소 후 재검사 가능

위 동작은 사용자 화면 검증 완료 상태로 고정한다.

---

# 12. Score / Grade

- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

F는 사용하지 않는다.

---

# 13. Export Report

지원:
- DOCX / XLSX / TXT

HWPX Report Export는 현재 범위에서 제외한다.
HWPX를 다시 임의 복원하거나 제품 필수조건으로 만들지 않는다.

---

# 14. Administration 데이터 관리

구성:
1. 검사 기준 관리
2. 환경 설정
3. 데이터 관리

삭제 정책:
- 전체 검사 이력 정리: Issues → Inspections, Project 유지
- Project 삭제: Issues → Inspections → Project
- Repository transaction 사용, 오류 시 rollback
- Stage 6에서 새 ON DELETE CASCADE를 강제하지 않음

기존 실제 삭제검증과 자동테스트는 완료 상태로 유지한다.

---

# 15. 감리결과서 기반 실무검증 결정

- 감리자료 114개 분석의 Canonical 결과는 `AUDIT_EVIDENCE_MAPPING.md`로 한다.
- Full Catalog 105를 감리 결과에 맞춘다는 이유로 임의 변경하지 않는다.
- 원래 미구현 85개 우선순위는 P1 13 / P2 23 / P3 21 / P4 28이었다.
- P1 13개는 2026-10-10 구현 완료되었으므로 이후 확장 우선순위는 P2 → P3 → P4로 한다.
- 감리자료 114개는 다시 처음부터 분석하지 않고 기존 매핑을 재사용한다.
- 새 감리자료가 추가되면 증분 반영한다.
- 신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Full Catalog 105나 실제 코드에 추가하지 않는다.

---

# 16. MVP20 실증검증 결정

Canonical:
- `MVP20_AUDIT_VALIDATION.md`

보완 완료 5개:
- AUD-001
- REQ-002
- REQ-003
- REQ-009
- FP-009

위 5개는 실제 감리사례 기반 구현 보완 후 targeted 및 전체 회귀를 통과했다.
새 결함이 없는 한 MVP20 실증검증을 처음부터 반복하지 않는다.

---

# 17. 배포 패키징 결정

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

**중요한 2026-10-10 추가 결정:**
- 기존 ZIP/MSI는 P1 13개 확장 전 빌드다.
- GitHub main은 33개 실행 Rule Freeze 상태다.
- 따라서 기존 ZIP/MSI를 33개 최종 제출본으로 간주하지 않는다.
- 33개 Freeze 소스로 ZIP(EXE) 재빌드·Local AI 스모크검증 후, 동일 dist 기준 MSI를 재빌드·실설치·스모크검증한다.
- 위 재검증이 성공한 뒤 README / HACKATHON_SUBMISSION에서 33개 배포 완료로 최종 표기한다.

---

# 18. 현재 완료 범위와 다음 단계

완료:
- 1~6단계
- UI Freeze
- Local AI / Severity / 감리판정
- Administration 데이터 관리
- 감리자료 114개 분석 / 105개 매핑
- MVP20 실증검증 및 5개 보완
- P1 13개 구현·Registry 활성·전체 회귀
- 소스 기준 실행 Rule 33개 Freeze

현재 다음 단계:
- **33개 Freeze 최신 소스 기준 ZIP(EXE) 재빌드 및 스모크검증**
- 이후 MSI 재빌드 및 실제 설치/Local AI 검증
- 배포검증 성공 후 README / HACKATHON_SUBMISSION 최종 현행화

이후 기능 확장은 P2 23개부터 시작하며, 제출 전 임의로 P2를 끼워 넣지 않는다.
