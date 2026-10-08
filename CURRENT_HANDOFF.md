# AI Auditor CURRENT HANDOFF

## 기준 시각
- 2026-10-08 KST
- 목적: 다음 대화/새 창에서 상태를 추측하지 않고 바로 이어가기 위한 최신 기준점

다음 세션 시작 순서:
`GitHub main → CURRENT_HANDOFF.md → DECISIONS.md → RULE_DESIGN.md → DEV_STATUS.md → 실제 코드`

---

# 1. 전체 완료 상태

- 1단계 기존 Rule 복원·재분류 — 완료
- 2단계 최종 5대 검사영역 / 105개 Rule 확정 — 완료
- 3단계 MVP 대표 Rule 20개 선정 — 완료
- 4단계 문서 Parser + Rule/AI/Hybrid 검사 Engine — 완료
- 5단계 제품 통합 / Local AI / Severity / 감리 개선판정 — 완료
- Inspection 실행 UX 보완 — 완료
- 6단계 Administration 데이터 관리 — 완료

**1~6단계는 새 결함이 없는 한 다시 구현하거나 재설계하지 않는다.**

---

# 2. 최종 검사체계

Full Rule Catalog:
- AUD 24
- REQ 28
- CHG 18
- FP 12
- AI 23
- 합계 105

MVP 실제 실행:
- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4
- 합계 20

실행방식:
- Rule 3
- AI 6
- Hybrid 11

---

# 3. 문서 Parser

지원 9종:
- DOCX / DOC
- XLSX / XLS
- PDF
- PPTX / PPT
- HWPX / HWP

공통 구조:
`원본 문서 → Parser → ParsedDocument / DocumentBlock → DocumentInspectionEngine`

OCR 기반 스캔 PDF는 현재 MVP 제외.

---

# 4. Local AI / Severity

기본 모델:
- Qwen3-4B Q4_K_M

Runtime:
- llama.cpp b11312

설정:
- reasoning off
- temp 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI 역할:
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

최종 Severity:
- deterministic Matrix 계산
- AI가 직접 결정하지 않음

감리 개선판정:
- 필수 / 협의 / 권고
- 단기 / 장기
- O / -
- Severity와 독립
- CHG-001은 비적용(NULL)

---

# 5. 최신 실제 Inspection 기준

Project: `tawga`
- Inspection ID: 40
- Score: 95
- Grade: A
- Issues: 7
- Critical 0
- High 0
- Medium 4
- Low 3

Grade:
- A 90+
- B 80+
- C 70+
- D 60+
- E 0~59

F는 사용하지 않는다.

---

# 6. Export

지원:
- DOCX
- XLSX
- TXT

HWPX:
- MVP 제외
- 다시 임의 복원/재실험하지 않음

---

# 7. Inspection 실행 UX 확정

- 예상 검사시간 표시
- 현재 Rule/단계 표시
- 완료 Rule 수 / Progress Bar 표시
- 예상 남은시간 표시
- Local AI 실행 중 취소 지원
- 취소 시 UI thread block 없음
- 취소 후 프로젝트명 / 파일 / 검사기준 유지
- 취소 결과 DB 미저장
- 취소 후 재검사 가능

사용자 화면 확인 완료.

---

# 8. Stage 6 Administration 데이터 관리 — 완료

Administration 최종 구성:
1. 검사 기준 관리
2. 환경 설정
3. 데이터 관리

## 전체 검사 이력 정리

기능:
- 모든 Issue 삭제
- 모든 Inspection 삭제
- Project 정보 유지

Modal 표시:
- 프로젝트 정보: N개 (유지)
- 검사 이력: N건 (삭제)
- 이슈: N건 (삭제)
- 복구 불가 경고

DB 삭제순서:
`Issues → Inspections`

## 프로젝트 관리

목록 표시:
- 프로젝트명
- 부서
- 검사 이력 수
- 이슈 수

Project 삭제 시:
`Issues → Inspections → Project`

다른 Project 데이터는 유지.

## UI 최종 기준

- Administration 메인 화면은 한 화면 구조 유지
- 데이터 관리 카드 내부 간격 사용자 확인 완료
- Project Management Modal 글자/카드 밀도 사용자 확인 완료
- Dark / Light Delete 버튼 시인성 수정 완료
- 전체 검사 이력 정리 Modal 크기/폰트 사용자 확인 완료

Danger 계층:
- `정리`: 낮은 강조 Danger
- `관리`: 기본 버튼
- 목록 `삭제`: Outline Danger
- 최종 `정리 실행 / 프로젝트 삭제`: Filled Danger

---

# 9. Stage 6 실제 DB 검증

## 프로젝트 삭제

실제 DB에 삭제전용 임시 데이터 생성:
- Project 1
- Inspection 1
- Issue 1

UI에서 Project 삭제 실행 후 확인:
- Project 0
- orphan Inspection 0
- orphan Issue 0

따라서 Project + 연결 Inspection + Issue 삭제 정상.

## 전체 검사 이력 정리

원본 DB 백업 후 실제 실행.

확인:
- Project 기존 수 유지
- Inspection 0
- Issue 0

검증 후 백업 DB 원복 완료.
기존 정상 데이터 복원 확인 완료.

---

# 10. Stage 6 자동테스트

파일:
`tests/test_data_management_repository.py`

검증항목:
- 전체 데이터 summary
- Project 관리 목록 impact count
- 전체 검사 이력 삭제 시 Project 유지
- Project delete impact
- 선택 Project tree 삭제
- 없는 Project 삭제 안전성

Targeted 결과:
- 6 passed

전체 회귀:
- `python -m pytest -q`
- 사용자 PC에서 정상 PASS
- 실패 0건

---

# 11. 주요 Stage 6 코드

- `app/database/repositories/data_management_repository.py`
- `ui/data_management_dialogs.py`
- `ui/administration_page.py`
- `tests/test_data_management_repository.py`

Repository API:
- `get_data_management_summary()`
- `get_projects_with_delete_impact()`
- `get_project_delete_impact(project_id)`
- `delete_all_inspection_history()`
- `delete_project_with_history(project_id)`

---

# 12. 절대 되돌리지 말아야 할 사항

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
- `프로젝트 정보: N개 (유지)` 문구
- 실제 비가역 실행 버튼만 Filled Danger

---

# 13. 다음 작업

다음은 **최종 배포/제출 마감 단계**이다.

순서:
1. GitHub main / 로컬 working tree 동기화 확인
2. 최신 PyInstaller EXE 재빌드
3. SQLite 외부 data 경로 확인
4. 아이콘/리소스 포함 확인
5. Qwen3-4B / llama.cpp runtime/model 포함 구조 확인
6. 인터넷 차단/폐쇄망 독립 실행 검증
7. EXE에서 실제 Inspection 1회
8. DB 저장/조회 확인
9. DOCX / XLSX / TXT Export 확인
10. 제출용 폴더 및 산출물 정리

**다음 세션에서 6단계를 다시 시작하지 않는다.**
