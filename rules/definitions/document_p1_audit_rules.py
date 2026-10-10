"""P1-C 계획·품질 Hybrid Rule 정의.

실제 Handler + targeted regression을 통과한 뒤 중앙 Registry에 등록한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p1_audit_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="AUD-010",
            name="WBS 완전성·비정상 항목 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="작업, 기간, 담당자 누락 및 비정상 기간 후보",
            check_points=(
                "WBS/일정표의 작업명·시작일·종료일·담당자 등 핵심정보 누락 여부",
                "종료일이 시작일보다 빠른 명확한 일정 역전 여부",
                "상위 요약행·구분행·마일스톤을 일반 작업행과 구분",
            ),
        ),
        DocumentRule(
            code="AUD-018",
            name="품질활동 계획 대비 수행 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="계획된 품질활동의 실제 수행 여부",
            check_points=(
                "품질보증·검토·점검 계획의 활동·주기·시점과 실제 수행근거 비교",
                "아직 수행시점이 도래하지 않은 활동은 미수행으로 판정하지 않음",
                "일부 문서만 업로드된 경우 근거 부재만으로 즉시 미수행 확정하지 않음",
            ),
        ),
    )
