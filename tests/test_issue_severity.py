import unittest

from rules.core.severity import AssessmentLevel, IssueSeverity, calculate_severity


class IssueSeverityMatrixTests(unittest.TestCase):
    def test_all_approved_matrix_combinations(self):
        expected = {
            (AssessmentLevel.HIGH, AssessmentLevel.LOW): IssueSeverity.MEDIUM,
            (AssessmentLevel.HIGH, AssessmentLevel.MEDIUM): IssueSeverity.HIGH,
            (AssessmentLevel.HIGH, AssessmentLevel.HIGH): IssueSeverity.CRITICAL,
            (AssessmentLevel.MEDIUM, AssessmentLevel.LOW): IssueSeverity.LOW,
            (AssessmentLevel.MEDIUM, AssessmentLevel.MEDIUM): IssueSeverity.MEDIUM,
            (AssessmentLevel.MEDIUM, AssessmentLevel.HIGH): IssueSeverity.HIGH,
            (AssessmentLevel.LOW, AssessmentLevel.LOW): IssueSeverity.LOW,
            (AssessmentLevel.LOW, AssessmentLevel.MEDIUM): IssueSeverity.LOW,
            (AssessmentLevel.LOW, AssessmentLevel.HIGH): IssueSeverity.MEDIUM,
        }

        for inputs, severity in expected.items():
            with self.subTest(impact=inputs[0], likelihood=inputs[1]):
                self.assertEqual(calculate_severity(*inputs), severity)

    def test_critical_requires_high_impact_and_high_likelihood(self):
        for impact in AssessmentLevel:
            for likelihood in AssessmentLevel:
                severity = calculate_severity(impact, likelihood)
                if severity == IssueSeverity.CRITICAL:
                    self.assertEqual(impact, AssessmentLevel.HIGH)
                    self.assertEqual(likelihood, AssessmentLevel.HIGH)


if __name__ == "__main__":
    unittest.main()
