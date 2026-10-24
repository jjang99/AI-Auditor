# 남은 제출자료 안내

1. 효과측정에는 `AI_Auditor_Effect_Measurement_1page.pdf`를 첨부합니다. Word는 편집용, Excel과 experiment/는 수치의 근거입니다.
2. 소스코드에는 https://github.com/jjang99/AI-Auditor/tree/codex/hackathon-submission 을 기입합니다. ZIP 첨부가 허용되면 `AI_Auditor_Source_Submission.zip`을 제출할 수 있습니다.
3. 영상은 기존 완료본(2분 58초), PPT는 사용자 최종본(10장 이내)을 별도로 제출합니다.

## 효과측정의 범위

이번 자료는 사전 정답표가 있는 합성 DOCX·XLSX를 실제 검사한 결과입니다. 4개 표적 결함 중 3개 검출(75%), 미탐 1개입니다. 네 결함을 정답표대로 스크립트가 고친 뒤 지적이 3건에서 0건이 되었습니다. 전후 입력·실제 지적·원응답·보고서를 함께 제공합니다.

실제 사람 대비 절감시간을 측정한 자료가 아닙니다. 제출처가 수동 대비 시간·비용 효과만 허용한다면 이 검증 자료로 대체 가능한지 확인이 필요합니다. 과거 실행결과 요약본은 제출용 효과측정으로 사용하지 마세요.

## GitHub 접근권한

현재 저장소는 비로그인 접속에서 열리지 않았습니다. 비공개 링크만 제출하면 심사위원이 열지 못할 수 있습니다. 심사위원 계정을 초대하거나, 소스 ZIP 첨부가 허용되는지 제출처에 확인하세요. 저장소 공개나 기본 브랜치 변경은 별도로 결정해야 합니다.

영상 보관용 codex/demo-video에는 프로그램 소스가 없습니다. 소스 제출에는 위 제출 브랜치 주소를 사용하세요.

## 파일 구성

- AI_Auditor_Effect_Measurement_1page.pdf / .docx: 1장 요약과 편집본.
- AI_Auditor_Measurement_Data.xlsx: 실제 측정값·정답표 대조·계산식·근거 파일 해시.
- AI_Auditor_Source_Submission.zip: 정리된 소스와 실행·검증 안내. 모델/runtime·실제 업무자료·개인 DB 제외.
- experiment/: 합성 문서와 실제 실행 증거. supporting_demo/: 기존 사용자 PC 시연의 참고 관찰값.
- REPRODUCE_WINDOWS.md: Python 실행 준비.
