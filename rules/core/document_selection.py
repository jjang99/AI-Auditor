"""Inspection Full Catalog 선택상태를 실제 실행 가능한 문서 Rule로 변환한다.

Full Catalog의 영역별 배열 순서는 document_rule_catalog.py의 Rule 순서를
기준으로 한다. 실제 실행 가능 여부는 document_rule_registry.py에서 관리한다.

기존 get_selected_document_mvp_rules()는 기존 코드/테스트 호환을 위해 유지한다.
"""

from rules.definitions.document_rule_catalog import get_document_rules
from rules.definitions.document_rule_registry import get_implemented_document_rules


def _catalog_selection_index_by_code():
    catalog_index_by_code = {}
    category_index = {}

    for catalog_rule in get_document_rules():
        index = category_index.get(catalog_rule.category, 0)
        catalog_index_by_code[catalog_rule.code] = (
            catalog_rule.category,
            index,
        )
        category_index[catalog_rule.category] = index + 1

    return catalog_index_by_code


def get_selected_document_rules(selection_state):
    """Full Catalog UI 선택상태에서 선택된 실제 실행 가능 Rule만 반환한다."""
    catalog_index_by_code = _catalog_selection_index_by_code()
    selected_rules = []

    for rule in get_implemented_document_rules():
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


def get_selected_document_mvp_rules(selection_state):
    """기존 MVP20 선택 API 호환용 별칭.

    7-0 이후 실제 선택기준은 중앙 Registry이며, 현재 활성화된 실행 Rule 전체를
    반환한다. 신규 호출부는 get_selected_document_rules()를 기준 API로 사용한다.
    """
    return get_selected_document_rules(selection_state)
