# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발의 **현재 최종 확정 기준(Canonical Decisions)** 을 기록한다.
과거 세부 변경 이력은 Git history에서 확인하며, 본 문서와 충돌하는 과거 문구는 본 문서의 최신 기준으로 대체한다.

---

# 1. 개발 진행 원칙

- 상태를 추측하지 않는다.
- 새 작업 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → P2_IMPLEMENTATION_PLAN.md → IMPLEMENTED_56_OFFICIAL_EVIDENCE_REVIEW_V2.md → HACKATHON_FINAL_SUBMISSION_PLAN.md → HACKATHON_SUBMISSION.md / README.md → 실제 코드/installer → 이전 대화` 순으로 확인한다.
- 한 군데만 보고 판단하지 말고 **코드 ↔ 문서 ↔ 테스트 결과 ↔ 이전 결정사항을 2~3회 교차검증**해서 현재 실제 상태를 먼저 정확히 복원한다.
- 과거 중요 결정의 최초 확정시점이나 적용범위가 문제되는 경우 **최신 요약문서만 보지 말고 Git history와 이전 대화까지 역추적**한다.
- 이미 완료된 기능은 **새 결함이 확인되지 않는 한 다시 구현·재설계·재검증하지 않는다.**
- 기능 단위 `공식근거 확인 → 상세설계 → 구현 → 전용 테스트 → Registry 활성 → 통합 회귀 → 전체 회귀 → 문서 현행화` 순서를 유지한다.
- 신규 Rule 선정 또는 구현 우선순위 변경 전에는 **공식근거 매핑표를 먼저 작성**한다.
- `공식 규범근거`와 `실제 감리사례 빈도/직접사례`는 서로 다른 근거축으로 분리해 기록한다.
- 사용자 로컬 명령은 PowerShell 기준 한 번에 하나씩 안내한다.

---

# 2. UI / 제품 고정 기준

- 2026-09-18 UI Freeze 유지
- 기본 Dark Mode / Light Mode 지원
- Home / Projects / Inspection / Reports / Administration 구조 유지
- 명시적 결함 또는 기능상 필수 변경 외 UI 임의 재설계 금지
- Grade A/B/C/D/E만 사용
- 스캔 이미지 PDF OCR 제외
- HWPX Report Export 제외
- MSIX 제외

---

# 3. 최종 검사체계 / 현재 실행범위

Full Catalog 105:
- AUD 24 / REQ 28 / CHG 18 / FP 12 / AI 23

최초 MVP20:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

P1:
- 13개 구현·Registry 활성·전체 회귀 완료
- Freeze 기준 33개

P2:
- 총 23개 구현·Registry 활성·통합·전체 회귀 완료
- P2-A 7 / 7
- P2-B 6 / 6
- P2-C 4 / 4
- P2-D 6 / 6

현재 실제 실행 Registry:
- **56개 = MVP20 + P1 13 + P2 23**
- **Rule 14 / AI 11 / Hybrid 31**

Full Catalog 105와 실행 Registry 56은 별도 개념이다.

---

# 4. Rule / Issue / Severity 역할 분리

- Rule = 무엇을 어떤 방식으로 검사할 것인가
- Issue = 실제 검사에서 무엇이 발견되었는가
- Severity = 발견 Issue의 위험도
- 감리 개선판정 = 감리 대응 관점 개선 방향

Severity:
`Impact × Likelihood → deterministic Severity Matrix`

AI가 최종 Severity를 직접 결정하지 않는다.

---

# 5. Local AI 최종 기준

- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 출력:
- Impact / Impact Reason
- Likelihood / Likelihood Reason

잘못된 JSON / 필수 필드 누락 / 허용되지 않은 값은 정상 판정으로 저장하지 않는다.
`models/`, `runtime/`은 Git 소스관리 대상에서 제외한다.

---

# 6. Parser / Export / Runtime

Parser 9종:
- DOCX / DOC / XLSX / XLS / PDF / PPTX / PPT / HWPX / HWP

Export:
- DOCX / XLSX / TXT

Inspection:
- 예상시간 / 진행률 / 예상 남은시간 표시
- Local AI 실행 중 취소 지원
- 취소 시 입력상태 유지
- 취소 검사는 DB 미저장

---

# 7. 감리자료 기반 실무검증

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`

확정:
- 감리자료 114개 분석 결과를 **실제 감리사례 검증층**으로 재사용한다.
- Full Catalog 105는 감리 결과 때문에 임의 변경하지 않는다.
- 원래 미구현 85개 우선순위: P1 13 / P2 23 / P3 21 / P4 28
- P1 완료
- **P2 23개 완료**
- 새 감리자료는 전체 재분석 대신 증분 반영
- 신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Catalog/코드에 추가 금지

