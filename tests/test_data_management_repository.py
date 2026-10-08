import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.database.database as database
from app.database.repositories import data_management_repository as repository


class DataManagementRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "ai_auditor_test.db"
        self.db_path_patcher = patch.object(database, "DB_PATH", self.db_path)
        self.data_dir_patcher = patch.object(database, "DATA_DIR", Path(self.temp_dir.name))
        self.db_path_patcher.start()
        self.data_dir_patcher.start()
        database.initialize_database()
        self._seed_data()

    def tearDown(self):
        self.data_dir_patcher.stop()
        self.db_path_patcher.stop()
        self.temp_dir.cleanup()

    def _seed_data(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO projects (
                id, name, department, project_type, note, created_at, updated_at
            ) VALUES (1, 'Project A', 'Dept A', NULL, NULL, '2026-10-08', '2026-10-08')
            """
        )
        cursor.execute(
            """
            INSERT INTO projects (
                id, name, department, project_type, note, created_at, updated_at
            ) VALUES (2, 'Project B', 'Dept B', NULL, NULL, '2026-10-08', '2026-10-08')
            """
        )

        cursor.execute(
            """
            INSERT INTO inspections (
                id, project_id, inspection_type, inspected_at, score, grade,
                status, rule_count, total_issues, resolved_issues
            ) VALUES (10, 1, '전체 검사', '2026-10-08', 95, 'A',
                      'AI 검사완료', 20, 1, 0)
            """
        )
        cursor.execute(
            """
            INSERT INTO inspections (
                id, project_id, inspection_type, inspected_at, score, grade,
                status, rule_count, total_issues, resolved_issues
            ) VALUES (20, 2, '전체 검사', '2026-10-08', 90, 'A',
                      'AI 검사완료', 20, 1, 0)
            """
        )

        cursor.execute(
            """
            INSERT INTO issues (
                id, inspection_id, severity, rule_code, title, status
            ) VALUES (100, 10, 'Medium', 'REQ-001', 'Issue A', '미조치')
            """
        )
        cursor.execute(
            """
            INSERT INTO issues (
                id, inspection_id, severity, rule_code, title, status
            ) VALUES (200, 20, 'Low', 'AUD-001', 'Issue B', '미조치')
            """
        )

        connection.commit()
        connection.close()

    def _counts(self):
        connection = sqlite3.connect(self.db_path)
        counts = {
            "projects": connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
            "inspections": connection.execute("SELECT COUNT(*) FROM inspections").fetchone()[0],
            "issues": connection.execute("SELECT COUNT(*) FROM issues").fetchone()[0],
        }
        connection.close()
        return counts

    def test_summary_returns_current_counts(self):
        self.assertEqual(
            repository.get_data_management_summary(),
            {"projects": 2, "inspections": 2, "issues": 2},
        )

    def test_delete_all_inspection_history_preserves_projects(self):
        result = repository.delete_all_inspection_history()

        self.assertEqual(result["deleted_inspections"], 2)
        self.assertEqual(result["deleted_issues"], 2)
        self.assertEqual(
            self._counts(),
            {"projects": 2, "inspections": 0, "issues": 0},
        )

    def test_project_delete_impact_returns_child_counts(self):
        impact = repository.get_project_delete_impact(1)

        self.assertEqual(impact["project_name"], "Project A")
        self.assertEqual(impact["inspections"], 1)
        self.assertEqual(impact["issues"], 1)

    def test_delete_project_with_history_removes_only_selected_project_tree(self):
        result = repository.delete_project_with_history(1)

        self.assertEqual(result["project_name"], "Project A")
        self.assertEqual(result["deleted_inspections"], 1)
        self.assertEqual(result["deleted_issues"], 1)
        self.assertEqual(
            self._counts(),
            {"projects": 1, "inspections": 1, "issues": 1},
        )

        connection = sqlite3.connect(self.db_path)
        remaining_project = connection.execute(
            "SELECT name FROM projects WHERE id = 2"
        ).fetchone()
        remaining_inspection = connection.execute(
            "SELECT id FROM inspections WHERE id = 20"
        ).fetchone()
        remaining_issue = connection.execute(
            "SELECT id FROM issues WHERE id = 200"
        ).fetchone()
        connection.close()

        self.assertEqual(remaining_project[0], "Project B")
        self.assertEqual(remaining_inspection[0], 20)
        self.assertEqual(remaining_issue[0], 200)

    def test_missing_project_returns_none_without_deleting_data(self):
        result = repository.delete_project_with_history(999)

        self.assertIsNone(result)
        self.assertEqual(
            self._counts(),
            {"projects": 2, "inspections": 2, "issues": 2},
        )


if __name__ == "__main__":
    unittest.main()
