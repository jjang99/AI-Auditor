from PySide6.QtWidgets import QDialog, QMessageBox

from app.database.database import get_connection
from rules.definitions.default_rules import get_default_rules
from rules.definitions.document_rule_catalog import (
    get_document_rule_categories,
    get_document_rules,
)
from ui.reinspect_dialog import ReInspectDialog


def _ensure_rule_selection_table():
    connection = get_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS inspection_rule_selections (
            inspection_id INTEGER NOT NULL,
            rule_code TEXT NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (inspection_id, rule_code),
            FOREIGN KEY (inspection_id) REFERENCES inspections (id)
        )
        """
    )
    connection.commit()
    connection.close()


def _save_rule_codes(inspection_id, rule_codes):
    if inspection_id is None:
        return
    codes = tuple(dict.fromkeys(str(code) for code in rule_codes if code))
    connection = get_connection()
    connection.execute(
        "DELETE FROM inspection_rule_selections WHERE inspection_id = ?",
        (inspection_id,),
    )
    connection.executemany(
        """
        INSERT INTO inspection_rule_selections (inspection_id, rule_code, position)
        VALUES (?, ?, ?)
        """,
        [(inspection_id, code, index) for index, code in enumerate(codes)],
    )
    connection.commit()
    connection.close()


def _load_rule_codes(inspection_id):
    if inspection_id is None:
        return ()
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT rule_code
        FROM inspection_rule_selections
        WHERE inspection_id = ?
        ORDER BY position, rule_code
        """,
        (inspection_id,),
    ).fetchall()
    connection.close()
    return tuple(row["rule_code"] for row in rows)


def _get_rule_count(inspection_id):
    if inspection_id is None:
        return None
    connection = get_connection()
    row = connection.execute(
        "SELECT rule_count FROM inspections WHERE id = ?",
        (inspection_id,),
    ).fetchone()
    connection.close()
    return int(row["rule_count"]) if row is not None else None


def _apply_rule_codes(page, rule_codes):
    selected = set(rule_codes)
    category_counts = {
        category.name: category.total_count
        for category in get_document_rule_categories()
    }
    state = {
        category: [False] * total
        for category, total in category_counts.items()
    }
    category_index = {}
    for rule in get_document_rules():
        index = category_index.get(rule.category, 0)
        category_index[rule.category] = index + 1
        if rule.code in selected and rule.category in state:
            if 0 <= index < len(state[rule.category]):
                state[rule.category][index] = True

    page.rule_selection_state = state
    page.selected_rule_categories = {
        category for category, values in state.items() if any(values)
    }
    page._refresh_rule_summary()


def apply_reinspect_rule_state_patch(InspectionPage, ProjectDetailPage, MainWindow):
    """Persist and restore the exact Rule set used by each completed inspection.

    Rule persistence happens from the GUI success callback after the worker has
    already saved the inspection row. This avoids touching worker-thread execution.
    """
    if getattr(MainWindow, "_reinspect_rule_state_patch_applied", False):
        return

    _ensure_rule_selection_table()

    original_success = InspectionPage._inspection_succeeded

    def patched_success(self, inspection_id, summary, elapsed):
        if inspection_id is not None:
            rule_codes = [
                rule.code
                for rule in self._selected_executable_rules()
                if getattr(rule, "code", None)
            ]
            _save_rule_codes(inspection_id, rule_codes)
        original_success(self, inspection_id, summary, elapsed)

    def open_reinspect_dialog(self):
        inspection_id = getattr(self, "current_inspection_id", None)
        project_id = getattr(self, "current_project_id", None)
        rule_count = _get_rule_count(inspection_id)
        dialog = ReInspectDialog(self, rule_count=rule_count)
        if dialog.exec() == QDialog.Accepted and dialog.selected_files:
            if inspection_id is None or project_id is None:
                return
            self.reinspect_requested.emit(
                list(dialog.selected_files),
                int(project_id),
                int(inspection_id),
            )

    def start_reinspection(self, file_paths, project_id, inspection_id):
        rule_codes = _load_rule_codes(inspection_id)

        if not rule_codes:
            # Legacy compatibility: old full-rule inspections are still safe to
            # reconstruct. Old partial inspections cannot be reconstructed exactly.
            rule_count = _get_rule_count(inspection_id)
            current_rules = tuple(get_default_rules())
            if rule_count == len(current_rules):
                rule_codes = tuple(rule.code for rule in current_rules)
            else:
                QMessageBox.warning(
                    self,
                    "재검사 기준 확인",
                    "이 검사는 개별 규칙 저장 기능 적용 전에 생성되어 당시 검사기준을 정확히 복원할 수 없습니다.\n"
                    "새 검사 결과부터는 선택한 검사기준이 Re-Inspect에서 그대로 복원됩니다.",
                )
                return

        self.header.hide()
        self.update_sidebar_selection("Inspection")
        self.inspection_page.prepare_existing_project_inspection(project_id)
        self.inspection_page.selected_files = list(file_paths)
        _apply_rule_codes(self.inspection_page, rule_codes)
        self.inspection_page._refresh_file_view()
        self.page_stack.setCurrentWidget(self.inspection_page)

    InspectionPage._inspection_succeeded = patched_success
    ProjectDetailPage.open_reinspect_dialog = open_reinspect_dialog
    MainWindow.start_reinspection = start_reinspection
    MainWindow._reinspect_rule_state_patch_applied = True
