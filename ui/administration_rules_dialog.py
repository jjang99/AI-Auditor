import os

from PySide6.QtCore import Qt, QSize
from rules.definitions.document_rule_catalog import get_document_rules_by_category
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)


class AdministrationRulesDialog(QDialog):
    def __init__(self, category_name, total, active, inactive, parent=None, icon_file=None, rule_states=None):
        super().__init__(parent)
        self.setWindowTitle(f"{category_name} - 규칙 목록")
        self.setModal(True)
        self.setFixedSize(700, 500)

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets", "icons", icon_file or "logo.svg"
        )
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)
        header_icon = QLabel()
        header_icon.setObjectName("adminDialogHeaderIcon")
        header_icon.setPixmap(QIcon(icon_path).pixmap(QSize(24, 24)))
        header_icon.setFixedSize(28, 28)
        header_icon.setAlignment(Qt.AlignCenter)
        title = QLabel(f"{category_name} - 규칙 목록")
        title.setObjectName("adminDialogTitle")
        header.addWidget(header_icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        total_label = QLabel(f"총 {total}개 규칙")
        total_label.setObjectName("adminSummaryTotal")
        self.active_count = active
        self.inactive_count = inactive
        self.rule_states = dict(rule_states or {})
        active_label = QLabel(f"활성 {active}개")
        active_label.setObjectName("adminSummaryActive")
        inactive_label = QLabel(f"비활성 {inactive}개")
        self.active_label = active_label
        self.inactive_label = inactive_label
        inactive_label.setObjectName("adminSummaryInactive")
        for widget in (total_label, active_label, inactive_label):
            summary_row.addWidget(widget)
            if widget is not inactive_label:
                separator = QLabel("|")
                separator.setObjectName("adminSummarySeparator")
                summary_row.addWidget(separator)
        summary_row.addStretch()
        layout.addLayout(summary_row)

        self.search = QLineEdit()
        self.search.setPlaceholderText("규칙 코드 또는 제목 검색")
        self.search.setObjectName("adminRuleSearch")
        self.search.setFixedHeight(38)
        self.search.textChanged.connect(self.filter_rows)
        layout.addWidget(self.search)

        table = QFrame()
        table.setObjectName("adminRuleTable")
        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Header and result rows use the exact same widths/spacing so columns line up.
        code_width = 86
        name_width = 142
        severity_width = 82
        status_width = 58
        column_spacing = 12

        table_header = QFrame()
        table_header.setObjectName("adminRuleHeader")
        table_header.setFixedHeight(40)
        header_layout = QHBoxLayout(table_header)
        header_layout.setContentsMargins(12, 0, 10, 0)
        header_layout.setSpacing(column_spacing)

        headers = [
            ("코드", code_width),
            ("규칙 제목", name_width),
            ("설명", 1),
            ("검사방식", severity_width),
            ("상태", status_width),
        ]
        for text, width in headers:
            label = QLabel(text)
            label.setObjectName("adminRuleHeaderText")
            label.setAlignment(Qt.AlignCenter)
            if width == 1:
                header_layout.addWidget(label, 1)
            else:
                label.setFixedWidth(width)
                header_layout.addWidget(label)
        table_layout.addWidget(table_header)

        scroll = QScrollArea()
        scroll.setObjectName("adminRuleScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("adminRuleContent")
        rows = QVBoxLayout(content)
        rows.setContentsMargins(0, 0, 0, 0)
        rows.setSpacing(0)

        category_code_map = {
            "감리 사전점검": "AUD",
            "요구사항 정합성": "REQ",
            "변경영향도": "CHG",
            "FP 검증": "FP",
            "AI 특화 검증": "AI",
        }

        category_code = category_code_map.get(category_name)
        catalog_rules = (
            get_document_rules_by_category(category_code)
            if category_code
            else ()
        )

        self.rule_rows = []
        for rule in catalog_rules:
            code_text = rule.code
            name = rule.name
            description = rule.description
            execution_type = rule.execution_type
            checked = self.rule_states.get(code_text, True)

            row = QFrame()
            row.setObjectName("adminRuleRow")
            row.setFixedHeight(66)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 6, 10, 6)
            row_layout.setSpacing(column_spacing)

            code_label = QLabel(code_text)
            code_label.setObjectName("adminRuleCode")
            code_label.setFixedWidth(code_width)
            code_label.setAlignment(Qt.AlignCenter)

            name_label = QLabel(name)
            name_label.setObjectName("adminRuleName")
            name_label.setFixedWidth(name_width)
            name_label.setWordWrap(True)
            name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            desc_label = QLabel(description)
            desc_label.setObjectName("adminRuleDescription")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            execution_label = QLabel(execution_type)
            execution_label.setObjectName("adminExecutionType")
            execution_label.setFixedSize(severity_width, 28)
            execution_label.setAlignment(Qt.AlignCenter)

            toggle = QPushButton("ON" if checked else "OFF")
            toggle.setObjectName("adminRuleToggle")
            toggle.setCheckable(True)
            toggle.setChecked(self.rule_states.get(code_text, checked))
            toggle.setCursor(Qt.PointingHandCursor)
            toggle.setFixedSize(50, 24)
            toggle.toggled.connect(
                lambda state, button=toggle, rule_code=code_text: self._rule_toggled(state, button, rule_code)
            )

            row_layout.addWidget(code_label)
            row_layout.addWidget(name_label)
            row_layout.addWidget(desc_label, 1)
            row_layout.addWidget(execution_label, 0, Qt.AlignCenter)
            row_layout.addWidget(toggle, 0, Qt.AlignCenter)

            rows.addWidget(row)
            self.rule_rows.append((row, code_text.lower(), name.lower()))

        rows.addStretch()
        scroll.setWidget(content)
        table_layout.addWidget(scroll)
        layout.addWidget(table, 1)

        footer = QHBoxLayout()
        notice = QLabel("ⓘ 규칙을 비활성화하면 기본 검사에서 제외됩니다.")
        notice.setObjectName("adminDialogNotice")
        close = QPushButton("닫기")
        close.setObjectName("adminDialogPrimaryButton")
        close.setCursor(Qt.PointingHandCursor)
        close.setFixedSize(88, 34)
        close.clicked.connect(self.accept)
        footer.addWidget(notice)
        footer.addStretch()
        footer.addWidget(close)
        layout.addLayout(footer)

        self.apply_theme()

    def _rule_toggled(self, state, button, rule_code):
        button.setText("ON" if state else "OFF")
        self.rule_states[rule_code] = state
        if state:
            self.active_count += 1
            self.inactive_count = max(0, self.inactive_count - 1)
        else:
            self.active_count = max(0, self.active_count - 1)
            self.inactive_count += 1
        self.active_label.setText(f"활성 {self.active_count}개")
        self.inactive_label.setText(f"비활성 {self.inactive_count}개")

    def open_rule_detail(self, code, name, description, execution_type, source_toggle):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{code} - Rule Detail")
        dialog.setModal(True)
        dialog.setFixedSize(500, 455)
        dialog.setWindowIcon(self.windowIcon())

        root = QVBoxLayout(dialog)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(10)

        title = QLabel("Rule Detail")
        title.setObjectName("adminDetailTitle")
        root.addWidget(title)

        def add_field(label_text, value_text):
            label = QLabel(label_text)
            label.setObjectName("adminDetailLabel")
            value = QLabel(value_text)
            value.setObjectName("adminDetailValue")
            value.setWordWrap(True)
            value.setFixedHeight(32)
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            root.addWidget(label)
            root.addWidget(value)
            root.addSpacing(3)

        add_field("Code", code)
        add_field("규칙 제목", name)
        add_field("설명", description)

        execution_row = QHBoxLayout()
        execution_row.setSpacing(10)

        execution_title = QLabel("검사방식")
        execution_title.setObjectName("adminDetailLabel")

        execution_badge = QLabel(execution_type)
        execution_badge.setObjectName("adminExecutionType")
        execution_badge.setFixedSize(82, 32)
        execution_badge.setAlignment(Qt.AlignCenter)

        execution_row.addWidget(execution_title)
        execution_row.addStretch()
        execution_row.addWidget(execution_badge)

        root.addLayout(execution_row)
        root.addSpacing(4)

        status_row = QHBoxLayout()
        status_label = QLabel("상태")
        status_label.setObjectName("adminDetailLabel")
        status_toggle = QPushButton("ON" if source_toggle.isChecked() else "OFF")
        status_toggle.setObjectName("adminRuleToggle")
        status_toggle.setCheckable(True)
        status_toggle.setChecked(source_toggle.isChecked())
        status_toggle.setFixedSize(82, 32)
        status_toggle.setCursor(Qt.PointingHandCursor)
        status_toggle.toggled.connect(lambda state: status_toggle.setText("ON" if state else "OFF"))
        status_row.addWidget(status_label)
        status_row.addStretch()
        status_row.addWidget(status_toggle)
        root.addLayout(status_row)
        root.addSpacing(6)
        notice = QLabel("ⓘ 규칙을 비활성화하면 기본 검사에서 제외됩니다.")
        notice.setObjectName("adminDialogNotice")
        root.addWidget(notice)

        buttons = QHBoxLayout()
        buttons.addStretch()
        close = QPushButton("닫기")
        close.setObjectName("adminDialogPrimaryButton")
        close.setFixedSize(88, 34)
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(dialog.accept)
        buttons.addWidget(close)
        root.addLayout(buttons)

        # Reuse the list dialog theme, adding only Rule Detail-specific typography.
        self.apply_theme()
        base_style = self.styleSheet()
        if "#101820" in base_style:
            detail_style = """
                #adminDetailTitle { color:#ffffff; font-size:20px; font-weight:900; }
                #adminDetailLabel { color:#d9e5ef; font-size:12px; font-weight:900; }
                #adminDetailValue { color:#ffffff; background:#111f2c; border:1px solid #587086; border-radius:7px; padding:0 12px; font-size:13px; font-weight:850; }
                #severityHigh, #severityCritical, #severityMedium, #severityLow, #adminRuleToggle { font-size:12px; font-weight:900; }
            """
        else:
            detail_style = """
                #adminDetailTitle { color:#142435; font-size:20px; font-weight:900; }
                #adminDetailLabel { color:#304a63; font-size:12px; font-weight:900; }
                #adminDetailValue { color:#10283f; background:#ffffff; border:1px solid #8fa8bd; border-radius:7px; padding:0 12px; font-size:13px; font-weight:850; }
                #severityHigh, #severityCritical, #severityMedium, #severityLow, #adminRuleToggle { font-size:12px; font-weight:900; }
            """
        dialog.setStyleSheet(base_style + detail_style)
        dialog.exec()

        # The MVP decision is immediate ON/OFF reflection.
        source_toggle.setChecked(status_toggle.isChecked())
        source_toggle.setText("ON" if status_toggle.isChecked() else "OFF")

    def filter_rows(self, text):
        keyword = text.strip().lower()
        for row, code, name in self.rule_rows:
            row.setVisible(not keyword or keyword in code or keyword in name)

    def apply_theme(self):
        host = self.parentWidget().window() if self.parentWidget() is not None else None
        is_dark = getattr(host, "is_dark_mode", True)
        if is_dark:
            self.setStyleSheet("""
                QDialog { background:#101820; color:#f8fafc; }
                #adminDialogHeaderIcon { background:transparent; border:none; }
                #adminDialogTitle { font-size:20px; font-weight:850; color:#ffffff; }
                #adminSummaryTotal { color:#f8fafc; font-size:13px; font-weight:850; }
                #adminSummaryActive { color:#22d36b; font-size:13px; font-weight:900; }
                #adminSummaryInactive { color:#ff6445; font-size:13px; font-weight:900; }
                #adminSummarySeparator { color:#7c8b9a; font-size:13px; font-weight:750; }
                #adminRuleSearch { background:#111f2c; color:#ffffff; border:1px solid #4a6276; border-radius:7px; padding:0 11px; font-size:12px; font-weight:650; }
                #adminRuleTable { background:#0d1721; border:1px solid #3b5368; border-radius:7px; }
                #adminRuleHeader { background:#1a3145; border-bottom:1px solid #526b80; }
                #adminRuleHeaderText { color:#ffffff; font-size:12px; font-weight:900; }
                #adminRuleScroll, #adminRuleContent { background:transparent; border:none; }
                #adminRuleRow { background:#0d1721; border-bottom:1px solid #31475a; }
                #adminRuleCode { color:#e6f0ff; font-size:12px; font-weight:900; }
                #adminRuleName { color:#ffffff; font-size:12px; font-weight:900; }
                #adminRuleDescription { color:#edf2f7; font-size:12px; font-weight:700; }
                #severityCritical { color:#ff7a7a; background:#381b22; border:1px solid #ef4444; border-radius:7px; font-size:10px; font-weight:900; }
                #severityHigh { color:#ffc06a; background:#392817; border:1px solid #f59e0b; border-radius:7px; font-size:10px; font-weight:900; }
                #severityMedium { color:#75b4ff; background:#14314d; border:1px solid #3b82f6; border-radius:7px; font-size:10px; font-weight:900; }
                #severityLow { color:#62e58d; background:#153a25; border:1px solid #22c55e; border-radius:7px; font-size:10px; font-weight:900; }
                #adminRuleToggle { background:#526274; color:#f1f5f9; border:none; border-radius:12px; font-size:9px; font-weight:900; }
                #adminRuleToggle:checked { background:#21c96a; color:#ffffff; }
                #adminDialogNotice { color:#f1f5f9; font-size:11px; font-weight:750; }
                #adminDialogPrimaryButton { background:#2563eb; color:#ffffff; border:none; border-radius:7px; font-size:12px; font-weight:900; }
                #adminDialogPrimaryButton:hover { background:#3475f5; }
                QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                QScrollBar::handle:vertical { background:#6f8396; min-height:28px; border-radius:4px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background:#f7f9fc; color:#172a3c; }
                #adminDialogHeaderIcon { background:transparent; border:none; }
                #adminDialogTitle { font-size:20px; font-weight:850; color:#142435; }
                #adminSummaryTotal { color:#26384a; font-size:13px; font-weight:850; }
                #adminSummaryActive { color:#13994a; font-size:13px; font-weight:900; }
                #adminSummaryInactive { color:#e04b30; font-size:13px; font-weight:900; }
                #adminSummarySeparator { color:#8ea0b1; font-size:13px; font-weight:750; }
                #adminRuleSearch { background:#ffffff; color:#172a3c; border:1px solid #9fb2c3; border-radius:7px; padding:0 11px; font-size:12px; font-weight:650; }
                #adminRuleTable { background:#ffffff; border:1px solid #aebfce; border-radius:7px; }
                #adminRuleHeader { background:#e2ebf3; border-bottom:1px solid #9eb0bf; }
                #adminRuleHeaderText { color:#203346; font-size:12px; font-weight:900; }
                #adminRuleScroll, #adminRuleContent { background:transparent; border:none; }
                #adminRuleRow { background:#ffffff; border-bottom:1px solid #cfd9e2; }
                #adminRuleCode { color:#1749b5; font-size:12px; font-weight:900; }
                #adminRuleName { color:#142435; font-size:12px; font-weight:900; }
                #adminRuleDescription { color:#2f4356; font-size:12px; font-weight:700; }
                #severityCritical { color:#b42318; background:#fff0f0; border:1px solid #e45858; border-radius:7px; font-size:10px; font-weight:900; }
                #severityHigh { color:#985600; background:#fff6e6; border:1px solid #d89523; border-radius:7px; font-size:10px; font-weight:900; }
                #severityMedium { color:#1859b4; background:#eaf3ff; border:1px solid #5b93dd; border-radius:7px; font-size:10px; font-weight:900; }
                #severityLow { color:#176f38; background:#edf9f1; border:1px solid #4dae6c; border-radius:7px; font-size:10px; font-weight:900; }
                #adminRuleToggle { background:#9eabb8; color:#ffffff; border:none; border-radius:12px; font-size:9px; font-weight:900; }
                #adminRuleToggle:checked { background:#20b85f; color:#ffffff; }
                #adminDialogNotice { color:#354a5f; font-size:11px; font-weight:750; }
                #adminDialogPrimaryButton { background:#2563eb; color:#ffffff; border:none; border-radius:7px; font-size:12px; font-weight:900; }
                #adminDialogPrimaryButton:hover { background:#1d4ed8; }
                QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                QScrollBar::handle:vertical { background:#8998aa; min-height:28px; border-radius:4px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }
            """)