중요 해석:
- 기존 `근거등급 / 대표근거 문서수`는 주로 **감리결과서 114개에서 직접 사례가 확인된 정도**를 의미한다.
- `미확인 / 0`은 **공식기준상 근거가 없다는 뜻이 아니다.**
- 실제 감리사례는 공식근거를 대체하지 않으며, 공식근거와 별도의 실무검증층으로 관리한다.

---

# 8. P1 확정

Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개는 전용 테스트, Registry 33개 통합검증, 전체 pytest 사용자 PC PASS 후 **33개 Freeze**로 확정한다.
새 결함이 없는 한 다시 구현·재설계·재검증하지 않는다.

---

# 9. P2 최종 확정

Canonical:
- `P2_IMPLEMENTATION_PLAN.md`

P2 총 23개:
- Rule 7 / AI 5 / Hybrid 11

Batch:
- P2-A 7개 — 완료
- P2-B 6개 — 완료
- P2-C 4개 — 완료
- P2-D 6개 — 완료

P2-C 원칙:
- CHG-008/010/FP-011은 명시적 변경관리 행과 대응 문서가 함께 업로드된 경우만 후보 생성
- CHG-010은 데이터/테이블/컬럼 영향이 명시된 변경에 한정
- FP-006은 구조형 FP 후보만 AI 판단
- 완전 동일 기능명 중복은 FP-002 책임영역
- 필요한 문서 한쪽만 업로드된 경우 AI 호출하지 않음

P2-D 원칙:
- 일반 문서가 아니라 AI/LLM/RAG 관련 근거가 확인되는 문서에만 적용
- 특정 목표값·보안수준·정책을 제품이 임의 생성하지 않음
- AI-003: 성능·품질 목표/평가기준 근거 후보가 있을 때만 판단
- AI-008: 민감정보 대상과 통제근거 후보 확인
- AI-013: 학습·참조데이터 출처/품질/적합성 근거 확인
- AI-015: RAG/검색증강/벡터검색 구조가 명시된 경우만 적용
- AI-017: 평가데이터와 정상/예외/위험 입력 시험 근거 확인
- AI-021: AI 입력/모델/조건/결과 추적과 운영 모니터링 근거 확인
- 일반 데이터모델 문서의 단순 `모델` 단어는 AI 문서 판별 신호에서 제외
- Hybrid 5개는 구조적 근거 후보가 없으면 AI 호출하지 않음

검증:
- P2-D 전용 + Service 사용자 PC PASS
- P2-A/B/C/D + Registry 56 + 선택 UI + Catalog/MVP 통합 PASS
- 최종 `python -m pytest -q` 사용자 PC PASS
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2 23/23 완료 / 실행 Rule 56개 Freeze 확정**

---

# 10. 최종 배포 패키징 결정

## Portable

Canonical 빌드:
- `scripts/build_portable.ps1`
- Folder: `dist/AI_Auditor/`
- ZIP: `dist/AI_Auditor_Portable.zip`
- SHA256 파일: `dist/AI_Auditor_Portable.zip.sha256.txt`

최종 검증:
- ZIP 약 2.35 GB
- 모델 약 2.33 GB
- SHA256: `A53BB20BD7CA531EB27F67C6D60371DF5C6E4BDC68410688A4F331B80A054672`
- EXE Home 실행 정상
- DB integrity `ok`
- llama.cpp build 11312 정상
- Qwen3-4B 모델 실제 로딩 정상
- Local AI health 정상
- Local AI 실제 응답 정상

## MSI

Canonical 빌드:
- `installer/build_msi.ps1`
- Output: `installer/output/`

최종 배포 구성:
- `AI_Auditor_Install.cmd`
- `AI_Auditor_Setup.msi`
- `aia1.cab`
- `aia2.cab`
- `Qwen3-4B-Q4_K_M.gguf`

최종 검증:
- 기존 설치본 제거 후 최신 MSI 실제 설치 성공
- `msiexec` Exit Code 0
- 설치 위치 `%LOCALAPPDATA%\Programs\AI Auditor`
- 설치 EXE Home 실행 정상
- 설치 경로 EXE / llama-server / 모델 / DB 존재 확인
- 설치 DB 정상
- 설치 경로 Qwen3-4B 모델 실제 로딩 정상
- 설치본 Local AI 실제 응답 정상
- 설치 Launcher 재실행 정상

Launcher 수정 확정:
- MSI 실행 실패 시 `Exit code:`가 비어 보일 수 있던 `%ERRORLEVEL%` 처리 문제를 수정한다.
- `EnableDelayedExpansion` + `!ERRORLEVEL!` 사용을 최종 기준으로 한다.
- 수정본 포함 최종 MSI 배포 폴더 재빌드 및 동작 확인 완료.

