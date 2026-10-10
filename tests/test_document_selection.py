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

        self.assertEqual(56, len(selected))
        self.assertEqual(56, len({rule.code for rule in selected}))
        selected_codes = {rule.code for rule in selected}
        self.assertTrue(
            {
                "AUD-005", "AUD-008", "AUD-010", "AUD-014", "AUD-015", "AUD-016",
                "AUD-018", "AUD-019", "AUD-020", "AUD-021", "AUD-022", "AUD-023",
                "REQ-006", "REQ-007", "REQ-012", "REQ-016", "REQ-017", "REQ-020",
                "REQ-021", "REQ-027", "REQ-028",
                "CHG-005", "CHG-008", "CHG-010",
                "FP-002", "FP-006", "FP-007", "FP-008", "FP-011",
                "AI-003", "AI-008", "AI-013", "AI-015", "AI-017", "AI-021", "AI-023",
            }.issubset(selected_codes)
        )

    def test_p1_executable_rule_selection_is_applied(self):
        state = self._all_selected()
        state["감리 사전점검"][7] = False
        selected = get_selected_document_rules(state)
        self.assertNotIn("AUD-008", {rule.code for rule in selected})
        self.assertEqual(55, len(selected))

    def test_p2_a_executable_rule_selection_is_applied(self):
        state = self._all_selected()
        state["요구사항 정합성"][19] = False
        selected = get_selected_document_rules(state)
        self.assertNotIn("REQ-020", {rule.code for rule in selected})
        self.assertEqual(55, len(selected))

    def test_p2_b_executable_rule_selection_is_applied(self):
        state = self._all_selected()
        state["요구사항 정합성"][26] = False
        selected = get_selected_document_rules(state)
        self.assertNotIn("REQ-027", {rule.code for rule in selected})
        self.assertEqual(55, len(selected))

    def test_p2_c_executable_rule_selection_is_applied(self):
        state = self._all_selected()
        state["변경영향도"][7] = False
        selected = get_selected_document_rules(state)
        self.assertNotIn("CHG-008", {rule.code for rule in selected})
        self.assertEqual(55, len(selected))

    def test_p2_d_executable_rule_selection_is_applied(self):
        state = self._all_selected()
        state["AI 특화 검증"][2] = False
        selected = get_selected_document_rules(state)
        self.assertNotIn("AI-003", {rule.code for rule in selected})
        self.assertEqual(55, len(selected))

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
