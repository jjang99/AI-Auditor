from datetime import datetime

from app.database.database import get_connection


def create_project(name, department=None, note=None):
    now = datetime.now().isoformat(timespec="seconds")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO projects (
            name,
            department,
            note,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            department,
            note,
            now,
            now,
        ),
    )

    project_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return project_id


def get_all_projects():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            name,
            department,
            note,
            created_at,
            updated_at
        FROM projects
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_project_by_id(project_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            name,
            department,
            note,
            created_at,
            updated_at
        FROM projects
        WHERE id = ?
        """,
        (project_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def get_project_by_name(name):
    connection = get_connection()

    normalized_name = " ".join(name.strip().split()).lower()

    rows = connection.execute(
        """
        SELECT
            id,
            name,
            department,
            note,
            created_at,
            updated_at
        FROM projects
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    for row in rows:
        saved_name = " ".join(row["name"].strip().split()).lower()

        if saved_name == normalized_name:
            return dict(row)

    return None
