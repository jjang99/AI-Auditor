from rules.core.models import RuleExecutionType
from rules.definitions.document_mvp_rules import get_document_mvp_rules


def test_document_mvp_execution_type_partition():
    """MVP 20개 Rule이 실행 방식별로 정확하게 분류되어 있는지 검증한다."""

    document_mvp_rules = get_document_mvp_rules()

    expected_rule_codes = {
        "AUD-001",
        "REQ-001",
        "FP-009",
    }

    expected_ai_codes = {
        "AUD-024",
        "REQ-002",
        "REQ-004",
        "CHG-006",
        "CHG-018",
        "AI-005",
    }

    expected_hybrid_codes = {
        "AUD-002",
        "AUD-007",
        "REQ-003",
        "REQ-009",
        "REQ-018",
        "CHG-001",
        "CHG-012",
        "FP-005",
        "AI-009",
        "AI-019",
        "AI-022",
    }

    actual_rule_codes = {
        rule.code
        for rule in document_mvp_rules
        if rule.execution_type == RuleExecutionType.RULE
    }

    actual_ai_codes = {
        rule.code
        for rule in document_mvp_rules
        if rule.execution_type == RuleExecutionType.AI
    }

    actual_hybrid_codes = {
        rule.code
        for rule in document_mvp_rules
        if rule.execution_type == RuleExecutionType.HYBRID
    }

    assert actual_rule_codes == expected_rule_codes
    assert actual_ai_codes == expected_ai_codes
    assert actual_hybrid_codes == expected_hybrid_codes

    # 세 실행 방식 사이에 중복 Rule이 없어야 한다.
    assert actual_rule_codes.isdisjoint(actual_ai_codes)
    assert actual_rule_codes.isdisjoint(actual_hybrid_codes)
    assert actual_ai_codes.isdisjoint(actual_hybrid_codes)

    # 세 실행 방식의 Rule을 합치면 MVP 전체 20개와 정확히 일치해야 한다.
    all_partitioned_codes = (
        actual_rule_codes
        | actual_ai_codes
        | actual_hybrid_codes
    )

    assert all_partitioned_codes == {
        rule.code for rule in document_mvp_rules
    }
    assert len(all_partitioned_codes) == 20

def test_document_mvp_category_distribution():
    """MVP 20개가 5대 검사영역에 계획대로 구성되어 있는지 검증한다."""

    document_mvp_rules = get_document_mvp_rules()

    expected_category_codes = {
        "감리 사전점검": {
            "AUD-001", "AUD-002", "AUD-007", "AUD-024",
        },
        "요구사항 정합성": {
            "REQ-001", "REQ-002", "REQ-003",
            "REQ-004", "REQ-009", "REQ-018",
        },
        "변경영향도": {
            "CHG-001", "CHG-006", "CHG-012", "CHG-018",
        },
        "FP 검증": {
            "FP-005", "FP-009",
        },
        "AI 특화 검증": {
            "AI-005", "AI-009", "AI-019", "AI-022",
        },
    }

    actual_category_codes = {}

    for rule in document_mvp_rules:
        actual_category_codes.setdefault(rule.category, set()).add(rule.code)

    assert actual_category_codes == expected_category_codes

    assert len(actual_category_codes["감리 사전점검"]) == 4
    assert len(actual_category_codes["요구사항 정합성"]) == 6
    assert len(actual_category_codes["변경영향도"]) == 4
    assert len(actual_category_codes["FP 검증"]) == 2
    assert len(actual_category_codes["AI 특화 검증"]) == 4

