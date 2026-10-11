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

## 7. 해커톤 최종 제출 준비 — V3

제출 요구사항:
1. 3분 시연 영상 또는 라이브 데모
2. 발표 PPT 10슬라이드 이내
3. 소스코드 또는 워크플로우 — GitHub
4. 효과측정지표 1장 요약

V3 작성 상태:
- `HACKATHON_FINAL_SUBMISSION_PLAN.md` V3 기준 현행화 완료
- `DEMO_3MIN_SCRIPT.md` 초보자 이해형 V3 현행화 완료
- `EFFECT_MEASUREMENT.md` 외부연구 기반 참고 시나리오 V3 현행화 완료
- 10슬라이드 발표 PPT V3 작성 및 렌더링 QA 완료
- 효과측정 1장 V3 작성 및 1페이지 렌더링 QA 완료
- 3분 시연 대본 V3 작성 및 1페이지 렌더링 QA 완료

제출 표현 기준:
- Full Catalog 105와 실제 실행 Registry 56을 반드시 구분
- 56개 = MVP20 + P1 13 + P2 23
- Rule 14 / AI 11 / Hybrid 31
- 감리자료 114개 실무근거
- MVP 실증보완 5개 + 전체 회귀 실패 0건
- Parser 9종
- Portable/MSI 실제 배포검증

효과측정 V3:
- AI Auditor 자체 실제 검증값과 외부연구 기반 참고 기대효과를 분리
- 외부 유사연구에서 약 12~40% 시간효과가 보고됨
- AI Auditor 자체 실측성과로 표현하지 않음
- 제출자료에는 **20% 보수적 참고 시나리오** 사용 가능
- 예시: 수작업 60분 → AI Auditor 활용 48분
- 비용 예시는 시간당 업무비용 30,000원 가정 시 30,000원 → 24,000원, 약 6,000원 상당 업무시간 차이
- 위 비용은 실제 절감액/ROI/인력대체로 표현하지 않음
- Local AI 외부 API 비용 0원은 장비·전력·개발비까지 0원이라는 의미가 아님

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

1. 사용자에게 V3 PPT / 효과측정표 / 시연대본 검토받기
2. 사용자의 피드백을 반영해 PPT 시안과 문구 최종 조정
3. 3분 데모 영상 촬영 또는 라이브 경로 확정
4. README / HACKATHON_SUBMISSION / 제출자료 간 숫자·표현 최종 교차검증
5. 최종 제출 패키지 확정

그 뒤 P3/P4 공식기준 재평가를 재개한다.
