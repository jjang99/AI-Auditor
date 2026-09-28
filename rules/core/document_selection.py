"""Inspection Full Catalog 선택상태를 문서 MVP 실행 Rule로 변환한다.

Full Catalog의 영역별 배열 순서는 document_rule_catalog.py의
Rule 순서를 기준으로 하며, MVP Rule은 Rule Code로 매핑한다.
"""

from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.definitions.document_rule_catalog import get_document_rules


def get_selected_document_mvp_rules(selection_state):
    """Full Catalog UI 선택상태에서 선택된 문서 MVP Rule만 반환한다."""

    catalog_rules = get_document_rules()

    catalog_index_by_code = {}
    category_index = {}

    for catalog_rule in catalog_rules:
        index = category_index.get(catalog_rule.category, 0)
        catalog_index_by_code[catalog_rule.code] = (
            catalog_rule.category,
            index,
        )
        category_index[catalog_rule.category] = index + 1

    selected_rules = []

    for rule in get_document_mvp_rules():
        mapping = catalog_index_by_code.get(rule.code)

        if mapping is None:
            continue

        category, index = mapping
        states = selection_state.get(category)

        if states is None:
            continue

        if 0 <= index < len(states) and states[index]:
            selected_rules.append(rule)

    return tuple(selected_rules)