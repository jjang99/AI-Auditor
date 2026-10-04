from app.database.database import get_connection


def _short(text, limit=180):
    value = " ".join(str(text or "").split())
    return value if len(value) <= limit else value[: limit - 3] + "..."


def main():
    connection = get_connection()
    latest = connection.execute(
        """
        SELECT i.id, i.project_id, p.name AS project_name, i.inspected_at,
               i.score, i.grade, i.total_issues
        FROM inspections i
        JOIN projects p ON p.id = i.project_id
        ORDER BY i.inspected_at DESC, i.id DESC
        LIMIT 1
        """
    ).fetchone()

    if latest is None:
        print("[LATEST INSPECTION] none")
        connection.close()
        return

    rows = connection.execute(
        """
        SELECT id, severity, rule_code, title, evidence,
               impact, likelihood,
               audit_recommendation_type, audit_improvement_timing, audit_important
        FROM issues
        WHERE inspection_id = ?
        ORDER BY id ASC
        """,
        (latest["id"],),
    ).fetchall()
    connection.close()

    print(
        f'[LATEST INSPECTION] id={latest["id"]} project={latest["project_name"]} '
        f'at={latest["inspected_at"]} score={latest["score"]} '
        f'grade={latest["grade"]} issues={latest["total_issues"]}'
    )
    print(f"[ISSUE ROWS] {len(rows)}")

    for index, row in enumerate(rows, 1):
        audit = " / ".join(
            str(row[key] or "판정 없음")
            for key in (
                "audit_recommendation_type",
                "audit_improvement_timing",
                "audit_important",
            )
        )
        print(f"\n[{index:02d}] id={row['id']} {row['rule_code']} severity={row['severity']}")
        print(f"  title: {_short(row['title'], 120)}")
        print(f"  impact/likelihood: {row['impact'] or '-'} / {row['likelihood'] or '-'}")
        print(f"  audit: {audit}")
        print(f"  evidence: {_short(row['evidence'])}")


if __name__ == "__main__":
    main()
