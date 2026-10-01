import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.database.database as database


EXPECTED_ASSESSMENT_COLUMNS = {
    "impact",
    "impact_reason",
    "likelihood",
    "likelihood_reason",
    "severity_reason",
    "audit_recommendation_type",
    "audit_improvement_timing",
    "audit_important",
}


class IssueAssessmentDatabaseMigrationTests(unittest.TestCase):
    def test_initialize_database_adds_assessment_columns_to_existing_issues_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "legacy.db"
            connection = sqlite3.connect(db_path)
            connection.execute(
                """
                CREATE TABLE issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inspection_id INTEGER NOT NULL,
                    severity TEXT NOT NULL,
                    rule_code TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    evidence TEXT,
                    impact TEXT,
                    ai_recommendation TEXT,
                    category TEXT,
                    status TEXT NOT NULL DEFAULT '미조치'
                )
                """
            )
            connection.commit()
            connection.close()

            with patch.object(database, "DB_PATH", db_path), patch.object(
                database, "DATA_DIR", Path(temp_dir)
            ):
                database.initialize_database()

            connection = sqlite3.connect(db_path)
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(issues)").fetchall()
            }
            connection.close()

            self.assertTrue(EXPECTED_ASSESSMENT_COLUMNS.issubset(columns))

    def test_initialize_database_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "repeatable.db"

            with patch.object(database, "DB_PATH", db_path), patch.object(
                database, "DATA_DIR", Path(temp_dir)
            ):
                database.initialize_database()
                database.initialize_database()

            connection = sqlite3.connect(db_path)
            columns = [
                row[1]
                for row in connection.execute("PRAGMA table_info(issues)").fetchall()
            ]
            connection.close()

            for column in EXPECTED_ASSESSMENT_COLUMNS:
                self.assertEqual(columns.count(column), 1)


if __name__ == "__main__":
    unittest.main()
