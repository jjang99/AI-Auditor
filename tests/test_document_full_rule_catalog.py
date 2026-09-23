from collections import Counter

from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.definitions.document_rule_catalog import (
    get_document_rule,
    get_document_rules,
    get_document_rules_by_category,
)


EXPECTED_COUNTS = {
    "AUD": 24,
    "REQ": 28,
    "CHG": 18,
    "FP": 12,
    "AI": 23,
}

VALID_EXECUTION_TYPES = {"Rule", "AI", "Hybrid"}


def test_full_catalog_has_exactly_105_unique_rules():
    rules = get_document_rules()

    assert len(rules) == 105

    codes = [rule.code for rule in rules]
    assert len(codes) == len(set(codes))


def test_full_catalog_category_counts_and_id_sequences():
    rules = get_document_rules()

    actual_counts = Counter(rule.category_code for rule in rules)
    assert actual_counts == Counter(EXPECTED_COUNTS)

    for category_code, expected_count in EXPECTED_COUNTS.items():
        category_rules = get_document_rules_by_category(category_code)

        assert len(category_rules) == expected_count

        actual_codes = [rule.code for rule in category_rules]
        expected_codes = [
            f"{category_code}-{number:03d}"
            for number in range(1, expected_count + 1)
        ]

        assert actual_codes == expected_codes


def test_full_catalog_required_fields_are_valid():
    for rule in get_document_rules():
        assert rule.code
        assert rule.name
        assert rule.category_code in EXPECTED_COUNTS
        assert rule.category
        assert rule.description
        assert rule.execution_type in VALID_EXECUTION_TYPES


def test_full_catalog_lookup_returns_exact_rule():
    for rule in get_document_rules():
        found = get_document_rule(rule.code)

        assert found is not None
        assert found == rule

    assert get_document_rule("UNKNOWN-999") is None


def test_mvp_20_rules_match_full_catalog():
    mvp_rules = get_document_mvp_rules()

    assert len(mvp_rules) == 20

    for mvp_rule in mvp_rules:
        catalog_rule = get_document_rule(mvp_rule.code)

        assert catalog_rule is not None
        assert catalog_rule.name == mvp_rule.name
        assert catalog_rule.category == mvp_rule.category
        assert catalog_rule.description == mvp_rule.description

        # MVP는 Enum, 전체 Catalog는 RULE_DESIGN.md의 문자열을 사용한다.
        assert catalog_rule.execution_type == mvp_rule.execution_type.value