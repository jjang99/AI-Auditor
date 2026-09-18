# AI Auditor 확정 결정사항

## 문서 목적
이 문서는 AI Auditor 개발 과정에서 사용자와 협의하여 최종 확정한 UI, 기능, 개발 원칙을 기록한다. 개발 시 실제 소스코드와 본 문서 및 기존 협의 내용을 함께 기준으로 사용한다. 코드와 확정 결정사항 사이에 차이가 발견될 경우 임의로 수정하지 않고 차이를 확인한 후 협의한다.

---

# 1. 공통 UI
- 기본 화면 크기는 Home에서 확정한 창 크기를 기준으로 한다.
- 다른 화면이라고 해서 임의로 가로폭을 넓히지 않는다.
- 필요한 경우 세로 스크롤을 사용한다.
- Dark / Light Mode를 제공하며 기본은 Dark Mode이다.
- 공통 메뉴: Home, Projects, Inspection, Reports, Administration
- 확정된 화면 구조, 메뉴, 기능 및 동작을 개발 중 임의로 추가·삭제·변경하지 않는다.

---

# 2. Home
- 기본 UI 구현 완료
- 최종 전체 UI 점검 단계에서 확정 시안과 비교하여 필요한 최소 보정만 수행한다.

---

# 3. Projects
- 최종 확정한 카드형 UI를 사용한다.
- 상단 `Search Projects`, `New Project` 유지
- 페이지당 5개, 최근 검사일 내림차순
- 카드 표시정보: Project Name, Department, Last Inspection Date, Score, Grade, Issues, Resolved
- Issues는 전체 이슈 수
- Resolved는 조치완료/전체 및 Progress Bar
- 상태는 AI 검사완료를 기본으로 하며 검사실패/검사취소 표시를 지원한다.
- 별도 필터, 카드/리스트 전환, 알림, 사용자 프로필, 불필요한 차트는 임의 추가하지 않는다.

---

# 4. Project Detail
- 기본 정보: Project Name, Department, Last Inspection Date
- 결과: Score + Grade, Issues 전체 건수, Resolved 조치완료/전체, Progress Bar
- Issues는 기본 8개 표시 후 `더 보기`
- 액션 순서: `Re-Inspect | New Inspection | Export Report`
- Re-Inspect는 기존 Inspection 당시 사용한 검사기준을 사용한다.
- 실제 검사결과 DB 조회 구조 연결 완료
- 2026-09-18 최종 UI 점검 완료 및 Project Detail UI Freeze
- Issue Distribution은 Critical / High / Medium / Low 4단계 유지
- Issues 목록은 기본 8개 표시 후 `더 보기`, 설명 자동 줄바꿈, 스크롤바는 내용이 넘칠 때만 표시
- Issues 심각도 배지는 Issue Detail의 심각도 배지와 동일한 높이/형태를 기준으로 유지
- Issue Detail의 제목 / 설명 / 근거 / 영향 / AI 권고 항목 간격은 2026-09-18 최종 보정 상태를 유지

---

# 5. Inspection
## 기본 구조
- 단일 화면 구조
- 프로젝트명 필수, 담당부서/비고 선택
- 프로젝트명 중복 확인 및 기존 프로젝트 확인 Modal
- 검사대상 파일 Drag & Drop / 파일 선택
- 검사기준은 기본 전체 선택
- `보기` Modal에서 개별 규칙을 확인하고 제외 가능
- 검사준비 요약: 파일 수, 라인 수, 선택 규칙 수, 소요시간 관련 정보
- `검사 시작`, Progress, 완료 상태 제공

## 2026-09-13 UI Freeze 사항
다음 Inspection 관련 UI는 사용자 최종 확인을 거쳐 만족 상태로 확정했으므로 특별한 사유나 사용자 요청 없이 다시 변경하지 않는다.
- 검사기준 카테고리 선택 체크박스 모양/크기/체크 표시
- 선택 변경 후 체크박스 크기 유지
- 검사기준 행의 텍스트 크기와 간격
- 규칙 Modal 카테고리 아이콘 및 크기
- 규칙 Modal의 `규칙명 / 설명 / 상태` 정렬
- 규칙 수 표기는 `항목`이 아니라 `규칙` 사용
- 기존 프로젝트 확인 Modal의 선택 UI
- 검사대상 파일 삭제/전체 삭제 휴지통 아이콘