**56개 Freeze 기준 Portable + MSI 최종 배포검증 완료.**

---

# 11. 공식근거 우선순위 — AI Auditor 전체 공통 원칙

이 우선순위는 P3/P4 전용으로 새로 만든 기준이 아니다.
**2026-09-23부터 AI Auditor의 감리 관련 Rule·판정·검사기준을 검토할 때 적용하는 전체 공통 원칙**으로 확정했다.

1순위: **현행 정보시스템 감리기준**
2순위: **NIA 정보시스템 감리 수행 가이드**
3순위: **NIA 지능정보기술 감리 실무 가이드 및 분야별 감리 가이드**
4순위: **실제 감리에서 사용하는 지적사항·개선권고 등의 판정/조치 체계**
보조: **NIST / OWASP / CVSS 등**

원칙:
- 국내 공식기준/가이드를 우선한다.
- 실제 감리결과서 114개는 공식근거와 별개의 사례근거 검증층으로 사용한다.
- 국제기준은 국내 공식 감리기준을 대체하지 않고 보조근거로 사용한다.
- 공식근거가 넓은 상위목적을 규정하고 AI Auditor가 이를 자동화 가능한 세부 Rule로 구체화한 경우에는 `동일 문구의 공식 Rule`처럼 표현하지 않는다.

---

# 12. 구현 56개 공식근거 역검증 — 최종 2차 결과

Canonical:
- `IMPLEMENTED_56_OFFICIAL_EVIDENCE_REVIEW_V2.md`

2차 역검증 결과:
- **A 28개** — 국내 공식근거 직접/명확
- **B 23개** — 국내 공식목적 세부화 또는 국내 실제 감리 직접사례 확인
- **C 2개** — 국내 직접근거 제한, 국제 기술기준 중심
- **M 3개** — 종합/메타 Rule
- **X 0개** — 즉시 근거부족으로 비활성화해야 할 Rule 없음

1차 대비 변경:
- AI-005 `AI 출력 신뢰성·환각 대응`: C → B
- AI-008 `민감정보 입력·출력 통제`: C → B
- AI-015 `RAG 검색근거 적정성`: C → B
- AI-022 `AI 모델·프롬프트 변경관리`: C → B(부분)
- AI-009 `Prompt Injection 대응`, AI-019 `Human-in-the-loop`: C 유지

중요 근거:
- 2025년 실제 공공 감리에서 RAG 정보오류, 할루시네이션 방지, RAG 검색/평가, 개인정보 LLM 전달 통제, 모델/RAG 변경대응, AI 성능목표·BMT·평가체계, 토큰/비용 최적화까지 실제 점검된 사례를 확인했다.
- 따라서 AI 특화 Rule도 모두 국제기준만으로 만든 것은 아니다.
- 다만 AI-009/AI-019는 현재 확보된 국내 감리자료에서 동일 수준 직접 점검근거를 확인하지 못했으므로 NIST/OWASP 보조근거 중심으로 유지한다.
- AI-022는 모델/RAG 변경대응 국내 근거는 확인했으나 `프롬프트 변경이력/버전관리`까지 직접 확인한 것은 아니므로 부분근거로 표시한다.

발표 표현:
- `56개 전부 법적·공식 필수항목`이라고 표현하지 않는다.
- `105개는 공식기관이 정한 105개`라고 표현하지 않는다.
- **현행 정보시스템 감리기준/NIA 가이드를 우선 근거로 검사체계를 설계하고, 실제 감리자료 114개로 현장 지적사례를 교차검증했으며, 최신 생성형 AI 특화 위험은 국내 실제 AI 감리사례와 NIST/OWASP 등을 보조근거로 적용**했다고 설명한다.

절차상 교훈:
- P1/P2 선정 전에 이 근거표를 먼저 남기지 않았던 문서화 절차 공백은 사실로 유지한다.
- 결과의 근거정합성이 확인됐다는 것과 선정절차 기록이 부족했다는 것은 별도 문제로 구분한다.

---

# 13. 현재 최우선 결정 — 해커톤 최종 제출 준비

현재 구현된 56개 Freeze 버전으로 해커톤 제출 준비를 진행한다.
P3/P4 49개 추가 구현은 제출 준비 완료까지 보류한다.

다음 순서:
1. `IMPLEMENTED_56_OFFICIAL_EVIDENCE_REVIEW_V2.md` 기준으로 PPT V9 재작성
2. 3분 시연 영상 원본 확보 및 편집
3. 효과측정 1장 최종 정리
4. README / HACKATHON_SUBMISSION / RULE_DESIGN / 제출자료 숫자·표현 교차검증
5. 최종 제출 패키지 확정
6. 제출 완료 후 P3/P4 49개 공식근거 재평가 재개
