from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox,
)


class AdministrationRulesDialog(QDialog):
    def __init__(self, category_name, total, active, inactive, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{category_name} - 규칙 목록")
        self.setModal(True)
        self.setFixedSize(700, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel(f"{category_name} - 규칙 목록")
        title.setObjectName("adminDialogTitle")
        close_button = QPushButton("×")
        close_button.setObjectName("adminDialogClose")
        close_button.setFixedSize(32, 32)
        close_button.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        summary = QLabel(f"총 {total}개 규칙   |   활성 {active}개   |   비활성 {inactive}개")
        summary.setObjectName("adminDialogSummary")
        layout.addWidget(summary)

        search = QLineEdit()
        search.setPlaceholderText("규칙 코드 또는 제목 검색")
        search.setObjectName("adminRuleSearch")
        search.setFixedHeight(34)
        layout.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
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

        prefix = "SEC" if "보안" in category_name else "RULE"
        for code, name, description, severity, checked in sample_rules:
            row = QFrame()
            row.setObjectName("adminRuleRow")
            row.setFixedHeight(62)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 6, 10, 6)
            row_layout.setSpacing(10)

            code_label = QLabel(f"{prefix}-{code}")
            code_label.setFixedWidth(72)
            name_label = QLabel(name)
            name_label.setFixedWidth(130)
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            severity_label = QLabel(severity)
            severity_label.setFixedWidth(62)
            toggle = QCheckBox("ON" if checked else "OFF")
            toggle.setChecked(checked)
            toggle.setFixedWidth(54)
            toggle.stateChanged.connect(
                lambda state, control=toggle: control.setText("ON" if state == Qt.Checked.value else "OFF")
            )

            row_layout.addWidget(code_label)
            row_layout.addWidget(name_label)
            row_layout.addWidget(desc_label, 1)
            row_layout.addWidget(severity_label)
            row_layout.addWidget(toggle)
            rows.addWidget(row)

        rows.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        footer = QHBoxLayout()
        notice = QLabel("ⓘ 규칙을 비활성화하면 기본 검사에서 제외됩니다.")
        close = QPushButton("닫기")
        close.setFixedSize(88, 34)
        close.clicked.connect(self.accept)
        footer.addWidget(notice)
        footer.addStretch()
        footer.addWidget(close)
        layout.addLayout(footer)

        self.setStyleSheet("""
            QDialog { background:#101820; color:#f8fafc; }
            #adminDialogTitle { font-size:18px; font-weight:800; color:#ffffff; }
            #adminDialogSummary { color:#cbd5e1; font-size:12px; }
            #adminDialogClose { background:transparent; border:none; color:#ffffff; font-size:22px; }
            #adminRuleSearch { background:#111c26; color:#ffffff; border:1px solid #334155; border-radius:7px; padding:0 10px; }
            #adminRuleRow { background:#0d1721; border-bottom:1px solid #263747; }
            QPushButton { background:#1d4ed8; color:#ffffff; border:none; border-radius:7px; font-weight:700; }
            QCheckBox { color:#ffffff; }
        """)
