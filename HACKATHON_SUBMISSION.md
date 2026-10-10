# AI Auditor 해커톤 제출용 최종 요약

> 기준일: 2026-10-10
> 본 문서는 현재 GitHub main의 실제 구현·검증·배포 상태를 기준으로 정리한 해커톤 제출용 최종 요약이다.
> 회사/대회에서 별도 제출 양식이나 분량 제한을 제공하는 경우 본 내용을 기준으로 해당 형식에 맞춰 재편집한다.

---

## 1. 작품명

**AI Auditor — AI 기반 프로젝트 품질 감사 플랫폼**

---

## 2. 한 줄 소개

정보시스템 프로젝트 산출물을 Rule + Local AI로 자동 분석하여 **실제 감리에서 지적될 가능성이 높은 품질 이슈를 사전에 찾아주는 폐쇄망 대응형 품질 감사 도구**입니다.

---

## 3. 해결하려는 문제

정보시스템 프로젝트에서는 요구사항정의서, 설계서, 시험자료, FP 산정자료 등 많은 산출물을 관리해야 합니다.

감리 또는 품질점검 직전에는 다음 문제가 반복됩니다.
- 산출물 누락 여부를 사람이 일일이 확인해야 함
- 요구사항과 설계/시험 간 정합성을 여러 파일에서 대조해야 함
- 변경사항이 관련 산출물에 모두 반영되었는지 추적하기 어려움
- FP 산정 오류를 표 단위로 재검토해야 함
- 최근 AI/RAG 적용 사업은 기존 점검방식만으로 신뢰성·보안·운영 리스크를 확인하기 어려움
- 실제 업무망은 인터넷 사용이 제한되거나 폐쇄망인 경우가 많음

AI Auditor는 이 반복 작업을 자동화하여 감리 대응 전에 위험요소를 먼저 발견하는 것을 목표로 합니다.

---

## 4. 해결 방법

검사 구조:

`프로젝트 산출물 업로드`
→ `문서 Parser`
→ `Rule / AI / Hybrid 검사`
→ `Issue 생성`
→ `Impact / Likelihood 평가`
→ `Severity 계산`
→ `감리 개선판정`
→ `Project Detail / Reports`

핵심은 단순 생성형 AI 질의가 아니라 **결정적 Rule + Local AI 의미판단 + 실제 감리근거**를 결합한 것입니다.

---

## 5. 주요 차별점

### 5.1 실제 감리자료 기반 검사체계

감리 관련 자료 **114개**를 분석하여 Full Rule Catalog **105개 전체**와 실무근거를 매핑했습니다.

- PDF 94개
- DOCX 19개
- XLSX 1개
- 2019~2025년 독립 감리보고서

요약 지적표만 보지 않고 상세본문과 FP / AI-RAG / 보안 / 데이터 / UI-UX 전문분야·별첨까지 교차검증했습니다.

Canonical 분석문서:
- `AUDIT_EVIDENCE_MAPPING.md`

### 5.2 MVP 20개 실제 감리사례 실증검증

MVP 20개를 실제 감리사례와 구현 코드에 다시 대조하여 실무 탐지범위를 검증했습니다.

실증검증 결과 실제 감리사례보다 구현범위가 좁다고 판단된 5개 Rule을 우선 보완했습니다.
- AUD-001 필수 산출물 누락
- REQ-002 요구사항 내용 중복
- REQ-003 요구사항 모호성
- REQ-009 요구사항 설계 반영 정합성
- FP-009 FP 산정값 재계산

Canonical 검증문서:
- `MVP20_AUDIT_VALIDATION.md`

### 5.3 Rule + AI + Hybrid

MVP 20개 실행기준:
- Rule 3개
- AI 6개
- Hybrid 11개

숫자·누락·ID처럼 결정적으로 판단 가능한 항목은 Rule로 처리하고,
상충·의미중복·설계반영·영향범위처럼 문맥판단이 필요한 부분에 AI를 사용합니다.

### 5.4 폐쇄망 Local AI

- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off
- 인터넷 차단 상태 실제 검사 확인

업무 문서를 외부 AI 서비스로 전송하지 않고 로컬 환경에서 검사할 수 있도록 구성했습니다.

### 5.5 AI가 최종 위험도를 임의 결정하지 않음

AI는 다음 항목을 판단합니다.
- Impact
- Impact Reason
- Likelihood
- Likelihood Reason

최종 Severity는 AI가 직접 결정하지 않고 deterministic Matrix로 계산합니다.

`Impact × Likelihood → Severity`

이를 통해 생성형 AI 판단과 최종 위험도 산정을 분리했습니다.

---

## 6. 검사체계

Full Rule Catalog 105개:
- AUD 감리 사전점검: 24개
- REQ 요구사항 정합성: 28개
- CHG 변경영향도: 18개
- FP 검증: 12개
- AI 특화 검증: 23개

