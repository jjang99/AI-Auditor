# AI Auditor Stage 6 학습자료 — Administration 데이터 관리

## 1. 이 문서의 목적

이 문서는 Stage 6에서 구현한 `Administration > 3. 데이터 관리` 기능을 나중에 혼자 다시 공부할 수 있도록 정리한 학습자료다.

단순히 “무엇을 만들었다”만 적지 않고 다음 흐름으로 이해할 수 있도록 구성한다.

1. 왜 데이터 관리 기능이 필요했는가
2. DB 구조가 어떻게 연결되는가
3. 왜 삭제 순서가 중요한가
4. Repository에서 어떤 역할을 맡았는가
5. UI는 어떤 원칙으로 설계했는가
6. 실제 삭제 기능을 어떻게 안전하게 검증했는가
7. 자동테스트는 무엇을 보장하는가
8. 유지보수 시 무엇을 건드리면 안 되는가

---

# 2. Stage 6의 목표

Stage 6의 목적은 Administration에서 사용자가 검사 데이터와 프로젝트 데이터를 안전하게 정리할 수 있게 하는 것이다.

최종 기능은 두 가지다.

### ① 전체 검사 이력 정리

삭제:
- 모든 Inspection
- 모든 Issue

유지:
- Project

즉 프로젝트 기본정보는 남기고 검사결과만 초기화하는 기능이다.

### ② 프로젝트 관리

프로젝트별로 다음 정보를 확인한다.

- 프로젝트명
- 부서
- 검사 이력 수
- 이슈 수

특정 프로젝트를 삭제하면 함께 삭제된다.

- 해당 Project
- 해당 Project의 Inspection
- 해당 Inspection의 Issue

---

# 3. 데이터 구조 이해

AI Auditor의 핵심 DB 관계는 다음과 같다.

```text
Project
  └─ Inspection
       └─ Issue
```

예를 들어:

```text
Project A
 ├─ Inspection 1
 │   ├─ Issue 1
 │   └─ Issue 2
 └─ Inspection 2
     └─ Issue 3
```

여기서 Project A를 삭제하려면 Issue → Inspection → Project 순서로 지워야 한다.

왜냐하면 Inspection이 Project를 참조하고, Issue가 Inspection을 참조하기 때문이다.

---

# 4. 왜 삭제 순서가 중요한가

현재 DB는 외래키 관계는 있지만 Stage 6에서 `ON DELETE CASCADE`를 새로 추가하지 않았다.

즉 DB가 자동으로 하위 데이터를 전부 지우게 만들지 않고, 프로그램이 삭제 순서를 명시적으로 제어한다.

프로젝트 삭제 순서:

```text
Issues → Inspections → Project
```

전체 검사 이력 정리:

```text
Issues → Inspections
```

Project는 유지한다.

이 방식의 장점은 삭제범위를 코드에서 명확하게 확인할 수 있다는 것이다.

---

# 5. Transaction과 Rollback

데이터 삭제는 중간에 실패하면 안 된다.

예를 들어 Project 삭제 중:

1. Issue 삭제 성공
2. Inspection 삭제 성공
3. Project 삭제 실패

이런 상황에서 그대로 끝나면 데이터가 반쯤 삭제된 상태가 된다.

그래서 Repository에서는 하나의 transaction 안에서 처리하고, 오류가 발생하면 rollback한다.

개념적으로는 다음과 같다.

```python
try:
    delete issues
    delete inspections
    delete project
    commit
except:
    rollback
```

핵심은 “전부 성공하거나, 전부 원상복구”다.

---

# 6. Repository 역할

Stage 6에서는 UI에서 직접 SQL을 실행하지 않는다.

UI는 사용자 동작과 화면표시를 담당하고, 실제 DB 조회/삭제는 Repository가 담당한다.

파일:

```text
app/database/repositories/data_management_repository.py
```

주요 함수는 다음과 같다.

---

## 6.1 get_data_management_summary()

현재 전체 데이터 수를 조회한다.

예:

```text
Projects: 30
Inspections: 40
Issues: 319
```

Administration 데이터 관리 카드의 `현재 데이터` 표시와 전체 삭제 영향범위 Modal에 사용한다.

---

## 6.2 get_projects_with_delete_impact()

프로젝트 관리 Modal 목록을 만들기 위한 함수다.

각 Project별로 다음 정보를 반환한다.

```text
project_id
project_name
department
inspections
issues
```

따라서 UI에서 프로젝트별 삭제 영향범위를 바로 보여줄 수 있다.

---

## 6.3 get_project_delete_impact(project_id)

특정 Project를 실제 삭제하기 직전에 영향범위를 조회한다.

예:

```text
Project: Project A
Inspection: 3
Issues: 21
```

최종 확인 Modal에 표시한다.

---

## 6.4 delete_all_inspection_history()

전체 검사 이력 정리 함수다.

처리:

```text
1. Issues 삭제
2. Inspections 삭제
3. Projects는 유지
4. commit
```

결과로 삭제된 검사/이슈 수를 반환한다.

---

## 6.5 delete_project_with_history(project_id)

특정 Project 전체 삭제 함수다.

처리:

```text
1. 해당 Project의 Inspection ID 확인
2. 해당 Inspection의 Issues 삭제
3. 해당 Inspections 삭제
4. Project 삭제
5. commit
```

다른 Project 데이터는 절대 삭제하지 않아야 한다.

---

# 7. UI 구조

관련 파일:

```text
ui/administration_page.py
ui/data_management_dialogs.py
```

Administration 최종 구성:

```text
1. 검사 기준 관리
2. 환경 설정
3. 데이터 관리
```

Stage 6에서는 기존 UI Freeze를 깨지 않도록 한 화면 안에 데이터 관리 카드를 추가했다.

메인 화면에 별도 스크롤을 추가하지 않았다.

---

# 8. 데이터 관리 카드

카드에는 다음이 표시된다.

```text
3. 데이터 관리
현재 데이터 · 프로젝트 N개 / 검사 이력 N건 / 이슈 N건

전체 검사 이력 정리                  [정리]
모든 검사 이력과 이슈를 삭제하며 프로젝트 정보는 유지합니다.

프로젝트 관리                        [관리]
프로젝트별 검사 이력과 이슈 범위를 확인한 뒤 프로젝트를 삭제합니다.
```

최종 간격 원칙:

- 제목과 현재 데이터는 하나의 정보 그룹처럼 가깝게 배치
- 현재 데이터와 첫 기능은 약간 분리
- 전체 검사 이력 정리와 프로젝트 관리는 구분선 + 여백으로 명확히 구분

---

# 9. 삭제 버튼을 모두 빨갛게 만들지 않은 이유

Stage 6에서 중요한 UI 결정 중 하나다.

모든 삭제 관련 버튼을 채운 빨강으로 만들면 화면 전체가 위험해 보이고, 사용자가 실제 실행단계와 단순 진입단계를 구분하기 어렵다.

그래서 위험도 계층을 나눴다.

```text
Administration [정리]
→ 위험 작업 진입
→ 낮은 강조 Danger

Administration [관리]
→ 단순 관리 화면 진입
→ 기본 버튼

Project 목록 [삭제]
→ 삭제 대상 선택
→ Outline Danger

최종 확인 [정리 실행] / [프로젝트 삭제]
→ 실제 비가역 실행
→ Filled Danger
```

핵심은 **실제 돌이킬 수 없는 순간을 가장 강하게 표시**하는 것이다.

---

# 10. DeleteConfirmDialog

파일:

```text
ui/data_management_dialogs.py
```

역할:
- 삭제 대상 설명
- 영향범위 표시
- 복구 불가 경고
- 취소
- 최종 실행

전체 검사 이력 정리 예:

```text
프로젝트 정보: 30개 (유지)
검사 이력: 40건 (삭제)
이슈: 319건 (삭제)

삭제된 데이터는 복구할 수 없습니다.
```

