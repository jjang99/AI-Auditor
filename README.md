# AI-Auditor

**AI 기반 프로젝트 품질 감사(Auditor) 플랫폼**

AI Auditor는 정보시스템 프로젝트의 요구사항·설계·시험·FP·AI 관련 산출물을 자동 분석하여,
실제 감리에서 반복되는 품질 이슈를 사전에 점검하고 검사결과·조치현황·재검사 이력을 관리하는 데스크톱 애플리케이션입니다.

핵심 목표는 **감리 직전에 사람이 산출물을 일일이 대조하는 부담을 줄이고, 실제 감리지적 가능성이 높은 항목을 사전에 발견하는 것**입니다.

---

## 1. 핵심 특징

- 프로젝트 등록 및 검사 이력 관리
- 5대 검사영역 / Full Rule Catalog 105개 관리
- 해커톤 MVP 실제 실행 Rule 20개
- Rule / AI / Hybrid 혼합 검사
- 요구사항 ID·중복·모호성·설계반영·추적성 검사
- 변경사항 및 영향도 검사
- FP 기능유형·산정값 검증
- AI/RAG 신뢰성·보안·관리체계 점검
- 감리 예상 지적사항 종합
- Impact / Likelihood 기반 Severity 계산
- 감리 개선권고 유형·시점·중요도 관리
- Re-Inspect 및 Inspection History 관리
- DOCX / XLSX / TXT 보고서 Export
- Local AI 기반 폐쇄망 독립 실행
- Administration을 통한 검사기준·환경·데이터 관리

---

## 2. 검사체계

### Full Rule Catalog

| 영역 | 코드 | 수량 |
|---|---|---:|
| 감리 사전점검 | AUD | 24 |
| 요구사항 정합성 | REQ | 28 |
| 변경영향도 | CHG | 18 |
| FP 검증 | FP | 12 |
| AI 특화 검증 | AI | 23 |
| **합계** |  | **105** |

### MVP 실제 실행 Rule

총 20개:
- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4

실행방식:
- Rule 3
- AI 6
- Hybrid 11

Full Catalog 105개와 MVP 실제 실행 20개는 구분하여 관리합니다.

---

## 3. 실제 감리사례 기반 검증

AI Auditor의 검사기준은 임의로 만든 체크리스트에만 의존하지 않습니다.

2026-10-09 기준 감리 관련 자료 **114개**를 분석하여 105개 Rule 전체와 매핑했습니다.

분석자료:
- PDF 94개
- DOCX 19개
- XLSX 1개
- 2019~2025년 독립 감리보고서

검증절차:

`파일/버전/중복 확인`
→ `감리지적 추출`
→ `유사지적 통합`
→ `105개 Rule 매핑`
→ `요약표 재검증`
→ `상세본문 재검증`
→ `FP·AI/RAG·보안·데이터·UI/UX 전문분야 교차검증`
→ `MVP20 실증검증`

실증검증 과정에서 탐지범위가 좁다고 확인된 아래 5개 Rule은 실제 감리사례 기반으로 보완했습니다.

- AUD-001 필수 산출물 누락
- REQ-002 요구사항 내용 중복
- REQ-003 요구사항 모호성
- REQ-009 요구사항 설계 반영 정합성
- FP-009 FP 산정값 재계산

최종 전체 `python -m pytest -q` 회귀테스트는 사용자 PC에서 실패 0건을 확인했습니다.

