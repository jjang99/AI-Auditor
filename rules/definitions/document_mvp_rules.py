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
        check_points=(\n            "필수 항목이나 필수 내용이 공란 또는 미작성 상태인지 확인",\n            "TBD·미정 등 임시표시로 인해 작성이 완료되지 않은 영역인지 확인",\n        ),\n        ),
        DocumentRule(
            code="AUD-007",
            name="미확정 표현 점검",
            category="감리 사전점검",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="TBD, 미정, 추후협의 등 미확정 표현",
        check_points=(\n            "TBD·미정·추후협의 등 확정되지 않은 표현이 존재하는지 확인",\n            "해당 표현이 실제로 후속 확정이 필요한 내용인지 문맥으로 확인",\n        ),\n        ),
        DocumentRule(
            code="AUD-024",
            name="감리 예상 지적사항 후보 도출",
            category="감리 사전점검",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="개별 결과를 종합해 근거 기반 지적 후보 제시",
        check_points=(\n            "개별 검사결과에서 확인된 사실을 종합해 감리 지적 후보가 되는지 확인",\n            "지적 후보는 입력 문서와 검사결과에서 확인되는 근거만 사용하고 새로운 사실을 추정하지 않음",\n        ),\n        ),

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
        check_points=(\n            "서로 다른 요구사항이 표현만 다르고 동일하거나 실질적으로 중복된 의미인지 확인",\n            "대상·조건·처리내용이 다른 요구사항을 단순 키워드 유사성만으로 중복 판정하지 않음",\n        ),\n        ),
        DocumentRule(
            code="REQ-003",
            name="요구사항 모호성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="적절히, 필요시 등 판단기준 불명확 표현·문맥",
        check_points=(\n            "적절히·필요시 등 객관적 판단기준이 불명확한 표현이 있는지 확인",\n            "대상·조건·범위·수준이 불명확해 구현 또는 검증 시 해석 차이가 생길 수 있는지 확인",\n        ),\n        ),
        DocumentRule(
            code="REQ-004",
            name="요구사항 상충 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="동시에 만족하기 어려운 요구사항 후보",
        check_points=(\n            "두 개 이상의 요구사항의 조건·처리내용·제약이 서로 양립하기 어려운지 확인",\n            "단순 표현 차이가 아니라 동시에 만족할 수 없는 근거가 문서에 있는 경우만 상충 후보로 판단",\n        ),\n        ),
        DocumentRule(
            code="REQ-009",
            name="요구사항 설계 반영 정합성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="요구사항의 설계·화면·데이터·인터페이스 반영",
        check_points=(\n            "요구사항의 기능·조건·데이터·화면·인터페이스 내용이 관련 설계에 반영되었는지 확인",\n            "요구사항과 설계의 연결만 존재하고 핵심 조건이나 처리내용이 누락·변경된 경우를 확인",\n        ),\n        ),
        DocumentRule(
            code="REQ-018",
            name="양방향 추적성 점검",
            category="요구사항 정합성",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="상위→하위 및 하위→상위 추적 가능 여부",
        check_points=(\n            "상위 요구사항에서 관련 설계·구현·시험 등 하위 산출물을 추적할 수 있는지 확인",\n            "하위 산출물에서 근거가 되는 상위 요구사항으로 역추적할 수 있는지 확인",\n        ),\n        ),

        # 변경영향도
        DocumentRule(
            code="CHG-001",
            name="변경사항 식별 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="이전/현재 산출물 간 실제 변경 식별",
        check_points=(\n            "이전 산출물과 현재 산출물 사이에서 실제 추가·수정·삭제된 내용을 식별",\n            "단순 서식·표현 변경과 기능·조건·데이터 등 의미 있는 변경을 구분",\n        ),\n        ),
        DocumentRule(
            code="CHG-006",
            name="변경 영향대상 식별",
            category="변경영향도",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="설계·화면·데이터·인터페이스·시험 영향 후보",
        check_points=(\n            "확인된 변경이 설계·화면·데이터·인터페이스·시험에 영향을 줄 수 있는지 확인",\n            "문서에서 확인되는 변경내용과 연관관계를 근거로 영향 후보를 제시하고 근거 없는 영향은 만들지 않음",\n        ),\n        ),
        DocumentRule(
            code="CHG-012",
            name="관련 시험 변경 미반영 점검",
            category="변경영향도",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="시험항목·조건·예상결과의 변경 누락",
        check_points=(\n            "변경된 요구·설계·기능과 관련된 시험항목이 함께 변경되었는지 확인",\n            "시험조건·입력·예상결과에 변경사항이 누락되어 기존 시험으로는 변경내용을 검증하기 어려운지 확인",\n        ),\n        ),
        DocumentRule(
            code="CHG-018",
            name="변경영향도 종합 위험 후보 도출",
            category="변경영향도",
            execution_type=RuleExecutionType.AI,
            severity="High",
            description="변경·영향·반영 결과를 종합한 위험 후보",
        check_points=(\n            "확인된 변경사항·영향대상·반영결과를 함께 검토해 미반영 또는 불일치 위험 후보를 확인",\n            "입력에서 확인되지 않은 변경이나 영향을 새로 가정하지 않음",\n        ),\n        ),

        # FP 검증
        DocumentRule(
            code="FP-005",
            name="기능유형 분류 적정성 점검",
            category="FP 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="EI/EO/EQ/ILF/EIF 분류의 적정성",
        check_points=(\n            "산정 대상 기능의 사용자 관점 처리와 데이터 유지·조회 특성을 근거로 EI·EO·EQ·ILF·EIF 분류가 적절한지 확인",\n            "분류 판단에 필요한 근거정보가 문서에 부족하면 임의로 기능유형을 단정하지 않음",\n        ),\n        ),
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
        check_points=(\n            "AI 출력의 정확성·근거성을 검증하는 절차 또는 통제가 정의되어 있는지 확인",\n            "허위·환각 가능 출력의 탐지·재검토·차단 등 대응방안이 있는지 확인",\n        ),\n        ),
        DocumentRule(
            code="AI-009",
            name="Prompt Injection 대응 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="악의적 지시에 의한 통제 우회 대응",
        check_points=(\n            "외부 입력의 악의적 지시가 시스템 지침이나 통제를 우회하지 못하도록 대응방안이 정의되어 있는지 확인",\n            "Prompt Injection 시험·필터링·권한제한 등 문서에서 확인되는 통제 근거를 확인",\n        ),\n        ),
        DocumentRule(
            code="AI-019",
            name="Human-in-the-loop 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="High",
            description="중요 판단의 사람 확인·승인 구조",
        check_points=(\n            "중요한 AI 판단에 사람의 확인 또는 승인 절차가 있는지 확인",\n            "사람의 검토나 승인 없이 AI 판단이 자동으로 최종 처리된다고 명시된 경우 지적 후보로 판단",\n            "사람 확인·승인 절차의 부재가 명시된 경우와 문서에서 단순히 확인되지 않는 경우를 구분",\n        ),\n        ),
        DocumentRule(
            code="AI-022",
            name="AI 모델·프롬프트 변경관리 점검",
            category="AI 특화 검증",
            execution_type=RuleExecutionType.HYBRID,
            severity="Medium",
            description="모델/프롬프트 변경기록 및 재검증",
        check_points=(\n            "AI 모델 또는 프롬프트 변경내용·버전·이력이 기록·관리되는지 확인",\n            "모델 또는 프롬프트 변경 후 필요한 재검증·시험 절차가 정의되고 수행 근거가 있는지 확인",\n        ),\n        ),
    )