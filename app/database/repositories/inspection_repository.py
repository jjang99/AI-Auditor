from datetime import datetime

from app.database.database import get_connection
from rules.core.models import InspectionSummary


NON_SCORING_RULE_CODES = frozenset({
    # 변경 사실 자체를 식별하는 정보성 결과다.
    "CHG-001",
    # 앞선 변경 관련 결과를 종합하는 후처리 위험 후보다.
    "CHG-018",
    # 앞선 검사결과를 종합한 감리 예상 지적 후보다.
    "AUD-024",
})


def calculate_score_grade(summary: InspectionSummary):
    """Return the deterministic MVP quality score from independently scorable issues."""
    weights = {"Critical": 20, "High": 10, "Medium": 5, "Low": 2}
    deduction = sum(
        weights.get(issue.severity, 0)
        for issue in summary.issues
        if issue.rule_code not in NON_SCORING_RULE_CODES
    )
    score = max(0, 100 - deduction)
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "E"
    return score, grade


def save_inspection_result(project_id: int, summary: InspectionSummary, inspection_type="전체 검사") -> int:
    inspected_at = datetime.now().isoformat(timespec="seconds")
    connection = get_connection()
    cursor = connection.cursor()
    score, grade = calculate_score_grade(summary)

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
            score,
            grade,
            "AI 검사완료",
            summary.rule_count,
            summary.total_issues,
        ),
    )
    inspection_id = cursor.lastrowid

    for issue in summary.issues:
        source = str(issue.file_path)
        if issue.line_number:
            source = f"{source}:{issue.line_number}"
        evidence = f"{source} | {issue.evidence}"
        assessment = issue.assessment
        audit_judgment = issue.audit_judgment
        stored_severity = (
            assessment.severity.value if assessment is not None else issue.severity
        )
        cursor.execute(
            """
            INSERT INTO issues (
                inspection_id, severity, rule_code, title, description,
                evidence, impact, impact_reason, likelihood, likelihood_reason,
                severity_reason, audit_recommendation_type,
                audit_improvement_timing, audit_important,
                ai_recommendation, category, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '미조치')
            """,
            (
                inspection_id,
                stored_severity,
                issue.rule_code,
                issue.title,
                issue.description,
                evidence,
                assessment.impact.value if assessment is not None else None,
                assessment.impact_reason if assessment is not None else None,
                assessment.likelihood.value if assessment is not None else None,
                assessment.likelihood_reason if assessment is not None else None,
                assessment.severity_reason if assessment is not None else None,
                (
                    audit_judgment.recommendation_type.value
                    if audit_judgment is not None else None
                ),
                (
                    audit_judgment.improvement_timing.value
                    if audit_judgment is not None else None
                ),
                (
                    audit_judgment.important.value
                    if audit_judgment is not None else None
                ),
                issue.recommendation,
                issue.category,
            ),
        )

    connection.commit()
    connection.close()
    return inspection_id


def get_latest_inspection(project_id: int):
    connection = get_connection()
    row = connection.execute(
        """
        SELECT id, project_id, inspection_type, inspected_at, score, grade,
               status, rule_count, total_issues, resolved_issues
        FROM inspections
        WHERE project_id = ?
        ORDER BY inspected_at DESC, id DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    connection.close()
    return dict(row) if row is not None else None


def get_inspection_history(project_id: int, limit: int = 3):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, inspection_type, inspected_at, score, grade, status,
               rule_count, total_issues, resolved_issues
        FROM inspections
        WHERE project_id = ?
        ORDER BY inspected_at DESC, id DESC
        LIMIT ?
        """,
        (project_id, limit),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_issues_for_inspection(inspection_id: int):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, inspection_id, severity, rule_code, title, description,
               evidence, impact, impact_reason, likelihood, likelihood_reason,
               severity_reason, audit_recommendation_type,
               audit_improvement_timing, audit_important,
               ai_recommendation, category, status
        FROM issues
        WHERE inspection_id = ?
        ORDER BY
            CASE severity
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END,
            id ASC
        """,
        (inspection_id,),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_report_rows():
    """Return inspection history joined with project data for the Reports screen."""
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT
            i.id AS inspection_id,
            i.project_id,
            p.name AS project_name,
            p.department,
            i.inspection_type,
            i.inspected_at,
            i.score,
            i.grade,
            i.status,
            i.rule_count,
            i.total_issues,
            i.resolved_issues
        FROM inspections i
        JOIN projects p ON p.id = i.project_id
        ORDER BY i.inspected_at DESC, i.id DESC
        """
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]