해커톤 MVP 실제 실행: **20개**

대표 검사:
- AUD-001 필수 산출물 누락
- REQ-001 요구사항 ID 누락·중복
- REQ-002 요구사항 내용 중복
- REQ-003 요구사항 모호성
- REQ-009 요구사항 설계 반영 정합성
- REQ-018 요구사항 추적성
- CHG-001 변경사항 식별
- CHG-006 변경 영향대상 식별
- CHG-012 관련 시험 변경 미반영
- CHG-018 종합 변경위험 후보
- FP-005 기능유형 분류 적정성
- FP-009 FP 산정값 재계산
- AI-005 AI 출력 신뢰성·환각 대응
- AI-009 Prompt Injection 대응
- AI-019 Human-in-the-loop
- AI-022 AI 모델·프롬프트 변경관리

Full Catalog 105개와 MVP 실제 실행 20개는 서로 다른 개념으로 관리합니다.

---

## 7. 실제 감리자료 검증 후 개선한 기능

### AUD-001
산출물목록과 테일러링 결과를 기준으로 현재 제출대상 산출물을 판단하고 실제 업로드 산출물과 비교합니다.
- 테일러링 미적용/제외 항목은 누락으로 판정하지 않음
- 시기미도래/해당없음 항목도 현재 누락에서 제외
- 기준자료가 없으면 임의 표준 산출물목록을 만들어 오탐하지 않음

### REQ-002
단순 동일문구 비교를 넘어 요구사항명과 의미가 유사한 후보까지 AI 비교대상으로 확장했습니다.

### REQ-003
단순 `적절히/필요시` 표현뿐 아니라 응답시간·처리량·횟수·기간 등 **정량기준이 필요한데 값이 빠진 요구사항**과 `협의 후 확정` 같은 미확정 표현을 탐지합니다.

### REQ-009
요구사항 문서 한 개만 보는 것이 아니라 화면/인터페이스/테이블/데이터/프로그램/아키텍처 등 **복수 설계 산출물과 교차검증**합니다.

### FP-009
- 단순 산식 재계산
- XLS/XLSX 표 기반 기능유형·복잡도 또는 RET/FTR·DET·기능개수·FP 값 재계산
- 계산 근거가 부족한 행은 임의 추정하지 않음

---

## 8. 지원 문서

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

모든 문서는 공통 `ParsedDocument / DocumentBlock` 구조로 변환하여 검사합니다.

현재 MVP 제외:
- 스캔 이미지 기반 PDF OCR

---

## 9. 주요 기능

- Home
- Projects
- Project Detail
- Inspection
- Reports
- Administration
- 검사 진행률 / 예상시간 / 예상 남은시간 표시
- 검사 중 취소
- 취소 시 입력상태 유지 및 DB 미저장
- Re-Inspect
- Inspection History
- Issue 상태관리
- Score / Grade
- DOCX / XLSX / TXT Report Export
- 검사기준 관리
- Local AI 설정
- 검사이력 / 프로젝트 데이터 관리

Grade:
- A / B / C / D / E

---

## 10. 검사결과 및 보고서

검사 결과에는 다음 정보를 제공합니다.
- 발견 Issue
- Rule Code / Rule Name
- 근거
- Impact / 근거
- Likelihood / 근거
- Severity / 판정근거
- 개선권고유형
- 개선시점
- 중요 여부
- 카테고리

Project Detail과 Reports는 동일한 최종 보고서 모델을 사용합니다.

보고서 Export:
- DOCX
- XLSX
- TXT

HWPX Report Export는 현재 MVP에서 제외합니다.

---

## 11. 기술 구성

- OS: Windows
- Python 3.13.15
- PySide6 6.11.2
- SQLite
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- PyInstaller 6.22.3 onedir
- WiX Toolset 7.0.0
- Microsoft .NET SDK 10.0.401 x64
- Git / GitHub

주요 Parser 라이브러리:
- python-docx
- openpyxl
- xlrd
- pypdf
- python-pptx
- pyhwpx
- olefile
- legacy-doc

---

## 12. 폐쇄망 실행 및 검증

최종 ZIP(EXE) 실행 구조:

```text
AI_Auditor/
├─ AI_Auditor.exe
├─ runtime/
│  └─ llama.cpp/
│     └─ llama-server.exe
├─ models/
│  └─ Qwen3-4B-Q4_K_M.gguf
└─ data/
   └─ (첫 실행 시 ai_auditor.db 자동 생성)
```

확인 완료:
- PyInstaller onedir 최신 EXE 실행 정상
- Local AI runtime/model 외부 경로 정상
- 개발 DB를 배포본에 포함하지 않고 첫 실행 시 새 DB 자동생성
- 인터넷 차단 상태에서 DOCX 1개 + REQ-003 Local AI 검사 정상
- 검사 결과 생성 및 DB 저장 정상
- Project Detail 표시 정상
- DOCX / XLSX / TXT Export 정상
- Administration 데이터 관리 정상
- 검사 예외 발생 시 오류 유형 + 상세내용 표시
- 전체 회귀테스트 사용자 PC 실패 0건 확인

