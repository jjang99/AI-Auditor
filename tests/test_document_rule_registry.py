from rules.definitions.document_rule_catalog import get_document_rule
from rules.definitions.document_rule_registry import (
    get_implemented_document_rule_codes,
    get_implemented_document_rules,
    get_p1_target_codes,
    get_p2_a_codes,
    get_p2_b_codes,
    get_p2_c_codes,
    is_document_rule_implemented,
)


EXPECTED_P1_CODES = (
    "AUD-008",
    "AUD-010",
    "AUD-014",
    "AUD-016",
    "AUD-018",
    "AUD-020",
    "AUD-022",
    "AUD-023",
    "REQ-007",
    "REQ-012",
    "REQ-017",
    "FP-002",
    "FP-008",
)

EXPECTED_P2_A_CODES = (
    "AUD-015",
    "AUD-019",
    "REQ-016",
    "REQ-020",
    "CHG-005",
    "FP-007",
    "AI-023",
)

EXPECTED_P2_B_CODES = (
    "AUD-005",
    "AUD-021",
    "REQ-006",
    "REQ-021",
    "REQ-027",
    "REQ-028",
)

EXPECTED_P2_C_CODES = (
    "CHG-008",
    "CHG-010",
    "FP-006",
    "FP-011",
)

ACTIVE_P1_CODES = set(EXPECTED_P1_CODES)
ACTIVE_P2_A_CODES = set(EXPECTED_P2_A_CODES)
ACTIVE_P2_B_CODES = set(EXPECTED_P2_B_CODES)
ACTIVE_P2_C_CODES = set(EXPECTED_P2_C_CODES)


def test_registry_has_mvp20_plus_all_p1_p2_a_p2_b_p2_c_rules():
    rules = get_implemented_document_rules()
    codes = get_implemented_document_rule_codes()

    assert len(rules) == 50
    assert len(codes) == 50
    assert len(set(codes)) == 50
    assert ACTIVE_P1_CODES.issubset(set(codes))
    assert ACTIVE_P2_A_CODES.issubset(set(codes))
    assert ACTIVE_P2_B_CODES.issubset(set(codes))
    assert ACTIVE_P2_C_CODES.issubset(set(codes))


def test_registry_rules_exist_and_match_full_catalog():
    for rule in get_implemented_document_rules():
        catalog_rule = get_document_rule(rule.code)

        assert catalog_rule is not None
        assert catalog_rule.name == rule.name
        assert catalog_rule.category == rule.category
        assert catalog_rule.description == rule.description
        assert catalog_rule.execution_type == rule.execution_type.value


def test_p1_target_is_exactly_13_confirmed_codes():
    assert get_p1_target_codes() == EXPECTED_P1_CODES
    assert len(get_p1_target_codes()) == 13

    for code in get_p1_target_codes():
        assert get_document_rule(code) is not None


def test_p2_a_is_exactly_seven_activated_codes():
    assert get_p2_a_codes() == EXPECTED_P2_A_CODES
    assert len(get_p2_a_codes()) == 7

    for code in get_p2_a_codes():
        assert get_document_rule(code) is not None
        assert is_document_rule_implemented(code)


def test_p2_b_is_exactly_six_activated_codes():
    assert get_p2_b_codes() == EXPECTED_P2_B_CODES
    assert len(get_p2_b_codes()) == 6

    for code in get_p2_b_codes():
        assert get_document_rule(code) is not None
        assert is_document_rule_implemented(code)


def test_p2_c_is_exactly_four_activated_codes():
    assert get_p2_c_codes() == EXPECTED_P2_C_CODES
    assert len(get_p2_c_codes()) == 4

    for code in get_p2_c_codes():
        assert get_document_rule(code) is not None
        assert is_document_rule_implemented(code)


def test_all_p1_rules_are_still_activated():
    implemented = set(get_implemented_document_rule_codes())
    active_p1 = implemented.intersection(get_p1_target_codes())

    assert active_p1 == ACTIVE_P1_CODES
    for code in ACTIVE_P1_CODES:
        assert is_document_rule_implemented(code)