자세한 근거:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`

---

## 4. 주요 검사 예시

### AUD-001 필수 산출물 누락

산출물목록과 테일러링 결과를 기준으로 현재 제출대상 산출물을 판단하고 실제 업로드 파일과 비교합니다.

- 테일러링 `미적용/제외` 항목은 누락으로 판정하지 않음
- `시기미도래/해당없음` 항목도 현재 누락에서 제외
- 기준문서가 없으면 임의 표준 산출물목록을 만들어 오탐하지 않음

### REQ-009 요구사항 ↔ 설계 반영 정합성

요구사항정의/기술/추적 문서와 화면·인터페이스·데이터·프로그램·아키텍처 등 설계 산출물을 서로 교차검증합니다.

### FP-009 FP 산정값 재계산

- 단순 산식 재계산
- XLS/XLSX 표 기반 기능유형·복잡도·RET/FTR·DET·기능개수·FP 값 검증
- 계산 근거가 부족한 행은 억지로 추정하지 않음

---

## 5. 지원 문서 형식

Parser 지원 9종:

- DOCX
- DOC
- XLSX
- XLS
- PDF
- PPTX
- PPT
- HWPX
- HWP

모든 문서는 공통 `ParsedDocument / DocumentBlock` 구조로 변환한 뒤 검사합니다.

현재 MVP 제외:
- 스캔 이미지 기반 PDF OCR

---

## 6. Local AI / 폐쇄망 실행

기본 Local AI:
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off

AI는 Issue의 다음 항목을 판단합니다.
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

최종 Severity는 AI가 직접 정하지 않고 아래 구조로 계산합니다.

`Impact × Likelihood → deterministic Severity Matrix`

인터넷 차단 상태에서 Local AI 검사를 실제 확인했습니다.
프로그램이 실행 중 모델을 인터넷에서 자동 다운로드하지 않습니다.

---

## 7. 주요 화면

- Home
- Projects
- Project Detail
- Inspection
- Reports
- Administration

UI는 Dark Mode를 기본으로 하고 Light Mode를 함께 지원합니다.
확정된 UI Freeze 기준을 유지하며 임의 재설계하지 않습니다.

---

## 8. 검사 실행 흐름

`Inspection`
→ `Rule 선택`
→ `문서 Parser`
→ `Rule / AI / Hybrid 검사`
→ `Issue 생성`
→ `Impact / Likelihood 평가`
→ `Severity Matrix`
→ `감리 개선판정`
→ `DB 저장`
→ `Project Detail / Reports`

검사 중 취소를 지원하며 취소된 검사는 DB에 저장하지 않습니다.

---

## 9. 보고서 Export

지원 형식:
- DOCX
- XLSX
- TXT

보고서에는 다음 정보를 포함합니다.
- Issue 내용
- Impact / 근거
- Likelihood / 근거
- Severity / 판정근거
- 개선권고유형
- 개선시점
- 중요 여부
- 카테고리

HWPX Export는 현재 MVP에서 제외합니다.

---

## 10. 개발 환경

- OS: Windows
- Python: 3.13.15
- UI Framework: PySide6 6.11.2
- Database: SQLite
- EXE Packaging: PyInstaller 6.22.3 onedir
- MSI Packaging: WiX Toolset 7.0.0 / .NET SDK 10.0.401 x64
- Version Control: Git / GitHub

주요 Parser 라이브러리는 `requirements.txt`를 기준으로 합니다.

---

## 11. 소스 실행

### 1) 가상환경 활성화

```bat
.venv\Scripts\activate.bat
```

### 2) 의존성 설치

```bat
python -m pip install -r requirements.txt
```

### 3) 실행

```bat
python main.py
```

### 4) 전체 테스트

```bat
python -m pytest -q
```

---

## 12. 최종 배포 구조

### ZIP(EXE)

```text
dist/
└─ AI_Auditor/
   ├─ AI_Auditor.exe
   ├─ runtime/
   │  └─ llama.cpp/
   │     └─ llama-server.exe
   ├─ models/
   │  └─ Qwen3-4B-Q4_K_M.gguf
   └─ data/
      └─ (첫 실행 시 ai_auditor.db 자동 생성)
