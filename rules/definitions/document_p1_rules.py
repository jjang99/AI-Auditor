"""P1 확장 Rule 상세정의.

이 파일에는 구현·검증 단계에 들어간 P1 Rule만 추가한다.
Registry 등록은 Handler + targeted test + 전체 회귀검증을 통과한 뒤 별도로 한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p1_deterministic_rules() -> tuple[DocumentRule, ...]:
    """P1-A 1차 결정형 Rule 정의를 반환한다."""
    return (
        DocumentRule(
            code="AUD-014",
            name="시험계획 완전성 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="시험항목, 방법, 예상결과 등 필수정보",
        ),
        DocumentRule(
            code="AUD-016",
            name="시험결함 조치상태 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="미조치·미종결 결함 존재 여부",
        ),
        DocumentRule(
            code="FP-008",
            name="상세 산정정보 적정성 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.RULE,
            severity="Medium",
            description="적용 방식에 따라 필요한 DET/FTR/RET 등 근거정보",
        ),
    )
