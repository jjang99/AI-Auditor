# AI Auditor 개발 현황

## 기준일
- 2026-10-09

## 현재 전체 상태
- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 해커톤 MVP 대표 Rule 20개 확정 — 완료
- 4단계 MVP 문서 검사 Engine 구현 — 완료
- 5단계 Administration·Inspection·Local AI·Severity·감리 개선판정 통합 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료
- 최종 EXE 안정화 — 완료
- 감리결과서 114개 분석 / 105개 전체 Rule 실무 매핑 — 완료
- MVP 20개 실제 감리사례 실증검증 — 완료
- 우선 보완 5개 구현 및 전체 회귀검증 — 완료
- 다음 단계: 해커톤 제출용 최종 문서화·정리

---

## 최종 검사체계

제품 전체 검사체계는 5대 영역 / 총 105개이다.

- 감리 사전점검(AUD): 24개
- 요구사항 정합성(REQ): 28개
- 변경영향도(CHG): 18개
- FP 검증(FP): 12개
- AI 특화 검증(AI): 23개

해커톤 MVP 실제 실행 대상은 20개이다.

- AUD: 4개
- REQ: 6개
- CHG: 4개
- FP: 2개
- AI: 4개

실행방식:
- Rule: 3개
- AI: 6개
- Hybrid: 11개

Full Rule Catalog 105개와 실제 실행 MVP 20개는 서로 다른 개념으로 관리한다.

---

## 문서 Parser

최종 지원 형식 9종:
- DOCX
- DOC
- XLSX
- XLS
- PDF
- PPTX
- PPT
- HWPX
- HWP

공통 구조:
`원본 문서 → 형식별 Parser → ParsedDocument / DocumentBlock → Rule / AI / Hybrid 검사`

스캔 이미지 기반 PDF OCR은 현재 MVP 범위에서 제외한다.

---

## 문서 검사 Engine

실행 흐름:
`Inspection → Full Catalog 선택상태 → MVP 20 추출 → Parser → Rule / AI / Hybrid → DocumentInspectionEngine → Issue → DB → UI`

기존 소스코드 정적분석 Rule Engine은 삭제하지 않고 향후 확장영역으로 보존한다.

---

## Local AI / Severity

기본 Local AI:
- Qwen3-4B Q4_K_M
- llama.cpp b11312
- reasoning off
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 역할:
- Impact 판정
- Impact 근거
- Likelihood 판정
- Likelihood 근거

최종 Severity는 AI가 직접 결정하지 않는다.

`Impact × Likelihood → deterministic Severity Matrix`

Critical은 High × High에서만 산정한다.

감리 개선판정은 Severity와 별도 관리한다.
- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -
- CHG-001은 감리 개선판정 비적용(NULL)

---

## Export 최종 기준

지원 형식:
- DOCX
- XLSX
- TXT

Project Detail과 Reports의 보고서 내보내기는 동일한 최종 보고서 구조를 사용한다.

최종 포함정보:
- Impact / Impact 근거
- Likelihood / Likelihood 근거
- Severity / Severity 판정근거
- 개선권고유형
- 개선시점
- 중요 여부
- 카테고리

HWPX Export는 MVP에서 제외한다.

---

# 최종 EXE 안정화 — 2026-10-08 완료

## 배포 구조

- `dist/AI_Auditor/AI_Auditor.exe`
- `dist/AI_Auditor/runtime/llama.cpp/llama-server.exe`
- `dist/AI_Auditor/models/Qwen3-4B-Q4_K_M.gguf`
- `dist/AI_Auditor/data/ai_auditor.db`

## 검증 완료

- PyInstaller 6.22.3 onedir 빌드 정상
- 최신 EXE 실행 정상
- runtime/model/data 외부 경로 정상
- 인터넷 차단 상태에서 Local AI 검사 정상
- DOCX 1개 + REQ-003 검사 정상 완료
- 결과 생성 및 DB 저장 정상
- Project Detail Export 정상
- Reports Export 정상
- DOCX/XLSX/TXT 실제 파일 열림 정상
- Administration 데이터 관리 정상
- 검사 예외 발생 시 빈 오류창 대신 오류 유형/상세내용 표시
- 오류진단 targeted test 정상
- 전체 `python -m pytest -q` 정상 PASS

## 참고 이슈

다수 실제 문서 + MVP 20개 전체 검사에서 한 차례 예외가 발생했으나, 폐쇄망 상태의 단일 DOCX + REQ-003 Local AI 검사는 정상 완료되어 폐쇄망 Local AI 자체 결함은 아닌 것으로 확인했다.
동일 예외가 재현되면 새 오류진단 메시지를 기준으로 원인을 특정한다.

---

# 감리결과서 기반 실무 검증 — 2026-10-09 완료

