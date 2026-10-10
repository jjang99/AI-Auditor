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
- 56개 Freeze 기준 Portable ZIP(EXE) 최종 재빌드 및 실제 스모크검증
- 56개 Freeze 기준 MSI 최종 재빌드·실설치·Local AI 검증

현재 상태:
- **P2 23/23 완료**
- **실행 Registry 56개 Freeze**
- **Portable + MSI 최종 배포검증 완료**
- **다음 단계는 P3/P4 49개 공식기준 재매핑 및 차기 구현 우선순위 재평가**

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

잔여 Full Catalog:
- P3 21개
- P4 28개
- 합계 49개

단, 기존 P3/P4 구분은 감리결과서 114개 직접사례 중심의 우선순위이므로 공식기준 재평가 후 차기 구현순위가 바뀔 수 있다.

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

새 결함이 없는 한 다시 구현·재설계·재검증하지 않는다.

---

## 4. P2 — 전체 완료/Freeze

P2-A 7개:
- AUD-015 / AUD-019 / REQ-016 / REQ-020 / CHG-005 / FP-007 / AI-023

P2-B 6개:
- AUD-005 / AUD-021 / REQ-006 / REQ-021 / REQ-027 / REQ-028

P2-C 4개:
- CHG-008 / CHG-010 / FP-006 / FP-011

P2-D 6개:
- AI-003 / AI-008 / AI-013 / AI-015 / AI-017 / AI-021

검증:
- 각 Batch 전용/Service 테스트 정상
- P2-A/B/C/D + Registry 56 + 선택 UI + Catalog/MVP 통합 정상
- 최종 `python -m pytest -q` 사용자 PC 정상
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2 23/23 완료 / 실행 Registry 56개 Freeze 확정**

새 결함이 없는 한 다시 구현·재설계·재검증하지 않는다.

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

## 7. Portable 최종 배포검증

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

## 8. MSI 최종 배포검증

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

## 9. P3/P4 공식기준 재평가 — 다음 단계

Canonical:
- `P3_P4_REEVALUATION_PLAN.md`

대상:
- P3 21개
- P4 28개
- 합계 **49개**

다음 단계는 코딩이 아니다.
먼저 49개를 아래 공식근거 순위로 재매핑한다.

1. 현행 정보시스템 감리기준
2. NIA 정보시스템 감리 수행 가이드
3. NIA 지능정보기술 감리 실무 가이드 및 분야별 감리 가이드
4. 실제 감리에서 사용하는 지적사항·개선권고 등의 판정/조치 체계
5. 보조: NIST / OWASP / CVSS 등

기존 `AUDIT_EVIDENCE_MAPPING.md`의 `미확인 / 0`은 기존 114개 감리결과서에서 직접 대표사례를 확인하지 못했다는 의미이며, 공식기준 근거가 없다는 뜻이 아니다.

기존 감리결과서 114개는 처음부터 다시 분석하지 않고 **사례근거 검증층**으로 재사용한다.

재평가 분류:
- A: 공식근거 강함 + 실무가치 높음 → 우선 구현
- B: 공식근거 있음 + 사례 제한적 → 구현 가능
- C: 예방·전략성 → 선택 구현
- D: 기존 Rule과 중복/흡수 가능 → 통합 검토
- E: 근거 부족 → 보류

**49개 공식기준 재평가가 완료되기 전에는 P3/P4 코딩을 시작하지 않는다.**

---

## 10. 현재 다음 작업

작업 제목:
**P3·P4 49개 Rule 공식기준 재매핑 및 차기 구현 우선순위 재평가**

다음 세션 순서:
1. 한 군데만 보고 판단하지 말고 코드 ↔ 문서 ↔ 테스트 결과 ↔ 이전 결정사항을 2~3회 교차검증하여 실제 상태 복원
2. 공식 기준/가이드 최신본 확보·버전 확인
3. 49개 재매핑 표준 컬럼 확정
4. 일부 Rule 샘플 재매핑으로 판정방식 검증
5. 49개 전체 재매핑
6. A/B/C/D/E 재분류
7. 차기 구현대상과 범위를 사용자와 확정
8. 그 뒤에만 상세설계 및 코드 구현

해커톤 제출 준비와 추가 구현 범위는 재평가 결과와 남은 일정을 함께 보고 결정한다.
