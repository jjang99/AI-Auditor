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
- 감리자료 114개 분석 결과를 재사용한다.
- Full Catalog 105는 감리 결과 때문에 임의 변경하지 않는다.
- 원래 미구현 85개 우선순위: P1 13 / P2 23 / P3 21 / P4 28
- P1 완료
- **P2 23개 완료**
- 새 감리자료는 전체 재분석 대신 증분 반영
- 신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Catalog/코드에 추가 금지

---

# 8. P1 확정

Canonical:
- `P1_IMPLEMENTATION_PLAN.md`

P1 13개는 전용 테스트, Registry 33개 통합검증, 전체 pytest 사용자 PC PASS 후 **33개 Freeze**로 확정한다.
새 결함이 없는 한 다시 구현하지 않는다.

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

## P2-C 확정 원칙
- CHG-008/010/FP-011은 명시적 변경관리 행과 대응 문서가 함께 업로드된 경우만 후보 생성
- CHG-010은 데이터/테이블/컬럼 영향이 명시된 변경에 한정
- FP-006은 구조형 FP 후보만 AI 판단
- 완전 동일 기능명 중복은 FP-002 책임영역
- 필요한 문서 한쪽만 업로드된 경우 AI 호출하지 않음

## P2-D 확정 원칙
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
- P2-D 전용 + Service 테스트 사용자 PC PASS
- P2-A/B/C/D + Registry 56 + 선택 UI + Catalog/MVP 통합 PASS
- 최종 `python -m pytest -q` 사용자 PC PASS
- 정확한 passed 숫자는 사용자 출력 미제공으로 임의 기록하지 않음

**P2 23/23 완료 / 실행 Rule 56개 Freeze 확정**

---

# 10. 배포 패키징 결정

기존 배포본:
- 기존 ZIP/MSI는 P1/P2 확장 전 빌드이므로 최종 제출본으로 간주하지 않는다.

Portable 최신 빌드:
- 스크립트: `scripts/build_portable.ps1`
- Folder: `dist/AI_Auditor/`
- ZIP: `dist/AI_Auditor_Portable.zip`
- SHA256: `dist/AI_Auditor_Portable.zip.sha256.txt`

MSI 최신 빌드:
- 스크립트: `installer/build_msi.ps1`
- Output: `installer/output/`

최종 순서:
1. 56개 Freeze 최신 main으로 Portable 재빌드
2. ZIP(EXE) 실제 실행 / DB / Local AI / 주요 Rule 스모크검증
3. 동일 `dist/AI_Auditor` 기준 MSI 재빌드
4. MSI 실제 설치 / 모델복사 / DB / Local AI 스모크검증
5. 성공 후 RULE_DESIGN / P2_IMPLEMENTATION_PLAN / README / HACKATHON_SUBMISSION 최종 현행화

---

# 11. 현재 다음 단계

1. 최신 문서 변경 로컬 반영
2. `scripts/build_portable.ps1` 실행
3. Portable ZIP 실제 스모크검증
4. `installer/build_msi.ps1` 실행
5. MSI 실제 설치/스모크검증
6. 최종 문서 현행화
7. Git 상태 확인 및 마무리

새 결함이 없는 한 완료된 P1/P2 범위를 다시 뜯지 않는다.