`프로젝트 정보`라는 표현을 사용한 이유는 단순히 “프로젝트”라고 쓰면 Project 자체도 삭제되는 것으로 오해할 수 있기 때문이다.

---

# 11. ProjectManagementDialog

프로젝트별로 다음을 표시한다.

```text
프로젝트명
부서 · 검사 이력 N건 · 이슈 N건
                                      [삭제]
```

최종 UI 보정:

- 프로젝트명 폰트 확대
- 부서/검사이력/이슈 폰트 확대
- 카드 높이 축소
- 카드 간격 축소
- Dark / Light 모두 Delete 버튼 시인성 확보

즉 “정보는 더 잘 보이고, 카드 자체는 덜 비어 보이게” 만든 것이 핵심이다.

---

# 12. 실제 삭제 검증을 왜 DB 백업 후 했는가

`전체 검사 이력 정리`는 실제 DB의 모든 검사결과를 지우는 기능이다.

따라서 바로 실행하면 기존 정상 검증 데이터까지 없어질 수 있다.

그래서 실제 검증 순서는 다음과 같이 했다.

```text
1. 원본 DB 백업
2. 전체 검사 이력 정리 실제 실행
3. DB 조회
4. Project 수 유지 확인
5. Inspection 0 확인
6. Issue 0 확인
7. 백업 DB 원복
8. 기존 데이터 복원 확인
```

실제 운영성 기능은 자동테스트만으로 끝내지 않고 실제 DB에서도 검증했다.

---

# 13. 프로젝트 삭제 실제 검증

기존 Project를 함부로 삭제하지 않기 위해 임시 데이터 세트를 만들었다.

```text
DELETE_TEST_6STEP
 └─ Inspection 1
     └─ Issue 1
```

Project Management에서 해당 테스트 Project를 실제 삭제했다.

삭제 후 DB 확인:

```text
project = 0
orphan_inspection = 0
orphan_issue = 0
```

이 검증으로 세 가지를 확인했다.

1. Project가 실제 삭제됨
2. 연결 Inspection도 삭제됨
3. 연결 Issue도 삭제됨

---

# 14. orphan 데이터란?

orphan은 부모 데이터가 없는데 자식 데이터만 남아 있는 상태를 의미한다.

예:

```text
Project 없음
Inspection은 남아 있음
```

또는:

```text
Inspection 없음
Issue는 남아 있음
```

이런 데이터는 DB 정합성을 깨뜨린다.

검증 쿼리는 다음 논리를 사용했다.

```sql
SELECT COUNT(*)
FROM inspections
WHERE project_id NOT IN (SELECT id FROM projects)
```

Issue도 같은 방식으로 확인했다.

최종 결과:

```text
orphan_inspection = 0
orphan_issue = 0
```

---

# 15. 자동테스트

파일:

```text
tests/test_data_management_repository.py
```

최종 6개 테스트가 있다.

---

## 15.1 summary count

현재 Project / Inspection / Issue 수가 정확히 집계되는지 확인한다.

---

## 15.2 project management impact list

프로젝트 관리 목록에 각 Project별 검사 이력과 Issue 수가 정확히 표시되는지 검증한다.

이 테스트는 Stage 6 후반에 추가 보강했다.

---

## 15.3 clear history preserves projects

전체 검사 이력 정리 후:

```text
Projects = 유지
Inspections = 0
Issues = 0
```

인지 확인한다.

---

## 15.4 project delete impact

Project 삭제 전에 계산된 영향범위가 정확한지 확인한다.

---

## 15.5 selected project tree delete

Project A를 삭제했을 때:

```text
Project A 삭제
Project A Inspection 삭제
Project A Issue 삭제
```

하지만 Project B 데이터는 남아 있어야 한다.

---

## 15.6 missing project safety

존재하지 않는 Project ID를 삭제 요청해도 다른 데이터가 손상되지 않아야 한다.

---

# 16. 테스트 결과

Stage 6 전용:

```text
python -m pytest tests/test_data_management_repository.py -q
```

결과:

```text
6 passed
```

