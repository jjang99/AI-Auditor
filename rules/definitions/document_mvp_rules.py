from rules.core.models import DocumentRule, RuleExecutionType


def get_document_mvp_rules() -> tuple[DocumentRule, ...]:
    return (
        # 감리 사전점검
        DocumentRule(
            code="AUD-001",
            name="필수 산출물 누락 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="사업/단계별 필수 산출물 제출 여부",
        ),
        DocumentRule(
            code="AUD-002",
            name="산출물 작성완전성 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="필수항목, 공란, TBD 등 미작성 영역",
        ),
        DocumentRule(
            code="AUD-007",
            name="미확정 표현 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="TBD, 미정, 추후협의 등 미확정 표현",
        ),
        DocumentRule(
            code="AUD-024",
            name="감리 예상 지적사항 후보 도출",
            category="감리 사전점검",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="개별 결과를 종합해 근거 기반 지적 후보 제시",
        ),

        # 요구사항 정합성
        DocumentRule(
            code="REQ-001",
            name="요구사항 ID 누락·중복 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="ID 미부여 및 중복 여부",
        ),
        DocumentRule(
            code="REQ-002",
            name="요구사항 내용 중복 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.AI,
            severity="Medium",
            description="표현은 다르지만 의미가 같은 요구사항 후보",
        ),
        DocumentRule(
            code="REQ-003",
            name="요구사항 모호성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="적절히, 필요시 등 판단기준 불명확 표현·문맥",
        ),
        DocumentRule(
            code="REQ-004",
            name="요구사항 상충 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="동시에 만족하기 어려운 요구사항 후보",
        ),
        DocumentRule(
            code="REQ-009",
            name="요구사항 설계 반영 정합성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="요구사항의 설계·화면·데이터·인터페이스 반영",
        ),
        DocumentRule(
            code="REQ-018",
            name="양방향 추적성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="상위→하위 및 하위→상위 추적 가능 여부",
        ),

        # 변경영향도
        DocumentRule(
            code="CHG-001",
            name="변경사항 식별 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="이전/현재 산출물 간 실제 변경 식별",
        ),
        DocumentRule(
            code="CHG-006",
            name="변경 영향대상 식별",
            category="변경영향도",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="설계·화면·데이터·인터페이스·시험 영향 후보",
        ),
        DocumentRule(
            code="CHG-012",
            name="관련 시험 변경 미반영 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="시험항목·조건·예상결과의 변경 누락",
        ),
        DocumentRule(
            code="CHG-018",
            name="변경영향도 종합 위험 후보 도출",
            category="변경영향도",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="변경·영향·반영 결과를 종합한 위험 후보",
        ),

        # FP 검증
        DocumentRule(
            code="FP-005",
            name="기능유형 분류 적정성 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="EI/EO/EQ/ILF/EIF 분류의 적정성",
        ),
        DocumentRule(
            code="FP-009",
            name="FP 산정값 재계산 검증",
            category="FP 검증",
            execution_type=RuleExecutionType.RULE,
            severity="High",
            description="입력 근거와 산식에 따른 수치 재계산",
        ),

        # AI 특화 검증
        DocumentRule(
            code="AI-005",
            name="AI 출력 신뢰성·환각 대응 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="정확성·근거성 검증과 허위/환각 대응",
        ),
        DocumentRule(
            code="AI-009",
            name="Prompt Injection 대응 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="악의적 지시에 의한 통제 우회 대응",
        ),
        DocumentRule(
            code="AI-019",
            name="Human-in-the-loop 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="중요 판단의 사람 확인·승인 구조",
        ),
        DocumentRule(
            code="AI-022",
            name="AI 모델·프롬프트 변경관리 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="모델/프롬프트 변경기록 및 재검증",
        ),
    )