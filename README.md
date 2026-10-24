# AI Auditor

프로젝트 산출물을 읽고 누락·중복·불일치 등 품질 위험 후보와 판단 근거를 제시하는 Windows 데스크톱 앱입니다. 담당자가 후보를 확인하고 최종 판단합니다.

`문서 등록 → 검사기준 선택 → 검사 → Issue 근거·위험도 확인 → 재검사·이력 → 보고서`

## 제출자료

| 자료 | 위치 |
|---|---|
| 실제 시연 영상 · 2분 58초 | [사용자 원본 녹화 편집본](https://github.com/jjang99/AI-Auditor/blob/5a96172acf8805a0e717e16ac3543b2bcb341c83/AI_Auditor_Demo_UserFootage.mp4) |
| 요약표 작성시간 비교 · 1장 | [PDF](submission/AI_Auditor_Report_Time_Comparison_1page.pdf) / [편집용 Word](submission/AI_Auditor_Report_Time_Comparison_1page.docx) |
| 제공시간·계산식·범위 | [Excel](submission/AI_Auditor_Report_Time_Data.xlsx) / [출처와 방법](submission/REPORT_TIME_METHOD.md) |
| 기존 가정 시나리오 참고 | [이전 추정 PDF](submission/AI_Auditor_Effect_Estimate_1page.pdf) / [가정과 계산](submission/EFFECT_ESTIMATE_METHOD.md) |
| 기존 기능검증 참고자료 | [결함 검출 PDF](submission/AI_Auditor_Effect_Measurement_1page.pdf) / [검증 Excel](submission/AI_Auditor_Measurement_Data.xlsx) / [실험 원본](submission/experiment/) |
| 소스 ZIP | [소스와 재현자료](submission/AI_Auditor_Source_Submission.zip) |
| 남은 제출자료 묶음 | [다운로드 ZIP](submission/AI_Auditor_Remaining_Submission.zip) |
| 발표 PPT | 사용자 최종본을 별도 제출 · **10장 이내** |

검증된 앱 코드 기준은 `03a4be2d81b1e75045b88f00db2beb180b2eb758`입니다. 제출 브랜치는 `codex/hackathon-submission`입니다. 이 정리는 안내·기록·검증자료에 한정하며 기존 앱 소스와 패치 적용 순서를 유지합니다.

## 요약표 작성시간 비교 · 사용자 보고 기준

같은 프로젝트의 기존 검사결과를 요약 8개 항목의 Word 문서로 작성·저장·열어 확인하는 단계에서 사용자가 보고한 근사시간은 수동 약 7분 22초, 자동 약 6초였습니다. 차이는 약 7분 16초입니다. 제출 요약에서는 전후 시간과 차이를 중심으로 제시하고, 비율은 계산 원자료의 참고 항목으로 구분했습니다. **동일인·각 1회·근사값**이며 전체 검사·감리 업무의 절감률은 아닙니다. 파일·영상·타이머 기록으로 독립 재검증하지 않았습니다. 자세한 범위와 정정은 [방법](submission/REPORT_TIME_METHOD.md)에 공개했습니다.

## 별도 자동검사 실측과 이전 가정 시나리오

자동검사 처리시간 **434.06초**는 사용자 PC의 단일 시연 실측값입니다. 수동 전체 작업시간 **30분**, AI 활용 후 문서 등록·사람의 후보 검토·보고서 저장 **10분**은 설명용 가정입니다. 이 조건에서 사용 후 약 17분 14초, 예상 약 12분 46초·42.6% 감소로 계산됩니다. **42.6%는 실제 달성한 절감률이 아닙니다.** 가정에 따라 시간이 늘어나는 경우도 새 자료에 표시했습니다.

## 별도 결함 검출 기능검증

합성 문서 DOCX·XLSX 각 1개에 사전 선언한 표적 결함 4개를 넣고 REQ-001 / REQ-006 / REQ-018을 실제 Local AI와 함께 실행했습니다. **3/4개 검출(75%), 미탐 1개**, 정답표 밖의 추가 지적은 관찰되지 않았습니다. 정답표에 따라 네 결함을 스크립트가 수정한 뒤에는 지적이 3건에서 0건으로 바뀌었습니다.

이는 단일 자체 검증입니다. 제품 전체 정확도나 사람 대비 시간절감률이 아니며, 앱이 문서를 자동 수정했다는 뜻도 아닙니다. 전체 검사 처리시간 434.06초·후보 7건의 사용자 PC 시연은 [별도 참고 관찰값](submission/supporting_demo/demo_observations.json)입니다.

## 실행

Python 3.13과 아래 모델/runtime을 준비합니다. 소스 ZIP에는 대용량 모델·실행 바이너리가 포함되지 않습니다.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

```text
models/Qwen3-4B-Q4_K_M.gguf
runtime/llama.cpp/llama-server.exe
```

모델은 Qwen3-4B Q4_K_M, runtime은 llama.cpp b11312입니다. 상세 준비와 원본 배포처는 [Windows 실행 안내](submission/REPRODUCE_WINDOWS.md)를 참고하세요.

## 코드 구조

| 경로 | 역할 |
|---|---|
| main.py / ui/ | 실행 진입점과 PySide6 화면 |
| app/ | 문서 파서, 검사 서비스, SQLite 저장소 |
| rules/ | 검사기준, Rule·AI·Hybrid 엔진, 위험도 평가 |
| assets/ | 화면 아이콘 |
| tests/ | 자동 회귀검증 |
| tools/ / scripts/ / installer/ | 진단·기준 생성·배포 도구 |
| submission/ | 제출물과 이번 측정 근거 |
| docs/archive/ | 과거 개발·계획 기록 |

## 구현과 검증 범위

- 전체 Catalog 105개 중 실제 실행 규칙 56개: Rule 14 / AI 11 / Hybrid 31.
- 지원 파서 9종: DOCX, DOC, XLSX, XLS, PDF, PPTX, PPT, HWPX, HWP. 스캔 PDF OCR 제외.
- 검사결과를 DOCX / XLSX / TXT로 내보냅니다. 최종 위험도는 Impact × Likelihood Matrix로 계산합니다.
- 테스트 명령: `.\.venv\Scripts\python.exe -m pytest -q`. 기술 회귀 결과는 실제 업무 오류율과 구분합니다.
- Local AI 추론 경로의 외부 AI API 사용료는 0원입니다. PC·전력·개발비를 포함한 총비용 0원을 뜻하지 않습니다.

검사 설계는 [RULE_DESIGN.md](RULE_DESIGN.md), 저장소 정리 근거는 [저장소 검토 기록](docs/REPOSITORY_REVIEW.md)에 있습니다.

## 제출 시 접근권한

비공개 저장소 링크는 심사위원이 열람할 수 있어야 합니다. 제출처가 허용하면 소스 ZIP을 첨부하거나 심사위원 계정을 초대하세요. 제출 절차는 [제출 안내](submission/SUBMISSION_GUIDE.md)를 참고하세요.
