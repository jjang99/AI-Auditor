from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from ui.project_detail_export_patch import (
    _export_report_docx,
    _export_report_txt,
    _export_report_xlsx,
)


def _build_report_data(project, inspection, issues):
    return {
        "project": project,
        "inspection": inspection,
        "issues": issues,
        "summary": [
            ("프로젝트명", project["name"]),
            ("부서명(기관명)", project.get("department") or "-"),
            ("프로젝트 구분", project.get("project_type") or "-"),
            ("검사일시", inspection.get("inspected_at") or "-"),
            ("검사유형", inspection.get("inspection_type") or "-"),
            (
                "Score / Grade",
                f"{inspection.get('score') if inspection.get('score') is not None else '-'} / {inspection.get('grade') or '-'}",
            ),
            ("적용 규칙", f"{inspection.get('rule_count') or 0}개"),
            ("전체 이슈", f"{inspection.get('total_issues') or 0}개"),
        ],
    }


def _export_selected_report(self):
    selected = self.report_table.selectionModel().selectedRows()
    if not selected:
        return

    row_index = selected[0].row()
    if row_index >= len(self.sample_reports):
        return

    selected_report = self.sample_reports[row_index]
    project_id, inspection_id = selected_report[6], selected_report[7]

    from app.database.repositories.project_repository import get_project_by_id
    from app.database.repositories.inspection_repository import (
        get_inspection_history,
        get_issues_for_inspection,
    )

    project = get_project_by_id(project_id)
    history = get_inspection_history(project_id, 100)
    inspection = next(
        (item for item in history if item["id"] == inspection_id),
        None,
    )
    if project is None or inspection is None:
        return

    issues = get_issues_for_inspection(inspection_id)
    safe_name = "".join(
        ch if ch not in '\\/:*?"<>|' else "_"
        for ch in project["name"]
    )

    file_path, selected_filter = QFileDialog.getSaveFileName(
        self,
        "검사 보고서 내보내기",
        f"{safe_name}_검사보고서.docx",
        "Word 문서 (*.docx);;Excel 통합문서 (*.xlsx);;텍스트 파일 (*.txt)",
    )
    if not file_path:
        return

    suffix_by_filter = {
        "Word 문서 (*.docx)": ".docx",
        "Excel 통합문서 (*.xlsx)": ".xlsx",
        "텍스트 파일 (*.txt)": ".txt",
    }
    path = Path(file_path)
    if not path.suffix:
        path = path.with_suffix(suffix_by_filter.get(selected_filter, ".docx"))

    report = _build_report_data(project, inspection, issues)
    suffix = path.suffix.lower()

    if suffix == ".docx":
        _export_report_docx(self, path, report)
    elif suffix == ".xlsx":
        _export_report_xlsx(self, path, report)
    elif suffix == ".txt":
        _export_report_txt(self, path, report)
    else:
        _export_report_docx(self, path.with_suffix(".docx"), report)


def apply_reports_export_patch(ReportsPage):
    """Use the same final report export model as Project Detail."""
    ReportsPage.export_selected_report = _export_selected_report
