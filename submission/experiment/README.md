# 결함 검출·수정 후 재검증 실험

protocol.json과 ground_truth.json은 실제 검사 실행 전에 확정한 계획과 정답표입니다. 원본 DOCX/XLSX, 실제 JSON 결과, Local AI 원응답, 앱의 DOCX/XLSX/TXT 내보내기 결과를 함께 제공합니다. 모두 자체 작성한 합성 자료입니다.

adjudication.json은 검사 후 정답표와 지적을 대조한 자체 판정입니다. 모델 응답을 교체하거나 탐지 결과가 좋아질 때까지 재실행하지 않았습니다. 수정본 실행은 정답표의 네 결함을 모두 고친 입력에 대한 별도 검사입니다.

재현 스크립트의 기본 저장 위치는 배포용으로 바꾸었고, 중복된 설명 문자열을 정리했습니다. 입력 생성·실제 검사·평가·보고서 생성의 동작과 앱 소스는 동일합니다.

Windows에서 저장소 루트에 모델/runtime과 가상환경을 준비한 다음 실행합니다.

```powershell
.\.venv\Scripts\python.exe .\submission\experiment\run_experiment.py --repo . --out .\temp\measurement-rerun
```

같은 출력 폴더를 덮어쓰지 않습니다. 새 실험은 새 폴더를 지정하세요. Local AI 실행 결과와 소요시간은 환경에 따라 달라질 수 있습니다.
