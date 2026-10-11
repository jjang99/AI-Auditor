# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발의 **현재 최종 확정 기준(Canonical Decisions)** 을 기록한다.
과거 세부 변경 이력은 Git history에서 확인하며, 본 문서와 충돌하는 과거 문구는 본 문서의 최신 기준으로 대체한다.

---

# 1. 개발 진행 원칙

- 상태를 추측하지 않는다.
- 새 작업 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → P2_IMPLEMENTATION_PLAN.md → HACKATHON_FINAL_SUBMISSION_PLAN.md → HACKATHON_SUBMISSION.md / README.md → 실제 코드/installer → 이전 대화` 순으로 확인한다.
- 한 군데만 보고 판단하지 말고 **코드 ↔ 문서 ↔ 테스트 결과 ↔ 이전 결정사항을 2~3회 교차검증**해서 현재 실제 상태를 먼저 정확히 복원한다.
- 이미 완료된 기능은 **새 결함이 확인되지 않는 한 다시 구현·재설계·재검증하지 않는다.**
- 기능 단위 `구현 → 전용 테스트 → Registry 활성 → 통합 회귀 → 전체 회귀 → 문서 현행화` 순서를 유지한다.
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
- 따라서 P3/P4는 향후 공식 감리기준/가이드 근거를 별도로 재매핑하여 다시 평가한다.

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

# 11. P3/P4 공식기준 재평가 — 후속 계획

Canonical:
- `P3_P4_REEVALUATION_PLAN.md`

대상:
- P3 21개
- P4 28개
- 합계 **49개**

49개는 바로 코딩하지 않고 다음 공식근거 우선순위로 재매핑한다.

1순위: **현행 정보시스템 감리기준**
2순위: **NIA 정보시스템 감리 수행 가이드**
3순위: **NIA 지능정보기술 감리 실무 가이드 및 분야별 감리 가이드**
4순위: **실제 감리에서 사용하는 지적사항·개선권고 등의 판정/조치 체계**
보조: **NIST / OWASP / CVSS 등**

원칙:
- 국내 공식기준/가이드를 우선한다.
- 기존 감리결과서 114개는 사례근거로 재사용한다.
- 국제기준은 보조근거로 사용한다.
- 기존 P3/P4 구분은 재평가 결과에 따라 차기 구현 우선순위가 바뀔 수 있다.
- 공식근거가 강한 기존 P4 Rule은 우선순위가 올라갈 수 있다.
- 기존 P3 Rule이라도 중복/근거 부족이면 통합 또는 보류할 수 있다.

재평가 분류:
- A: 공식근거 강함 + 실무가치 높음 → 우선 구현
- B: 공식근거 있음 + 사례 제한적 → 구현 가능
- C: 예방·전략성 → 선택 구현
- D: 기존 Rule과 중복/흡수 가능 → 통합 검토
- E: 근거 부족 → 보류

**49개 공식기준 재평가가 끝나기 전에는 P3/P4 코딩을 시작하지 않는다.**

---

# 12. 현재 최우선 결정 — 해커톤 최종 제출 준비

2026-10-11 사용자 결정:
- 현재 구현된 **56개 Freeze 버전으로 해커톤 최종 제출물을 우선 완성**한다.
- P3/P4 49개 공식기준 재매핑은 제출 준비가 끝날 때까지 잠시 보류한다.
- 기존 P1/P2 기능·UI는 새 결함이 없는 한 변경하지 않는다.

제출 요구사항:
1. 3분 시연 영상 또는 라이브 데모
2. 발표 PPT 10슬라이드 이내
3. 소스코드 또는 워크플로우 — GitHub 저장소
4. 효과측정지표 1장 요약

Canonical:
- `HACKATHON_FINAL_SUBMISSION_PLAN.md`
- `DEMO_3MIN_SCRIPT.md`
- `EFFECT_MEASUREMENT.md`
- `HACKATHON_SUBMISSION.md`

제출 표현 원칙:
- **Full Catalog 105개 설계 / 실제 실행 Registry 56개**를 명확히 구분한다.
- 105개 전체 구현으로 표현하지 않는다.
- 실행 Registry 56개 = MVP20 + P1 13 + P2 23.
- 누적 실행방식 = Rule 14 / AI 11 / Hybrid 31.
- 감리자료 114개 분석결과는 실제 사례근거 검증층으로 표현한다.
- Local AI 외부 API 호출비 0원은 추론 API 비용 기준이며 장비·전력·개발비까지 0원이라고 표현하지 않는다.

2026-10-11 효과측정 V3 추가 결정:
- 사용자가 동일 샘플의 수동/AI Auditor A/B 실측을 새로 수행하기 어려운 시간·샘플 제약이 있음.
- 따라서 수동검토시간·절감률을 임의로 AI Auditor 실측성과라고 작성하지 않는다.
- Microsoft Research / HBS+BCG / MIT / IEEE RE 등 **유사 AI 문서·지식업무의 외부 연구를 참고 기대효과 근거로 사용**할 수 있다.
- 외부 연구의 12~40% 수준 시간효과는 AI Auditor 자체 실측성과가 아니다.
- 제출자료에서는 **20%를 보수적 설명용 참고 시나리오**로 사용할 수 있으나 반드시 `AI Auditor 자체 실측값이 아닌 외부 연구 기반 참고치`라고 표시한다.
- 비용은 예를 들어 `60분 → 48분`, 시간당 업무비용 30,000원 가정 시 `30,000원 → 24,000원`처럼 **한 번의 1차 점검단위에서 단순 환산**한다.
- 위 비용은 실제 절감액·인건비절감·ROI로 표현하지 않는다.
- AI Auditor의 역할은 `인력대체`가 아니라 `반복적인 1차 문서점검 선행`으로 정의한다.

검증 표현 V3:
- `감리자료 114 → 검사기준 105 → 실행 Rule 56 → MVP 실증보완 5개 → 전체 회귀 실패 0건 → Portable/MSI 실배포 검증`
- 작은 개별 실행시간 사례보다 위 다층 검증구조를 제출자료 전면에 배치한다.

---

# 13. 제출 완료 후 진행 순서

1. V3 PPT / 효과측정 1장 / 데모 대본 사용자 검토
2. 해커톤 3분 데모 촬영 또는 라이브 경로 확정
3. 10슬라이드 PPT 최종 조정
4. 효과측정 1장 출처·표현 최종 확인
5. README / HACKATHON_SUBMISSION / 제출자료 숫자·표현 최종 교차검증
6. 최종 제출 패키지 확정
7. 제출 완료 후 `P3_P4_REEVALUATION_PLAN.md`에 따라 P3/P4 49개 공식기준 재매핑 재개
