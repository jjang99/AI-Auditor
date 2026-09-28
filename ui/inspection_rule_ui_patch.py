from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QDialog, QFrame, QLabel, QPushButton, QStyle

from rules.core.document_selection import get_selected_document_mvp_rules
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.definitions.document_rule_catalog import get_document_rule_categories
from ui.inspection_rules_dialog import InspectionRulesDialog


CATEGORY_COUNTS = {
    category.name: category.total_count
    for category in get_document_rule_categories()
}

def executable_rule_index(rule):
    """실행 Rule 자체에 정의된 UI 선택 위치를 사용한다."""
    return (rule.category, rule.selection_index) if rule.selection_index is not None else None

def apply_inspection_rule_ui_patch(InspectionPage):
    """Inspection runtime 적용 이후, Rule 선택 UI/상태 표시를 보정한다."""

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table

    def patched_init(self):
        original_init(self)

        self.rule_selection_state = {
            category: [True] * total
            for category, total in CATEGORY_COUNTS.items()
        }
        self.selected_rule_categories = set(CATEGORY_COUNTS)

        upload_text = self.findChild(QLabel, "inspectionUploadText")
        if upload_text:
            upload_text.setText("파일을 드래그 앤 드롭하거나")

        trash_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        for button in self.findChildren(QPushButton, "inspectionSmallButton"):
            if "전체 삭제" in button.text():
                button.setText("전체 삭제")
                button.setIcon(trash_icon)
                button.setIconSize(QSize(12, 12))
                button.setToolTip("등록된 파일 전체 삭제")

        # 검사기준 선택 체크박스는 주변 아이콘/텍스트와 균형이 맞도록 더 작게 고정한다.
        for toggle in self.findChildren(QPushButton, "inspectionCheck"):
            toggle.setFixedSize(14, 14)

        # Do not attach a page-local stylesheet here.  It overrides MainWindow's
        # light/dark theme selectors and was the cause of the rule rows retaining
        # dark text/buttons in Light Mode.  Visual sizing is handled below and
        # colors remain owned by the central theme.


        self._refresh_file_table()
        self._refresh_rule_summary()

    def selected_count(self, category):
        states = getattr(self, "rule_selection_state", {}).get(category)
        if states is None:
            return CATEGORY_COUNTS.get(category, 0) if category in getattr(self, "selected_rule_categories", set()) else 0
        return sum(1 for checked in states if checked)

    def sync_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            category = row.property("ruleCategory")
            if category not in CATEGORY_COUNTS:
                continue

            current = selected_count(self, category)
            total = CATEGORY_COUNTS[category]

            count_label = row.findChild(QLabel, "inspectionRuleCount")
            if count_label:
                count_label.setText(f"{current} / {total}개 규칙")

            toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle:
                toggle.setFixedSize(14, 14)
                toggle.blockSignals(True)
                toggle.setChecked(current > 0)
                toggle.setText("✓" if current > 0 else "")
                toggle.setToolTip(
                    "선택된 규칙 있음" if current == total
                    else "일부 규칙 선택됨" if current > 0
                    else "선택된 규칙 없음"
                )
                toggle.blockSignals(False)

    def set_rule_category(self, category, selected):
        if not hasattr(self, "rule_selection_state"):
            self.rule_selection_state = {name: [True] * total for name, total in CATEGORY_COUNTS.items()}
        self.rule_selection_state[category] = [selected] * CATEGORY_COUNTS[category]
        if selected: self.selected_rule_categories.add(category)
        else: self.selected_rule_categories.discard(category)
        self._refresh_rule_summary()

    def set_all_rule_categories(self, selected):
        if not hasattr(self, "rule_selection_state"): self.rule_selection_state = {}
        for category, total in CATEGORY_COUNTS.items(): self.rule_selection_state[category] = [selected] * total
        self.selected_rule_categories = set(CATEGORY_COUNTS) if selected else set(); self._refresh_rule_summary()

    def refresh_rule_summary(self):
        # 카테고리 행은 Full Catalog 105개 선택상태를 보여주고,
        # '적용 규칙'은 그중 실제 실행 가능한 문서 MVP 20개 기준으로 표시한다.
        sync_rule_rows(self)
        executable_rules = self._selected_executable_rules()
        total_executable = len(get_document_mvp_rules())
        summary_values = self.findChildren(QLabel, "inspectionSummaryValue")
        summary_details = self.findChildren(QLabel, "inspectionSummaryDetail")
        if len(summary_values) > 1:
            summary_values[1].setText(f"{len(executable_rules)} / {total_executable}개")
        if len(summary_details) > 1:
            summary_details[1].setText("(실제 실행 규칙)")

    def selected_executable_rules(self):
        return list(
            get_selected_document_mvp_rules(
                getattr(self, "rule_selection_state", {})
            )
        )

    def open_rule_category_dialog(self, category):
        if not hasattr(self, "rule_selection_state"):
            self.rule_selection_state = {name: [True] * total for name, total in CATEGORY_COUNTS.items()}
        dialog = InspectionRulesDialog(self); total = CATEGORY_COUNTS.get(category, 0); working = list(self.rule_selection_state[category])
        title = dialog.findChild(QLabel, "rulesDialogTitle"); count = dialog.findChild(QLabel, "rulesDialogCount"); header_icon = dialog.findChild(QLabel, "rulesDialogShieldIcon")
        if title: title.setText(category)
        if count: count.setText(f"{total}개 규칙")
        source_icon = None
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            if row.property("ruleCategory") == category:
                source_icon = row.findChild(QLabel, "inspectionRuleIcon"); break
        if header_icon is not None and source_icon is not None:
            captured = source_icon.grab()
            if not captured.isNull():
                header_icon.clear(); header_icon.setPixmap(captured.scaled(QSize(40, 34), Qt.KeepAspectRatio, Qt.SmoothTransformation)); header_icon.setAlignment(Qt.AlignCenter); header_icon.setFixedSize(44, 36); header_icon.show()
        header_labels = dialog.findChildren(QLabel, "rulesTableHeaderText")
        for label in header_labels:
            if label.text() == "항목명": label.setText("규칙명"); label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            elif label.text() == "설명": label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            elif label.text() == "상태": label.setAlignment(Qt.AlignCenter)
        for label in dialog.findChildren(QLabel):
            if label.text() == "적용할 항목을 선택하거나 제외할 수 있습니다.": label.setText("적용할 규칙을 선택하거나 제외할 수 있습니다.")
        for label in dialog.findChildren(QLabel, "rulesRowText"): label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for label in dialog.findChildren(QLabel, "rulesRowDescription"): label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for label in dialog.findChildren(QLabel, "rulesRowState"): label.setAlignment(Qt.AlignCenter)
        try:
            from ui.inspection_runtime import CATEGORY_DIALOG_ROWS
            samples = CATEGORY_DIALOG_ROWS.get(category, [])
        except Exception: samples = []
        rows = dialog.findChildren(QFrame, "rulesTableRow")
        for index, row in enumerate(rows):
            labels = [label for label in row.findChildren(QLabel) if label.objectName() in {"rulesRowText", "rulesRowDescription"}]
            if index < len(samples) and len(labels) >= 2: labels[0].setText(samples[index][0]); labels[1].setText(samples[index][1])
        checkboxes = list(dialog.rule_checkboxes); state_labels = list(dialog.state_labels)
        for checkbox in checkboxes:
            try: checkbox.stateChanged.disconnect()
            except (RuntimeError, TypeError): pass
        def update_count_label(): dialog.selected_count.setText(f"선택됨 {sum(1 for checked in working if checked)} / {total}개 규칙")
        def set_visible_state(index, checked):
            if index < len(working): working[index] = checked
            if index < len(state_labels): state_labels[index].setText("활성" if checked else "비활성"); state_labels[index].setAlignment(Qt.AlignCenter)
            update_count_label()
        for index, checkbox in enumerate(checkboxes):
            checked = working[index] if index < len(working) else False; checkbox.blockSignals(True); checkbox.setChecked(checked); checkbox.blockSignals(False)
            if index < len(state_labels): state_labels[index].setText("활성" if checked else "비활성"); state_labels[index].setAlignment(Qt.AlignCenter)
            checkbox.stateChanged.connect(lambda state, idx=index: set_visible_state(idx, state == Qt.Checked.value))
        def set_all(checked):
            for i in range(len(working)): working[i] = checked
            for index, checkbox in enumerate(checkboxes):
                checkbox.blockSignals(True); checkbox.setChecked(checked); checkbox.blockSignals(False)
                if index < len(state_labels): state_labels[index].setText("활성" if checked else "비활성"); state_labels[index].setAlignment(Qt.AlignCenter)
            update_count_label()
        for button in dialog.findChildren(QPushButton, "rulesDialogSmallButton"):
            try: button.clicked.disconnect()
            except (RuntimeError, TypeError): pass
            if button.text() == "전체 선택": button.clicked.connect(lambda _checked=False: set_all(True))
            elif button.text() == "전체 해제": button.clicked.connect(lambda _checked=False: set_all(False))
        update_count_label()
        if dialog.exec() == QDialog.Accepted:
            self.rule_selection_state[category] = working; current = sum(1 for checked in working if checked)
            if current > 0: self.selected_rule_categories.add(category)
            else: self.selected_rule_categories.discard(category)
            self._refresh_rule_summary()

    def refresh_file_table(self):
        original_refresh_file_table(self); trash_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        for button in self.findChildren(QPushButton, "inspectionFileDeleteButton"):
            button.setText(""); button.setIcon(trash_icon); button.setIconSize(QSize(12, 12))

    InspectionPage.__init__ = patched_init
    InspectionPage.set_rule_category = set_rule_category
    InspectionPage.set_all_rule_categories = set_all_rule_categories
    InspectionPage._refresh_rule_summary = refresh_rule_summary
    InspectionPage._selected_executable_rules = selected_executable_rules
    InspectionPage.open_rule_category_dialog = open_rule_category_dialog
    InspectionPage._refresh_file_table = refresh_file_table
