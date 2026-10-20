# AI Auditor 개발 현황

## 기준일
- 2026-10-13

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
- P2-A 7개 / P2-B 6개 / P2-C 4개 / P2-D 6개 전체 구현·활성·전체 회귀
- 56개 Freeze 기준 Portable ZIP(EXE) 최종 재빌드 및 실제 스모크검증
- 56개 Freeze 기준 MSI 최종 재빌드·실설치·Local AI 검증
- **구현 56개 공식근거 1차 역검증 완료**

현재 상태:
- **P2 23/23 완료**
- **실행 Registry 56개 Freeze**
- **Portable + MSI 최종 배포검증 완료**
- **현재 최우선 작업은 해커톤 최종 제출 준비 전 56개 공식근거 역검증 마무리**
- P3/P4 49개 공식기준 재매핑은 제출 준비 완료 시점까지 보류

---

## 2. 검사체계

Full Catalog 105:
- AUD 24 / REQ 28 / CHG 18 / FP 12 / AI 23

최초 MVP20:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

현재 실행 Registry:
- **56개 = MVP20 + P1 13 + P2 23**
- **Rule 14 / AI 11 / Hybrid 31**

P2:
- P2-A 7 / 7
- P2-B 6 / 6
- P2-C 4 / 4
- P2-D 6 / 6
- **총 23 / 23 완료**

잔여 Full Catalog:
- P3 21개
- P4 28개
- 합계 49개

단, 기존 P3/P4 구분은 향후 공식기준 재평가 후 차기 구현순위가 변경될 수 있다.

---

## 3. 공식근거 우선순위 복원 및 56개 역검증

2026-10-13 Git history 재확인 결과:
- 공식근거 우선순위는 P3/P4 전용 신규 기준이 아니다.
- 2026-09-23부터 `AI Auditor의 감리 관련 Rule·판정·검사기준을 검토할 때` 적용하는 전체 기본원칙으로 확정돼 있었다.

우선순위:
1. 현행 정보시스템 감리기준
2. NIA 정보시스템 감리 수행 가이드
3. NIA 지능정보기술 감리 실무 가이드 및 분야별 감리 가이드
4. 실제 감리에서 사용하는 지적사항·개선권고 등의 판정/조치 체계
5. 보조: NIST / OWASP / CVSS 등

Canonical 역검증 문서:
- `IMPLEMENTED_56_OFFICIAL_EVIDENCE_REVIEW.md`

1차 역검증 결과:
- **A 28개** — 국내 공식근거 직접/명확
- **B 19개** — 국내 공식근거 간접/세부화
- **C 6개** — 국내 직접근거 제한, NIST/OWASP 등 국제·기술 보조근거 중심
- **M 3개** — 하위 Issue 종합형 제품 메타 Rule
- **X 0개** — 현재 단계에서 즉시 근거 부족으로 비활성화 판정한 Rule 없음

핵심 해석:
- 비AI 45개는 국내 정보시스템 감리기준·NIA 수행체계·실제 감리사례와 전반적으로 높은 정합성이 확인됨.
- AI 특화 11개는 국내 지능정보/운영가이드로 연결 가능한 항목과 국제기술기준 비중이 높은 생성형 AI 특화항목이 혼재함.
- Prompt Injection, RAG, Human-in-the-loop 등 일부는 국내 직접근거보다 NIST/OWASP 보조근거가 더 강함.
- 56개 각각의 공식근거를 선정 전에 표로 남기지 않은 **문서화/검증 절차 공백**이 확인됨.
- 현재 1차 역검증 결과만으로 코드를 되돌리거나 Rule을 비활성화할 필요가 있는 X등급은 없음.

후속:
1. B 19개 중 발표 대표 Rule의 NIA 가이드 구체 위치 2차 확인
2. C 6개를 NIST/OWASP 세부 항목과 정확히 연결
3. M 3개를 발표에서 종합분석 기능으로 명확히 구분
4. 검증결과 반영 후 PPT V9 제작

---

## 4. P1 / P2 Freeze

