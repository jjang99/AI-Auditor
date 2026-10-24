# AI Auditor 사용자 촬영본 시연영상

최신 완성본: **AI_Auditor_Demo_UserFootage.mp4** · **2분 58초** · 1920×1080

사용자가 새로 촬영한 Windows 앱 원본만으로 편집했습니다.
프로젝트명: **요구사항 품질점검**

## 영상 흐름

Home → 프로젝트·문서 등록 → Rule 선택 → 실제 검사 진행 → 검사 결과
→ REQ-018 / REQ-001 근거·위험도 → Re-Inspect 준비 → Inspection History
→ 보고서 Export → 실제 Word 보고서 → Local AI → 13번 Home 화면으로 돌아와 마무리

- 검사 문서: DOCX 1개 + XLSX 1개
- 선택한 실제 규칙: REQ-001 / REQ-006 / REQ-018
- 촬영된 실제 결과: **69점 / D등급 / 이슈 7개**
- Full Catalog 105개와 실제 실행 가능 Rule 56개를 구분하여 표기
- Re-Inspect는 수정본 v0.2의 문서 등록과 기존 검사기준 재사용 준비 화면
- Word 보고서는 사용자가 보낸 최종 촬영본 사용
- 실제 대기 구간만 삭제하고 원본 재생속도를 유지
- 대부분 전체 화면을 고정하고, 근거와 모델 확인에서만 조금 확대(최대 1.16배)
- 둥근 남색 자막 박스 · 얇은 파란 포인트 선 · 정돈된 글자와 여백
- 클릭 위치의 은은한 강조

재검사 완료 결과나 촬영되지 않은 동작을 새로 만들지 않았습니다.
앱 소스는 변경하지 않았습니다. 자막은 영상에 포함되어 있습니다.

마무리 문구: **AI가 먼저 짚는 위험, 사람이 완성하는 품질.**

Home 화면과 문구가 함께 천천히 사라지고 짧은 검은 화면으로 끝납니다.

## Windows에서 다운로드하고 재생하기

AI-Auditor 폴더의 터미널에서 아래 세 줄을 실행합니다.

```powershell
git fetch origin codex/demo-video
git restore --source=FETCH_HEAD --worktree -- AI_Auditor_Demo_UserFootage.mp4
Invoke-Item .\AI_Auditor_Demo_UserFootage.mp4
```

영상은 `main.py`와 같은 폴더에 저장됩니다.
별도 자막 파일은 `AI_Auditor_Demo_UserFootage.srt`입니다.
