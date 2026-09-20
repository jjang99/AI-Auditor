from rules.core.models import RuleExecutionType
from rules.definitions.document_mvp_rules import get_document_mvp_rules


def test_document_mvp_rule_inventory():
    rules = get_document_mvp_rules()

    assert len(rules) == 20

    codes = [rule.code for rule in rules]

    assert len(codes) == len(set(codes))

    assert codes == [
        "AUD-001",
        "AUD-002",
        "AUD-007",
        "AUD-024",
        "REQ-001",
        "REQ-002",
        "REQ-003",
        "REQ-004",
        "REQ-009",
        "REQ-018",
        "CHG-001",
        "CHG-006",
        "CHG-012",
        "CHG-018",
        "FP-005",
        "FP-009",
        "AI-005",
        "AI-009",
        "AI-019",
        "AI-022",
    ]


def test_document_mvp_rule_execution_types():
    rules = get_document_mvp_rules()

    execution_types = {rule.execution_type for rule in rules}

    assert execution_types == {
        RuleExecutionType.RULE,
        RuleExecutionType.AI,
        RuleExecutionType.HYBRID,
    }

def test_document_mvp_rules_have_required_metadata():
    rules = get_document_mvp_rules()

    for rule in rules:
        assert rule.code.strip()
        assert rule.name.strip()
        assert rule.category.strip()
        assert rule.description.strip()
        assert rule.severity.strip()

        assert rule.category in {
            "감리 사전점검",
            "요구사항 정합성",
            "변경영향도",
            "FP 검증",
            "AI 특화 검증",
        }