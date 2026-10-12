# AI Auditor 효과측정지표 1장 요약 기준

## 1. 측정 원칙

해커톤 제출용 효과측정은 **AI Auditor 자체에서 실제 확인된 값**과 **외부 연구 참고값**을 명확히 분리한다.

### A. AI Auditor 자체 실제 검증값
- 실제 구현·실행·회귀·배포 과정에서 확인된 수치만 확정값으로 사용한다.
- Full Catalog 105 / 실행 Registry 56 / 감리자료 114 / Parser 9종 / Local AI 외부 API 0원 등을 사용한다.

### B. 외부 연구 참고값
- 유사한 AI 문서·지식업무에서 보고된 시간효과는 참고근거로만 사용한다.
- 외부 연구 결과를 AI Auditor의 자체 시간절감률·비용절감액으로 환산해 본문 성과로 제시하지 않는다.
- 자체 A/B 실측이 없는 상태에서 `20% 절감`, `60분→48분`, `6,000원 절감` 같은 가정 시나리오는 최종 PPT의 성과수치로 사용하지 않는다.

---

## 2. AI Auditor 자체 확정 지표

| 구분 | 지표 | 현재 값 | 근거/의미 |
|---|---|---:|---|
| 설계범위 | 프로젝트 정의 Full Rule Catalog | 105개 | AUD 24 / REQ 28 / CHG 18 / FP 12 / AI 23 |
| 실행범위 | 실제 실행 Rule | 56개 | MVP20 + P1 13 + P2 23 |
| 실행률 | Full Catalog 대비 실행범위 | 53.3% | 56 / 105 × 100, 품질향상률이 아님 |
| 검사방식 | Rule / AI / Hybrid | 14 / 11 / 31 | 중앙 Registry 기준 |
| 실무근거 | 분석한 감리자료 | 114개 | 105개 Catalog와 실무근거 매핑 및 우선순위/보완 검증에 활용 |
| 문서호환 | Parser 지원 형식 | 9종 | DOCX/DOC/XLSX/XLS/PDF/PPTX/PPT/HWPX/HWP |
| Local AI | 외부 생성형 AI API 사용료 | 0원 | Qwen3-4B + llama.cpp 로컬 추론 기준, PC/전력/개발비 제외 |
| 배포검증 | Portable / MSI | PASS | EXE, DB, 모델 로딩, Local AI 실제 응답 검증 |

추가 실제 검증근거:
- MVP20을 `Rule 정의 ↔ 실제 코드 동작 ↔ 실제 감리사례 ↔ 자동테스트` 관점으로 실증검증
- 실제 감리사례보다 탐지범위가 좁았던 5개 Rule(AUD-001, REQ-002, REQ-003, REQ-009, FP-009) 보완
- 보완 후 전체 `python -m pytest -q` 사용자 PC 실패 0건 확인
- P1/P2 포함 실제 실행 Registry 56개 Freeze

---

## 3. 기능 단위 실제 실행사례

아래 값은 전체 업무시간 절감률이 아니라 **특정 문서/Rule/PC 조건의 기술 실측 사례**이다.

- HWP 실문서 파싱 + AUD-002/AUD-007 Rule 검사: **8,657 blocks / 13.71초**
- REQ-004 Local AI 검증: **12 evidence / 5 candidate groups / 27.79초**

주의:
- 특정 샘플·Rule 실행시간이므로 전체 프로젝트 평균으로 일반화하지 않는다.
- 사람의 수동검토시간과 직접 비교한 값이 아니므로 시간절감률로 표현하지 않는다.

---

## 4. 아직 자체 실측하지 않은 효과

현재 자체 A/B 실측이 없어 아래 값은 AI Auditor 성과로 확정하지 않는다.

- 사람 수동검토 대비 end-to-end 시간절감률
- 실제 프로젝트 기준 탐지율 / 미탐률 / 오탐률 변화
- 회사 인건비 기준 실제 비용절감액

외부 연구에서 유사 AI 문서·지식업무의 시간효과가 보고된 사례는 있으나, 이는 AI Auditor 자체 성과가 아니다.

참고 출처:
- Microsoft Research, `Early Impacts of M365 Copilot`
- Harvard Business School AI Institute / BCG, `Navigating the Jagged Technological Frontier`
- MIT, ChatGPT professional writing task productivity study
- IEEE RE 2024, LLM-based software requirements evaluation study

---

## 5. 제출용 핵심 메시지

**AI Auditor는 현재 105개 프로젝트 품질점검 Catalog 중 56개를 실제 실행 가능한 형태로 구현·검증했으며, 114개 감리자료를 실무검증 근거로 활용하고 9종 문서를 Local AI와 Rule/Hybrid 방식으로 폐쇄망에서 점검할 수 있다.**

시간절감률이나 비용절감액은 자체 A/B 실측 전까지 제품의 확정 성과로 주장하지 않는다.
