# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-10 KST
- 목적: 다음 대화/새 창에서 상태를 추측하지 않고 바로 이어가기 위한 최신 기준점

다음 세션 시작 순서:
`GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → README.md / HACKATHON_SUBMISSION.md → 실제 코드 및 installer 관련 파일 → 이전 대화/저장된 결정사항`

## 작업 전 필수 다중 교차검증

새 작업을 바로 시작하지 않는다.

- GitHub 실제 코드 / 프로젝트 구조 / CURRENT_HANDOFF.md / DECISIONS.md / RULE_DESIGN.md / DEV_STATUS.md / README.md / HACKATHON_SUBMISSION.md / 실제 코드 및 installer 관련 파일 / 기존 테스트 결과 / 이전 대화 / 저장된 결정사항을 먼저 확인한다.
- 한 번 확인한 내용만 믿고 진행하지 않는다. 최소 2~3회 서로 다른 관점으로 재확인한다.
- `코드 ↔ 문서 ↔ 테스트 결과 ↔ 이전 대화/결정사항`을 교차검증하여 서로 일치하는지 확인한다.
- 충돌 시 최신 GitHub 실제 코드와 실제 동작을 우선 확인하되, 기존 확정 결정사항과의 충돌 여부를 다시 검토한다.
- 충분히 확인되지 않은 상태에서는 추측으로 수정하지 않고, 이미 완료된 기능을 다시 만들지 않는다.
- 검증 후 현재 구조를 가장 적게 흔들면서 안전하고 효율적인 방안을 선택한다.
- 가능한 작업은 먼저 GitHub 코드와 자료를 직접 확인·수정하고, 사용자에게는 실제 필요한 로컬 명령과 확인사항만 단계별로 안내한다.

---

# 1. 전체 완료 상태

- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 MVP 대표 Rule 20개 선정 — 완료
- 4단계 문서 Parser + Rule/AI/Hybrid 검사 Engine — 완료
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료
- 최종 EXE 안정화 — 완료
- 감리결과서 114개 실무 분석 / 105개 전체 Rule 매핑 — 완료
- MVP 20개 실제 감리사례 실증검증 — 완료
- 실증검증 우선 보완 5개 수정 및 전체 회귀검증 — 완료
- 감리분석 보완사항 반영 후 ZIP(EXE) 재빌드·스모크검증 — 완료
- WiX 기반 MSI 설치형 패키지 제작·실설치·Local AI 스모크검증 — 완료
- `HACKATHON_SUBMISSION.md` 최종 구현·검증·배포 상태 현행화 — 완료

**1~6단계, 감리자료 분석, MVP20 실증검증, 감리분석 보완 5개, 최종 ZIP(EXE)/MSI 패키징은 새 결함이 없는 한 다시 구현·재설계·재분석하지 않는다.**

---

# 2. 최종 검사체계

Full Rule Catalog 105개:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23

MVP 실제 실행 20개:
- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4

실행방식:
- Rule 3
- AI 6
- Hybrid 11

Full Catalog 105개와 MVP 실제 실행 20개는 서로 다른 개념으로 관리한다.

---

# 3. 최종 EXE 안정화 기준 — 2026-10-08 완료

최종 배포 구조:
- `dist/AI_Auditor/AI_Auditor.exe`
- `dist/AI_Auditor/runtime/llama.cpp/llama-server.exe`
- `dist/AI_Auditor/models/Qwen3-4B-Q4_K_M.gguf`
- 실행 시 `dist/AI_Auditor/data/ai_auditor.db` 자동 생성

확인 완료:
- PyInstaller onedir 최신 EXE 빌드 정상
- 최신 EXE 실행 정상
- SQLite 외부 DB 경로 정상
- Local AI runtime/model 외부 경로 정상
- 인터넷 차단 상태에서 DOCX 1개 + REQ-003 Local AI 검사 정상 완료
- 폐쇄망 독립 실행 가능 확인
- Project Detail Export: DOCX / XLSX / TXT 정상
- Reports Export: Project Detail과 동일한 DOCX / XLSX / TXT 정상
- Export 결과에 최신 판정정보 반영
  - Impact / 근거
  - Likelihood / 근거
  - Severity / 판정근거
  - 개선권고유형
  - 개선시점
  - 중요 여부
  - 카테고리
