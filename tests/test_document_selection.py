import unittest

from rules.core.document_selection import (
    get_selected_document_mvp_rules,
    get_selected_document_rules,
)
from rules.definitions.document_rule_catalog import get_document_rule_categories


class DocumentSelectionTest(unittest.TestCase):

    def _all_selected(self):
        return {
            category.name: [True] * category.total_count
            for category in get_document_rule_categories()
        }

    def test_all_selected_returns_all_current_executable_rules(self):
        state = self._all_selected()

        selected = get_selected_document_rules(state)

        # 7-0에서는 Registry의 실제 실행 가능 Rule이 기존 MVP20과 동일하다.
        self.assertEqual(20, len(selected))
        self.assertEqual(20, len({rule.code for rule in selected}))

    def test_full_catalog_selection_controls_matching_executable_rule(self):
        state = self._all_selected()

        # AUD-024는 감리 사전점검 Full Catalog의 24번째 Rule이며 현재 실행 가능하다.
        state["감리 사전점검"][23] = False

        selected = get_selected_document_rules(state)
        selected_codes = {rule.code for rule in selected}

        self.assertNotIn("AUD-024", selected_codes)
        self.assertIn("AUD-001", selected_codes)
        self.assertEqual(19, len(selected))

    def test_unimplemented_rule_selection_does_not_change_executable_count(self):
        state = self._all_selected()

        # AUD-008은 P1 대상이지만 7-0 시점에는 아직 Registry에 등록되지 않았다.
        state["감리 사전점검"][7] = False

        selected = get_selected_document_rules(state)

        self.assertEqual(20, len(selected))
        self.assertNotIn("AUD-008", {rule.code for rule in selected})

    def test_empty_selection_returns_no_executable_rules(self):
        state = {
            category.name: [False] * category.total_count
            for category in get_document_rule_categories()
        }

        selected = get_selected_document_rules(state)

        self.assertEqual((), selected)

    def test_legacy_mvp_selection_api_matches_new_registry_api(self):
        state = self._all_selected()

        self.assertEqual(
            get_selected_document_rules(state),
            get_selected_document_mvp_rules(state),
        )


if __name__ == "__main__":
    unittest.main()
