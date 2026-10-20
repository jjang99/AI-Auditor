import time

from PySide6.QtCore import QObject, QThread, Qt, Slot
from PySide6.QtWidgets import QComboBox, QLineEdit, QMessageBox

from app.database.repositories.project_repository import create_project, get_project_by_name
from rules.core.models import RuleExecutionType
from ui.inspection_execution_patch import _estimate_inspection_seconds
import ui.inspection_runtime as inspection_runtime


class _InspectionUiBridge(QObject):
    """Deliver worker callbacks through a QObject that lives on the GUI thread."""

    def __init__(self, page):
        super().__init__(page)
        self.page = page

    @Slot(object, object, float)
    def on_finished(self, inspection_id, summary, elapsed):
        self.page._inspection_succeeded(inspection_id, summary, elapsed)

    @Slot(str)
    def on_failed(self, message):
        self.page._inspection_failed(message)

    @Slot()
    def on_cancelled(self):
        self.page._inspection_cancelled()

    @Slot(int, int, str)
    def on_progress(self, completed, total, current):
        self.page._on_execution_progress(completed, total, current)


def apply_inspection_safe_start_patch(InspectionPage):
    """Remove the start/rewire race and guarantee GUI-thread callbacks."""
    if getattr(InspectionPage, "_safe_start_patch_applied", False):
        return

    def start_real_inspection(self):
        if getattr(self, "_inspection_thread", None) is not None:
            return

        name = self.project_name.text().strip()
        if not name:
            QMessageBox.warning(self, "프로젝트 정보 확인", "Project Name을 입력해 주세요.")
            return
        if not self.selected_files:
            QMessageBox.warning(self, "검사 대상 확인", "검사할 파일을 먼저 선택해 주세요.")
            return

        selected_rules = list(self._selected_executable_rules())
        if not selected_rules:
            QMessageBox.warning(self, "검사 기준 확인", "실행할 검사 기준을 하나 이상 선택해 주세요.")
            return

        inputs = self.findChildren(QLineEdit, "inspectionInput")
        note = inputs[1].text().strip() if len(inputs) > 1 else None
        department = inputs[2].text().strip() if len(inputs) > 2 else None

        project = get_project_by_name(name)
        if self.existing_project_id is not None:
            if project is None or project["id"] != self.existing_project_id:
                QMessageBox.warning(
                    self,
                    "프로젝트 정보 확인",
                    "기존 프로젝트 정보가 변경되었습니다. Project Detail에서 New Inspection을 다시 선택해 주세요.",
                )
                return
            project_id = self.existing_project_id
        elif project is not None:
            self._show_existing_project_dialog(project)
            return
        else:
            project_id = None

        project_type_combo = self.findChild(QComboBox, "inspectionCombo")
        project_type = project_type_combo.currentText().strip() if project_type_combo else ""
        if project_id is None and (not project_type or project_type == "선택"):
            QMessageBox.warning(self, "프로젝트 정보 확인", "프로젝트 구분을 선택해 주세요.")
            return

        if project_id is None:
            project_id = create_project(
                name,
                department=department or None,
                project_type=project_type,
                note=note or None,
            )

        self.last_project_id = project_id
        self.summary_card.hide()
        self.complete_card.hide()
        self.progress_card.show()

        self._inspection_estimated_seconds = _estimate_inspection_seconds(
            list(self.selected_files),
            selected_rules,
        )
        self._inspection_started_at = time.perf_counter()
        self._inspection_completed_rules = 0
        self._inspection_total_rules = len(selected_rules)
        self._inspection_postprocessing = False
        self._set_progress_state("검사 진행 중")

        use_local_ai = any(
            getattr(rule, "execution_type", None)
            in {RuleExecutionType.AI, RuleExecutionType.HYBRID}
            for rule in selected_rules
        )

        thread = QThread(self)
        worker = inspection_runtime.InspectionWorker(
            list(self.selected_files),
            project_id,
            "전체 검사",
            selected_rules,
            use_local_ai=use_local_ai,
        )
        worker.moveToThread(thread)

        bridge = _InspectionUiBridge(self)
        self._inspection_thread = thread
        self._inspection_worker = worker
        self._inspection_ui_bridge = bridge

        # Wire every callback before the thread starts. The previous flow started
        # the worker first and then disconnected/reconnected callbacks, which
        # allowed fast Rule-only inspections to lose their finished signal.
        thread.started.connect(worker.run)
        worker.finished.connect(bridge.on_finished, Qt.ConnectionType.QueuedConnection)
        worker.failed.connect(bridge.on_failed, Qt.ConnectionType.QueuedConnection)
        worker.cancelled.connect(bridge.on_cancelled, Qt.ConnectionType.QueuedConnection)
        if hasattr(worker, "progress"):
            worker.progress.connect(bridge.on_progress, Qt.ConnectionType.QueuedConnection)

        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.cancelled.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        if hasattr(self, "_execution_progress_timer"):
            self._execution_progress_timer.start()
            self._tick_execution_progress()

        thread.start()

    InspectionPage.start_real_inspection = start_real_inspection
    InspectionPage._safe_start_patch_applied = True
