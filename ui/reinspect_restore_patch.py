import threading

from PySide6.QtWidgets import QDialog, QMessageBox

from app.database.database import get_connection
from rules.definitions.default_rules import get_default_rules
from rules.definitions.document_rule_catalog import (
    get_document_rule_categories,
    get_document_rules,
)
from ui.reinspect_dialog import ReInspectDialog


_rule_context = threading.local()


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
        [
            (inspection_id, code, position)
            for position, code in enumerate(codes)
        ],
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


def _get_inspection_rule_count(inspection_id):
    if inspection_id is None:
        return None
    connection = get_connection()
    row = connection.execute(
        "SELECT rule_count FROM inspections WHERE id = ?",
        (inspection_id,),
    ).fetchone()
    connection.close()
    return int(row["rule_count"]) if row is not None else None


def _set_selected_rule_codes(page, rule_codes):
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
        category
        for category, values in state.items()
        if any(values)
    }
    page._refresh_rule_summary()


def _wrap_worker_rule_context(worker_cls):
    # Check only attributes defined on this exact class. DiagnosticInspectionExecutionWorker
    # overrides run(), so an inherited marker from InspectionExecutionWorker must not cause
    # this subclass to be skipped.
    if worker_cls.__dict__.get("_reinspect_rule_context_patch_applied", False):
        return
    original_run = worker_cls.run

    def patched_run(self):
        _rule_context.codes = tuple(
            rule.code for rule in getattr(self, "rules", ()) if getattr(rule, "code", None)
        )
        try:
            return original_run(self)
        finally:
            _rule_context.codes = ()

    worker_cls.run = patched_run
    worker_cls._reinspect_rule_context_patch_applied = True


def _wrap_save_result(original_save):
    if getattr(original_save, "_reinspect_rule_save_patch_applied", False):
        return original_save

    def patched_save(*args, **kwargs):
        inspection_id = original_save(*args, **kwargs)
        codes = tuple(getattr(_rule_context, "codes", ()) or ())
        if inspection_id is not None and codes:
            _save_rule_codes(inspection_id, codes)
        return inspection_id

    patched_save._reinspect_rule_save_patch_applied = True
    return patched_save


def apply_reinspect_restore_patch(InspectionPage, ProjectDetailPage, MainWindow):
    """Persist and restore the exact executable Rule set for Re-Inspect."""
    if getattr(MainWindow, "_reinspect_restore_patch_applied", False):
        return

    _ensure_rule_selection_table()

    import ui.inspection_execution_patch as execution_patch
    import ui.inspection_error_patch as error_patch

    _wrap_worker_rule_context(execution_patch.InspectionExecutionWorker)
    _wrap_worker_rule_context(error_patch.DiagnosticInspectionExecutionWorker)
    execution_patch.save_inspection_result = _wrap_save_result(
        execution_patch.save_inspection_result
    )
    error_patch.save_inspection_result = _wrap_save_result(
        error_patch.save_inspection_result
    )

    def set_selected_rule_codes(self, rule_codes):
        _set_selected_rule_codes(self, rule_codes)

    def open_reinspect_dialog(self):
        inspection_id = getattr(self, "current_inspection_id", None)
        project_id = getattr(self, "current_project_id", None)
        rule_count = _get_inspection_rule_count(inspection_id)
        dialog = ReInspectDialog(self, rule_count=rule_count)
        if dialog.exec() == QDialog.Accepted and dialog.selected_files:
            if inspection_id is None or project_id is None:
                return
            # The existing signal's third integer now carries the exact source
            # inspection id. MainWindow uses it to restore that inspection's
            # persisted Rule-code set.
            self.reinspect_requested.emit(
                list(dialog.selected_files),
                int(project_id),
                int(inspection_id),
            )

    def start_reinspection(self, file_paths, project_id, inspection_id):
        rule_codes = _load_rule_codes(inspection_id)

        if not rule_codes:
            # Backward compatibility for legacy inspections created before
            # exact Rule-code persistence existed: a full-selection inspection
            # can still be reconstructed safely from the current full registry.
            rule_count = _get_inspection_rule_count(inspection_id)
            current_rules = tuple(get_default_rules())
            if rule_count == len(current_rules):
                rule_codes = tuple(rule.code for rule in current_rules)
            else:
                QMessageBox.warning(
                    self,
                    "재검사 기준 확인",
                    "이 검사는 개별 규칙 저장 기능 적용 전에 생성되어 당시 검사기준을 정확히 복원할 수 없습니다.\n"
                    "새 검사 결과부터는 선택한 검사기준이 저장되어 Re-Inspect에서 그대로 복원됩니다.",
                )
                return

        self.header.hide()
        self.update_sidebar_selection("Inspection")
        self.inspection_page.prepare_existing_project_inspection(project_id)
        self.inspection_page.selected_files = list(file_paths)
        self.inspection_page.set_selected_rule_codes(rule_codes)
        self.inspection_page._refresh_file_view()
        self.page_stack.setCurrentWidget(self.inspection_page)

    InspectionPage.set_selected_rule_codes = set_selected_rule_codes
    ProjectDetailPage.open_reinspect_dialog = open_reinspect_dialog
    MainWindow.start_reinspection = start_reinspection
    MainWindow._reinspect_restore_patch_applied = True