감리결과서는 MVP 20개만 검증하기 위한 자료가 아니라 Full Rule Catalog 105개 전체의 실무근거로 분석하였다.

분석 원본:
- 114개
- PDF 94 / DOCX 19 / XLSX 1
- 독립 보고서 연도 2019~2025
- 일부 2025 보고서에 2026년 후속 일정 포함

분석 절차:
- 파일 인벤토리/중복·버전 확인
- 감리 지적사항 추출
- 유사 지적 통합 / 중복 제거 / 일반화
- 요약 지적표 재검증
- 상세본문 재검증
- FP / AI-RAG / 보안 / 데이터 / UI-UX 전문분야·별첨 교차검증
- 감리 지적유형 ↔ 105개 전체 Rule 매핑
- MVP 20 / 미구현 85 / 신규 Rule 후보 분류

Canonical 분석문서:
- `AUDIT_EVIDENCE_MAPPING.md`

미구현 85개 구현 우선순위:
- P1: 13개
- P2: 23개
- P3: 21개
- P4: 28개

P1:
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
- 9개 유지 + 1개 조건부
- 현재 105개 Catalog에는 추가하지 않음
- 사용자 승인 전 임의 추가 금지

핵심 신규 후보:
- 프로젝트 진척·지연/만회계획
- 위험·이슈·Action Item 사후관리
- 데이터 모델/물리DB 구조·무결성
- 데이터 품질진단/이관·전환 정합성
- 아키텍처·인프라·자원 적정성
- 성능·용량·부하·튜닝
- 일반 보안취약점·개발보안
- UI/UX 사용성
- 운영절차·백업복구·서비스관리
- 교육·인수인계·시스템전환·하자보수 준비도(조건부)

재사용 정책:
- 향후 85개 구현 시 감리자료 114개를 처음부터 다시 분석하지 않는다.
- `AUDIT_EVIDENCE_MAPPING.md`를 구현 우선순위와 실무근거의 기준점으로 재사용한다.
- 새 감리자료는 증분 반영한다.
- `미확인` Rule은 삭제 대상이 아니라 현재 코퍼스에서 직접사례가 부족한 예방/전략 Rule이다.

---

# MVP 20개 실제 감리사례 실증검증 — 2026-10-09 완료

Canonical 문서:
- `MVP20_AUDIT_VALIDATION.md`

1차 검증에서 실제 감리사례보다 구현범위가 좁아 `보완필요`로 확인된 5개:
- AUD-001
- REQ-002
- REQ-003
- REQ-009
- FP-009

보완 완료:
- AUD-001: 산출물목록 우선 + 테일러링 제외/미적용 + 시기미도래 제외 + 실제 업로드 파일 비교
- REQ-002: 동일문구 중심에서 요구사항명/의미 유사 후보까지 비교 확장
- REQ-003: 정량목표·횟수·조건 누락 및 협의 후 확정형 모호성 후보 확장
- REQ-009: 요구사항 문서 ↔ 화면/인터페이스/데이터/프로그램/아키텍처 등 복수 설계 산출물 교차검증 추가
- FP-009: 기존 한 줄 산식 + XLS/XLSX 구조형 FP 행 재계산 추가

신규/보완 구현:
- `rules/core/deliverable_baseline.py`
- `rules/core/requirement_design_alignment.py`
- `rules/core/fp_calculator.py`
- `rules/core/document_engine.py`
- `rules/core/ai_engine.py`
- `rules/core/hybrid_engine.py`
- `app/services/inspection_service.py`

회귀검증:
- 실제 감리사례 형태의 targeted regression 추가
- AUD-001 / REQ-002 / REQ-003 / REQ-009 / FP-009 개별 검증 정상
- 기존 AI/Hybrid/MVP 통합 테스트 정상
- 최종 `python -m pytest -q` 사용자 PC 실패 0건 확인

남은 정밀보완 후보는 제출 차단 결함으로 보지 않는다.
- REQ-001 적용 문서/ID 범위
- REQ-018 완전한 역방향 추적
- CHG-001 서로 다른 산출물 간 변경근거 연결
- AI-009/019/022 관리체계 부재검사
- AUD-002 구조형 빈 셀/필수열 검증

---

## 다음 작업

1. 해커톤 제출용 최종 문서화·정리
2. 신규 Rule 후보는 사용자 검토 후 추가 여부 결정
3. 제출 후 나머지 85개 Rule을 `AUDIT_EVIDENCE_MAPPING.md`의 P1 → P2 → P3 → P4 순서를 기본으로 구현
4. 105개 전체 통합 검증

감리결과서 114개 분석과 MVP 20개 실증검증은 완료 상태이므로 다음 작업에서 처음부터 반복하지 않는다.
