"""P2-B 감리·요구사항 의미/교차문서 Rule 정의.

Registry 등록은 전용/통합/전체 회귀검증 후 별도로 한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p2_b_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="AUD-005",
            name="문서 간 용어 일관성 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.AI,
            severity="Medium",
            description="동일 대상을 서로 다른 용어로 기술하는지",
        ),
        DocumentRule(
            code="AUD-021",
            name="인터페이스 문서정보 일치 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="시스템, 방식, 주기 등 문서 간 불일치",
        ),
        DocumentRule(
            code="REQ-006",
            name="요구사항 완전성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="구현대상·조건·범위가 충분히 정의됐는지",
        ),
        DocumentRule(
            code="REQ-021",
            name="요구사항 상태·승인정보 정합성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="완료/보류/삭제 및 승인·확정상태 불일치",
        ),
        DocumentRule(
            code="REQ-027",
            name="요구사항 출처·상위요구 및 추가기능 근거 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="RFP/계약 등 출처 추적과 근거 없는 추가기능 후보",
        ),
        DocumentRule(
            code="REQ-028",
            name="요구사항 정합성 종합 위험 후보 도출",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="정합성 결과를 종합해 근거 기반 위험 후보 제시",
        ),
    )
