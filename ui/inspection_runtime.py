import warnings
import time
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtWidgets import QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton, QScrollArea

from app.database.repositories.project_repository import create_project, get_project_by_id, get_project_by_name
from app.services.local_ai_runtime import get_local_ai_runtime
from app.services.inspection_service import (
    InspectionService,
    SUPPORTED_DOCUMENT_EXTENSIONS,
    SUPPORTED_TEXT_EXTENSIONS,
)
from rules.core.engine import InspectionCancelled
from rules.definitions.default_rules import get_default_rules
from rules.providers.local_ai_provider import LlamaCppAIProvider
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from ui.inspection_rules_dialog import InspectionRulesDialog
from ui.existing_project_dialog import ExistingProjectDialog


CATEGORY_COUNTS = {
    "보안 취약점": 32,
    "코드 품질": 45,
    "AI 특화 검증": 15,
    "성능 및 효율성": 10,
}

CATEGORY_DIALOG_ROWS = {
    "보안 취약점": [("SQL Injection", "사용자 입력값에 대한 SQL 삽입 취약점 검사"), ("Cross Site Scripting (XSS)", "웹 페이지 내 스크립트 삽입 취약점 검사"), ("Cross Site Request Forgery (CSRF)", "요청 위조 공격 가능성 검사"), ("Hard Coding (민감정보)", "소스코드 내 하드코딩된 민감정보 검사"), ("Weak Password Usage", "약한 암호 사용 여부 검사"), ("Insufficient Authentication", "인증 로직 부재 또는 우회 가능성 검사"), ("Broken Access Control", "접근 권한 검증 누락 검사"), ("Sensitive Data Exposure", "민감 데이터 노출 가능성 검사")],
    "코드 품질": [("TODO/FIXME 잔존", "완료되지 않은 작업 표시 잔존 여부 검사"), ("디버그 출력 잔존", "임시 디버그 출력 코드 잔존 여부 검사"), ("중복 코드", "유사·중복 구현 가능성 검사"), ("과도한 함수 복잡도", "함수 및 메서드 복잡도 검사"), ("명명 규칙", "변수·함수·클래스 명명 규칙 검사"), ("예외 처리", "예외 처리 누락 및 부적절한 처리 검사"), ("주석 품질", "불필요하거나 부족한 주석 검사"), ("미사용 코드", "사용되지 않는 코드 가능성 검사")],
    "AI 특화 검증": [("AI 생성 산출물 표시", "AI 생성 또는 보조 산출물 식별 여부 검사"), ("모델 정보 관리", "사용 모델 및 버전 정보 관리 여부 검사"), ("프롬프트 관리", "주요 프롬프트의 관리 및 추적 가능성 검사"), ("학습 데이터 근거", "학습·참조 데이터 출처 및 근거 관리 검사"), ("개인정보 포함", "AI 입력·출력 내 개인정보 포함 가능성 검사"), ("결과 검증 절차", "AI 결과에 대한 사람의 검증 절차 검사"), ("환각 대응", "부정확한 AI 응답에 대한 대응 기준 검사"), ("AI 변경 추적", "모델·프롬프트 변경 이력 관리 검사")],
    "성능 및 효율성": [("무한 반복문", "종료 조건이 불명확한 반복문 검사"), ("비효율적 쿼리", "과도한 조회 및 비효율적 쿼리 가능성 검사"), ("반복 I/O", "반복문 내부의 과도한 I/O 검사"), ("대용량 처리", "대용량 데이터 처리 방식 검사"), ("불필요한 객체 생성", "반복적인 객체 생성 가능성 검사"), ("캐시 미사용", "반복 조회 데이터의 캐시 활용 가능성 검사"), ("동기 블로킹", "불필요한 동기·블로킹 처리 검사"), ("리소스 해제", "파일·연결 등 리소스 해제 여부 검사")],
}


