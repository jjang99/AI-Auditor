\# AI Auditor 개발 현황



\## 기준일



\* 2026-09-05



\## 현재 개발 단계



\* Home 기본 UI 구현 완료

\* 공통 MainWindow 및 상단 메뉴 구현 완료

\* Dark / Light 테마 전환 구현 완료

\* Projects 메뉴 연결 완료

\* Projects 화면은 기본 뼈대까지만 구현된 상태

\* 다음 개발 대상: Projects 확정 UI 구현



\## 현재 정상 구동 상태



\* `python main.py` 실행 정상

\* AI Auditor Home 화면 정상 표시

\* Projects 메뉴 선택 시 `ProjectsPage` 연결 구조 구현됨



\## 현재 주요 파일



\* `main.py`

\* `ui/main\_window.py`

\* `ui/home\_page.py`

\* `ui/projects\_page.py`

\* `ui/theme.py`

\* `assets/icons/`



\## Projects 현재 구현 상태



\* `ProjectsPage` 클래스 생성 완료

\* MainWindow의 Projects 메뉴와 연결 완료

\* 현재 Projects 화면에는 제목과 임시 설명만 존재

\* 확정된 카드형 Projects UI는 아직 구현 전



\## Git 상태



\* 2026-08-29까지 진행한 UI 작업은 로컬에 존재

\* 해당 UI 작업은 아직 GitHub 원격 저장소에 반영되지 않은 상태에서 2026-09-05 개발 재개

\* 현재 작업을 기준점으로 저장 후 Projects 개발 진행 예정



\## 다음 작업



1\. 현재 UI 작업 기준점 Git 저장

2\. Projects 확정 UI 구현

3\. 화면 동작 확인

4\. Git commit / push

5\. DEV\_STATUS.md 현행화

6\. DECISIONS.md 현행화



\## 개발 진행 원칙



\* 기존 파일과 실제 코드를 먼저 확인한 후 수정한다.

\* 이미 만들어진 파일을 임의로 다시 만들거나 덮어쓰지 않는다.

\* 확정된 UI 구조·기능·메뉴·동작을 임의로 변경하지 않는다.

\* 코드 상태와 대화에서 확정한 내용을 모두 개발 기준으로 사용한다.

\* 코드와 결정사항이 충돌하면 임의 판단하지 않고 차이를 확인한다.

\* 개발 종료 시 코드, DEV\_STATUS.md, DECISIONS.md를 함께 저장한다.



