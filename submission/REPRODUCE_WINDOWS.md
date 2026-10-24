# 소스코드 제출 및 실행 안내

프로그램 코드 기준: `03a4be2d81b1e75045b88f00db2beb180b2eb758`
검증된 소스: https://github.com/jjang99/AI-Auditor/tree/03a4be2d81b1e75045b88f00db2beb180b2eb758
제출 브랜치: `codex/hackathon-submission` (앱 소스는 위 코드 기준과 동일)

## 소스 구성

`main.py`가 프로그램 실행 진입점이며 `ui/`, `app/`, `rules/`, `tests/`가 주요 소스입니다.
압축본의 앱 소스는 이 버전과 동일하며, 문서는 제출용으로 정리하고 자체 검증용 합성 문서·결과를 포함했습니다. 실제 업무 검사 문서·개인 DB·가상환경·모델 및 실행 바이너리는 포함하지 않습니다. experiment/의 문서와 보고서는 자체 생성한 검증용입니다.

## Windows 실행

Python 3.13을 준비하고 `AI-Auditor` 폴더에서 다음 명령을 실행합니다.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Local AI를 사용하려면 다음 두 경로를 별도로 준비합니다. 실행파일과 함께 배포된 DLL도 같은 runtime 폴더에 둡니다.

```text
models/Qwen3-4B-Q4_K_M.gguf
runtime/llama.cpp/llama-server.exe
```

공식 모델: https://huggingface.co/Qwen/Qwen3-4B-GGUF
검증한 모델 revision: `bc640142c66e1fdd12af0bd68f40445458f3869b`
검증한 모델 SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
llama.cpp runtime: https://github.com/ggml-org/llama.cpp/releases/tag/b11312
Windows CPU x64용 배포본을 사용합니다. 모델·runtime 대용량 파일은 이 소스 ZIP에 포함하지 않습니다.

준비 후 실행합니다.

```powershell
.\.venv\Scripts\python.exe main.py
```

자동 테스트 실행:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 검증 범위

코드 기준 `03a4be2`에서 클라우드 전체 회귀 결과는 328 passed + 51 subtests passed였습니다. 이는 별도의 기술 검증이며 실제 프로젝트 오류율 0%라는 뜻이 아닙니다.
이 버전은 GUI 콜백의 실행 스레드를 바로잡은 수정본입니다. 새 patch 파일을 추가하지 않았고, 앱 소스 변경은 기존 `ui/inspection_runtime.py`에 한정했습니다.

최종 실제 시연은 DOCX+XLSX 2개와 REQ-001 / REQ-006 / REQ-018을 사용했습니다. 434.06초, 69점·D등급·후보 7건은 그 시연 사례의 결과이며 다른 입력에 동일 결과를 보장하지 않습니다.

## 접근권한

이 저장소는 비로그인 상태에서 404 응답이 확인되었습니다. 저장소 링크를 제출할 때 심사위원의 열람권한을 확인해야 합니다. 제출처가 첨부를 허용하면 소스 ZIP을 함께 제출할 수 있습니다. 저장소 공개나 계정 초대는 자동으로 변경하지 않았습니다.

## 효과측정 재현

`submission/experiment/README.md`의 명령으로 합성 문서 생성부터 실제 Local AI 검사·보고서 내보내기를 재실행할 수 있습니다. 기존 정답표·원응답을 함께 제공합니다. 실제 사람 대비 작업시간을 측정한 실험은 아닙니다.
