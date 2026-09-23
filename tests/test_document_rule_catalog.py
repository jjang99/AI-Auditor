from collections import Counter

from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.definitions.document_rule_catalog import (
    get_document_rule_categories,
    get_total_mvp_count,
    get_total_rule_count,
)


def test_document_rule_catalog_counts():
    categories = get_document_rule_categories()

    assert len(categories) == 5
    assert get_total_rule_count() == 105
    assert get_total_mvp_count() == 20

    expected = {
        "AUD": ("감리 사전점검", 24, 4),
        "REQ": ("요구사항 정합성", 28, 6),
        "CHG": ("변경영향도", 18, 4),
        "FP": ("FP 검증", 12, 2),
        "AI": ("AI 특화 검증", 23, 4),
    }

    actual = {
        category.code: (
            category.name,
            category.total_count,
            category.mvp_count,
        )
        for category in categories
    }

    assert actual == expected


def test_document_rule_catalog_matches_mvp_rules():
    categories = get_document_rule_categories()
    mvp_rules = get_document_mvp_rules()

    assert len(mvp_rules) == 20

    actual_counts = Counter(
        rule.code.split("-", 1)[0]
        for rule in mvp_rules
    )

    expected_counts = {
        category.code: category.mvp_count
        for category in categories
    }

    assert dict(actual_counts) == expected_counts