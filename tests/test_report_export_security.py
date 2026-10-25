from pathlib import Path

import pytest
from docx import Document
from openpyxl import load_workbook

from ui.project_detail_export_patch import (
    _export_report_docx,
    _export_report_txt,
    _export_report_xlsx,
)
from ui.reports_export_patch import _build_report_data


def sample_report(project_name="요구사항 품질점검", issue_text="요구사항 ID 중복"):
    return _build_report_data(
        {"name": project_name, "department": "품질관리", "project_type": "신규 구축"},
        {
            "inspected_at": "2026-10-24T07:42:32",
            "inspection_type": "전체 검사",
            "score": 69,
            "grade": "D",
            "rule_count": 3,
            "total_issues": 7,
        },
        [{
            "severity": "High",
            "rule_code": "REQ-001",
            "title": issue_text,
            "description": issue_text,
            "evidence": issue_text,
            "status": "미조치",
            "impact": "High",
            "likelihood": "Medium",
        }],
    )


@pytest.mark.parametrize(
    "text",
    ["=1+1", "=SUM(1,2)", "+1+1", "-1+1", "@SUM(1,2)", "\t=1+1", "#N/A", "요구사항 ID 중복"],
)
def test_xlsx_roundtrip_preserves_untrusted_text_without_formulas(tmp_path: Path, text):
    path = tmp_path / "report.xlsx"
    report = sample_report(project_name=text, issue_text=text)

    _export_report_xlsx(None, path, report)

    workbook = load_workbook(path, data_only=False)
    try:
        for sheet, address in [
            ("검사요약", "B2"),
            ("Issues", "D2"),
            ("Issues", "F2"),
            ("Issues", "G2"),
        ]:
            cell = workbook[sheet][address]
            assert cell.value == text
            assert cell.data_type == "s"
        assert all(cell.data_type != "f" for sheet in workbook for row in sheet for cell in row)
    finally:
        workbook.close()


def test_xlsx_preserves_summary_issue_layout_and_numeric_values(tmp_path: Path):
    path = tmp_path / "report.xlsx"
    report = sample_report()
    _export_report_xlsx(None, path, report)

    workbook = load_workbook(path, data_only=False)
    try:
        assert workbook.sheetnames == ["검사요약", "Issues"]
        summary = workbook["검사요약"]
        assert list(summary.iter_rows(min_row=2, values_only=True)) == [tuple(row) for row in report["summary"]]
        issues = workbook["Issues"]
        assert issues.max_column == 16
        assert issues["A2"].value == 1
        assert issues["A2"].data_type == "n"
        assert issues["C2"].value == "REQ-001"
        assert issues["H2"].value == "High"
        assert issues["J2"].value == "Medium"
        assert summary.column_dimensions["B"].width == 48
        assert issues.column_dimensions["G"].width == 60
    finally:
        workbook.close()


@pytest.mark.parametrize("export_format", ["docx", "txt"])
def test_other_report_formats_preserve_summary_and_evidence(tmp_path: Path, export_format):
    path = tmp_path / f"report.{export_format}"
    report = sample_report()
    if export_format == "docx":
        _export_report_docx(None, path, report)
        document = Document(path)
        summary = [[cell.text for cell in row.cells] for row in document.tables[0].rows]
        assert summary == [[str(label), str(value)] for label, value in report["summary"]]
        content = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        _export_report_txt(None, path, report)
        content = path.read_text(encoding="utf-8-sig")
        for label, value in report["summary"]:
            assert f"{label}: {value}" in content
    assert "REQ-001" in content
    assert "요구사항 ID 중복" in content
    assert "Impact" in content
    assert "Likelihood" in content
