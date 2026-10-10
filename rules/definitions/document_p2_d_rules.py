"""P2-D AI/RAG 품질·보안·운영 Rule 정의.

Registry 등록은 전용/Service/통합/전체 회귀검증 후 별도로 한다.
"""

from rules.core.models import DocumentRule, RuleExecutionType


def get_p2_d_rules() -> tuple[DocumentRule, ...]:
    return (
        DocumentRule(
            code="AI-003",
            name="AI 성능·품질 목표 정의 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="평가기준·목표값·허용수준 정의",
            check_points=("정확도", "품질", "응답시간", "평가기준", "목표값", "허용수준"),
        ),
        DocumentRule(
            code="AI-008",
            name="민감정보 입력·출력 통제 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="개인정보·기밀의 부적절한 입력/노출 방지",
            check_points=("개인정보", "기밀", "민감정보", "마스킹", "차단", "필터링", "권한"),
        ),
        DocumentRule(
            code="AI-013",
            name="학습·참조데이터 적정성 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="데이터 출처·품질·적합성 관리",
            check_points=("학습데이터", "참조데이터", "데이터셋", "출처", "품질", "정제", "검증"),
        ),
        DocumentRule(
            code="AI-015",
            name="RAG 검색근거 적정성 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="검색 문서와 실제 답변 근거의 적합성",
            check_points=("RAG", "검색증강", "벡터검색", "임베딩", "검색근거", "답변근거"),
        ),
        DocumentRule(
            code="AI-017",
            name="AI 평가·테스트 체계 적정성 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="대표성 있는 평가데이터와 정상/예외/위험 입력 시험",
            check_points=("평가데이터", "테스트", "시험", "정상입력", "예외입력", "위험입력", "평가기준"),
        ),
        DocumentRule(
            code="AI-021",
            name="AI 로그·추적성 및 운영 모니터링 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="입력·모델·조건·결과 추적과 운영 품질/이상 모니터링",
            check_points=("AI 로그", "추적성", "모델버전", "입력", "결과", "모니터링", "이상탐지"),
        ),
    )
