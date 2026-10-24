# AI Auditor 제출자료 · 2026-10-24

이 브랜치는 검증된 프로그램 코드 `03a4be2`와 제출자료를 함께 담고 있습니다.

- **[효과측정 1장 PDF](submission/AI_Auditor_Effect_Measurement_1page.pdf)** · [편집용 Word](submission/AI_Auditor_Effect_Measurement_1page.docx)
- **[남은 제출자료 전체 ZIP](submission/AI_Auditor_Remaining_Submission.zip)** · [소스코드 ZIP](submission/AI_Auditor_Source_03a4be2.zip)
- [제출 안내 및 심사위원 접근권한 확인](submission/SUBMISSION_GUIDE.md)
- [Windows 소스 실행 방법](submission/REPRODUCE_WINDOWS.md)
- [추가 전후 비교측정 기록지](submission/AI_Auditor_Measurement_Worksheet.xlsx)
- [완성된 실제 시연 영상 · 2분 58초](https://github.com/jjang99/AI-Auditor/blob/5a96172acf8805a0e717e16ac3543b2bcb341c83/AI_Auditor_Demo_UserFootage.mp4)

현재 효과측정 자료는 사용자 PC의 실제 시연값(DOCX+XLSX 2개, 3개 규칙, 처리시간 434.06초, Issue 후보 7건, Word 보고서 6쪽)을 정리했습니다. 수동 검토 기록이 없어 시간절감률·오류율 감소·인건비 절감액을 산정하지 않았습니다. 처리시간에는 문서 등록·사람의 결과 검토·보고서 저장 전체 과정이 포함되지 않습니다.

저장소 링크를 제출할 때는 심사위원의 열람권한을 확인해야 합니다. 이 브랜치를 준비하며 저장소 공개 설정이나 앱 실행 코드를 변경하지 않았습니다.

---

# AI-Auditor

**AI 기반 프로젝트 품질 감사(Auditor) 플랫폼**

AI Auditor는 정보시스템 프로젝트의 요구사항·설계·시험·FP·AI 관련 산출물을 자동 분석하여,
실제 감리에서 반복되는 품질 이슈를 사전에 점검하고 검사결과·조치현황·재검사 이력을 관리하는 데스크톱 애플리케이션입니다.

핵심 목표는 **감리 직전에 사람이 산출물을 일일이 대조하는 부담을 줄이고, 실제 감리지적 가능성이 높은 항목을 사전에 발견하는 것**입니다.

---

## 1. 핵심 특징

- 프로젝트 등록 및 검사 이력 관리
- 5대 검사영역 / Full Rule Catalog 105개 관리
- 최초 MVP20 + P1 13 + P2 23 확장
- 현재 실제 실행 Rule **56개**
- Rule / AI / Hybrid 혼합 검사
- 요구사항·설계·시험·변경·FP·AI 관련 품질검사
- 감리 예상 지적사항 종합
- Impact / Likelihood 기반 Severity 계산
- 감리 개선권고 유형·시점·중요도 관리
- Re-Inspect 및 Inspection History 관리
- DOCX / XLSX / TXT 보고서 Export
- Local AI 기반 폐쇄망 독립 실행
- Administration을 통한 검사기준·환경·데이터 관리
- Portable ZIP(EXE) 및 MSI 설치형 배포 지원

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

### 최초 MVP20 기준선

- AUD 4
- REQ 6
- CHG 4
- FP 2
- AI 4

최초 실행방식:
- Rule 3
- AI 6
- Hybrid 11

### 현재 실제 실행 Registry

2026-10-10 기준:
- **56개 = MVP20 + P1 13 + P2 23**
- **Rule 14**
- **AI 11**
- **Hybrid 31**

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

P2 23개:
- AUD-005 / AUD-015 / AUD-019 / AUD-021
- REQ-006 / REQ-016 / REQ-020 / REQ-021 / REQ-027 / REQ-028
- CHG-005 / CHG-008 / CHG-010
- FP-006 / FP-007 / FP-011
- AI-003 / AI-008 / AI-013 / AI-015 / AI-017 / AI-021 / AI-023

Full Catalog 105와 실제 실행 Registry 56은 구분하여 관리합니다.
`MVP20`은 최초 기준선 명칭으로 유지합니다.

---

## 3. 실제 감리사례 기반 검증

감리 관련 자료 **114개**를 분석하여 Full Catalog 105개 전체와 실무근거를 매핑했습니다.

분석자료:
- PDF 94개
- DOCX 19개
- XLSX 1개
- 2019~2025년 독립 감리보고서

MVP20 실증검증 과정에서 실제 감리사례보다 구현범위가 좁다고 확인된 5개 Rule을 우선 보완했습니다.

- AUD-001 필수 산출물 누락
- REQ-002 요구사항 내용 중복
- REQ-003 요구사항 모호성
- REQ-009 요구사항 설계 반영 정합성
- FP-009 FP 산정값 재계산

이후 감리근거 우선순위 P1 13개와 P2 23개를 추가 구현했고, 2026-10-10 사용자 PC에서 통합 및 전체 회귀검증까지 완료했습니다.

자세한 근거:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`
- `P1_IMPLEMENTATION_PLAN.md`
- `P2_IMPLEMENTATION_PLAN.md`

---

## 4. P1 / P2 확장 핵심

### P1
- 계획 대비 산출물 작성상태
- WBS 구조/일정 이상
- 시험계획/결함 조치상태
- 품질활동 계획↔수행근거
- 인터페이스 정의 완전성
- 계약/RFP/과업 이행근거
- 적용 기준·지침 준수근거
- 요구사항 검증가능성/시험연계/추적누락
- FP 상세근거 및 중복산정 후보

### P2
- 문서 간 용어 일관성
- 시험 수행·결과 완전성
- 품질지적사항 미조치
- 인터페이스 문서정보 일치
- 요구사항 완전성/상태·승인/출처·상위요구/종합위험
- 변경 승인 및 설계·데이터설계 반영
- FP 분할·통합/산정기준/변경반영
- AI 성능·품질 목표
- 민감정보 통제
- 학습·참조데이터 적정성
- RAG 검색근거
- AI 평가·테스트 체계
- AI 로그·추적성/운영 모니터링
- AI 자원사용·호출 제한

P2의 AI/RAG Rule은 일반 문서에 강제 적용하지 않고 AI/LLM/RAG 맥락과 구조적 근거가 확인될 때만 후보화합니다.

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

제외:
- 스캔 이미지 기반 PDF OCR

---

## 6. Local AI / 폐쇄망 실행

기본 Local AI:
- Qwen3-4B GGUF Q4_K_M
- llama.cpp b11312
- Windows CPU 실행
- reasoning off

검증 설정:
- temperature 0.7
- top-p 0.8
- top-k 20
- min-p 0
- seed 42

AI는 Issue의 Impact / Likelihood와 근거를 판단합니다.
최종 Severity는 AI가 직접 정하지 않고 deterministic Matrix로 계산합니다.

`Impact × Likelihood → Severity`

Portable과 MSI 설치본 모두 실제 Qwen3-4B 모델 로딩 및 Local AI 응답을 확인했습니다.

---

## 7. 검사 실행 흐름

`Inspection`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 56 필터`
→ `문서 Parser`
→ `Rule / AI / Hybrid 검사`
→ `교차문서 비교/후처리`
→ `Issue 생성`
→ `Impact / Likelihood 평가`
→ `Severity Matrix`
→ `감리 개선판정`
→ `DB 저장`
→ `Project Detail / Reports`

검사 중 취소를 지원하며 취소된 검사는 DB에 저장하지 않습니다.

---

## 8. 보고서 Export

지원 형식:
- DOCX
- XLSX
- TXT

HWPX Report Export는 현재 범위에서 제외합니다.

---

## 9. 개발 환경

- OS: Windows
- Python: 3.13.15
- UI Framework: PySide6 6.11.2
- Database: SQLite
- EXE Packaging: PyInstaller 6.22.3 onedir
- MSI Packaging: WiX Toolset 7.0.0 / .NET SDK 10.0.401 x64
- Version Control: Git / GitHub

---

## 10. 소스 실행

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python main.py
```

전체 테스트:

```bat
python -m pytest -q
```

2026-10-10 P2-D 활성 후 Registry 56 통합검증과 전체 회귀테스트를 사용자 PC에서 정상 PASS 확인했습니다.
정확한 passed/subtests 숫자는 사용자 출력 미제공으로 임의 기록하지 않습니다.

---

## 11. 배포 구조

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

최종 검증:
- ZIP 약 2.35 GB
- 모델 약 2.33 GB
- SHA256: `A53BB20BD7CA531EB27F67C6D60371DF5C6E4BDC68410688A4F331B80A054672`
- EXE Home 실행 정상
- DB integrity `ok`
- llama.cpp build 11312 정상
- Qwen3-4B 모델 실제 로딩 정상
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

Qwen 모델은 2GB를 초과하므로 MSI File table에 직접 포함하지 않고 Launcher가 설치 후 모델을 복사하고 크기를 검증합니다.

최종 검증:
- 기존 설치본 제거 후 최신 MSI 실제 설치 성공
- `msiexec` Exit Code 0
- 설치 위치 `%LOCALAPPDATA%\Programs\AI Auditor`
- 설치 EXE Home 실행 정상
- EXE / llama-server / 모델 / DB 존재 확인
- 설치 DB 정상
- 설치 경로 Qwen3-4B 실제 로딩 정상
- 설치본 Local AI 실제 응답 정상
- 설치 Launcher 재실행 정상

`AI_Auditor_Install.cmd`는 MSI 오류코드 출력 문제를 `EnableDelayedExpansion` + `!ERRORLEVEL!` 방식으로 보완했으며, 수정본 포함 최종 재빌드와 동작검증을 완료했습니다.

---

## 12. 데이터 관리

Administration에서 다음을 제공합니다.

- 전체 검사 이력 정리: Issue / Inspection 삭제, Project 유지
- 프로젝트 삭제: 해당 Project의 Issue / Inspection / Project 삭제

삭제는 명시적 순서와 transaction으로 처리하며 오류 발생 시 rollback합니다.

---

## 13. 현재 상태

2026-10-10 기준:

- 1~6단계 개발 완료
- UI Freeze 완료
- Local AI / Severity / 감리판정 완료
- 감리자료 114개 분석 / 105개 매핑 완료
- MVP20 실증검증 및 5개 우선보완 완료
- P1 13개 구현·활성·전체 회귀 완료
- P2 23개 구현·활성·전체 회귀 완료
- **현재 실제 실행 Registry 56개 Freeze 완료**
- **Portable ZIP(EXE) 최종 재빌드·스모크 완료**
- **MSI 최종 재빌드·실설치·Local AI 스모크 완료**

---

## 14. 제한사항 및 향후 확장

현재 의도적으로 남겨둔 범위:
- 스캔 PDF OCR 제외
- HWPX Report Export 제외
- MSIX 제외

후속 Rule 확장 우선순위:
- P3 21개
- P4 28개

신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Full Catalog 105에 추가하지 않습니다.

---

## 15. 주요 문서

- `HACKATHON_SUBMISSION.md` — 해커톤 제출용 최종 요약
- `AUDIT_EVIDENCE_MAPPING.md` — 114개 감리자료 ↔ 105개 Rule 실무근거
- `MVP20_AUDIT_VALIDATION.md` — MVP20 실제 감리사례 실증검증
- `P1_IMPLEMENTATION_PLAN.md` — P1 13개 구현 기준
- `P2_IMPLEMENTATION_PLAN.md` — P2 23개 구현 기준/완료결과
- `RULE_DESIGN.md` — 검사기준/실행구조 설계
- `DECISIONS.md` — 확정 의사결정
- `DEV_STATUS.md` — 개발 진행현황
- `CURRENT_HANDOFF.md` — 최신 인수인계 기준점

프로젝트 산출물·실행데이터 등 민감할 수 있는 실제 업무자료는 GitHub에 저장하지 않습니다.
