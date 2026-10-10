# AI-Auditor

**AI 기반 프로젝트 품질 감사(Auditor) 플랫폼**

AI Auditor는 정보시스템 프로젝트의 요구사항·설계·시험·FP·AI 관련 산출물을 자동 분석하여,
실제 감리에서 반복되는 품질 이슈를 사전에 점검하고 검사결과·조치현황·재검사 이력을 관리하는 데스크톱 애플리케이션입니다.

핵심 목표는 **감리 직전에 사람이 산출물을 일일이 대조하는 부담을 줄이고, 실제 감리지적 가능성이 높은 항목을 사전에 발견하는 것**입니다.

---

## 1. 핵심 특징

- 프로젝트 등록 및 검사 이력 관리
- 5대 검사영역 / Full Rule Catalog 105개 관리
- 최초 MVP20 기준선 + P1 확장 13개
- 현재 소스 기준 실제 실행 Rule 33개
- Rule / AI / Hybrid 혼합 검사
- 요구사항·설계·시험·변경·FP·AI 관련 품질검사
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
- **33개 = MVP20 + P1 13개**
- Rule 7
- AI 6
- Hybrid 20

P1 13개:
- AUD-008 / AUD-010 / AUD-014 / AUD-016 / AUD-018 / AUD-020 / AUD-022 / AUD-023
- REQ-007 / REQ-012 / REQ-017
- FP-002 / FP-008

Full Catalog 105개와 실제 실행 Registry 33개는 구분하여 관리합니다.
`MVP20`은 최초 기준선 명칭으로 유지합니다.

---

## 3. 실제 감리사례 기반 검증

2026-10-09 기준 감리 관련 자료 **114개**를 분석하여 105개 Rule 전체와 매핑했습니다.

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

이후 감리근거 우선순위 P1 13개를 추가 구현했고 2026-10-10 전체 회귀검증까지 완료했습니다.

자세한 근거:
- `AUDIT_EVIDENCE_MAPPING.md`
- `MVP20_AUDIT_VALIDATION.md`
- `P1_IMPLEMENTATION_PLAN.md`

---

## 4. P1 확장 핵심

P1-A:
- AUD-008 / AUD-014 / AUD-016 / FP-008

P1-B:
- REQ-007 / REQ-012 / REQ-017

P1-C:
- AUD-010 / AUD-018

P1-D:
- AUD-020 / AUD-022 / AUD-023

P1-E:
- FP-002

대표 확장 기능:
- 계획 대비 산출물 작성상태
- WBS 구조/일정 이상
- 시험계획/결함 조치상태
- 품질활동 계획↔수행근거
- 인터페이스 정의 완전성
- 계약/RFP/과업 이행근거
- 적용 기준·지침 준수근거
- 요구사항 검증가능성/시험연계/추적누락
- FP 상세근거 및 중복산정 후보

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

---

## 7. 검사 실행 흐름

`Inspection`
→ `Full Catalog 105 선택상태`
→ `실행 Registry 33 필터`
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

2026-10-10 P1 13개 활성 후 사용자 PC 전체 회귀테스트 정상 PASS를 확인했습니다.

---

## 11. 배포 구조

ZIP(EXE):

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

MSI 설치형:

```text
installer/output/
├─ AI_Auditor_Install.cmd
├─ AI_Auditor_Setup.msi
├─ aia1.cab
├─ aia2.cab
└─ Qwen3-4B-Q4_K_M.gguf
```

Qwen 모델은 2GB를 초과하므로 MSI File table에 직접 포함하지 않고 Launcher가 설치 후 모델을 복사하고 크기를 검증합니다.

---

## 12. 현재 배포 상태 주의

기존 ZIP(EXE) 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\AI_Auditor_ZIP_EXE_Final.zip`

기존 MSI 설치형 위치:
`C:\Users\jjang\Desktop\해커톤\Development\AI-Auditor\installer\output\`

기존 패키지는 P1 확장 전 빌드입니다.
현재 GitHub main은 **33개 실행 Rule Freeze** 상태이므로, 제출용 최종 패키지는 최신 소스로 다시 빌드해야 합니다.

다음 배포 절차:
1. 33개 Freeze 소스로 ZIP(EXE) 재빌드
2. ZIP 실행 / Local AI 스모크검증
3. 동일 dist 기준 MSI 재빌드
4. MSI 실제 설치 / DB 자동생성 / Local AI 스모크검증
5. 성공 후 제출문서에 33개 배포 완료로 최종 반영

---

## 13. 데이터 관리

Administration에서 다음을 제공합니다.

- 전체 검사 이력 정리: Issue / Inspection 삭제, Project 유지
- 프로젝트 삭제: 해당 Project의 Issue / Inspection / Project 삭제

삭제는 명시적 순서와 transaction으로 처리하며 오류 발생 시 rollback합니다.

---

## 14. 현재 상태

2026-10-10 기준:

- 1~6단계 개발 완료
- UI Freeze 완료
- Local AI / Severity / 감리판정 완료
- 감리자료 114개 분석 / 105개 매핑 완료
- MVP20 실증검증 및 5개 우선보완 완료
- P1 13개 구현·활성·전체 회귀 완료
- 현재 실제 실행 Registry 33개 Freeze 완료
- **33개 Freeze 기준 ZIP/MSI 재빌드 전**

---

## 15. 제한사항 및 향후 확장

현재 의도적으로 남겨둔 범위:
- 스캔 PDF OCR 제외
- HWPX Report Export 제외
- MSIX 제외

후속 Rule 확장 우선순위:
- P2 23개
- P3 21개
- P4 28개

신규 Rule 후보 9개 + 조건부 1개는 사용자 승인 전 Full Catalog 105에 추가하지 않습니다.

---

## 16. 주요 문서

- `HACKATHON_SUBMISSION.md` — 해커톤 제출용 요약
- `AUDIT_EVIDENCE_MAPPING.md` — 114개 감리자료 ↔ 105개 Rule 실무근거
- `MVP20_AUDIT_VALIDATION.md` — MVP20 실제 감리사례 실증검증
- `P1_IMPLEMENTATION_PLAN.md` — P1 13개 구현 기준
- `RULE_DESIGN.md` — 검사기준/실행구조 설계
- `DECISIONS.md` — 확정 의사결정
- `DEV_STATUS.md` — 개발 진행현황
- `CURRENT_HANDOFF.md` — 최신 인수인계 기준점

프로젝트 산출물·실행데이터 등 민감할 수 있는 실제 업무자료는 GitHub에 저장하지 않습니다.
