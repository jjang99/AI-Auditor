# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발의 **현재 최종 확정 기준(Canonical Decisions)** 을 기록한다.
과거 세부 변경 이력은 Git history에서 확인하며, 본 문서와 충돌하는 과거 문구는 본 문서의 최신 기준으로 대체한다.

---

# 1. 개발 진행 원칙

- 상태를 추측하지 않는다.
- 새 작업 시작 시 `GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → P2_IMPLEMENTATION_PLAN.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드/installer → 이전 대화` 순으로 확인한다.
- 코드 ↔ 문서 ↔ 테스트 ↔ 이전 결정사항을 최소 2~3회 교차검증한다.
- 이미 완료된 범위는 새 결함 없이 재구현하지 않는다.
- 기능 단위 `구현 → 전용 테스트 → Registry 활성 → 통합 회귀 → 전체 회귀 → 문서 현행화` 순서를 유지한다.
- 검증되지 않은 Rule을 Registry에 선등록하지 않는다.
- 사용자가 개발 초보이므로 로컬 명령은 PowerShell 기준 한 번에 하나씩 안내한다.

---

# 2. UI / 제품 고정 기준

- 2026-09-18 UI Freeze 유지
- 기본 Dark Mode / Light Mode 지원
- Home / Projects / Inspection / Reports / Administration 구조 유지
- 명시적 결함 또는 기능상 필수 변경 외 UI 임의 재설계 금지
- Grade A/B/C/D/E만 사용
- 스캔 이미지 PDF OCR 제외
- HWPX Report Export 제외

---

# 3. 최종 검사체계 / 현재 실행범위

Full Catalog 105:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23

최초 MVP20 기준선:
- AUD 4 / REQ 6 / CHG 4 / FP 2 / AI 4
- Rule 3 / AI 6 / Hybrid 11

P1 13개:
- 2026-10-10 구현·Registry 활성·전체 회귀 완료
- P1 Freeze 기준: 실행 Rule 33개

P2-A 7개:
- AUD-015 / AUD-019 / REQ-016 / REQ-020 / CHG-005 / FP-007 / AI-023
- 전용 테스트 PASS
- Registry 40개 통합검증 PASS
- 전체 `python -m pytest -q` 사용자 PC PASS

현재 실제 실행 Registry:
- **40개 = MVP20 + P1 13 + P2-A 7**
- Rule 14 / AI 6 / Hybrid 20

`MVP20`은 최초 기준선 명칭으로 유지하며, Full Catalog 105와 실행 Registry 수는 별도 개념이다.

---

# 4. Rule / Issue / Severity 역할 분리

- Rule = 무엇을 어떤 방식으로 검사할 것인가
- Issue = 실제 검사에서 무엇이 발견되었는가
- Severity = 발견 Issue의 위험도
- 감리 개선판정 = 감리 대응 관점 개선 방향

Rule 자체에 최종 Severity를 고정하지 않는다.

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
`models/`, `runtime/`은 Git 소스관리 대상에서 제외하며 프로그램이 인터넷에서 자동 다운로드하지 않는다.

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

# 7. Administration 데이터 관리

삭제 정책:
- 전체 검사 이력 정리: Issues → Inspections, Project 유지
- Project 삭제: Issues → Inspections → Project
- Repository transaction 사용, 오류 시 rollback
- 새 ON DELETE CASCADE를 강제하지 않음

기존 실제 삭제검증과 자동테스트 완료 상태를 유지한다.

---

# 8. 감리자료 기반 실무검증 결정

Canonical:
- `AUDIT_EVIDENCE_MAPPING.md`

확정:
- 감리자료 114개 분석 결과를 재사용한다.
- Full Catalog 105는 감리 결과 때문에 임의 변경하지 않는다.
- 원래 미구현 85개 우선순위: P1 13 / P2 23 / P3 21 / P4 28
- P1 완료, P2 현재 진행
- 새 감리자료는 전체 재분석 대신 증분 반영
- 신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Catalog/코드에 추가 금지

---

# 9. P1 확정

Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개는 전용 테스트, Registry 33개 통합검증, 전체 pytest 사용자 PC PASS 후 **33개 Freeze**로 확정한다.
새 결함이 없는 한 다시 구현하지 않는다.

---

# 10. P2 구현 결정

Canonical:
- `P2_IMPLEMENTATION_PLAN.md`

P2 총 23개:
- AUD 4 / REQ 6 / CHG 3 / FP 3 / AI 7
- Rule 7 / AI 5 / Hybrid 11

Batch:
- P2-A 7개 — **완료**
- P2-B 6개 — **현재 구현 완료, 전용/Service 검증 전 Registry 비활성**
- P2-C 4개
- P2-D 6개

P2-A 완료 기준:
- P2-A 전용 테스트 PASS
- Registry 40개 + 선택 UI + Full Catalog/MVP/P1 통합 PASS
- 전체 pytest PASS

P2-B 대상:
- AUD-005 문서 간 용어 일관성 — 교차문서 AI
- AUD-021 인터페이스 문서정보 일치 — 교차문서 Hybrid
- REQ-006 요구사항 완전성 — AI
- REQ-021 요구사항 상태·승인정보 정합성 — Hybrid
- REQ-027 요구사항 출처·상위요구 및 추가기능 근거 — Hybrid
- REQ-028 요구사항 정합성 종합 위험 — REQ 지적 종합 AI

P2-B 원칙:
- AUD-005는 동일 ID가 여러 문서에서 실제 다른 명칭으로 사용된 경우만 AI 후보
- AUD-021은 동일 인터페이스 ID의 송수신/방식/주기/데이터 정의가 문서 간 다를 때만 후보
- REQ-021은 상태/승인정보의 명확한 구조적 모순만 후보
- REQ-027은 출처/상위요구 필드가 존재하는 구조에서 근거 공란만 후보화하고 N/A/비대상 등 제외
- REQ-028은 원문 일반 요약이 아니라 앞선 REQ 실제 지적사항이 있을 때만 종합 실행
- 전용/Service 검증 전에 Registry 활성 금지

P2 전체 완료 목표:
- **56개 실행 Rule = MVP20 + P1 13 + P2 23**
- Rule 14 / AI 11 / Hybrid 31

---

# 11. 배포 패키징 결정

배포형태:
- ZIP(EXE)
- MSI 설치형

기존 배포본:
- ZIP: `C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`
- MSI: `C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

최신 결정:
- 기존 ZIP/MSI는 P1/P2 확장 전 빌드이므로 최종 제출본으로 간주하지 않는다.
- P2 23개 전체 구현·Registry 활성·전체 회귀 후 **56개 Freeze**를 만든다.
- 그 뒤 56개 최신 main으로 ZIP(EXE) 재빌드 → 실제 실행/Local AI/DB/주요 Rule 스모크검증
- 동일 최신 dist로 MSI 재빌드 → 실제 설치/모델복사/DB/Local AI 스모크검증
- 성공 후 README / HACKATHON_SUBMISSION을 최종 배포완료 상태로 갱신한다.

---

# 12. 현재 다음 단계

1. P2-B 소스 로컬 반영
2. `tests/test_p2_b_rules.py` + `tests/test_p2_b_service.py` 전용검증
3. 정상일 때만 P2-B 6개 Registry 활성 → 46개
4. Registry/선택/P1/P2-A 통합검증
5. 전체 pytest
6. P2-B 완료 문서 현행화
7. P2-C 진행

새 결함이 없는 한 완료된 P1/P2-A 범위를 다시 뜯지 않는다.
