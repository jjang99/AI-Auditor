from datetime import datetime

from app.database.database import get_connection
from rules.core.models import InspectionSummary


def save_inspection_result(project_id: int, summary: InspectionSummary, inspection_type="전체 검사") -> int:
    inspected_at = datetime.now().isoformat(timespec="seconds")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO inspections (
            project_id, inspection_type, inspected_at, score, grade,
            status, rule_count, total_issues, resolved_issues
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            project_id,
            inspection_type,
            inspected_at,
            None,
            None,
            "AI 검사완료",
            summary.rule_count,
            summary.total_issues,
        ),
    )
    inspection_id = cursor.lastrowid

    for issue in summary.issues:
        evidence = f"{issue.file_path}:{issue.line_number} | {issue.evidence}"
        cursor.execute(
            """
            INSERT INTO issues (
                inspection_id, severity, rule_code, title, description,
                evidence, impact, ai_recommendation, category, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '미조치')
            """,
            (
                inspection_id,
                issue.severity,
                issue.rule_code,
                issue.title,
                issue.description,
                evidence,
                None,
                issue.recommendation,
                issue.category,
            ),
        )

    connection.commit()
    connection.close()
    return inspection_id
