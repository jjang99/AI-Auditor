# AI Auditor 효과측정지표 1장 요약 기준

## 1. 측정 원칙

해커톤 제출용 효과측정은 다음 두 층을 명확히 구분한다.

### A. AI Auditor 자체 실제 검증값
- 실제 구현·실행·회귀·배포 과정에서 확인된 수치만 확정값으로 사용한다.
- Full Catalog 105 / 실행 Registry 56 / 감리자료 114 / Parser 9종 / Local AI 외부 API 0원 등을 사용한다.

### B. 외부 연구 기반 참고 기대효과
- 사용자가 동일 샘플 수동/자동 A/B 실측을 수행하기 어려운 현실을 반영한다.
- 유사한 AI 문서·지식업무의 외부 연구를 참고 범위로 제시할 수 있다.
- 외부 연구 결과를 AI Auditor 자체 실측 성과로 표현하지 않는다.
- 제출본에서는 **보수적 설명용 시나리오 20%**를 사용할 수 있으나, 반드시 `자체 실측이 아닌 외부 연구 기반 참고 시나리오`라고 표시한다.

---

## 2. AI Auditor 자체 확정 지표

| 구분 | 지표 | 현재 값 | 근거/의미 |
|---|---|---:|---|
| 실무근거 | 분석한 감리자료 | 114개 | 실제 감리지적 유형을 사례근거로 활용 |
| 설계범위 | Full Rule Catalog | 105개 | AUD 24 / REQ 28 / CHG 18 / FP 12 / AI 23 |
| 실행범위 | 실제 실행 Rule | 56개 | MVP20 + P1 13 + P2 23 |
| 실행률 | Full Catalog 대비 실행범위 | 53.3% | 56 / 105 × 100, 품질향상률이 아님 |
| 검사방식 | Rule / AI / Hybrid | 14 / 11 / 31 | 중앙 Registry 기준 |
| 문서호환 | Parser 지원 형식 | 9종 | DOCX/DOC/XLSX/XLS/PDF/PPTX/PPT/HWPX/HWP |
| Local AI | 외부 생성형 AI API 사용료 | 0원 | Qwen3-4B + llama.cpp 로컬 추론 기준, PC/전력/개발비 제외 |
| 배포검증 | Portable / MSI | PASS | EXE, DB, 모델 로딩, Local AI 실제 응답 검증 |

검증 강조:
- 감리자료 114개 분석
- Full Catalog 105개 실무 매핑
- MVP20 실증검증
- 실증에서 탐지범위가 좁았던 5개 Rule 실제 보완
- 보완 후 전체 `python -m pytest -q` 사용자 PC 실패 0건 확인
- P1/P2 포함 실제 실행 Registry 56개 Freeze
- Portable / MSI 실배포 검증 완료

---

## 3. 외부 연구 기반 참고 범위

### Microsoft Research — Early Impacts of M365 Copilot (2025)
- 56개 기업, 6,000명 이상 근로자 대상 실제 업무 실험
- Copilot 사용자는 문서를 약 **12% 더 빠르게 완료**

### Harvard Business School + BCG (2023)
- 컨설턴트 758명 대상 실험
- AI가 적합한 과업에서 작업을 약 **25.1% 더 빠르게 수행**
- AI가 모든 과업에서 항상 더 정확한 것은 아니라는 제한도 확인됨

### MIT (2023)
- 전문직 453명 대상 문서형 업무 실험
- ChatGPT 사용 시 작업시간 약 **40% 감소**, 품질평가 약 18% 향상
- 실제 조직의 모든 복잡한 업무환경을 그대로 재현한 것은 아니라는 제한이 있음

### IEEE RE 2024 — Software Requirements
- LLM이 소프트웨어 요구사항 문서의 문제를 식별하고 개선 피드백을 제공할 수 있음을 실험적으로 확인
- 요구사항 생성·검증·수정에서 시간과 노력을 줄일 가능성을 보고

중요:
**12~40%는 AI Auditor의 실측효과가 아니라 유사 업무의 외부 연구 참고 범위이다.**

---

## 4. 제출용 보수적 참고 시나리오

해커톤 심사위원이 효과를 직관적으로 이해할 수 있도록 다음 예시를 사용할 수 있다.

- 기존 수작업 1차 문서점검: **60분**
- AI Auditor 활용 참고 시나리오: **48분**
- 설명용 절감률: **20%**
- 설명용 차이: **12분**

표기:
> `※ AI Auditor 자체 실측값이 아니라 외부 유사연구를 바탕으로 한 보수적 참고 시나리오입니다.`

### 비용 환산 예시

시간당 업무비용을 30,000원으로 단순 가정하면:
- 수작업 60분: 30,000원 상당 업무시간
- AI Auditor 활용 48분: 24,000원 상당 업무시간
- 참고 차이: 약 6,000원 상당 업무시간

주의:
- 실제 회사 인건비·점검시간에 따라 달라진다.
- `실제 절감액` 또는 `ROI 실측값`으로 표현하지 않는다.
- 감리/품질관리 인력 전체를 대체하거나 인건비를 직접 줄인다고 확대해석하지 않는다.

---

## 5. 제출용 핵심 메시지

**AI Auditor는 사람을 대체하는 것이 아니라 반복적인 1차 문서점검을 먼저 수행하는 도구이다.**

- 실제 검증실적: 114개 감리자료 / 105개 검사기준 / 56개 실행 Rule / 9종 문서 / Local AI
- 기대효과: 유사 AI 문서·지식업무 연구에서 12~40% 시간효과가 보고됨
- 제출 표현: 보수적으로 20% 참고 시나리오를 사용하되 자체 실측값이 아님을 명확히 표시

외부 참고 출처:
- Microsoft Research, `Early Impacts of M365 Copilot`, 2025
- Harvard Business School AI Institute / BCG, `Navigating the Jagged Technological Frontier`, 2023
- MIT News, `Study finds ChatGPT boosts worker productivity for some writing tasks`, 2023
- IEEE RE 2024, `Using LLMs in Software Requirements Specifications: An Empirical Evaluation`
