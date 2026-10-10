"""P1-E FP-002 Hybrid Rule 정의.

Registry에는 targeted/integration regression 완료 후 등록한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p1_fp_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="FP-002",
            name="FP 산정대상 중복 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="동일 기능의 중복 산정",
            check_points=(
                "구조형 FP 산정표에서 동일/유사 기능명과 FP 유형의 중복 후보",
                "처리조건·사용자 관점·입출력 차이가 명확한 경우 별도 기능으로 구분",
                "합계·소계·요약행 제외",
            ),
        ),
    )