def test_document_mvp_rules_are_routed_to_correct_engines():
    """MVP 20개가 실행 방식에 따라 각 Engine으로 정확히 라우팅되는지 검증한다."""

    from rules.core.ai_engine import DocumentAIEngine
    from rules.core.hybrid_engine import DocumentHybridEngine
    from rules.core.ai_provider import BaseAIProvider, AIInspectionResult


    class DummyAIProvider(BaseAIProvider):
        def inspect(self, document, rule, context=None):
            return AIInspectionResult(
                rule_code=rule.code,
                findings=(),
            )


    document_mvp_rules = get_document_mvp_rules()
    provider = DummyAIProvider()

    ai_engine = DocumentAIEngine(
        document_mvp_rules,
        provider,
    )

    hybrid_engine = DocumentHybridEngine(
        document_mvp_rules,
        provider,
    )

    ai_codes = {rule.code for rule in ai_engine.rules}
    hybrid_codes = {rule.code for rule in hybrid_engine.rules}

    assert ai_codes == {
        "AUD-024",
        "REQ-002",
        "REQ-004",
        "CHG-006",
        "CHG-018",
        "AI-005",
    }

    assert hybrid_codes == {
        "AUD-002",
        "AUD-007",
        "REQ-003",
        "REQ-009",
        "REQ-018",
        "CHG-001",
        "CHG-012",
        "FP-005",
        "AI-009",
        "AI-019",
        "AI-022",
    }

    assert len(ai_codes) == 6
    assert len(hybrid_codes) == 11
    assert ai_codes.isdisjoint(hybrid_codes)

def test_document_mvp_ai_and_hybrid_rules_follow_strategy_execution():
    """AI/Hybrid Rule이 전략별로 필요한 경우에만 Provider를 호출하는지 검증한다."""

    from pathlib import Path

    from app.parsers.models import DocumentBlock, ParsedDocument
    from rules.core.ai_provider import BaseAIProvider, AIInspectionResult
    from rules.core.inspection_engine import DocumentInspectionEngine

    class RecordingAIProvider(BaseAIProvider):
        def __init__(self):
            self.executed_rule_codes = []

        def inspect(self, document, rule, context=None):
            self.executed_rule_codes.append(rule.code)
            return AIInspectionResult(rule_code=rule.code, findings=())

    document = ParsedDocument(
        file_path=Path("mvp_integration_test.txt"),
        file_type="txt",
        blocks=(
            DocumentBlock(block_type="paragraph", text="REQ-001 | 로그인 기능"),
            DocumentBlock(block_type="paragraph", text="REQ-002 | 사용자 인증 기능"),
            DocumentBlock(block_type="paragraph", text="요구사항은 필요시 관리자 승인을 받는다."),
            DocumentBlock(block_type="paragraph", text="Prompt Injection 입력 필터링과 권한제한을 적용한다."),
            DocumentBlock(block_type="paragraph", text="AI 모델과 프롬프트 변경 이력 및 재검증 절차를 관리한다."),
        ),
        metadata={},
    )

    provider = RecordingAIProvider()
    engine = DocumentInspectionEngine(get_document_mvp_rules(), provider)
    engine.inspect_document(document)

    executed_codes = set(provider.executed_rule_codes)

    # 비교형 REQ-002/004는 확정 비교 후보가 있을 때만 Provider를 호출한다.
    # 이 fixture의 두 요구사항은 동일 내용이 아니므로 추정 비교를 실행하지 않는다.
    assert "REQ-002" not in executed_codes
    assert "REQ-004" not in executed_codes
    # 후보추출/근거확인형은 실제 관련 근거가 있을 때만 실행된다.
    assert {"REQ-003", "AI-009", "AI-022"} <= executed_codes
    # REQ-018은 구조적 누락 후보가 없으면 AI를 호출하지 않는다.
    assert "REQ-018" not in executed_codes
    # 종합형은 원문 직접검사 단계에서 실행하지 않는다.
    assert "AUD-024" not in executed_codes
    assert "CHG-006" not in executed_codes
    assert "CHG-018" not in executed_codes


def test_document_mvp_ai_and_hybrid_rules_have_check_points():
    """실제 AI 판정에 필요한 AI/Hybrid 17개 Rule의 체크포인트가 비어 있지 않은지 검증한다."""

    ai_hybrid_rules = [
        rule
        for rule in get_document_mvp_rules()
        if rule.execution_type in (RuleExecutionType.AI, RuleExecutionType.HYBRID)
    ]

    assert len(ai_hybrid_rules) == 17
    assert all(rule.check_points for rule in ai_hybrid_rules)
    assert all(
        all(point.strip() for point in rule.check_points)
        for rule in ai_hybrid_rules
    )