```

최종 ZIP(EXE)는 위 폴더 전체를 하나의 실행 패키지로 취급합니다.
`AI_Auditor.exe`만 별도로 이동하면 Local AI나 DB 경로가 정상 동작하지 않을 수 있습니다.

사용자 PC 최종 ZIP 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

### MSI 설치형

최종 구성:

```text
installer/output/
├─ AI_Auditor_Install.cmd
├─ AI_Auditor_Setup.msi
├─ aia1.cab
├─ aia2.cab
└─ Qwen3-4B-Q4_K_M.gguf
```

Qwen3-4B 모델은 2GB를 초과하므로 Windows Installer의 일반 File table에 직접 포함하지 않습니다.
사용자는 `AI_Auditor_Setup.msi`를 단독 실행하지 않고 `AI_Auditor_Install.cmd`를 실행합니다.
Launcher가 MSI 설치 후 모델을 설치 경로의 `models/`로 복사하고 파일크기를 검증합니다.

사용자 PC 최종 MSI 설치형 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

실제 설치 위치:
`%LOCALAPPDATA%\Programs\AI Auditor`

---

## 13. 프로젝트 구조

```text
AI-Auditor
├─ app/
│  ├─ database/
│  ├─ parsers/
│  ├─ services/
│  └─ ...
├─ assets/
├─ config/
├─ data/
├─ installer/
├─ reports/
├─ rules/
│  ├─ core/
│  ├─ definitions/
│  └─ providers/
├─ tests/
├─ AUDIT_EVIDENCE_MAPPING.md
├─ MVP20_AUDIT_VALIDATION.md
├─ RULE_DESIGN.md
├─ DECISIONS.md
├─ DEV_STATUS.md
├─ CURRENT_HANDOFF.md
├─ HACKATHON_SUBMISSION.md
├─ main.py
├─ requirements.txt
└─ README.md
```

---

## 14. 데이터 관리

Administration에서 다음을 제공합니다.

- 전체 검사 이력 정리: Issue / Inspection 삭제, Project 유지
- 프로젝트 삭제: 해당 Project의 Issue / Inspection / Project 삭제

삭제는 명시적 순서와 transaction으로 처리하며 오류 발생 시 rollback합니다.

---

## 15. 현재 상태

2026-10-10 기준:

- 1~6단계 개발 완료
- 최종 EXE 안정화 완료
- 폐쇄망 Local AI 실행 확인
- 감리자료 114개 분석 완료
- Full Catalog 105개 실무매핑 완료
- MVP20 감리사례 실증검증 완료
- 실증 우선보완 5개 수정 완료
- 전체 회귀테스트 PASS
- 최신 코드 기준 ZIP(EXE) 재빌드 및 실제 REQ-003 스모크검증 완료
- MSI 설치형 제작, 실제 설치, DB 자동생성, Local AI REQ-003 검사 검증 완료
- `HACKATHON_SUBMISSION.md` 최종 현행화 완료
- 해커톤 제출 전 최종 문서·파일 체크 단계

---

## 16. 제한사항 및 향후 확장

현재 MVP에서 의도적으로 남겨둔 범위:
- 스캔 PDF OCR 제외
- HWPX 보고서 Export 제외
- 일부 Rule은 실제 감리 직접사례가 제한적인 예방/전략 Rule
- Full Catalog 105개 중 실제 실행은 MVP20
- MSIX는 인증서/정책 복잡성으로 현재 배포범위 제외

제출 이후에는 `AUDIT_EVIDENCE_MAPPING.md`에 확정한 P1 → P2 → P3 → P4 우선순위를 기본으로 나머지 85개 Rule을 확장할 수 있습니다.

---

## 17. 주요 문서

- `README.md` — 제품 소개 및 실행 안내
- `HACKATHON_SUBMISSION.md` — 해커톤 제출용 최종 요약
- `AUDIT_EVIDENCE_MAPPING.md` — 114개 감리자료 ↔ 105개 Rule 실무근거
- `MVP20_AUDIT_VALIDATION.md` — MVP20 실제 감리사례 실증검증
- `RULE_DESIGN.md` — 검사기준/실행구조 설계
- `DECISIONS.md` — 확정 의사결정
- `DEV_STATUS.md` — 개발 진행현황
- `CURRENT_HANDOFF.md` — 최신 인수인계 기준점

프로젝트 산출물·실행데이터 등 민감할 수 있는 실제 업무자료는 GitHub에 저장하지 않습니다.