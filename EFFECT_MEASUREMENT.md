# 효과지표: 실측과 자동화 전후 효과 추정

이번에 합의한 제출용 1장은 [자동화 전후 효과 추정 PDF](submission/AI_Auditor_Effect_Estimate_1page.pdf)입니다.

| 구분 | 값 | 성격 |
|---|---|---|
| 사용 전: 수동 검토·정리·보고서 전체 | 30분 | 설명용 가정 |
| 사용 후: 자동검사 처리구간 | 434.06초 | 사용자 PC의 단일 실측 |
| 사용 후: 등록·후보 검토·보고서 저장 | 10분 | 설명용 가정 |
| 사용 후 전체 | 약 17분 14초 | 실측+가정의 추정 |
| 예상 차이 | 약 12분 46초·42.6% 감소 | 위 조건에서의 추정 |

수동 전체 30분과 추가 10분은 확인된 평균·사용자 경험값·보수적 실측 기준이 아닙니다. 실제 시간절감률은 측정하지 않았습니다. 수동 15분을 가정하면 오히려 약 2분 14초 증가합니다. 계산과 조건은 [방법](submission/EFFECT_ESTIMATE_METHOD.md), [Excel](submission/AI_Auditor_Effect_Estimate.xlsx), [가정 JSON](submission/estimate_assumptions.json)에 공개했습니다.

기존 [결함 검출 PDF](submission/AI_Auditor_Effect_Measurement_1page.pdf)는 기능검증 참고자료로 보존합니다. 합성 결함 4개 중 3개 검출·미탐 1개와 문서 수정 후 지적 3건→0건은 전후 업무효과나 시간절감률을 입증하지 않습니다.
