"""P1-B 요구사항·시험·추적성 Rule 정의.

실제 Handler + targeted regression을 통과한 뒤 중앙 Registry에 등록한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p1_requirement_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="REQ-007",
            name="요구사항 검증가능성·검증방법 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="객관적 검증 가능성과 시험/분석/검토 방법 정의",
            check_points=(
                "요구사항별 객관적 판정기준 또는 수용조건이 정의되어 있는지 확인",
                "시험·분석·검토 등 요구내용을 확인할 수 있는 검증방법이 정의되어 있는지 확인",
                "숫자 기준이 없는 것만으로 모든 기능 요구사항을 검증불가로 판정하지 않음",
            ),
        ),
        DocumentRule(
            code="REQ-012",
            name="요구사항 시험항목 누락 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="요구사항에 대응하는 시험항목 부재",
            check_points=(
                "시험대상 요구사항에 대응하는 시험 ID 또는 시험항목이 존재하는지 확인",
                "명시된 시험 추적관계가 실제 시험항목을 가리키는지 확인",
                "시험대상 아님·해당없음·N/A 표시는 누락으로 판정하지 않음",
            ),
        ),
        DocumentRule(
            code="REQ-017",
            name="요구사항 추적관계 누락 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="후속 산출물과의 추적 링크 누락",
            check_points=(
                "추적대상으로 정의된 요구사항의 필수 후속 링크가 비어 있는지 확인",
                "명시된 후속 링크가 실제 존재하는 산출물 ID를 가리키는지 확인",
                "N/A·해당없음·별도 시트 참조는 누락으로 판정하지 않음",
            ),
        ),
    )
