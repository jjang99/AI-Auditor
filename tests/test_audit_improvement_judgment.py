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
    AuditImprovementJudgment,
    AuditImprovementTiming,
    AuditImportantFlag,
    AuditRecommendationType,
)


class AuditImprovementJudgmentRepositoryTests(unittest.TestCase):
    def test_audit_judgment_is_persisted_separately_from_severity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "audit_judgment.db"

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
                    rule_code="TEST-002",
                    rule_name="감리판정 저장 테스트",
                    category="감리 사전점검",
                    severity="High",
                    file_path="sample.docx",
                    line_number=1,
                    evidence="근거",
                    description="설명",
                    audit_judgment=AuditImprovementJudgment(
                        recommendation_type=AuditRecommendationType.CONSULT,
                        improvement_timing=AuditImprovementTiming.LONG_TERM,
                        important=AuditImportantFlag.YES,
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
            self.assertEqual(saved["severity"], "High")
            self.assertEqual(saved["audit_recommendation_type"], "협의")
            self.assertEqual(saved["audit_improvement_timing"], "장기")
            self.assertEqual(saved["audit_important"], "O")

    def test_issue_without_audit_judgment_stores_null_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "no_audit_judgment.db"

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
                    rule_code="TEST-003",
                    rule_name="감리판정 없음 테스트",
                    category="감리 사전점검",
                    severity="Low",
                    file_path="sample.docx",
                    line_number=1,
                    evidence="근거",
                    description="설명",
                )
                summary = InspectionSummary(
                    file_count=1,
                    rule_count=1,
                    executed_rule_count=1,
                    issues=(issue,),
                )

                inspection_id = save_inspection_result(project_id, summary)
                saved = get_issues_for_inspection(inspection_id)[0]

            self.assertIsNone(saved["audit_recommendation_type"])
            self.assertIsNone(saved["audit_improvement_timing"])
            self.assertIsNone(saved["audit_important"])


if __name__ == "__main__":
    unittest.main()