P1 13개와 P2 23개는 전용/Service/Registry 통합/전체 회귀를 완료했다.
최종 `python -m pytest -q` 사용자 PC 정상 PASS.
정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않는다.

**P1/P2 포함 실행 Registry 56개 Freeze 확정**

새 결함이 없는 한 다시 구현·재설계하지 않는다.
다만 2026-10-13부터 공식근거 역검증은 코드 변경이 아닌 **선정근거 검증/문서 보완 작업**으로 별도 진행한다.

---

## 5. 최종 Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

AI:
`DocumentAIEngine → P2CAIEngine → P2DAIEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine → P2CHybridEngine → P2DHybridEngine`

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 56 → Parser → Rule/AI/Hybrid → 교차문서/종합 후처리 → Issue → Assessment → DB → UI`

---

## 6. Parser / Local AI / Severity 고정

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
- MSIX

---

## 7. 최종 배포검증

### Portable
- `scripts/build_portable.ps1`
- ZIP 약 2.35 GB / 모델 약 2.33 GB
- SHA256: `A53BB20BD7CA531EB27F67C6D60371DF5C6E4BDC68410688A4F331B80A054672`
- EXE / DB integrity / llama.cpp b11312 / Qwen3-4B 로딩 / Local AI 응답 PASS

### MSI
- `installer/build_msi.ps1`
- `installer/output/`
- 실제 설치 성공 (`msiexec` Exit Code 0)
- 설치 위치 `%LOCALAPPDATA%\Programs\AI Auditor`
- EXE / llama-server / 모델 / DB / Local AI 실제 응답 PASS
- `AI_Auditor_Install.cmd` ERRORLEVEL 표시 문제 수정 및 최종 재검증 PASS

**Portable + MSI PASS**

---

## 8. 해커톤 최종 제출 준비

제출 요구사항:
1. 3분 시연 영상 또는 라이브 데모
2. 발표 PPT — 되도록 10장, 설명완결성 우선
3. 소스코드 또는 워크플로우 — GitHub
4. 효과측정지표 1장 요약

현재 방향:
- PPT V8은 제3자 설명형 초안까지 작성
- PPT V9는 **56개 공식근거 역검증 2차 확인 후 제작**
- 발표자료는 `공식근거 → 실제 감리사례 → 검사체계 → 구현 → 실제 예시 → 검증` 흐름으로 구성
- 105/56/114/9 숫자 반복보다 선정·분류·구현근거와 구체 예시를 설명

제출 표현 기준:
- Full Catalog 105와 실제 실행 Registry 56을 반드시 구분
- 56개 = MVP20 + P1 13 + P2 23
- Rule 14 / AI 11 / Hybrid 31
- 감리자료 114개는 실제 사례근거 검증층
- 국내 공식기준/NIA 가이드와 국제 보조기준을 구분
- AI 특화 C등급 항목은 NIST/OWASP 보조근거임을 명시
- M등급 종합 Rule은 독립 감리기준으로 표현하지 않음
- 자체 실측이 없는 시간절감률/비용절감액은 확정성과로 주장하지 않음

---

## 9. P3/P4 — 제출 완료 후 재개

Canonical:
- `P3_P4_REEVALUATION_PLAN.md`

대상:
- P3 21개
- P4 28개
- 합계 49개

P3/P4 재평가는 새로운 기준을 만드는 작업이 아니라, 2026-09-23부터 존재한 전체 공식근거 우선순위를 남은 49개에 체계적으로 재적용하는 작업이다.
제출 준비 기간에는 코딩을 진행하지 않는다.

---

## 10. 현재 다음 작업

1. 구현 56개 공식근거 2차 역검증 마무리
2. B등급 발표 대표 Rule의 NIA 가이드 구체 근거 확인
3. C등급 AI 특화 Rule의 NIST/OWASP 연결 확정
4. 결과 반영 PPT V9 제작
5. 3분 시연 영상 촬영/편집
6. 효과측정표 및 GitHub 제출문서 최종 교차검증
7. 최종 제출 패키지 확정

그 뒤 P3/P4 공식기준 재평가를 재개한다.
