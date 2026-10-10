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

        self.assertEqual(27, len(selected))
        self.assertEqual(27, len({rule.code for rule in selected}))
        selected_codes = {rule.code for rule in selected}
        self.assertTrue(
            {
                "AUD-008", "AUD-014", "AUD-016",
                "REQ-007", "REQ-012", "REQ-017",
                "FP-008",
            }.issubset(selected_codes)
        )

    def test_full_catalog_selection_controls_matching_executable_rule(self):
        state = self._all_selected()

        state["감리 사전점검"][23] = False

        selected = get_selected_document_rules(state)
        selected_codes = {rule.code for rule in selected}

        self.assertNotIn("AUD-024", selected_codes)
        self.assertIn("AUD-001", selected_codes)
        self.assertEqual(26, len(selected))

    def test_p1_a_executable_rule_selection_is_applied(self):
        state = self._all_selected()

        state["감리 사전점검"][7] = False

        selected = get_selected_document_rules(state)
        selected_codes = {rule.code for rule in selected}

        self.assertNotIn("AUD-008", selected_codes)
        self.assertEqual(26, len(selected))

    def test_p1_b_executable_rule_selection_is_applied(self):
        state = self._all_selected()

        # REQ-012는 요구사항 정합성 Full Catalog의 12번째 Rule이다.
        state["요구사항 정합성"][11] = False

        selected = get_selected_document_rules(state)
        selected_codes = {rule.code for rule in selected}

        self.assertNotIn("REQ-012", selected_codes)
        self.assertEqual(26, len(selected))

    def test_unimplemented_p1_rule_selection_does_not_change_executable_count(self):
        state = self._all_selected()

        # AUD-010은 P1 대상이지만 아직 Registry에 등록되지 않았다.
        state["감리 사전점검"][9] = False

        selected = get_selected_document_rules(state)

        self.assertEqual(27, len(selected))
        self.assertNotIn("AUD-010", {rule.code for rule in selected})

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