## 규칙 수 의미
- 화면에 보이는 4개 검사기준 행은 개별 Rule이 아니라 상위 카테고리이다.
- 개념상 검사기준 체계 수량은 총 102개(보안 32, 코드 품질 45, AI 특화 15, 성능 10)이다.
- 이 102개는 현재 실제 실행 가능한 Rule 102개가 구현됐다는 의미가 아니다.
- `적용 규칙`은 장기적으로 선택된 개별 실행 Rule 수를 기준으로 표시하는 구조로 통일한다.

---

# 6. Rule Engine
## 현재 구현 기준
- deterministic Rule Engine을 우선 구현한다.
- 현재 실제 실행 가능한 기본 Rule은 5개이다.
  - 보안 2개
  - 코드 품질 2개
  - 성능 1개
  - AI 특화 0개
- 현재 기본 Rule은 구조 및 실제 실행 흐름을 검증하기 위한 초기 Rule이다.

## MVP 방향
- 최종 후보 검사기준 체계는 약 100개 수준을 유지한다.
- MVP에서는 약 20개의 실제 실행 가능한 Rule을 완성도 있게 구현한다.
- 네 가지 핵심 기능 방향은 유지하며 후순위 기능은 구현 깊이를 조절할 수 있다.
- AI 특화 검증도 MVP 실행 Rule에 의미 있는 항목을 포함한다.
- 감리결과서 원문 1~2건으로 모델을 직접 파인튜닝하는 방식은 우선 사용하지 않는다.
- 확보한 감리 지적사례는 사업 특화/중복 내용을 걸러 일반화된 Rule 후보로 변환해 활용한다.
- 향후 UI 규칙 목록과 실제 Rule Engine은 동일한 Rule 정의 데이터를 바라보도록 정리한다.
- 화면의 102개를 실제 구현 102개인 것처럼 표현하지 않는다.

---

# 7. Administration
- 검사 기준 관리 기능을 제공한다.
- 확정된 Inspection Rules Management 및 Rule Detail 구조를 유지한다.
- 규칙 비활성화 시 기본 검사에서 제외한다.
- 확정 시안의 버튼 및 안내문 배치를 임의 변경하지 않는다.

---

# 8. 개발 진행 원칙
- 기존 코드를 확인하기 전에 새 파일을 만들지 않는다.
- 동일 기능의 기존 파일이 있으면 해당 파일에서 이어서 개발한다.
- 파일을 임의로 덮어쓰지 않는다.
- 기존 정상 동작을 먼저 확인한 후 수정한다.
- 개발 중 확정사항이 불명확하면 기존 대화/문서/코드를 먼저 확인한다.
- 코드와 결정사항이 충돌하면 임의 판단하지 않고 차이를 확인한다.
- 필요하면 사용자와 협의한 후 변경한다.

## 개발 종료 시
1. 프로그램 정상 실행 확인
2. Git 상태 및 변경 코드 확인
3. `DEV_STATUS.md` 업데이트
4. `DECISIONS.md` 업데이트
5. Git commit / GitHub push
6. 다음 개발 시작점 기록

## 다음 개발 시작 시
1. GitHub 최신 실제 코드 확인
2. `DEV_STATUS.md` 확인
3. `DECISIONS.md` 확인
4. 기존 확정 대화와 비교
5. 정확한 재개 지점 확인 후 개발 시작

---

# 9. 현재 재개 지점 — 2026-09-18
- Inspection 실제 기능 및 Rule Engine 기본 구조 구현 완료
- Inspection UI Freeze 완료
- Project Detail 최종 UI 보정 및 UI Freeze 완료
- 다음 작업은 Reports 최종 UI 점검
- 이후 Administration → 공통 UI/화면 이동 최종 점검
- 전체 UI Freeze 후 실제 MVP Rule 약 20개 구현 단계로 이동