전체 회귀:

```text
python -m pytest -q
```

사용자 PC에서 정상 PASS / 실패 0건 확인.

---

# 17. Stage 6에서 중요했던 문제와 해결

## 문제 1. Project Delete 버튼이 Light/Dark에서 보이지 않음

원인:
- QSS Selector 적용 우선순위와 내부 ScrollArea QWidget 스타일 영향

해결:
- `QPushButton#projectManageDelete`로 대상 Selector를 명확히 지정
- ScrollArea 내부의 광범위한 QWidget 스타일 적용을 줄임
- Dark / Light 각각 명확한 Delete 색상 지정

---

## 문제 2. Modal 글씨가 작고 창이 커 보임

해결:
- Delete Confirm Modal 크기 축소
- 본문/영향범위/경고 폰트 확대
- 불필요한 여백 축소

---

## 문제 3. Project 카드가 너무 커 보임

해결:
- 프로젝트명/메타정보 글자 크기는 확대
- 카드 높이는 축소
- 카드 사이 간격 축소
- 내부 상하 여백 축소

결과:
- 가독성은 증가
- 정보밀도도 증가

---

## 문제 4. 데이터 관리 카드 내부 간격 불균형

기존:
- 제목과 현재 데이터가 떨어져 보임
- 두 기능 항목은 너무 붙어 보임

해결:
- 제목 ↔ 현재 데이터 간격 축소
- 현재 데이터 ↔ 첫 기능 간격 확대
- 두 기능 사이 구분선 위/아래 여백 추가

---

# 18. 유지보수 시 주의사항

다음은 임의 변경하지 않는다.

### DB 정책
- Project 삭제순서 `Issues → Inspections → Project`
- 전체 이력 정리 `Issues → Inspections`
- 전체 이력 정리 시 Project 유지

### UI 정책
- 최종 실행만 Filled Danger
- `관리`는 기본 버튼
- Project 목록 Delete는 Outline Danger
- `프로젝트 정보: N개 (유지)` 표현 유지

### 안전정책
- 삭제 전 영향범위 표시
- 복구 불가 경고
- transaction / rollback 유지

---

# 19. Stage 6 전체 흐름 한 번에 보기

```text
Administration
   ↓
3. 데이터 관리
   ├─ 전체 검사 이력 정리
   │    ↓
   │  Summary 조회
   │    ↓
   │  Confirm Modal
   │    ↓
   │  Issues 삭제
   │    ↓
   │  Inspections 삭제
   │    ↓
   │  Project 유지
   │
   └─ 프로젝트 관리
        ↓
      Project별 영향범위 목록
        ↓
      Project 선택
        ↓
      Confirm Modal
        ↓
      Issues 삭제
        ↓
      Inspections 삭제
        ↓
      Project 삭제
```

---

# 20. 직접 복습할 때 볼 파일

우선순위:

```text
1. app/database/repositories/data_management_repository.py
2. tests/test_data_management_repository.py
3. ui/data_management_dialogs.py
4. ui/administration_page.py
5. DECISIONS.md
6. RULE_DESIGN.md
7. DEV_STATUS.md
8. CURRENT_HANDOFF.md
```

Repository → Test → UI 순서로 보면 이해하기 쉽다.

---

# 21. Stage 6 완료 기준

다음이 모두 충족되어 Stage 6을 완료로 확정했다.

- Administration 데이터 관리 UI 구현
- 전체 검사 이력 정리 구현
- Project 관리 구현
- 영향범위 Modal 구현
- 복구불가 경고 구현
- Project 유지 정책 확인
- Project tree 삭제 확인
- 실제 DB 안전 검증
- orphan 데이터 0 확인
- 전용 자동테스트 6 passed
- 전체 pytest 실패 0건
- Dark / Light UI 사용자 확인
- DEV_STATUS / DECISIONS / RULE_DESIGN / CURRENT_HANDOFF 최신화

다음 단계는 Stage 6 기능개발이 아니라 **최종 EXE / 폐쇄망 / 제출 마감**이다.
