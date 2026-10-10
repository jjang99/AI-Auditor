"""P1 AUD-008 상세정의.

Handler + targeted test 검증 전에는 중앙 Registry에 등록하지 않는다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p1_aud008_rule() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="AUD-008",
            name="계획 대비 산출물 작성상태 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="계획된 산출물과 실제 작성·제출상태 비교",
        ),
    )
