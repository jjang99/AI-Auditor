import unittest

from rules.core.document_selection import get_selected_document_mvp_rules
from rules.definitions.document_rule_catalog import get_document_rule_categories


class DocumentSelectionTest(unittest.TestCase):

    def _all_selected(self):
        return {
            category.name: [True] * category.total_count
            for category in get_document_rule_categories()
        }

    def test_all_selected_returns_all_20_mvp_rules(self):
        state = self._all_selected()

        selected = get_selected_document_mvp_rules(state)

        self.assertEqual(20, len(selected))
        self.assertEqual(20, len({rule.code for rule in selected}))

    def test_full_catalog_selection_controls_matching_mvp_rule(self):
        state = self._all_selected()

        # AUD-024는 감리 사전점검 Full Catalog의 24번째 Rule
        state["감리 사전점검"][23] = False

        selected = get_selected_document_mvp_rules(state)
        selected_codes = {rule.code for rule in selected}

        self.assertNotIn("AUD-024", selected_codes)
        self.assertIn("AUD-001", selected_codes)
        self.assertEqual(19, len(selected))

    def test_non_mvp_rule_selection_does_not_change_mvp_count(self):
        state = self._all_selected()

        # AUD-003은 Full Catalog에는 있지만 MVP 20개에는 포함되지 않음
        state["감리 사전점검"][2] = False

        selected = get_selected_document_mvp_rules(state)

        self.assertEqual(20, len(selected))

    def test_empty_selection_returns_no_mvp_rules(self):
        state = {
            category.name: [False] * category.total_count
            for category in get_document_rule_categories()
        }

        selected = get_selected_document_mvp_rules(state)

        self.assertEqual((), selected)


if __name__ == "__main__":
    unittest.main()