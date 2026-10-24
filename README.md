# AI Auditor 실제 앱 시연영상

최신 완성본: **AI_Auditor_Demo_Complete.mp4** · 2분 17초 · 1920×1080 · 한글 자막 포함

가이드 기준 가상 프로젝트 자료로 실제 앱을 자동조작하여 녹화했습니다.
프로젝트명: **공공서비스 통합포털 품질 점검**

- 문서 4개 선택 → REQ-001 / REQ-018 / FP-009 선택 → 검사 시작
- 중복 요구사항 ID, 누락된 추적정보, FP 계산 오류의 근거와 위험도 확인
- 수정본 4개로 Re-Inspect → 동일한 규칙 3개 복원 → 실제 검사 시작
- 초기 63점·D등급·이슈 5개 → 수정본 100점·A등급·이슈 0개
- 검사 이력 및 Reports 결과 비교 → Word 보고서 저장 → Local AI 모델 확인

검사 대기 구간만 축약했습니다. 실제 초기 검사는 약 123초였습니다.
실제 Local AI를 사용했고, 앱 소스는 변경하지 않았습니다.
이슈 0개는 선택한 세 규칙의 검사 결과입니다.

**AI_Auditor_Demo_Materials.zip**에는 초기본·수정본 8개 문서와 실제 저장한 Word 보고서, 자료 안내, 참고 가이드가 들어 있습니다.

## Windows에서 영상 받기

AI-Auditor 폴더에서 터미널을 열고 다음 세 줄을 실행합니다.

```powershell
git fetch origin codex/demo-video
git restore --source=FETCH_HEAD --worktree -- AI_Auditor_Demo_Complete.mp4
Invoke-Item .\AI_Auditor_Demo_Complete.mp4
```

영상은 `main.py`와 같은 폴더에 저장됩니다.
자료도 받으려면 다음 줄을 실행합니다.

```powershell
git restore --source=FETCH_HEAD --worktree -- AI_Auditor_Demo_Materials.zip
```
