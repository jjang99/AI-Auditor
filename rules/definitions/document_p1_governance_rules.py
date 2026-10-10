"""P1-D 인터페이스·계약·기준 Hybrid Rule 정의.

Registry에는 targeted/integration regression 완료 후 등록한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p1_governance_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="AUD-020",
            name="인터페이스 정의 완전성 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="필요한 연계/인터페이스 정의 누락",
            check_points=(
                "인터페이스 ID, 송신/수신 시스템, 방식, 데이터, 주기 등 핵심정보 누락",
                "명시된 연계 대상에 대응하는 인터페이스 정의 여부",
                "단순 외부기관 언급과 실제 연계 정의를 구분",
            ),
        ),
        DocumentRule(
            code="AUD-022",
            name="계약·과업내용 반영 및 이행 증적 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="계약·RFP·과업 의무사항의 반영 및 수행증적",
            check_points=(
                "명시적 의무/납품/수행 요구와 계획·산출물·수행근거의 연결",
                "일반 설명문이 아니라 의무 표현이 있는 항목만 후보화",
                "수행시점 미도래 항목은 즉시 미이행으로 확정하지 않음",
            ),
        ),
        DocumentRule(
            code="AUD-023",
            name="관련 기준·지침 준수 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="적용 법령·표준·가이드·지침의 준수근거",
            check_points=(
                "문서에 적용대상으로 명시된 법령·표준·가이드·지침 후보",
                "준수방안·점검·검증·적용결과 근거의 존재 여부",
                "법적 위반을 새로 해석하지 않고 문서 근거의 대응 여부만 확인",
            ),
        ),
    )