- Administration 데이터 관리 정상
- 검사 예외 발생 시 빈 오류창 대신 `오류 유형 + 상세 내용` 표시하도록 보완
- 오류 진단 전용 테스트 정상
- 전체 `python -m pytest -q` 사용자 PC 정상 PASS

참고:
- 다수 실제 문서 + MVP 20개 전체 검사에서 한 차례 예외가 있었으나, 인터넷 차단 상태의 단일 DOCX + REQ-003 검사는 정상 완료되어 폐쇄망 Local AI 자체 문제는 아님을 확인했다.
- 향후 동일 예외 재현 시 새 오류 진단 메시지로 원인을 특정한다.

---

# 4. Export 최종 기준

지원:
- DOCX
- XLSX
- TXT

Project Detail과 Reports는 동일한 최종 보고서 모델을 사용한다.
HWPX Export는 MVP에서 제외한다.

---

# 5. Local AI / Severity 기준

기본 Local AI:
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- reasoning off

AI 역할:
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

최종 Severity:
`Impact × Likelihood → deterministic Severity Matrix`

AI가 최종 Severity를 직접 결정하지 않는다.

감리 개선판정은 Severity와 별도 관리한다.
- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -
- CHG-001은 비적용(NULL)

---

# 6. Administration 데이터 관리 기준

전체 검사 이력 정리:
`Issues → Inspections`
- Project 유지

프로젝트 삭제:
`Issues → Inspections → Project`

모든 삭제는 transaction으로 처리하고 오류 시 rollback한다.
실제 DB 검증 완료.

---

# 7. 절대 되돌리지 말아야 할 사항

- 2026-09-18 UI Freeze 전체 방향
- Project Detail 정렬 QComboBox
- HWPX MVP 제외
- Grade A/B/C/D/E
- Final Severity는 Matrix 계산
- Severity와 감리 개선판정 분리
- CHG-001 감리판정 비적용
- Qwen3-4B Q4_K_M 기본 Local AI
- Inspection 취소 후 입력상태 유지 + DB 미저장
- Stage 6 데이터 삭제 정책
- Project Detail / Reports Export 3종 통일
- 검사 오류는 빈 Modal이 아니라 오류 유형/상세내용 표시
- 작업 전 2~3회 다중 교차검증 원칙
- 배포명칭은 `ZIP(EXE)`와 `MSI 설치형`으로 구분
- MSI 설치형의 2GB 초과 GGUF 모델은 MSI File table에 직접 포함하지 않음

---

# 8. 감리결과서 기반 105개 실무 검증 — 2026-10-09 완료

분석 기준:
- 사용자 업로드 감리 관련 파일 114개
- 형식: PDF 94 / DOCX 19 / XLSX 1
- 독립 보고서 기준 2019~2025 자료 확인
- 2025 보고서 일부에 2026년 후속 일정 포함
- 완전 동일본 3쌍은 중복 빈도에서 제외
- 초안/수정본, PDF/DOCX, 전문별첨은 내용 차이 검토를 위해 유지
- 요약 지적표 → 상세본문 → 전문분야/별첨의 3회 교차검증 수행

Canonical 분석문서:
- `AUDIT_EVIDENCE_MAPPING.md`

105개 전체 분류:
- MVP 구현 20개
- 미구현 85개

미구현 85개 구현 우선순위:
- P1: 13개
- P2: 23개
- P3: 21개
- P4: 28개

P1 13개:
- AUD-008
- AUD-010
- AUD-014
- AUD-016
- AUD-018
- AUD-020
- AUD-022
- AUD-023
- REQ-007
- REQ-012
- REQ-017
- FP-002
- FP-008

