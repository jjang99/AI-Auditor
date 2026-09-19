import sqlite3
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    # PyInstaller EXE 실행 시: EXE가 있는 폴더 기준
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Python 개발환경 실행 시: 프로젝트 루트 기준
    BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "ai_auditor.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            project_type TEXT,
            note TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    project_columns = [
        row["name"]
        for row in cursor.execute("PRAGMA table_info(projects)").fetchall()
    ]

    if "project_type" not in project_columns:
        cursor.execute(
            "ALTER TABLE projects ADD COLUMN project_type TEXT"
        )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            inspection_type TEXT NOT NULL,
            inspected_at TEXT NOT NULL,
            score INTEGER,
            grade TEXT,
            status TEXT NOT NULL,
            rule_count INTEGER NOT NULL DEFAULT 0,
            total_issues INTEGER NOT NULL DEFAULT 0,
            resolved_issues INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (project_id)
                REFERENCES projects (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS issues (
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
            status TEXT NOT NULL DEFAULT '미조치',
            FOREIGN KEY (inspection_id)
                REFERENCES inspections (id)
        )
        """
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DB_PATH}")