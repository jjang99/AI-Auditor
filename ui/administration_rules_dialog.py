from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)


class AdministrationRulesDialog(QDialog):
    def __init__(self, category_name, total, active, inactive, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{category_name} - 규칙 목록")
        self.setModal(True)
        self.setFixedSize(700, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel(f"{category_name} - 규칙 목록")
        title.setObjectName("adminDialogTitle")
        close_button = QPushButton("×")
        close_button.setObjectName("adminDialogClose")
        close_button.setFixedSize(32, 32)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        summary = QLabel(f"총 {total}개 규칙   |   활성 {active}개   |   비활성 {inactive}개")
        summary.setObjectName("adminDialogSummary")
        layout.addWidget(summary)

        self.search = QLineEdit()
        self.search.setPlaceholderText("규칙 코드 또는 제목 검색")
        self.search.setObjectName("adminRuleSearch")
        self.search.setFixedHeight(34)
        self.search.textChanged.connect(self.filter_rows)
        layout.addWidget(self.search)

        table = QFrame()
        table.setObjectName("adminRuleTable")
        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        table_header = QFrame()
        table_header.setObjectName("adminRuleHeader")
        table_header.setFixedHeight(36)
        header_layout = QHBoxLayout(table_header)
        header_layout.setContentsMargins(12, 0, 10, 0)
        header_layout.setSpacing(10)

        headers = [
            ("코드", 72),
            ("규칙 제목", 130),
            ("설명", 1),
            ("심각도", 72),
            ("상태", 58),
        ]
        for text, width in headers:
            label = QLabel(text)
            label.setObjectName("adminRuleHeaderText")
            label.setAlignment(Qt.AlignCenter if text in {"코드", "심각도", "상태"} else Qt.AlignLeft | Qt.AlignVCenter)
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

        sample_rules = [
            ("001", "기본 규칙 1", "검사 기준에 따라 항목을 점검합니다.", "High", True),
            ("002", "기본 규칙 2", "검사 대상의 적정성을 확인합니다.", "Critical", True),
            ("003", "기본 규칙 3", "누락 또는 오류 가능성을 확인합니다.", "High", True),
            ("004", "기본 규칙 4", "검사 항목의 일관성을 확인합니다.", "Medium", True),
            ("005", "기본 규칙 5", "검사 기준 위반 여부를 확인합니다.", "Medium", False),
        ]

        if "요구사항" in category_name:
            prefix = "REQ"
        elif "설계" in category_name:
            prefix = "DES"
        elif "보안" in category_name:
            prefix = "SEC"
        elif "코드" in category_name:
            prefix = "COD"
        else:
            prefix = "AI"

        self.rule_rows = []
        for code, name, description, severity, checked in sample_rules:
            row = QFrame()
            row.setObjectName("adminRuleRow")
            row.setFixedHeight(62)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 6, 10, 6)
            row_layout.setSpacing(10)

            code_text = f"{prefix}-{code}"
            code_label = QLabel(code_text)
            code_label.setObjectName("adminRuleCode")
            code_label.setFixedWidth(72)
            code_label.setAlignment(Qt.AlignCenter)

            name_label = QLabel(name)
            name_label.setObjectName("adminRuleName")
            name_label.setFixedWidth(130)

            desc_label = QLabel(description)
            desc_label.setObjectName("adminRuleDescription")
            desc_label.setWordWrap(True)

            severity_label = QLabel(severity)
            severity_label.setObjectName(f"severity{severity}")
            severity_label.setFixedSize(72, 26)
            severity_label.setAlignment(Qt.AlignCenter)

            toggle = QPushButton("ON" if checked else "OFF")
            toggle.setObjectName("adminRuleToggle")
            toggle.setCheckable(True)
            toggle.setChecked(checked)
            toggle.setCursor(Qt.PointingHandCursor)
            toggle.setFixedSize(50, 24)
            toggle.toggled.connect(lambda state, button=toggle: button.setText("ON" if state else "OFF"))

            row_layout.addWidget(code_label)
            row_layout.addWidget(name_label)
            row_layout.addWidget(desc_label, 1)
            row_layout.addWidget(severity_label, 0, Qt.AlignCenter)
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
                #adminDialogTitle { font-size:20px; font-weight:850; color:#ffffff; }
                #adminDialogSummary { color:#d4dee8; font-size:12px; font-weight:700; }
                #adminDialogClose { background:transparent; border:none; color:#ffffff; font-size:22px; }
                #adminDialogClose:hover { background:#1b2d3d; border-radius:6px; }
                #adminRuleSearch { background:#111c26; color:#ffffff; border:1px solid #42576b; border-radius:7px; padding:0 10px; font-size:12px; }
                #adminRuleTable { background:#0d1721; border:1px solid #31475a; border-radius:7px; }
                #adminRuleHeader { background:#172838; border-bottom:1px solid #40586c; }
                #adminRuleHeaderText { color:#e8eef5; font-size:11px; font-weight:850; }
                #adminRuleScroll, #adminRuleContent { background:transparent; border:none; }
                #adminRuleRow { background:#0d1721; border-bottom:1px solid #293d50; }
                #adminRuleRow:hover { background:#132536; }
                #adminRuleCode { color:#dbeafe; font-size:11px; font-weight:800; }
                #adminRuleName { color:#ffffff; font-size:11px; font-weight:800; }
                #adminRuleDescription { color:#d7e0e9; font-size:11px; font-weight:600; }
                #severityCritical { color:#ff6b6b; background:#341a20; border:1px solid #ef4444; border-radius:7px; font-size:10px; font-weight:850; }
                #severityHigh { color:#ffb35c; background:#342718; border:1px solid #f59e0b; border-radius:7px; font-size:10px; font-weight:850; }
                #severityMedium { color:#60a5fa; background:#132c45; border:1px solid #3b82f6; border-radius:7px; font-size:10px; font-weight:850; }
                #severityLow { color:#4ade80; background:#143423; border:1px solid #22c55e; border-radius:7px; font-size:10px; font-weight:850; }
                #adminRuleToggle { background:#475569; color:#e2e8f0; border:none; border-radius:12px; font-size:9px; font-weight:850; }
                #adminRuleToggle:checked { background:#22c55e; color:#ffffff; }
                #adminDialogNotice { color:#d4dee8; font-size:11px; font-weight:650; }
                #adminDialogPrimaryButton { background:#2563eb; color:#ffffff; border:none; border-radius:7px; font-size:12px; font-weight:850; }
                #adminDialogPrimaryButton:hover { background:#3475f5; }
                QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                QScrollBar::handle:vertical { background:#60758a; min-height:28px; border-radius:4px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background:#f7f9fc; color:#172a3c; }
                #adminDialogTitle { font-size:20px; font-weight:850; color:#142435; }
                #adminDialogSummary { color:#4a5e72; font-size:12px; font-weight:700; }
                #adminDialogClose { background:transparent; border:none; color:#142435; font-size:22px; }
                #adminDialogClose:hover { background:#e9eff5; border-radius:6px; }
                #adminRuleSearch { background:#ffffff; color:#172a3c; border:1px solid #aab9c7; border-radius:7px; padding:0 10px; font-size:12px; }
                #adminRuleTable { background:#ffffff; border:1px solid #b7c5d2; border-radius:7px; }
                #adminRuleHeader { background:#e7eef5; border-bottom:1px solid #aebdcb; }
                #adminRuleHeaderText { color:#243648; font-size:11px; font-weight:850; }
                #adminRuleScroll, #adminRuleContent { background:transparent; border:none; }
                #adminRuleRow { background:#ffffff; border-bottom:1px solid #d3dde6; }
                #adminRuleRow:hover { background:#f2f6fa; }
                #adminRuleCode { color:#1d4ed8; font-size:11px; font-weight:800; }
                #adminRuleName { color:#142435; font-size:11px; font-weight:800; }
                #adminRuleDescription { color:#425466; font-size:11px; font-weight:600; }
                #severityCritical { color:#b42318; background:#fff0f0; border:1px solid #e45858; border-radius:7px; font-size:10px; font-weight:850; }
                #severityHigh { color:#a15c00; background:#fff7e8; border:1px solid #e7a22b; border-radius:7px; font-size:10px; font-weight:850; }
                #severityMedium { color:#1d5fbf; background:#eef5ff; border:1px solid #5b93dd; border-radius:7px; font-size:10px; font-weight:850; }
                #severityLow { color:#18733a; background:#edf9f1; border:1px solid #4dae6c; border-radius:7px; font-size:10px; font-weight:850; }
                #adminRuleToggle { background:#aab6c3; color:#ffffff; border:none; border-radius:12px; font-size:9px; font-weight:850; }
                #adminRuleToggle:checked { background:#20b85f; color:#ffffff; }
                #adminDialogNotice { color:#4a5e72; font-size:11px; font-weight:650; }
                #adminDialogPrimaryButton { background:#2563eb; color:#ffffff; border:none; border-radius:7px; font-size:12px; font-weight:850; }
                #adminDialogPrimaryButton:hover { background:#1d4ed8; }
                QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                QScrollBar::handle:vertical { background:#8998aa; min-height:28px; border-radius:4px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }
            """)