신규 Rule 후보:
- 9개 유지 + 1개 조건부 검토
- 기존 105개에는 아직 추가하지 않음
- 사용자 승인 전 Catalog 변경 금지

후보:
- NEW-PM-01 프로젝트 진척·지연 및 만회계획 점검
- NEW-PM-02 위험·이슈·Action Item 사후관리 점검
- NEW-DATA-01 데이터 모델·물리DB 구조·무결성 적정성 점검
- NEW-DATA-02 데이터 품질진단·이관·전환 정합성 점검
- NEW-ARCH-01 아키텍처·인프라 구성 및 자원 적정성 점검
- NEW-PERF-01 성능·용량·부하·튜닝 적정성 점검
- NEW-SEC-01 일반 보안취약점·개발보안 진단 및 조치 점검
- NEW-UX-01 UI/UX 사용성·편의성 적정성 점검
- NEW-OPS-01 운영절차·백업복구·서비스관리 준비도 점검
- NEW-REL-01 교육·인수인계·시스템전환·하자보수 준비도 점검 — 조건부 통합 검토

재사용 원칙:
- 향후 85개 Rule 구현 시 114개 감리자료를 처음부터 다시 분석하지 않는다.
- 기본 구현순서는 P1 → P2 → P3 → P4를 사용한다.
- 새 감리자료가 추가되면 기존 매핑에 증분 반영한다.
- `미확인`은 삭제 대상이 아니라 현재 코퍼스에서 직접 감리사례가 부족한 전략/예방 Rule을 뜻한다.

---

# 9. MVP 20개 감리사례 실증검증 — 2026-10-09 완료

Canonical 문서:
- `MVP20_AUDIT_VALIDATION.md`

1차 실증검증에서 즉시 보완이 필요했던 5개:
- AUD-001 필수 산출물 누락
- REQ-002 요구사항 내용 중복
- REQ-003 요구사항 모호성
- REQ-009 요구사항 설계 반영 정합성
- FP-009 FP 산정값 재계산

보완 완료:
- AUD-001: 업로드된 `산출물목록`을 1순위 기준으로 사용하고 테일러링 미적용/제외, 시기미도래/해당없음을 제외한 뒤 실제 업로드 산출물과 비교한다. 기준자료가 없으면 임의 목록을 만들지 않는다.
- REQ-002: 동일문구 비교를 넘어 요구사항명/의미 유사 후보를 AI 비교대상으로 확장했다.
- REQ-003: `적절히/필요시` 외 정량목표·횟수·조건 누락 및 `협의 후 확정`형 모호성 후보까지 확장했다.
- REQ-009: 요구사항 정의/기술/추적 문서와 화면·인터페이스·테이블·데이터·프로그램·아키텍처 등 설계 산출물을 교차검증하도록 변경했다.
- FP-009: 기존 단일 산식 검사에 더해 XLS/XLSX의 기능유형·복잡도 또는 RET/FTR+DET·기능개수·기능점수 기반 구조형 재계산을 추가했다.

신규/핵심 보완 파일:
- `rules/core/deliverable_baseline.py`
- `rules/core/requirement_design_alignment.py`
- `rules/core/fp_calculator.py`
- `rules/core/document_engine.py`
- `rules/core/ai_engine.py`
- `rules/core/hybrid_engine.py`
- `app/services/inspection_service.py`
- `tests/test_audit_case_regressions.py`
- `tests/test_fp009_audit_regressions.py`

검증:
- 단계별 targeted regression 모두 PASS
- 기존 AI/Hybrid/MVP 통합 테스트 PASS
- Document Rule Engine 회귀 PASS
- 최종 `python -m pytest -q` 사용자 PC 실패 0건 확인

남은 `부분적합/실무사례 제한` Rule은 제출 차단 결함으로 보지 않으며 후속 정밀확장 대상으로 관리한다.

---

# 10. 최종 배포 패키징 — 2026-10-10 완료

## ZIP(EXE)

