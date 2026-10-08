from app.database.database import get_connection


def get_data_management_summary():
    """Return current project / inspection / issue counts."""
    connection = get_connection()

    try:
        project_count = connection.execute(
            "SELECT COUNT(*) FROM projects"
        ).fetchone()[0]
        inspection_count = connection.execute(
            "SELECT COUNT(*) FROM inspections"
        ).fetchone()[0]
        issue_count = connection.execute(
            "SELECT COUNT(*) FROM issues"
        ).fetchone()[0]

        return {
            "projects": project_count,
            "inspections": inspection_count,
            "issues": issue_count,
        }
    finally:
        connection.close()


def get_project_delete_impact(project_id: int):
    """Return the data affected when one project is deleted."""
    connection = get_connection()

    try:
        project = connection.execute(
            """
            SELECT id, name, department
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()

        if project is None:
            return None

        inspection_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM inspections
            WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()[0]

        issue_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM issues
            WHERE inspection_id IN (
                SELECT id
                FROM inspections
                WHERE project_id = ?
            )
            """,
            (project_id,),
        ).fetchone()[0]

        return {
            "project_id": project["id"],
            "project_name": project["name"],
            "department": project["department"],
            "inspections": inspection_count,
            "issues": issue_count,
        }
    finally:
        connection.close()


def delete_all_inspection_history():
    """Delete every inspection and its issues while preserving projects."""
    connection = get_connection()

    try:
        inspection_count = connection.execute(
            "SELECT COUNT(*) FROM inspections"
        ).fetchone()[0]
        issue_count = connection.execute(
            "SELECT COUNT(*) FROM issues"
        ).fetchone()[0]

        connection.execute("DELETE FROM issues")
        connection.execute("DELETE FROM inspections")
        connection.commit()

        return {
            "deleted_inspections": inspection_count,
            "deleted_issues": issue_count,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_project_with_history(project_id: int):
    """Delete one project together with its inspections and issues."""
    connection = get_connection()

    try:
        project = connection.execute(
            """
            SELECT id, name
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()

        if project is None:
            return None

        inspection_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM inspections
            WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()[0]

        issue_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM issues
            WHERE inspection_id IN (
                SELECT id
                FROM inspections
                WHERE project_id = ?
            )
            """,
            (project_id,),
        ).fetchone()[0]

        connection.execute(
            """
            DELETE FROM issues
            WHERE inspection_id IN (
                SELECT id
                FROM inspections
                WHERE project_id = ?
            )
            """,
            (project_id,),
        )
        connection.execute(
            "DELETE FROM inspections WHERE project_id = ?",
            (project_id,),
        )
        connection.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,),
        )
        connection.commit()

        return {
            "project_id": project["id"],
            "project_name": project["name"],
            "deleted_inspections": inspection_count,
            "deleted_issues": issue_count,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
