"""P2-C 변경영향·FP Rule 정의.

Registry 등록은 전용/Service/전체 회귀검증 후 별도로 한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p2_c_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="CHG-008",
            name="관련 설계 변경 미반영 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="영향받는 설계의 미갱신",
        ),
        DocumentRule(
            code="CHG-010",
            name="관련 데이터설계 변경 미반영 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="영향받는 데이터 정의의 미갱신",
        ),
        DocumentRule(
            code="FP-006",
            name="기능 단위 분할·통합 적정성 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.AI,
            severity="Medium",
            description="과도한 분할 또는 서로 다른 기능의 부적절한 통합",
        ),
        DocumentRule(
            code="FP-011",
            name="FP 변경반영 누락 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="요구 변경에 따른 FP 갱신 누락",
        ),
    )
