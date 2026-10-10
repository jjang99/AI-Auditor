"""P2-A 구조형/결정형 Rule 정의.

Registry에는 전용 테스트와 통합 회귀 완료 후 등록한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p2_a_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="AUD-015",
            name="시험 수행·결과 완전성 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="대상 시험의 결과 작성 및 수행상태",
        ),
        DocumentRule(
            code="AUD-019",
            name="품질지적사항 미조치 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="검토·품질점검 지적사항의 미조치 여부",
        ),
        DocumentRule(
            code="REQ-016",
            name="중요 요구사항 시험범위 누락 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="중요 요구사항의 시험 제외·누락",
        ),
        DocumentRule(
            code="REQ-020",
            name="잘못된 요구사항 참조 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="존재하지 않거나 잘못된 ID 참조",
        ),
        DocumentRule(
            code="CHG-005",
            name="변경 승인상태 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="미승인 변경의 후속 반영 여부",
        ),
        DocumentRule(
            code="FP-007",
            name="FP 산정방식·적용기준 적정성 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.RULE,
            severity="Medium",
            description="적용 산정방식과 기준의 적합성",
        ),
        DocumentRule(
            code="AI-023",
            name="AI 자원사용·호출 제한 적정성 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.RULE,
            severity="Medium",
            description="요청·입력·출력·반복호출 등 자원사용 통제",
        ),
    )
