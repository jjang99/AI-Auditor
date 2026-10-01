import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.database.database as database
from app.database.repositories.inspection_repository import (
    get_issues_for_inspection,
    save_inspection_result,
)
from rules.core.models import InspectionSummary, RuleIssue
from rules.core.severity import (
    AssessmentLevel,
    IssueAssessment,
    IssueSeverity,
)


class IssueAssessmentRepositoryTests(unittest.TestCase):
    def test_assessment_is_persisted_with_calculated_severity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "assessment.db"

            with patch.object(database, "DB_PATH", db_path), patch.object(
                database, "DATA_DIR", Path(temp_dir)
            ):
                database.initialize_database()

                connection = database.get_connection()
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO projects (
                        name, department, project_type, note, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ("테스트", "", "", "", "2026-10-01", "2026-10-01"),
                )
                project_id = cursor.lastrowid
                connection.commit()
                connection.close()

                issue = RuleIssue(
                    rule_code="TEST-001",
                    rule_name="판정 저장 테스트",
                    category="감리 사전점검",
                    severity="Low",
                    file_path="sample.docx",
                    line_number=1,
                    evidence="근거",
                    description="설명",
                    assessment=IssueAssessment(
                        impact=AssessmentLevel.HIGH,
                        impact_reason="영향도 근거",
                        likelihood=AssessmentLevel.HIGH,
                        likelihood_reason="발생가능성 근거",
                        severity=IssueSeverity.CRITICAL,
                        severity_reason="High × High = Critical",
                    ),
                )
                summary = InspectionSummary(
                    file_count=1,
                    rule_count=1,
                    executed_rule_count=1,
                    issues=(issue,),
                )

                inspection_id = save_inspection_result(project_id, summary)
                rows = get_issues_for_inspection(inspection_id)

            self.assertEqual(len(rows), 1)
            saved = rows[0]
            self.assertEqual(saved["severity"], "Critical")
            self.assertEqual(saved["impact"], "High")
            self.assertEqual(saved["impact_reason"], "영향도 근거")
            self.assertEqual(saved["likelihood"], "High")
            self.assertEqual(saved["likelihood_reason"], "발생가능성 근거")
            self.assertEqual(saved["severity_reason"], "High × High = Critical")


if __name__ == "__main__":
    unittest.main()
