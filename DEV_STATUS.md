# AI Auditor 개발 현황

## 기준일
- 2026-10-10

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
- P2-A 7개 전체 구현·활성·전체 회귀
- P2-B 6개 전체 구현·활성·전체 회귀
- P2-C 4개 전체 구현·활성·전체 회귀
- P2-D 6개 전체 구현·활성·전체 회귀
- **56개 Freeze 기준 Portable ZIP(EXE) 최종 재빌드 및 실제 스모크검증**
- **56개 Freeze 기준 MSI 최종 재빌드·실설치·Local AI 검증**

현재 상태:
- **P2 23/23 완료**
- **실행 Registry 56개 Freeze**
- **Portable + MSI 최종 배포검증 완료**

---

## 2. 검사체계

Full Catalog 105:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23

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

---

## 3. P1 — 완료/Freeze

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

검증:
- 각 Batch 전용 테스트 PASS
- Registry 33 통합 PASS
- 전체 pytest 사용자 PC PASS

**P1 Freeze = 실행 Rule 33개**

---

## 4. P2-A — 완료

대상 7개:
- AUD-015 / AUD-019 / REQ-016 / REQ-020 / CHG-005 / FP-007 / AI-023

**Registry 40 시점 검증 완료**

---

## 5. P2-B — 완료

대상 6개:
- AUD-005 / AUD-021 / REQ-006 / REQ-021 / REQ-027 / REQ-028

**Registry 46 시점 검증 완료**

---

## 6. P2-C — 완료

대상 4개:
- CHG-008 관련 설계 변경 미반영 — Hybrid
- CHG-010 관련 데이터설계 변경 미반영 — Hybrid
- FP-006 기능 단위 분할·통합 적정성 — AI
- FP-011 FP 변경반영 누락 — Hybrid

검증:
- 전용 + Service 사용자 PC 정상
- Registry 50 + 선택 UI + P2-A/B + Catalog/MVP 통합 정상
- 전체 pytest 사용자 PC 정상
- Registry truncation 오류 복구 후 동일 통합/전체 회귀 재검증 정상

---

## 7. P2-D — 완료

대상 6개:
- AI-003 AI 성능·품질 목표 정의 — Hybrid
- AI-008 민감정보 입력·출력 통제 — Hybrid
- AI-013 학습·참조데이터 적정성 — Hybrid
- AI-015 RAG 검색근거 적정성 — AI
- AI-017 AI 평가·테스트 체계 적정성 — Hybrid
- AI-021 AI 로그·추적성 및 운영 모니터링 — Hybrid

원칙:
- AI/LLM/RAG 관련 근거가 확인된 문서에만 적용
- 특정 목표값·보안기준·정책을 임의 생성하지 않음
- AI-015는 RAG/검색증강 근거가 있을 때만 적용
- AI-021은 일반 애플리케이션 로그만으로 충족 판정하지 않음
- Hybrid 5개는 사전근거가 없으면 AI 호출하지 않음
- 일반 데이터모델 문서의 단순 `모델` 단어는 AI 문서 판별 신호에서 제외

검증:
- P2-D 전용 + Service 정상
- P2-A/B/C/D + Registry 56 + 선택 UI + Catalog/MVP 통합 정상
- 최종 `python -m pytest -q` 사용자 PC 정상
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2-D 완료 / P2 23/23 완료 / 실행 Registry 56개 Freeze 확정**

---

## 8. 최종 Engine 구조

Rule:
`DocumentRuleEngine → P1DocumentRuleEngine → P2DocumentRuleEngine`

AI:
`DocumentAIEngine → P2CAIEngine → P2DAIEngine`

Hybrid:
`DocumentHybridEngine → P1RequirementHybridEngine → P1AuditHybridEngine → P1GovernanceHybridEngine → P1FPHybridEngine → P2BHybridEngine → P2CHybridEngine → P2DHybridEngine`

실행 흐름:
`Inspection → Full Catalog 105 선택상태 → 실행 Registry 56 → Parser → Rule/AI/Hybrid → 교차문서/종합 후처리 → Issue → Assessment → DB → UI`

---

## 9. Parser / Local AI / Severity 고정

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

## 10. Portable 최종 배포검증

빌드:
- `scripts/build_portable.ps1`
- Folder: `dist/AI_Auditor/`
- ZIP: `dist/AI_Auditor_Portable.zip`
- SHA256 파일: `dist/AI_Auditor_Portable.zip.sha256.txt`

실제 결과:
- 모델 약 2.33 GB
- ZIP 약 2.35 GB
- SHA256: `A53BB20BD7CA531EB27F67C6D60371DF5C6E4BDC68410688A4F331B80A054672`

스모크:
- EXE Home 정상
- DB integrity `ok`
- llama.cpp build 11312 정상
- Qwen3-4B 실제 로딩 정상
- `/health` 정상
- Local AI 실제 응답 정상

**Portable PASS**

---

## 11. MSI 최종 배포검증

빌드:
- `installer/build_msi.ps1`
- 출력: `installer/output/`

최종 배포 구성:
- `AI_Auditor_Install.cmd`
- `AI_Auditor_Setup.msi`
- `aia1.cab`
- `aia2.cab`
- `Qwen3-4B-Q4_K_M.gguf`

실제 검증:
- 기존 설치본 정상 제거
- 최신 MSI 실제 설치 성공 (`msiexec` Exit Code 0)
- 설치 위치 `%LOCALAPPDATA%\Programs\AI Auditor`
- EXE / llama-server / 모델 / DB 존재 확인
- 설치 EXE Home 정상
- 설치 DB 정상
- 설치 경로 Qwen3-4B 실제 로딩 정상
- 설치본 Local AI 실제 응답 정상
- 설치 Launcher 재실행 정상

Launcher 보완:
- MSI 실패 시 `Exit code:`가 비어 보이던 `%ERRORLEVEL%` 처리 문제를 `EnableDelayedExpansion` + `!ERRORLEVEL!`로 수정
- 수정본 포함 최종 배포 폴더 재빌드 및 정상 동작 확인

**MSI PASS**

---

## 12. 현재 다음 작업

핵심 개발·P2·최종 배포검증은 완료 상태다.

남은 것은 제출 준비 성격의 작업이다.
1. 최종 Git 동기화/working tree 확인
2. 실제 해커톤 제출 규격·용량·파일명 최종 확인
3. 필요 시 사용자 매뉴얼 / 데모 시나리오 / 발표자료 정리
4. P3/P4는 제출 이후 별도 범위로 진행
