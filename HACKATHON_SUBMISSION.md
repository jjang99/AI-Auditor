# AI Auditor 해커톤 제출용 최종 요약

> 기준일: 2026-10-10
> 본 문서는 현재 GitHub main의 실제 구현·검증 상태를 기준으로 정리한다.
> **실행 Registry 56개 Freeze 및 Portable/MSI 실제 배포검증 완료 상태**다.

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
- FP 산정 오류·중복을 표 단위로 재검토해야 함
- 최근 AI/RAG 적용 사업은 신뢰성·보안·운영 리스크 점검이 필요함
- 실제 업무망은 인터넷 사용이 제한되거나 폐쇄망인 경우가 많음

AI Auditor는 이 반복 작업을 자동화하여 감리 대응 전에 위험요소를 먼저 발견하는 것을 목표로 합니다.

---

## 4. 해결 방법

검사 구조:

`프로젝트 산출물 업로드`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 56 필터`
→ `문서 Parser`
→ `Rule / AI / Hybrid 검사`
→ `문서별 사전분석 / 교차문서 비교`
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

Canonical 분석문서:
- `AUDIT_EVIDENCE_MAPPING.md`

### 5.2 MVP20 실증검증 + P1/P2 확장

최초 MVP20을 실제 감리사례와 코드에 다시 대조해 탐지범위를 검증했습니다.

실증 우선보완 5개:
- AUD-001 필수 산출물 누락
- REQ-002 요구사항 내용 중복
- REQ-003 요구사항 모호성
- REQ-009 요구사항 설계 반영 정합성
- FP-009 FP 산정값 재계산

그 후 감리자료 기반 우선순위에 따라:
- P1 13개 구현 완료
- P2 23개 구현 완료

2026-10-10 기준 P1/P2는 모두 Registry 활성 및 통합·전체 회귀검증을 완료했습니다.

### 5.3 현재 실제 실행 Rule 56개

- 최초 MVP20 기준선
- P1 13개 추가
- P2 23개 추가
- 현재 실제 실행 Registry: **56개**

실행방식:
- **Rule 14**
- **AI 11**
- **Hybrid 31**

`MVP20`은 최초 기준선 명칭이며 현재 실제 실행 범위는 56개입니다.

### 5.4 Rule + AI + Hybrid

숫자·누락·ID처럼 결정적으로 판단 가능한 항목은 Rule로 처리하고,
상충·의미중복·설계반영·영향범위처럼 문맥판단이 필요한 부분에 AI를 사용합니다.
Hybrid는 Rule 기반 후보추출 후 필요한 경우에만 AI를 호출합니다.

### 5.5 폐쇄망 Local AI

- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off
- 인터넷 연결 없이 로컬 실행

업무 문서를 외부 AI 서비스로 전송하지 않고 로컬 환경에서 검사할 수 있도록 구성했습니다.
Portable과 MSI 설치본 모두 실제 모델 로딩과 AI 응답을 확인했습니다.

### 5.6 AI가 최종 위험도를 임의 결정하지 않음

AI는 Impact / Likelihood와 근거를 판단하고,
최종 Severity는 deterministic Matrix로 계산합니다.

`Impact × Likelihood → Severity`

### 5.7 AI/RAG Rule의 오탐 방지

P2-D의 AI 특화 Rule은 일반 문서에 강제로 적용하지 않습니다.
AI/LLM/RAG 문맥과 구조적 근거가 확인될 때만 후보를 생성하며,
단순 `모델`이라는 단어만으로 AI 문서라고 판단하지 않습니다.

---

## 6. Full Catalog / 실제 실행 범위

Full Rule Catalog 105개:
- AUD: 24
- REQ: 28
- CHG: 18
- FP: 12
- AI: 23

현재 실제 실행 Registry:
- **56개 = MVP20 + P1 13 + P2 23**

대표 검사:
- AUD-001 필수 산출물 누락
- AUD-008 계획 대비 산출물 작성상태
- AUD-010 WBS 완전성·비정상 항목
- AUD-015 시험 수행·결과 완전성
- AUD-018 품질활동 계획 대비 수행
- AUD-020 인터페이스 정의 완전성
- AUD-021 인터페이스 문서정보 일치
- AUD-022 계약·과업내용 반영 및 이행 증적
- AUD-023 관련 기준·지침 준수
- REQ-001 요구사항 ID 누락·중복
- REQ-006 요구사항 완전성
- REQ-007 요구사항 검증가능성·검증방법
- REQ-009 요구사항 설계 반영 정합성
- REQ-012 요구사항 시험항목 누락
- REQ-016 중요 요구사항 시험범위 누락
- REQ-017 요구사항 추적관계 누락
- REQ-027 요구사항 출처·상위요구/추가기능 근거
- CHG-001 / CHG-006 / CHG-008 / CHG-010 / CHG-012 / CHG-018 변경영향도 계열
- FP-002 FP 산정대상 중복
- FP-006 기능 단위 분할·통합 적정성
- FP-007 FP 산정방식·적용기준 적정성
- FP-008 상세 산정정보 적정성
- FP-009 FP 산정값 재계산
- FP-011 FP 변경반영 누락
- AI-003 / AI-008 / AI-013 / AI-015 / AI-017 / AI-021 / AI-023 AI 특화 검증

---

## 7. P2 확장 핵심 예시

### CHG-008 / CHG-010
확인된 변경사항과 설계/데이터설계 문서를 교차비교합니다.
변경자료와 대응 산출물이 함께 있을 때만 후보를 생성하며, CHG-010은 데이터/테이블/컬럼 영향이 명시된 변경에 한정합니다.

### FP-006
구조형 FP 행의 기능명·유형·상세근거를 묶어 과도 분할 또는 이질 기능 통합 후보를 AI에 전달합니다.
완전 동일 기능명 중복은 FP-002 역할로 분리합니다.

### AI-015
RAG/검색증강/벡터검색 구조가 명시된 문서에만 적용하며, 검색근거와 답변근거의 적합성 관련 설계·검증 근거를 판단합니다.

### AI-021
AI 입력·모델·조건·결과의 추적근거와 운영 품질·이상 모니터링 근거를 확인합니다.
단순 애플리케이션 로그 존재만으로 AI 추적성이 충족됐다고 판단하지 않습니다.

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

제외:
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

## 10. 기술 구성

- Windows
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

## 11. 검증 상태

2026-10-10 기준:
- 1~6단계 개발 완료
- UI Freeze 완료
- Local AI 통합 완료
- 감리자료 114개 분석 완료
- Full Catalog 105 실무매핑 완료
- MVP20 실증검증 및 우선보완 5개 완료
- P1 13개 구현·활성·전체 회귀 완료
- P2 23개 구현·활성·전체 회귀 완료
- Registry 56 + 선택 UI + Catalog/MVP 통합 테스트 PASS
- 최종 `python -m pytest -q` 사용자 PC 정상 PASS

정확한 passed/subtests 숫자는 사용자 출력 미제공으로 임의 기록하지 않습니다.

---

## 12. 배포 패키지 구조 및 실제 검증

### Portable ZIP(EXE)

```text
dist/
├─ AI_Auditor/
│  ├─ AI_Auditor.exe
│  ├─ runtime/
│  │  └─ llama.cpp/
│  │     └─ llama-server.exe
│  ├─ models/
│  │  └─ Qwen3-4B-Q4_K_M.gguf
│  └─ data/
│     └─ ai_auditor.db
├─ AI_Auditor_Portable.zip
└─ AI_Auditor_Portable.zip.sha256.txt
```

Portable 실제 검증:
- ZIP 약 2.35 GB
- 모델 약 2.33 GB
- SHA256 `A53BB20BD7CA531EB27F67C6D60371DF5C6E4BDC68410688A4F331B80A054672`
- EXE Home 실행 정상
- DB integrity `ok`
- llama.cpp build 11312 정상
- Qwen3-4B 실제 로딩 정상
- Local AI health/응답 정상

### MSI 설치형

```text
installer/output/
├─ AI_Auditor_Install.cmd
├─ AI_Auditor_Setup.msi
├─ aia1.cab
├─ aia2.cab
└─ Qwen3-4B-Q4_K_M.gguf
```

Qwen 모델은 2GB를 초과하므로 MSI File table에 직접 포함하지 않고 설치 Launcher가 설치 후 모델을 복사하고 크기를 검증합니다.

MSI 실제 검증:
- 기존 설치본 제거 후 최신 MSI 실제 설치 성공
- `msiexec` Exit Code 0
- 설치 위치 `%LOCALAPPDATA%\Programs\AI Auditor`
- 설치 EXE Home 실행 정상
- EXE / llama-server / 모델 / DB 존재 확인
- 설치 DB 정상
- 설치 경로 Qwen3-4B 실제 로딩 정상
- 설치본 Local AI 실제 응답 정상
- 최종 설치 Launcher 재실행 정상

설치 Launcher에서 MSI 오류코드가 비어 보일 수 있던 `%ERRORLEVEL%` 처리 문제는 `EnableDelayedExpansion` + `!ERRORLEVEL!` 방식으로 수정했고, 수정본 포함 최종 재빌드와 동작확인을 완료했습니다.

**56개 Freeze 기준 Portable + MSI 배포검증 완료.**

---

## 13. 한계 및 향후 발전

현재 의도적 제한:
- 스캔 PDF OCR 제외
- HWPX Report Export 제외
- MSIX 제외

향후 Rule 확장 우선순위:
- P3 21개
- P4 28개

신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Full Catalog 105에 추가하지 않습니다.

---

## 14. 기대효과

- 감리 전 사전점검 시간 단축
- 반복적인 산출물 대조 작업 감소
- 누락·불일치·미확정 요구사항 조기 발견
- 변경 영향 미반영 위험 감소
- FP 산정 오류·중복 사전 발견
- AI/RAG 사업의 신규 품질·보안 위험 사전점검
- 실제 감리근거를 축적하여 Rule을 지속적으로 개선 가능
- 폐쇄망에서도 민감한 프로젝트 산출물을 외부 전송하지 않고 검사 가능

---

## 15. 핵심 메시지

**AI Auditor는 일반적인 문서 요약 AI가 아니라, 실제 감리자료를 실무 검증 근거로 삼아 프로젝트 산출물의 품질 위험을 사전에 찾아주는 폐쇄망 대응형 품질 감사 플랫폼입니다.**
