# 남은 제출자료 안내

| 항목 | 이번 제출용 파일 |
|---|---|
| 자동화 전후 효과 추정 1장 | **AI_Auditor_Effect_Estimate_1page.pdf** |
| 소스 ZIP · 첨부 허용 시 | **AI_Auditor_Source_Submission.zip** |
| 소스 주소 · URL 제출 시 | https://github.com/jjang99/AI-Auditor/tree/codex/hackathon-submission |

영상은 기존 완료본(2분 58초), PPT는 사용자 최종본(10장 이내)을 별도로 제출합니다.

## 새 자료의 성격

제목은 ‘자동화 전후 효과 추정’입니다. 사용자 PC의 자동검사 처리시간 434.06초는 실측이고, 수동 전체 30분과 사용 후 추가 작업 10분은 설명용 가정입니다. 이 조건에서 사용 후 약 17분 14초, 예상 약 12분 46초·42.6% 감소로 계산됩니다. 가정이 달라지면 시간이 증가하는 경우도 함께 표시했습니다.

수동 비교 및 사람의 추가 작업시간을 실제로 재지 않았으므로 42.6%를 실제 달성한 성과로 표현하지 않습니다. 추정치 사용이 허용되는 제출 형식에서 사용하세요. 상세 계산은 EFFECT_ESTIMATE_METHOD.md와 AI_Auditor_Effect_Estimate.xlsx에 있습니다.

## 기존 자료 보관

AI_Auditor_Effect_Measurement_1page.pdf와 AI_Auditor_Measurement_Data.xlsx는 합성 문서의 결함 검출 기능검증 참고자료입니다. 새 전후 효과 추정본과 구분하여 보관했습니다. experiment/와 supporting_demo/의 원자료도 유지합니다. 이전 파일은 시간절감 비교의 최종본으로 선택하지 마세요.

## GitHub 접근권한

현재 저장소는 비로그인 접속에서 열리지 않았습니다. 비공개 링크 제출 시 심사위원 계정을 초대하거나, 소스 ZIP 첨부가 허용되는지 제출처에 확인하세요. 저장소 공개나 기본 브랜치 변경은 별도로 결정해야 합니다. 영상 보관용 codex/demo-video에는 프로그램 소스가 없습니다.

## 편집·실행 자료

- AI_Auditor_Effect_Estimate_1page.docx: 새 추정본 편집용.
- AI_Auditor_Effect_Estimate.xlsx / estimate_assumptions.json: 가정과 계산식.
- REPRODUCE_WINDOWS.md: Python 실행·모델/runtime 준비 안내.
- AI_Auditor_Remaining_Submission.zip: 새 자료와 기존 근거를 함께 담은 묶음.