감리분석 우선 보완 5개가 반영된 최신 코드로 PyInstaller onedir를 다시 빌드했다.

최종 구성:
- `AI_Auditor.exe`
- `runtime/llama.cpp/llama-server.exe`
- `models/Qwen3-4B-Q4_K_M.gguf`
- `data/` — DB는 포함하지 않고 첫 실행 시 자동 생성

검증:
- 최신 EXE 실행 정상
- runtime/model 존재 확인
- 깨끗한 DB 자동 생성 확인
- `zip_smoke_req003.docx` + REQ-003 실제 Local AI 검사 정상
- 검사 결과 DB 저장 및 Project Detail 표시 정상
- 스모크검증 후 배포본 DB 삭제하여 clean 상태로 ZIP 생성

사용자 PC 최종 ZIP 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

## MSI 설치형

빌드 도구:
- Microsoft .NET SDK 10.0.401 x64
- WiX Toolset 7.0.0

설치원칙:
- 현재 frozen 실행 구조가 EXE 옆 `data/`에 SQLite DB를 생성하므로 MSI는 per-user로 설치한다.
- 실제 설치 위치: `%LOCALAPPDATA%\Programs\AI Auditor`
- `Qwen3-4B-Q4_K_M.gguf` 실제 크기: 2,497,280,256 bytes
- WiX/Windows Installer File table의 단일 파일 2GB 제한으로 모델을 MSI File 항목에 직접 포함하지 않는다.
- 최종 MSI 세트는 MSI + CAB + 외부 GGUF + 설치 Launcher CMD로 구성한다.
- 사용자는 `AI_Auditor_Setup.msi`를 단독 실행하지 않고 `AI_Auditor_Install.cmd`를 실행한다.
- Launcher가 MSI 설치 후 `robocopy`로 모델을 `models/`에 복사하고 원본/대상 파일 크기를 비교한다.

최종 MSI 설치형 구성:
- `AI_Auditor_Install.cmd`
- `AI_Auditor_Setup.msi`
- `aia1.cab`
- `aia2.cab`
- `Qwen3-4B-Q4_K_M.gguf`

사용자 PC 최종 MSI 설치형 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

실설치 검증:
- MSI 프로그램 설치 정상
- 설치 EXE 실행 정상
- `runtime/llama.cpp/llama-server.exe` 존재 확인
- 모델 복사 정상 및 크기 2,497,280,256 bytes 일치
- `data/ai_auditor.db` 첫 실행 자동 생성 확인
- 동일 REQ-003 스모크 문서로 Local AI 실제 검사 정상
- 결과 생성 및 DB 저장 정상

MSIX는 인증서/정책 복잡성 때문에 현재 최종 배포범위에서 제외한다.
Qwen3-4B Q4_K_M 모델은 현재 검증 품질 기준을 유지하기 위해 임의로 경량 모델로 교체하지 않는다.

---

# 11. 다음 단계

현재 해커톤 제출용 핵심 요약문서 `HACKATHON_SUBMISSION.md`의 최종 현행화는 완료했다.

제출 전 남은 작업:
1. README / CURRENT_HANDOFF / DECISIONS / RULE_DESIGN / DEV_STATUS / HACKATHON_SUBMISSION 상호 일치 최종 확인
2. 제출 대상 파일과 배포 패키지 최종 체크리스트 정리
3. 필요 시 시연·발표용 핵심 흐름 정리

제출 후:
1. 신규 Rule 후보 사용자 검토 및 추가 여부 결정
2. 미구현 85개를 `AUDIT_EVIDENCE_MAPPING.md`의 P1 → P2 → P3 → P4 순서로 구현
3. 105개 전체 통합 검증

**다음 세션에서 감리결과서 114개를 처음부터 다시 분석하지 않는다.**
**MVP 20개 실증검증과 우선 보완 5개를 다시 반복하지 않는다.**
**ZIP(EXE)/MSI 패키징과 동일 스모크검증도 새 결함이 없는 한 다시 반복하지 않는다.**