class InspectionWorker(QObject):
    finished = Signal(object, object, float)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, file_paths, project_id, inspection_type, rules, use_local_ai=False):
        super().__init__(); self.file_paths = file_paths; self.project_id = project_id; self.inspection_type = inspection_type; self.rules = rules; self.use_local_ai = use_local_ai; self._cancel_requested = False

    def request_cancel(self):
        self._cancel_requested = True

    def is_cancel_requested(self):
        return self._cancel_requested

    def run(self):
        started = time.perf_counter()
        try:
            if self.use_local_ai:
                local_ai_runtime = get_local_ai_runtime()
                local_ai_runtime.start()
                ai_provider = LlamaCppAIProvider()
                issue_assessor = LocalAIIssueAssessor(ai_provider)
                service = InspectionService(
                    rules=self.rules,
                    ai_provider=ai_provider,
                    issue_assessor=issue_assessor,
                )
            else:
                service = InspectionService(rules=self.rules)

            inspection_id, summary = service.run(
                self.file_paths,
                project_id=self.project_id,
                inspection_type=self.inspection_type,
                cancel_requested=self.is_cancel_requested,
            )
            self.finished.emit(inspection_id, summary, time.perf_counter() - started)
        except InspectionCancelled:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))


def _format_size(byte_count):
    if byte_count < 1024: return f"{byte_count} B"
    if byte_count < 1024 * 1024: return f"{byte_count / 1024:.1f} KB"
    return f"{byte_count / (1024 * 1024):.1f} MB"