---

## 13. 최종 배포 패키지

### 13.1 ZIP(EXE)

감리분석 우선 보완 5개가 반영된 최신 코드로 재빌드하고 실제 Local AI 스모크검증을 완료했습니다.

최종 ZIP 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

최종 원칙:
- `AI_Auditor.exe`만 별도로 이동하지 않고 전체 폴더를 하나의 실행 패키지로 취급
- runtime/model 포함
- 개발 DB 미포함
- 첫 실행 시 `data/ai_auditor.db` 자동 생성

### 13.2 MSI 설치형

최종 MSI 설치형 구성:

```text
installer/output/
├─ AI_Auditor_Install.cmd
├─ AI_Auditor_Setup.msi
├─ aia1.cab
├─ aia2.cab
└─ Qwen3-4B-Q4_K_M.gguf
```

최종 설치형 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

설치 방식:
- 사용자는 **`AI_Auditor_Install.cmd`를 실행**
- `AI_Auditor_Setup.msi` 단독 실행 방식은 최종 배포 방식이 아님
- 설치 범위: per-user
- 설치 위치: `%LOCALAPPDATA%\Programs\AI Auditor`
- 2GB를 초과하는 Qwen GGUF 모델은 MSI File table에 직접 포함하지 않음
- Launcher가 MSI 설치 후 `robocopy`로 모델을 설치 경로의 `models/`에 복사
- 원본/대상 모델 파일크기 검증
- 부분설치 상태에서는 설치된 EXE 존재 여부를 확인하여 MSI 재설치를 건너뜀

실제 설치 검증 완료:
- 프로그램 설치 정상
- EXE 실행 정상
- `runtime/llama.cpp/llama-server.exe` 존재 확인
- Qwen 모델 복사 및 파일크기 일치 확인
- `data/ai_auditor.db` 첫 실행 자동 생성
- 동일 REQ-003 스모크 문서로 Local AI 실제 검사 정상
- 결과 생성 및 DB 저장 정상

MSIX는 인증서/정책 복잡성으로 현재 최종 배포범위에서 제외합니다.

---

## 14. 검증 상태

2026-10-10 기준:
- 1~6단계 개발 완료
- UI Freeze 완료
- Local AI 통합 완료
- 최종 EXE 안정화 완료
- 인터넷 차단 Local AI 검사 확인
- 감리자료 114개 분석 완료
- Full Catalog 105개 실무매핑 완료
- MVP20 감리사례 실증검증 완료
- 실증 우선보완 5개 수정 완료
- 전체 `python -m pytest -q` 사용자 PC 실패 0건 확인
- 최신 코드 기준 ZIP(EXE) 재빌드 및 REQ-003 실제 스모크검증 완료
- MSI 설치형 제작 및 실제 설치 완료
- MSI 설치본 DB 자동생성 및 Local AI REQ-003 검사 검증 완료
- 해커톤 제출용 최종 문서화·정리 단계

---

## 15. 한계 및 향후 발전

현재 MVP에서 의도적으로 제한한 부분:
- Full Catalog 105개 중 실제 실행은 MVP 20개
- 스캔 PDF OCR 제외
- HWPX Report Export 제외
- 일부 예방/전략 Rule은 현재 감리자료에서 직접사례가 제한됨
- MSIX는 현재 배포범위 제외

향후에는 `AUDIT_EVIDENCE_MAPPING.md`에 확정한 실무 우선순위를 기준으로 미구현 85개 Rule을 순차 확장합니다.

우선순위:
- P1 13개
- P2 23개
- P3 21개
- P4 28개

신규 Rule 후보는 현재 105개 Catalog에 임의 추가하지 않고 사용자 검토 후 반영 여부를 결정합니다.

---

## 16. 기대효과

- 감리 전 사전점검 시간 단축
- 반복적인 산출물 대조 작업 감소
- 누락·불일치·미확정 요구사항 조기 발견
- 변경 영향 미반영 위험 감소
- FP 산정 오류 사전 발견
- AI/RAG 사업의 신규 품질·보안 위험 사전점검
- 실제 감리근거를 축적하여 향후 Rule을 지속적으로 개선 가능
- 폐쇄망에서도 민감한 프로젝트 산출물을 외부 전송하지 않고 검사 가능
- ZIP(EXE)와 MSI 설치형을 통해 폐쇄망 현장 배포 방식 선택 가능

---

## 17. 핵심 메시지

**AI Auditor는 일반적인 문서 요약 AI가 아니라, 실제 감리자료를 실무 검증 근거로 삼아 프로젝트 산출물의 품질 위험을 사전에 찾아주는 폐쇄망 대응형 품질 감사 플랫폼입니다.**
