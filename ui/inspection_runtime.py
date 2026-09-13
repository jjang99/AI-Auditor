import time
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton

from app.database.repositories.project_repository import create_project, get_project_by_name
from app.services.inspection_service import InspectionService


class InspectionWorker(QObject):
    finished = Signal(object, object, float)
    failed = Signal(str)

    def __init__(self, file_paths, project_id, inspection_type):
        super().__init__()
        self.file_paths = file_paths
        self.project_id = project_id
        self.inspection_type = inspection_type

    def run(self):
        started = time.perf_counter()
        try:
            service = InspectionService()
            inspection_id, summary = service.run(
                self.file_paths,
                project_id=self.project_id,
                inspection_type=self.inspection_type,
            )
            self.finished.emit(inspection_id, summary, time.perf_counter() - started)
        except Exception as exc:
            self.failed.emit(str(exc))


def _format_size(byte_count):
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    return f"{byte_count / (1024 * 1024):.1f} MB"


def apply_inspection_runtime(InspectionPage):
    original_init = InspectionPage.__init__
    original_progress = InspectionPage.create_progress_card
    original_complete = InspectionPage.create_complete_card

    def runtime_init(self):
        original_init(self)
        self.selected_files = []
        self.last_inspection_id = None
        self.last_project_id = None
        self._inspection_thread = None
        self._inspection_worker = None

        self.demo_timer.stop()
        try:
            self.demo_timer.timeout.disconnect()
        except RuntimeError:
            pass

        file_button = self.findChild(QPushButton, "inspectionFileButton")
        if file_button:
            file_button.clicked.connect(self.select_inspection_files)

        for button in self.findChildren(QPushButton, "inspectionSmallButton"):
            if "전체 삭제" in button.text():
                button.clicked.connect(self.clear_inspection_files)

        try:
            self.start_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.start_button.clicked.connect(self.start_real_inspection)
        self._refresh_file_view()

    def select_inspection_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "검사 대상 파일 선택",
            "",
            "텍스트/소스 파일 (*.py *.java *.js *.ts *.yml *.yaml *.xml *.json *.md *.txt *.properties *.sql);;모든 파일 (*.*)",
        )
        if not paths:
            return
        existing = set(self.selected_files)
        for path in paths:
            if path not in existing:
                self.selected_files.append(path)
                existing.add(path)
        self._refresh_file_view()

    def clear_inspection_files(self):
        self.selected_files.clear()
        self._refresh_file_view()

    def _refresh_file_table(self):
        table = self.findChild(QFrame, "inspectionFileTable")
        if table is None or table.layout() is None:
            return
        layout = table.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for raw_path in self.selected_files[:5]:
            path = Path(raw_path)
            row = QFrame()
            row.setObjectName("inspectionFileRow")
            row.setFixedHeight(24)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 2, 10, 2)
            name_label = QLabel(f"▣  {path.name}")
            name_label.setObjectName("inspectionTableText")
            name_label.setFixedWidth(190)
            path_label = QLabel(str(path.parent))
            path_label.setObjectName("inspectionTableMuted")
            size_label = QLabel(_format_size(path.stat().st_size) if path.is_file() else "-")
            size_label.setObjectName("inspectionTableText")
            size_label.setFixedWidth(52)
            delete_label = QLabel("♜")
            delete_label.setObjectName("inspectionTableText")
            delete_label.setFixedWidth(18)
            row_layout.addWidget(name_label)
            row_layout.addWidget(path_label, 1)
            row_layout.addWidget(size_label)
            row_layout.addWidget(delete_label)
            layout.addWidget(row)

    def _refresh_file_view(self):
        total_bytes = sum(Path(path).stat().st_size for path in self.selected_files if Path(path).is_file())
        self._refresh_file_table()
        count_label = self.findChild(QLabel, "inspectionFileCount")
        if count_label:
            count_label.setText(f"등록된 파일 {len(self.selected_files)}개 ({_format_size(total_bytes)})")

        for label in self.findChildren(QLabel, "inspectionTableMuted"):
            if label.text().startswith("외 "):
                hidden_count = max(0, len(self.selected_files) - 5)
                label.setText(f"외 {hidden_count}개 파일" if hidden_count else "")
            elif label.text().startswith("총 "):
                label.setText(f"총 {_format_size(total_bytes)}")

        summary_values = self.findChildren(QLabel, "inspectionSummaryValue")
        summary_details = self.findChildren(QLabel, "inspectionSummaryDetail")
        if summary_values:
            summary_values[0].setText(f"{len(self.selected_files)}개 파일")
        if summary_details:
            summary_details[0].setText(f"({_format_size(total_bytes)})")
        if len(summary_values) > 1:
            summary_values[1].setText("5 / 5개")
        if len(summary_details) > 1:
            summary_details[1].setText("(기본 실행 규칙)")
        if len(summary_values) > 2:
            summary_values[2].setText("실행 시 측정")
        if len(summary_details) > 2:
            summary_details[2].setText("(로컬 Rule Engine)")

    def start_real_inspection(self):
        name = self.project_name.text().strip()
        if not name:
            QMessageBox.warning(self, "프로젝트 정보 확인", "Project Name을 입력해 주세요.")
            return
        if not self.selected_files:
            QMessageBox.warning(self, "검사 대상 확인", "검사할 파일을 먼저 선택해 주세요.")
            return

        inputs = self.findChildren(QLineEdit, "inspectionInput")
        note = inputs[1].text().strip() if len(inputs) > 1 else None
        department = inputs[2].text().strip() if len(inputs) > 2 else None
        project = get_project_by_name(name)
        if project is None:
            project_id = create_project(name, department=department or None, note=note or None)
        else:
            project_id = project["id"]
        self.last_project_id = project_id

        self.summary_card.hide()
        self.complete_card.hide()
        self.progress_card.show()
        self._set_progress_state("검사 진행 중")

        self._inspection_thread = QThread(self)
        self._inspection_worker = InspectionWorker(list(self.selected_files), project_id, "전체 검사")
        self._inspection_worker.moveToThread(self._inspection_thread)
        self._inspection_thread.started.connect(self._inspection_worker.run)
        self._inspection_worker.finished.connect(self._inspection_succeeded)
        self._inspection_worker.failed.connect(self._inspection_failed)
        self._inspection_worker.finished.connect(self._inspection_thread.quit)
        self._inspection_worker.failed.connect(self._inspection_thread.quit)
        self._inspection_thread.finished.connect(self._inspection_worker.deleteLater)
        self._inspection_thread.finished.connect(self._inspection_thread.deleteLater)
        self._inspection_thread.start()

    def _set_progress_state(self, status):
        self.runtime_progress_percent.setText("…")
        self.runtime_progress_bar.setRange(0, 0)
        self.runtime_progress_count.setText("실행 중")
        self.runtime_progress_rule.setText("로컬 Rule Engine 검사")
        self.runtime_progress_time.setText("측정 중")
        self.runtime_progress_status.setText(status)

    def _inspection_succeeded(self, inspection_id, summary, elapsed):
        self.last_inspection_id = inspection_id
        self.progress_card.hide()
        self.summary_card.hide()
        self.complete_card.show()
        self.runtime_complete_rules.setText(f"{summary.rule_count} / {summary.rule_count}개")
        self.runtime_complete_issues.setText(f"{summary.total_issues}개")
        self.runtime_complete_time.setText(f"{elapsed:.2f}초")
        self.runtime_complete_files.setText(f"{summary.file_count}개")
        self._inspection_thread = None
        self._inspection_worker = None

    def _inspection_failed(self, message):
        self.progress_card.hide()
        self.complete_card.hide()
        self.summary_card.show()
        self._inspection_thread = None
        self._inspection_worker = None
        QMessageBox.critical(self, "검사 실행 오류", message)

    def runtime_progress_card(self):
        card = original_progress(self)
        self.runtime_progress_percent = card.findChild(QLabel, "inspectionProgressPercent")
        self.runtime_progress_bar = card.findChild(QProgressBar, "inspectionProgressBar")
        values = card.findChildren(QLabel, "inspectionProgressInfoValue")
        self.runtime_progress_count, self.runtime_progress_rule, self.runtime_progress_time, self.runtime_progress_status = values[:4]
        return card

    def runtime_complete_card(self):
        card = original_complete(self)
        values = card.findChildren(QLabel, "inspectionCompleteInfoValue")
        self.runtime_complete_rules, self.runtime_complete_issues, self.runtime_complete_time, self.runtime_complete_files = values[:4]
        return card

    InspectionPage.__init__ = runtime_init
    InspectionPage.create_progress_card = runtime_progress_card
    InspectionPage.create_complete_card = runtime_complete_card
    InspectionPage.select_inspection_files = select_inspection_files
    InspectionPage.clear_inspection_files = clear_inspection_files
    InspectionPage._refresh_file_table = _refresh_file_table
    InspectionPage._refresh_file_view = _refresh_file_view
    InspectionPage.start_real_inspection = start_real_inspection
    InspectionPage._set_progress_state = _set_progress_state
    InspectionPage._inspection_succeeded = _inspection_succeeded
    InspectionPage._inspection_failed = _inspection_failed
