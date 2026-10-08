# AI Auditor 개발 현황

## 기준일
- 2026-10-08

## 현재 전체 상태
- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 해커톤 MVP 대표 Rule 20개 확정 — 완료
- 4단계 MVP 문서 검사 Engine 구현 — 완료
- 5단계 Administration·Inspection·Local AI·Severity·감리 개선판정 통합 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료
- 최종 EXE 안정화 — 완료
- 다음 단계: 감리결과서 분석 → 105개 전체 Rule 매핑 → MVP 20개 실증검증 → 제출 마감

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
- Git working tree clean 확인

## 참고 이슈

다수 실제 문서 + MVP 20개 전체 검사에서 한 차례 예외가 발생했으나, 폐쇄망 상태의 단일 DOCX + REQ-003 Local AI 검사는 정상 완료되어 폐쇄망 Local AI 자체 결함은 아닌 것으로 확인했다.
동일 예외가 재현되면 새 오류진단 메시지를 기준으로 원인을 특정한다.

---

# 감리결과서 활용 원칙 — 다음 단계

감리결과서는 MVP 20개만 검증하기 위한 자료가 아니다.

분석 결과는 **Full Rule Catalog 105개 전체와 매핑**한다.

진행 원칙:
- 감리 지적사항 추출
- 유사 지적 통합 / 중복 제거 / 일반화
- 감리 지적유형 ↔ 105개 전체 Rule 매핑
- 현재 MVP 20개 구현여부 확인
- 미구현 85개 Rule의 향후 구현 우선순위 산정
- 105개에 없는 반복·중요 지적은 신규 Rule 후보화
- 향후 85개 구현 시 감리결과서를 처음부터 다시 분석하지 않고 기존 매핑표를 재사용

---

## 다음 작업

1. 감리결과서 지적사항 추출
2. 유사 지적 통합 / 중복 제거 / 일반화
3. 감리 지적유형 ↔ 105개 전체 Rule 매핑
4. MVP 20개 / 미구현 85개 / 신규 Rule 후보 분류
5. 실제 감리 사례로 MVP 20개 검증
6. 최종 문서화·제출
7. 제출 후 나머지 85개 Rule 순차 구현
8. 105개 전체 통합 검증
