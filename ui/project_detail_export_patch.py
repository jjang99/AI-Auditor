from docx import Document
from openpyxl import Workbook


def _value(issue, key):
    value = issue.get(key)
    return value if value not in (None, "") else "-"


def _issue_rows(report):
    rows = []
    for index, issue in enumerate(report["issues"], 1):
        rows.append([
            index,
            _value(issue, "severity"),
            _value(issue, "rule_code"),
            _value(issue, "title"),
            _value(issue, "status"),
            _value(issue, "description"),
            _value(issue, "evidence"),
            _value(issue, "impact"),
            _value(issue, "impact_reason"),
            _value(issue, "likelihood"),
            _value(issue, "likelihood_reason"),
            _value(issue, "severity_reason"),
            _value(issue, "audit_recommendation_type"),
            _value(issue, "audit_improvement_timing"),
            _value(issue, "audit_important"),
            _value(issue, "category"),
        ])
    return rows


def _export_report_txt(self, path, report):
    lines = ["AI Auditor 검사 보고서", "=" * 48]
    lines.extend(f"{label}: {value}" for label, value in report["summary"])
    lines.extend(["", "[Issues]"])
    rows = _issue_rows(report)

    if not rows:
        lines.append("이슈 없음")
    else:
        for row in rows:
            lines.extend([
                f"{row[0]}. [{row[1]}] {row[2]} - {row[3]}",
                f"   상태: {row[4]}",
                f"   설명: {row[5]}",
                f"   검사 근거: {row[6]}",
                f"   Impact: {row[7]}",
                f"   Impact 근거: {row[8]}",
                f"   Likelihood: {row[9]}",
                f"   Likelihood 근거: {row[10]}",
                f"   Severity: {row[1]}",
                f"   Severity 판정근거: {row[11]}",
                "   감리 개선판정:",
                f"      개선권고유형: {row[12]}",
                f"      개선시점: {row[13]}",
                f"      중요 여부: {row[14]}",
                f"   카테고리: {row[15]}",
                "",
            ])

    path.write_text("\n".join(lines), encoding="utf-8-sig")


def _export_report_docx(self, path, report):
    document = Document()
    document.add_heading("AI Auditor 검사 보고서", level=0)

    table = document.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    for label, value in report["summary"]:
        cells = table.add_row().cells
        cells[0].text = str(label)
        cells[1].text = str(value)

    document.add_heading("Issues", level=1)
    rows = _issue_rows(report)
    if not rows:
        document.add_paragraph("이슈 없음")
    else:
        for row in rows:
            document.add_heading(
                f"{row[0]}. [{row[1]}] {row[2]} - {row[3]}",
                level=2,
            )
            fields = [
                ("상태", row[4]),
                ("설명", row[5]),
                ("검사 근거", row[6]),
                ("Impact", row[7]),
                ("Impact 근거", row[8]),
                ("Likelihood", row[9]),
                ("Likelihood 근거", row[10]),
                ("Severity", row[1]),
                ("Severity 판정근거", row[11]),
                ("개선권고유형", row[12]),
                ("개선시점", row[13]),
                ("중요 여부", row[14]),
                ("카테고리", row[15]),
            ]
            for label, value in fields:
                document.add_paragraph(f"{label}: {value}")

    document.save(path)


def _export_report_xlsx(self, path, report):
    workbook = Workbook()

    summary_sheet = workbook.active
    summary_sheet.title = "검사요약"
    summary_sheet.append(["AI Auditor 검사 보고서", ""])
    for label, value in report["summary"]:
        summary_sheet.append([label, value])
    summary_sheet.column_dimensions["A"].width = 22
    summary_sheet.column_dimensions["B"].width = 48

    issue_sheet = workbook.create_sheet("Issues")
    headers = [
        "No.",
        "Severity",
        "Rule",
        "제목",
        "상태",
        "설명",
        "검사 근거",
        "Impact",
        "Impact 근거",
        "Likelihood",
        "Likelihood 근거",
        "Severity 판정근거",
        "개선권고유형",
        "개선시점",
        "중요 여부",
        "카테고리",
    ]
    issue_sheet.append(headers)
    for row in _issue_rows(report):
        issue_sheet.append(row)

    widths = [
        7, 12, 14, 28, 12, 45, 60, 12,
        50, 12, 50, 55, 16, 12, 12, 20,
    ]
    for index, width in enumerate(widths, 1):
        issue_sheet.column_dimensions[
            issue_sheet.cell(row=1, column=index).column_letter
        ].width = width

    workbook.save(path)


def apply_project_detail_export_patch(ProjectDetailPage):
    """Align all report exports with the final Project Detail assessment model."""
    ProjectDetailPage._issue_rows = staticmethod(_issue_rows)
    ProjectDetailPage._export_report_txt = _export_report_txt
    ProjectDetailPage._export_report_docx = _export_report_docx
    ProjectDetailPage._export_report_xlsx = _export_report_xlsx
