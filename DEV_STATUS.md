# AI Auditor 개발 현황

## 기준일
- 2026-10-11

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

현재 상태:
- **P2 23/23 완료**
- **실행 Registry 56개 Freeze**
- **Portable + MSI 최종 배포검증 완료**
- **현재 최우선 작업은 해커톤 최종 제출 준비**
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

## 3. P1 / P2 Freeze

P1 13개와 P2 23개는 전용/Service/Registry 통합/전체 회귀를 완료했다.
최종 `python -m pytest -q` 사용자 PC 정상 PASS.
정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않는다.

**P1/P2 포함 실행 Registry 56개 Freeze 확정**

새 결함이 없는 한 다시 구현·재설계·재검증하지 않는다.

---

## 4. 최종 Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

AI:
`DocumentAIEngine → P2CAIEngine → P2DAIEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine → P2CHybridEngine → P2DHybridEngine`

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 56 → Parser → Rule/AI/Hybrid → 교차문서/종합 후처리 → Issue → Assessment → DB → UI`

---

## 5. Parser / Local AI / Severity 고정

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

## 6. 최종 배포검증

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

## 7. 해커톤 최종 제출 준비 — 현재 작업

제출 요구사항:
1. 3분 시연 영상 또는 라이브 데모
2. 발표 PPT 10슬라이드 이내
3. 소스코드 또는 워크플로우 — GitHub
4. 효과측정지표 1장 요약

현재 작성 완료/진행:
- `HACKATHON_FINAL_SUBMISSION_PLAN.md` 작성 완료
- `DEMO_3MIN_SCRIPT.md` 작성 완료
- `EFFECT_MEASUREMENT.md` 작성 완료
- 10슬라이드 발표 PPT 초안 작성 완료
- 1장 효과측정 요약 초안 작성 완료
- 3분 시연 대본 문서 작성 완료

제출 표현 기준:
- Full Catalog 105와 실제 실행 Registry 56을 반드시 구분
- 56개 = MVP20 + P1 13 + P2 23
- Rule 14 / AI 11 / Hybrid 31
- 감리자료 114개 실무근거
- Parser 9종
- Portable/MSI 실제 배포검증

효과측정:
- 확정값: 56 / 105 = 53.3% 실행범위, 감리자료 114개, Parser 9종, Local AI 외부 API 호출비 0원(장비·전력비 제외)
- 특정 사용자 PC 실측사례는 전체 평균으로 일반화하지 않음
- 수동검토시간 / 시간절감률 / 오류율 변화는 동일 샘플 A/B 실측 후 확정
- 임의 수치 작성 금지

---

## 8. P3/P4 — 제출 완료 후 재개

Canonical:
- `P3_P4_REEVALUATION_PLAN.md`

대상:
- P3 21개
- P4 28개
- 합계 49개

제출 준비 기간에는 재매핑/코딩을 진행하지 않는다.
제출 완료 후 공식기준 최신본 확인 → 49개 재매핑 → A/B/C/D/E 재분류 → 사용자 승인 → 상세설계/구현 순으로 재개한다.

---

## 9. 현재 다음 작업

1. 3분 데모 리허설 및 촬영/라이브 경로 확정
2. PPT 10장 최종 문구·화면 구성 검토
3. 효과측정 1장 최종 검토
4. 동일 샘플 수동/자동 A/B 시간 측정
5. README / HACKATHON_SUBMISSION / 제출자료 간 숫자·표현 최종 교차검증
6. 최종 제출 패키지 확인

그 뒤 P3/P4 공식기준 재평가를 재개한다.