def apply_inspection_runtime(InspectionPage):
    original_init = InspectionPage.__init__; original_progress = InspectionPage.create_progress_card; original_complete = InspectionPage.create_complete_card

    def runtime_init(self):
        original_init(self); self.selected_files = []; self.selected_rule_categories = set(CATEGORY_COUNTS); self.last_inspection_id = None; self.last_project_id = None; self.existing_project_id = None; self._inspection_thread = None; self._inspection_worker = None
        self.demo_timer.stop()
        try: self.demo_timer.timeout.disconnect()
        except RuntimeError: pass
        file_button = self.findChild(QPushButton, "inspectionFileButton")
        if file_button: file_button.clicked.connect(self.select_inspection_files)
        for button in self.findChildren(QPushButton, "inspectionSmallButton"):
            if "전체 삭제" in button.text(): button.clicked.connect(self.clear_inspection_files)
            elif button.text() == "전체 선택": button.clicked.connect(lambda _checked=False: self.set_all_rule_categories(True))
            elif button.text() == "전체 해제": button.clicked.connect(lambda _checked=False: self.set_all_rule_categories(False))
        self._wire_rule_rows()
        try: self.start_button.clicked.disconnect()
        except RuntimeError: pass
        self.start_button.clicked.connect(self.start_real_inspection)
        cancel_button = self.progress_card.findChild(QPushButton, "inspectionCancelButton")
        if cancel_button:
            try: cancel_button.clicked.disconnect()
            except (RuntimeError, TypeError): pass
            cancel_button.clicked.connect(self.cancel_real_inspection)
        self._refresh_file_view(); self._refresh_rule_summary()

    def _wire_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            name_label = row.findChild(QLabel, "inspectionRuleName"); check_label = row.findChild(QLabel, "inspectionCheck"); view_button = row.findChild(QPushButton, "inspectionViewButton")
            if name_label is None: continue
            category = name_label.text(); row.setProperty("ruleCategory", category)
            if check_label is not None and row.layout() is not None:
                index = row.layout().indexOf(check_label); row.layout().removeWidget(check_label); check_label.hide()
                toggle = QPushButton("✓"); toggle.setObjectName("inspectionCheck"); toggle.setCheckable(True); toggle.setChecked(True); toggle.setCursor(Qt.PointingHandCursor); toggle.setFixedSize(15, 15)
                toggle.clicked.connect(lambda checked, name=category: self.set_rule_category(name, checked)); row.layout().insertWidget(index, toggle)
            if view_button is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", RuntimeWarning)
                        view_button.clicked.disconnect()
                except (RuntimeError, TypeError):
                    pass
                except Warning:
                    pass
                view_button.clicked.connect(lambda _checked=False, name=category: self.open_rule_category_dialog(name))

    def set_rule_category(self, category, selected):
        if selected: self.selected_rule_categories.add(category)
        else: self.selected_rule_categories.discard(category)
        self._sync_rule_toggle_buttons(); self._refresh_rule_summary()

    def set_all_rule_categories(self, selected):
        self.selected_rule_categories = set(CATEGORY_COUNTS) if selected else set(); self._sync_rule_toggle_buttons(); self._refresh_rule_summary()

    def _sync_rule_toggle_buttons(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            category = row.property("ruleCategory"); toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle is not None:
                toggle.blockSignals(True); toggle.setChecked(category in self.selected_rule_categories); toggle.setText("✓" if toggle.isChecked() else ""); toggle.blockSignals(False)

    def _selected_executable_rules(self): return [rule for rule in get_default_rules() if rule.category in self.selected_rule_categories]

    def _refresh_rule_summary(self):
        self._sync_rule_toggle_buttons(); executable_rules = self._selected_executable_rules(); total_executable = len(get_default_rules()); summary_values = self.findChildren(QLabel, "inspectionSummaryValue"); summary_details = self.findChildren(QLabel, "inspectionSummaryDetail")
        if len(summary_values) > 1: summary_values[1].setText(f"{len(executable_rules)} / {total_executable}개")
        if len(summary_details) > 1: summary_details[1].setText("(현재 구현된 기본 규칙)")

    def open_rule_category_dialog(self, category):
        dialog = InspectionRulesDialog(self); dialog.setWindowTitle(category); title = dialog.findChild(QLabel, "rulesDialogTitle"); count = dialog.findChild(QLabel, "rulesDialogCount")
        if title: title.setText(category)
        if count: count.setText(f"{CATEGORY_COUNTS.get(category, 0)}개 항목")
        rows = dialog.findChildren(QFrame, "rulesTableRow"); samples = CATEGORY_DIALOG_ROWS.get(category, [])
        for index, row in enumerate(rows):
            labels = [label for label in row.findChildren(QLabel) if label.objectName() in {"rulesRowText", "rulesRowDescription"}]
            if index < len(samples) and len(labels) >= 2: labels[0].setText(samples[index][0]); labels[1].setText(samples[index][1])
        dialog.exec()

    def select_inspection_files(self):
        document_patterns = " ".join(
            f"*{extension}"
            for extension in sorted(SUPPORTED_DOCUMENT_EXTENSIONS)
        )

        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "검사 대상 파일 선택",
            "",
            f"문서 파일 ({document_patterns});;"
            "텍스트/소스 파일 (*.py *.java *.js *.ts *.yml *.yaml *.xml *.json *.md *.txt *.properties *.sql);;"
            "모든 지원 파일 (*.*)",
        )
        if not paths: return
        existing = set(self.selected_files)
        unsupported = []
        for path in paths:
            suffix = Path(path).suffix.lower()
            if (
                suffix not in SUPPORTED_TEXT_EXTENSIONS
                and suffix not in SUPPORTED_DOCUMENT_EXTENSIONS
            ):
                unsupported.append(Path(path).name)
                continue
            if path not in existing:
                self.selected_files.append(path)
                existing.add(path)
        self._refresh_file_view()
        if unsupported:
            names = "\n".join(f"• {name}" for name in unsupported[:8])
            more = f"\n외 {len(unsupported) - 8}개" if len(unsupported) > 8 else ""
            warning = QMessageBox(self)
            warning.setIcon(QMessageBox.Warning)
            warning.setWindowTitle("지원하지 않는 파일 형식")
            warning.setText("지원하지 않는 파일은 등록에서 제외했습니다.")
            warning.setInformativeText(
                f"{names}{more}\n\n"
                "지원 형식: 문서 Parser 지원 형식 및 기존 텍스트/소스 파일"
            )
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setStyleSheet(
                "QLabel { font-size: 12px; }"
                "QLabel#qt_msgbox_label { font-size: 13px; font-weight: 700; }"
                "QPushButton { min-width: 72px; min-height: 28px; font-size: 11px; font-weight: 600; }"
            )
            warning.exec()

    def clear_inspection_files(self): self.selected_files.clear(); self._refresh_file_view()
    def remove_inspection_file(self, file_path):
        try: self.selected_files.remove(file_path)
        except ValueError: return
        self._refresh_file_view()

    def _refresh_file_table(self):
        table = self.findChild(QFrame, "inspectionFileTable")
        if table is None or table.layout() is None: return
        layout = table.layout(); layout.setAlignment(Qt.AlignTop)
        while layout.count():
            item = layout.takeAt(0); widget = item.widget()
            if widget is not None: widget.deleteLater()
        visible_files = self.selected_files
        for raw_path in visible_files:
            path = Path(raw_path); row = QFrame(); row.setObjectName("inspectionFileRow"); row.setFixedHeight(30); row_layout = QHBoxLayout(row); row_layout.setContentsMargins(10, 2, 10, 2)
            name_label = QLabel(path.name); name_label.setObjectName("inspectionTableText"); name_label.setFixedWidth(240); path_label = QLabel(str(path.parent)); path_label.setFixedWidth(240); path_label.setObjectName("inspectionTableMuted"); size_label = QLabel(_format_size(path.stat().st_size) if path.is_file() else "-"); size_label.setObjectName("inspectionTableText"); size_label.setFixedWidth(52); delete_button = QPushButton("♜"); delete_button.setObjectName("inspectionFileDeleteButton"); delete_button.setCursor(Qt.PointingHandCursor); delete_button.setToolTip(f"{path.name} 삭제"); delete_button.setFlat(True); delete_button.setFixedSize(24, 24); delete_button.clicked.connect(lambda _checked=False, file_path=raw_path: self.remove_inspection_file(file_path))
            row_layout.addWidget(name_label); row_layout.addWidget(path_label, 1); row_layout.addWidget(size_label); row_layout.addWidget(delete_button); layout.addWidget(row)
        needed_height = max(88, len(visible_files) * 30); table.setMinimumHeight(needed_height); table.setMaximumHeight(needed_height); scroll = self.findChild(QScrollArea, "inspectionFileScroll")
        if scroll is not None: scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff if len(visible_files) <= 3 else Qt.ScrollBarAsNeeded)

    def _refresh_file_view(self):
        total_bytes = sum(Path(path).stat().st_size for path in self.selected_files if Path(path).is_file()); self._refresh_file_table(); count_label = self.findChild(QLabel, "inspectionFileCount")
        if count_label: count_label.setText(f"등록된 파일 {len(self.selected_files)}개 ({_format_size(total_bytes)})")
        for label in self.findChildren(QLabel, "inspectionTableMuted"):
            if label.text().startswith("외 "): hidden_count = max(0, len(self.selected_files) - 5); label.setText(f"외 {hidden_count}개 파일" if hidden_count else "")
            elif label.text().startswith("총 "): label.setText(f"총 {_format_size(total_bytes)}")
        summary_values = self.findChildren(QLabel, "inspectionSummaryValue"); summary_details = self.findChildren(QLabel, "inspectionSummaryDetail")
        if summary_values: summary_values[0].setText(f"{len(self.selected_files)}개 파일")
        if summary_details: summary_details[0].setText(f"({_format_size(total_bytes)})")
        if len(summary_values) > 2: summary_values[2].setText("실행 시 측정")
        if len(summary_details) > 2: summary_details[2].setText("(로컬 Rule Engine)")
        self._refresh_rule_summary()

    def _show_existing_project_dialog(self, project):
        dialog_project = {
            "id": project["id"],
            "name": project["name"],
            "department": project.get("department") or "-",
            "type": "기존 프로젝트",
            "date": (project.get("updated_at") or project.get("created_at") or "-")[:10].replace("-", "."),
        }
        dialog = ExistingProjectDialog(self, projects=[dialog_project])
        dialog.exec()

    def start_real_inspection(self):
        name = self.project_name.text().strip()
        if not name:
            warning = QMessageBox(self)
            warning.setIcon(QMessageBox.Warning)
            warning.setWindowTitle("프로젝트 정보 확인")
            warning.setText("Project Name을 입력해 주세요.")
            warning.setStandardButtons(QMessageBox.Ok)
            main_window = self.window()
            is_dark = getattr(main_window, "is_dark_mode", True)
            if is_dark:
                warning.setStyleSheet(
                    "QMessageBox { background:#111a23; }"
                    "QLabel#qt_msgbox_label { color:#f1f5f9; font-size:13px; font-weight:700; padding:8px 6px 6px 4px; }"
                    "QPushButton { min-width:58px; max-width:58px; min-height:26px; max-height:26px; color:#f1f5f9; background:#1b2a38; border:1px solid #526b80; border-radius:6px; padding:0; font-size:11px; font-weight:600; }"
                    "QPushButton:hover { background:#27465e; border-color:#6f91a9; }"
                )
            else:
                warning.setStyleSheet(
                    "QMessageBox { background:#ffffff; }"
                    "QLabel#qt_msgbox_label { color:#172a3c; font-size:13px; font-weight:700; padding:8px 6px 6px 4px; }"
                    "QPushButton { min-width:58px; max-width:58px; min-height:26px; max-height:26px; color:#172a3c; background:#f8fafc; border:1px solid #97adbd; border-radius:6px; padding:0; font-size:11px; font-weight:600; }"
                    "QPushButton:hover { background:#edf3f7; border-color:#7f9bad; }"
                )
            warning.setFixedWidth(340)
            warning.exec()
            return
        if not self.selected_files: QMessageBox.warning(self, "검사 대상 확인", "검사할 파일을 먼저 선택해 주세요."); return
        selected_rules = self._selected_executable_rules()
        if not selected_rules: QMessageBox.warning(self, "검사 기준 확인", "실행할 검사 기준을 하나 이상 선택해 주세요."); return
        inputs = self.findChildren(QLineEdit, "inspectionInput"); note = inputs[1].text().strip() if len(inputs) > 1 else None; department = inputs[2].text().strip() if len(inputs) > 2 else None
        project = get_project_by_name(name)
        if self.existing_project_id is not None:
            if project is None or project["id"] != self.existing_project_id:
                QMessageBox.warning(self, "프로젝트 정보 확인", "기존 프로젝트 정보가 변경되었습니다. Project Detail에서 New Inspection을 다시 선택해 주세요.")
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
            QMessageBox.warning(
                self,
                "프로젝트 정보 확인",
                "프로젝트 구분을 선택해 주세요."
            )
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
        self._set_progress_state("검사 진행 중")

        self._inspection_thread = QThread(self)
        self._inspection_worker = InspectionWorker(
            list(self.selected_files),
            project_id,
            "전체 검사",
            selected_rules,
            use_local_ai=True,
        )

        # All worker -> QWidget callbacks must be queued explicitly. The worker
        # runs on a QThread and these callbacks update GUI widgets/QTimers.
        if hasattr(self._inspection_worker, "progress"):
            self._inspection_worker.progress.connect(
                self._on_execution_progress,
                Qt.QueuedConnection,
            )
        self._inspection_worker.finished.connect(
            self._inspection_succeeded,
            Qt.QueuedConnection,
        )
        self._inspection_worker.failed.connect(
            self._inspection_failed,
            Qt.QueuedConnection,
        )
        self._inspection_worker.cancelled.connect(
            self._inspection_cancelled,
            Qt.QueuedConnection,
        )

        self._inspection_worker.moveToThread(self._inspection_thread)
        self._inspection_thread.started.connect(self._inspection_worker.run)
        self._inspection_worker.finished.connect(self._inspection_thread.quit)
        self._inspection_worker.failed.connect(self._inspection_thread.quit)
        self._inspection_worker.cancelled.connect(self._inspection_thread.quit)
        self._inspection_thread.finished.connect(self._inspection_worker.deleteLater)
        self._inspection_thread.finished.connect(self._inspection_thread.deleteLater)
        self._inspection_thread.start()

    def _set_progress_state(self, status):
        self.runtime_progress_percent.setText("…"); self.runtime_progress_bar.setRange(0, 0); self.runtime_progress_count.setText("실행 중"); self.runtime_progress_rule.setText("로컬 Rule Engine 검사"); self.runtime_progress_time.setText("측정 중"); self.runtime_progress_status.setText(status)

    def _inspection_succeeded(self, inspection_id, summary, elapsed):
        self.last_inspection_id = inspection_id; self.progress_card.hide(); self.summary_card.hide(); self.complete_card.show(); self.runtime_complete_rules.setText(f"{summary.rule_count} / {summary.rule_count}개"); self.runtime_complete_issues.setText(f"{summary.total_issues}개"); self.runtime_complete_time.setText(f"{elapsed:.2f}초"); self.runtime_complete_files.setText(f"{summary.file_count}개"); self._inspection_thread = None; self._inspection_worker = None

    def cancel_real_inspection(self):
        if self._inspection_worker is None or self._inspection_thread is None:
            return
        self._set_progress_state("검사 취소 중")
        self._inspection_worker.request_cancel()

    def _inspection_cancelled(self):
        self.progress_card.hide()
        self.complete_card.hide()
        self.summary_card.show()
        self._inspection_thread = None
        self._inspection_worker = None
        self._refresh_file_view()

    def _inspection_failed(self, message):
        self.progress_card.hide(); self.complete_card.hide(); self.summary_card.show(); self._inspection_thread = None; self._inspection_worker = None; QMessageBox.critical(self, "검사 실행 오류", message)

    def prepare_existing_project_inspection(self, project_id):
        if self._inspection_thread is not None:
            return
        project = get_project_by_id(project_id)
        if project is None:
            return
        self.prepare_new_inspection()
        self.existing_project_id = project_id
        self.project_name.setText(project.get("name") or "")
        inputs = self.findChildren(QLineEdit, "inspectionInput")
        if len(inputs) > 1:
            inputs[1].setText(project.get("note") or "")
        if len(inputs) > 2:
            inputs[2].setText(project.get("department") or "")
        project_type_combo = self.findChild(QComboBox, "inspectionCombo")
        if project_type_combo is not None:
            saved_type = str(project.get("project_type") or "").strip()
            normalized_type = {
                "신규": "신규 구축",
                "신규구축": "신규 구축",
                "신규 구축": "신규 구축",
                "고도화": "고도화",
                "유지보수": "유지보수",
            }.get(saved_type.replace(" ", "") if saved_type else "", saved_type)
            if normalized_type:
                index = project_type_combo.findText(normalized_type, Qt.MatchFixedString)
                if index < 0:
                    project_type_combo.addItem(normalized_type)
                    index = project_type_combo.count() - 1
                project_type_combo.setCurrentIndex(index)

    def prepare_new_inspection(self):
        if self._inspection_thread is not None:
            return

        self.progress_card.hide()
        self.complete_card.hide()
        self.summary_card.show()
        self.selected_files = []
        self.existing_project_id = None
        self.last_inspection_id = None
        self.last_project_id = None
        self.project_name.clear()
        inputs = self.findChildren(QLineEdit, "inspectionInput")
        for input_widget in inputs[1:]:
            input_widget.clear()
        project_type_combo = self.findChild(QComboBox, "inspectionCombo")
        if project_type_combo is not None:
            project_type_combo.setCurrentIndex(0)
        self.set_all_rule_categories(True)
        self._refresh_file_view()

    def runtime_progress_card(self):
        card = original_progress(self)
        self.runtime_progress_percent = card.findChild(QLabel, "inspectionProgressPercent")
        self.runtime_progress_bar = card.findChild(QProgressBar, "inspectionProgressBar")
        values = card.findChildren(QLabel, "inspectionProgressInfoValue")
        self.runtime_progress_count, self.runtime_progress_rule, self.runtime_progress_time, self.runtime_progress_status = values[:4]
        return card

    def runtime_complete_card(self):
        card = original_complete(self); values = card.findChildren(QLabel, "inspectionCompleteInfoValue"); self.runtime_complete_rules, self.runtime_complete_issues, self.runtime_complete_time, self.runtime_complete_files = values[:4]; return card

    InspectionPage.__init__ = runtime_init; InspectionPage.create_progress_card = runtime_progress_card; InspectionPage.create_complete_card = runtime_complete_card
    InspectionPage._wire_rule_rows = _wire_rule_rows; InspectionPage.set_rule_category = set_rule_category; InspectionPage.set_all_rule_categories = set_all_rule_categories; InspectionPage._sync_rule_toggle_buttons = _sync_rule_toggle_buttons; InspectionPage._selected_executable_rules = _selected_executable_rules; InspectionPage._refresh_rule_summary = _refresh_rule_summary; InspectionPage.open_rule_category_dialog = open_rule_category_dialog
    InspectionPage.select_inspection_files = select_inspection_files; InspectionPage.clear_inspection_files = clear_inspection_files; InspectionPage.remove_inspection_file = remove_inspection_file; InspectionPage._refresh_file_table = _refresh_file_table; InspectionPage._refresh_file_view = _refresh_file_view
    InspectionPage._show_existing_project_dialog = _show_existing_project_dialog; InspectionPage.prepare_existing_project_inspection = prepare_existing_project_inspection; InspectionPage.start_real_inspection = start_real_inspection; InspectionPage.cancel_real_inspection = cancel_real_inspection; InspectionPage._set_progress_state = _set_progress_state; InspectionPage._inspection_succeeded = _inspection_succeeded; InspectionPage._inspection_cancelled = _inspection_cancelled; InspectionPage._inspection_failed = _inspection_failed; InspectionPage.prepare_new_inspection = prepare_new_inspection
