# AI-Auditor

**AI 기반 프로젝트 품질 감사(Auditor) 플랫폼**

AI Auditor는 프로젝트 산출물을 자동으로 분석하여 품질 이슈를 사전에 점검하고, 검사 결과와 조치 현황 및 재검사 이력을 관리하기 위한 프로젝트 품질 감사 플랫폼입니다.

## 주요 기능

* 프로젝트 등록 및 관리
* 프로젝트 산출물 업로드 및 검사
* 검사 기준(Rule) 기반 품질 점검
* 검사 결과 및 Issue 관리
* 조치 현황 관리
* 기존 검사 기준을 활용한 재검사(Re-Inspect)
* 검사 이력 관리
* 검사 결과 보고서 생성 및 Export
* 검사 기준 관리(Administration)
* Local AI / External AI 확장 구조

## 주요 화면

* Home
* Projects
* Project Detail
* Inspection
* Reports
* Administration

## 개발 환경

* OS: Windows
* Language: Python 3.13.15
* UI Framework: PySide6 6.11.2
* Database: SQLite
* IDE: Visual Studio Code
* Version Control: Git / GitHub

## 프로젝트 구조

```text
AI-Auditor
├─ app
│  ├─ ai
│  ├─ database
│  │  └─ repositories
│  ├─ models
│  ├─ parsers
│  ├─ services
│  ├─ ui
│  └─ utils
├─ assets
│  ├─ icons
│  └─ styles
├─ config
├─ data
├─ reports
├─ rules
│  ├─ core
│  └─ definitions
├─ tests
├─ main.py
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## 실행 방법

### 1. 가상환경 활성화

Windows Command Prompt 기준:

```bat
.venv\Scripts\activate.bat
```

### 2. 필요한 라이브러리 설치

```bat
python -m pip install -r requirements.txt
```

### 3. AI Auditor 실행

```bat
python main.py
```

## 현재 개발 상태

* GitHub Repository 구성 완료
* Python 개발환경 구성 완료
* Python 가상환경(.venv) 구성 완료
* VS Code 개발환경 구성 완료
* Git / GitHub 연동 완료
* 프로젝트 기본 폴더 구조 구성 완료
* PySide6 설치 및 실행 검증 완료
* 기본 UI 실행 테스트 완료

## 개발 원칙

* 확정된 UI 및 사용자 시나리오를 개발 기준으로 유지
* 개발 과정에서 확정된 화면 구조·기능·메뉴·동작을 임의로 변경하지 않음
* 검사 규칙은 단계적으로 구현 및 검증
* 프로젝트 데이터와 검사 대상 산출물 등 민감할 수 있는 실행 데이터는 GitHub에 저장하지 않음
* 최종적으로 인터넷 연결 없이 폐쇄망에서 실행 가능한 독립 실행형 프로그램(EXE)을 목표로 함
