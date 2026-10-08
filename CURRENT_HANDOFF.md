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
- 최종 EXE 안정화 — 완료

**1~6단계와 최종 EXE 안정화는 새 결함이 없는 한 다시 구현하거나 재설계하지 않는다.**

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
- `dist/AI_Auditor/data/ai_auditor.db`

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
- 로컬 Git 상태 `## main...origin/main` clean 확인

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

---

# 8. 다음 단계 — 감리결과서 기반 실무 검증

최종 EXE 안정화 다음 작업은 감리결과서 분석이다.

핵심 원칙:
- 감리결과서를 MVP 20개에만 매핑하지 않는다.
- 확보한 감리결과서의 지적사항을 추출·중복제거·일반화한 뒤 **Full Rule Catalog 105개 전체와 매핑**한다.
- 이 매핑 결과는 현재 MVP 20개 검증뿐 아니라 향후 미구현 85개 Rule의 구현 우선순위와 실무 근거로 재사용한다.
- 향후 85개 구현 때 감리결과서를 처음부터 다시 분석하지 않는다.
- 105개 어디에도 대응되지 않는 반복적·중요 지적유형은 106번 이후 신규 Rule 후보로 관리한다.

진행 순서:
1. 감리결과서 지적사항 추출
2. 유사 지적 통합 / 중복 제거 / 일반화
3. 감리 지적유형 ↔ 105개 전체 Rule 매핑
4. MVP 20개 구현여부 / 미구현 85개 / 신규 Rule 후보 분류
5. 실제 감리 사례로 현재 MVP 20개 검증
6. 해커톤 최종 문서화·제출
7. 제출 후 나머지 85개 Rule을 우선순위에 따라 순차 구현
8. 105개 전체 통합 검증

**다음 세션에서 최종 EXE 안정화를 다시 처음부터 반복하지 않는다.**
