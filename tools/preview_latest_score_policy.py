from __future__ import annotations

from app.database.database import get_connection
from app.database.repositories.inspection_repository import calculate_score_grade
from rules.core.models import InspectionSummary, RuleIssue


def _finding_from_stored_evidence(value: str | None) -> str:
    text = str(value or "").strip()
    if " | " in text:
        return text.split(" | ", 1)[1].strip()
    if "|" in text:
        return text.split("|", 1)[1].strip()
    return text


def _rule_name(rule_code: str, stored_title: str | None) -> str:
    title = str(stored_title or "").strip()
    prefix = f"{rule_code} "
    return title[len(prefix):].strip() if title.startswith(prefix) else title


def main() -> None:
    connection = get_connection()
    latest = connection.execute(
        """
        SELECT id, project_id, inspected_at, score, grade, total_issues, rule_count
        FROM inspections
        ORDER BY inspected_at DESC, id DESC
        LIMIT 1
        """
    ).fetchone()
    if latest is None:
        connection.close()
        print("[LATEST INSPECTION] none")
        return

    rows = connection.execute(
        """
        SELECT id, severity, rule_code, title, description, evidence, category
        FROM issues
        WHERE inspection_id = ?
        ORDER BY id ASC
        """,
        (latest["id"],),
    ).fetchall()
    connection.close()

    issues = tuple(
        RuleIssue(
            rule_code=row["rule_code"],
            rule_name=_rule_name(row["rule_code"], row["title"]),
            category=row["category"] or "",
            severity=row["severity"],
            file_path="",
            line_number=0,
            evidence=_finding_from_stored_evidence(row["evidence"]),
            description=row["description"] or "",
        )
        for row in rows
    )
    summary = InspectionSummary(
        file_count=0,
        rule_count=latest["rule_count"],
        executed_rule_count=latest["rule_count"],
        issues=issues,
    )
    current_score, current_grade = calculate_score_grade(summary)

    print(
        f'[LATEST INSPECTION] id={latest["id"]} at={latest["inspected_at"]} '
        f'issues={latest["total_issues"]}'
    )
    print(f'[STORED SCORE] {latest["score"]} / {latest["grade"]}')
    print(f'[CURRENT POLICY SCORE] {current_score} / {current_grade}')
    print('[CURRENT CHG-001 TITLES]')
    found = False
    for issue in issues:
        if issue.rule_code != "CHG-001":
            continue
        found = True
        print(f'  - {issue.title}')
    if not found:
        print('  - none')


if __name__ == "__main__":
    main()
