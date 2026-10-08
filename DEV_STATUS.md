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
- 다음 단계: 최신 EXE 재빌드 / 폐쇄망 독립 실행 / 제출 마감

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

Matrix:

| Impact \ Likelihood | Low | Medium | High |
|---|---|---|---|
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

Critical은 High × High에서만 산정한다.

감리 개선판정은 Severity와 별도 관리한다.
- 개선권고유형: 필수 / 협의 / 권고
- 개선시점: 단기 / 장기
- 중요 여부: O / -
- CHG-001은 감리 개선판정 비적용(NULL)

---

## 최신 실제 검사 기준

Project: `tawga`
- Inspection ID: 40
- Score: 95
- Grade: A
- Issues: 7
- Critical 0 / High 0 / Medium 4 / Low 3

Grade는 A/B/C/D/E만 사용한다.
- A: 90 이상
- B: 80 이상
- C: 70 이상
- D: 60 이상
- E: 0~59

Export Report 지원:
- DOCX
- XLSX
- TXT

HWPX Export는 MVP에서 제외한다.

---

## Inspection 실행 UX 보완 — 2026-10-08 완료

- 검사 전 예상 검사시간 표시
- 현재 실행 Rule/단계 표시
- 실제 완료 Rule 수 / Progress Bar 표시
- 예상 남은시간 표시
- Local AI 실행 중 검사 취소 지원
- Local AI 종료를 UI thread를 막지 않는 방식으로 처리
- 취소 후 프로젝트명 / 등록 파일 / 검사기준 상태 유지
- 취소된 검사는 DB에 저장하지 않음
- 취소 후 다시 검사 가능
- 사용자 화면 확인 완료
- 전체 회귀테스트 정상 확인

---

# 6단계 Administration 데이터 관리 — 2026-10-08 최종 완료

## 구현 기능

Administration에 `3. 데이터 관리` 영역을 추가하였다.

### 전체 검사 이력 정리
- 모든 Inspection 삭제
- 모든 Issue 삭제
- Project 정보 유지
- 실행 전 영향범위 확인 Modal 표시
- 복구 불가 경고 표시
- 최종 실제 실행 버튼은 Danger Filled 스타일 사용

표시 예:
- 프로젝트 정보: N개 (유지)
- 검사 이력: N건 (삭제)
- 이슈: N건 (삭제)

### 프로젝트 관리
- 등록 프로젝트 목록 표시
- 프로젝트명 / 부서 / 검사 이력 수 / 이슈 수 표시
- 프로젝트별 삭제 가능
- 프로젝트 삭제 시 해당 Project의 Inspection + Issue도 함께 삭제
- 삭제 전 영향범위와 복구 불가 확인 Modal 표시

## DB 삭제 정책

SQLite 외래키에 ON DELETE CASCADE를 추가하지 않고 애플리케이션 Repository에서 명시적 삭제순서를 사용한다.

프로젝트 삭제:
`Issues → Inspections → Project`

전체 검사 이력 정리:
`Issues → Inspections`

Project 정보는 유지한다.

모든 삭제는 하나의 transaction으로 처리하고 오류 시 rollback한다.

## 주요 구현 파일

- `app/database/repositories/data_management_repository.py`
- `ui/data_management_dialogs.py`
- `ui/administration_page.py`
- `tests/test_data_management_repository.py`

Repository 주요 함수:
- `get_data_management_summary()`
- `get_projects_with_delete_impact()`
- `get_project_delete_impact(project_id)`
- `delete_all_inspection_history()`
- `delete_project_with_history(project_id)`

## UI 최종 기준

Administration 화면은 기존 한 화면 구조를 유지하며 메인 스크롤을 추가하지 않는다.

데이터 관리 카드:
- 제목과 현재 데이터 요약은 하나의 정보 그룹처럼 배치
- 전체 검사 이력 정리와 프로젝트 관리는 구분선 및 적절한 세로 간격으로 구분
- 카드 전체 높이는 기존 전체 화면 균형을 유지

Danger Action 계층:
- Administration `정리`: 위험작업 진입을 알리는 낮은 강조 Danger
- Administration `관리`: 관리 화면 진입이므로 기본 버튼
- 프로젝트 목록 `삭제`: 빨간 테두리 Danger
- 최종 확인 Modal `정리 실행 / 프로젝트 삭제`: 채운 빨강 Danger

프로젝트 관리 Modal:
- 프로젝트명과 메타정보 가독성 강화
- 카드 높이와 카드 간격을 축소하여 정보 밀도 개선
- Dark / Light 모두 삭제 버튼 시인성 확보

전체 검사 이력 정리 Modal:
- 본문 대비 과도한 Modal 크기 축소
- 영향범위/경고 문구 폰트 확대
- `프로젝트 정보: N개 (유지)` 문구 사용

## 실제 DB 검증

### 프로젝트 삭제 검증
테스트용 Project / Inspection / Issue를 실제 DB에 생성한 뒤 UI에서 삭제하였다.

검증 결과:
- 테스트 Project 삭제 확인
- 연결 Inspection 삭제 확인
- 연결 Issue 삭제 확인
- 고아 Inspection 0건
- 고아 Issue 0건

### 전체 검사 이력 정리 검증
실제 DB를 별도 백업한 뒤 전체 정리를 실행하였다.

검증 결과:
- Project 수 유지
- Inspection 0건
- Issue 0건

검증 후 백업 DB를 원복하여 기존 정상 검사데이터를 복구하였다.

## 자동테스트

`tests/test_data_management_repository.py`
- 현재 데이터 요약 집계
- 프로젝트별 삭제 영향범위 목록 집계
- 전체 검사 이력 정리 시 Project 유지
- 프로젝트 삭제 영향범위 조회
- 선택 프로젝트 트리만 삭제
- 없는 프로젝트 삭제 시 데이터 보존

전용 테스트 결과:
- `6 passed`

최신 전체 회귀테스트:
- 사용자 PC에서 `python -m pytest -q` 정상 PASS
- 실패 0건 확인

---

## 개발 완료 원칙

- 1~6단계는 완료 상태로 유지한다.
- 새로운 명시적 결함이 없는 한 완료된 기능을 다시 재설계하지 않는다.
- UI Freeze 상태를 유지한다.
- 기능 변경 시 기존 코드 / CURRENT_HANDOFF.md / DECISIONS.md / RULE_DESIGN.md / DEV_STATUS.md를 먼저 확인한다.
- 다음 개발은 기능 추가가 아니라 최종 배포/제출 마감 단계로 진행한다.

---

## 다음 작업

1. 최신 GitHub main / working tree 확인
2. 최신 PyInstaller EXE 재빌드
3. SQLite 외부 data 경로 확인
4. 아이콘/리소스 포함 확인
5. Qwen3-4B + llama.cpp runtime/model 포함 구조 확인
6. 인터넷 차단/폐쇄망 독립 실행 검증
7. EXE에서 실제 Inspection 1회
8. DB 저장/조회 확인
9. DOCX / XLSX / TXT Export 확인
10. 제출용 폴더 및 산출물 정리
