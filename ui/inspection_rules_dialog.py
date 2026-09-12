from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class InspectionRulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("보안 취약점")
        self.setModal(True)
        self.setFixedSize(700, 470)

        self.setWindowFlags(
            Qt.Dialog | Qt.FramelessWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("rulesDialogPanel")
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(9)

        # ==================================================
        # Header
        # ==================================================
        header = QHBoxLayout()

        title = QLabel("♢  보안 취약점")
        title.setObjectName("rulesDialogTitle")

        count = QLabel("(32개 항목)")
        count.setObjectName("rulesDialogCount")

        close_button = QPushButton("×")
        close_button.setObjectName("rulesDialogClose")
        close_button.setFixedSize(28, 28)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)

        header.addWidget(title)
        header.addWidget(count)
        header.addStretch()
        header.addWidget(close_button)

        layout.addLayout(header)

        description = QLabel(
            "적용할 항목을 선택하거나 제외할 수 있습니다."
        )
        description.setObjectName("rulesDialogDescription")
        layout.addWidget(description)

        note = QLabel(
            "※ 변경 사항은 이번 검사에만 적용됩니다."
        )
        note.setObjectName("rulesDialogNote")
        layout.addWidget(note)

        # ==================================================
        # 전체 선택 / 해제
        # ==================================================
        select_row = QHBoxLayout()
        select_row.addStretch()

        select_all = QPushButton("전체 선택")
        select_all.setObjectName("rulesDialogSmallButton")
        select_all.setFixedSize(84, 30)
        select_all.clicked.connect(
            lambda: self.set_all_checked(True)
        )

        clear_all = QPushButton("전체 해제")
        clear_all.setObjectName("rulesDialogSmallButton")
        clear_all.setFixedSize(84, 30)
        clear_all.clicked.connect(
            lambda: self.set_all_checked(False)
        )

        select_row.addWidget(select_all)
        select_row.addWidget(clear_all)

        layout.addLayout(select_row)

        # ==================================================
        # 테이블 Header
        # ==================================================
        table = QFrame()
        table.setObjectName("rulesTable")

        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        table_header = QFrame()
        table_header.setObjectName("rulesTableHeader")

        header_layout = QHBoxLayout(table_header)
        header_layout.setContentsMargins(12, 7, 12, 7)

        h1 = QLabel("항목명")
        h2 = QLabel("설명")
        h3 = QLabel("기본 상태")

        for label in (h1, h2, h3):
            label.setObjectName("rulesTableHeaderText")

        h1.setFixedWidth(245)
        h3.setFixedWidth(70)

        header_layout.addWidget(h1)
        header_layout.addWidget(h2, 1)
        header_layout.addWidget(h3)

        table_layout.addWidget(table_header)

        self.rule_checkboxes = []

        rules = [
            (
                "SQL Injection",
                "사용자 입력값에 대한 SQL 삽입 취약점 검사",
                True,
            ),
            (
                "Cross Site Scripting (XSS)",
                "웹 페이지 내 스크립트 삽입 취약점 검사",
                True,
            ),
            (
                "Cross Site Request Forgery (CSRF)",
                "요청 위조 공격 가능성 검사",
                False,
            ),
            (
                "Hard Coding (민감정보)",
                "소스코드 내 하드코딩된 민감정보 검사",
                True,
            ),
            (
                "Weak Password Usage",
                "약한 암호 사용 여부 검사",
                False,
            ),
            (
                "Insufficient Authentication",
                "인증 로직 부재 또는 우회 가능성 검사",
                True,
            ),
            (
                "Broken Access Control",
                "접근 권한 검증 누락 검사",
                True,
            ),
            (
                "Sensitive Data Exposure",
                "민감 데이터 노출 가능성 검사",
                True,
            ),
        ]

        for name, desc, checked in rules:
            row = QFrame()
            row.setObjectName("rulesTableRow")
            row.setFixedHeight(34)

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 3, 12, 3)
            row_layout.setSpacing(8)

            checkbox = QCheckBox()
            checkbox.setChecked(checked)
            self.rule_checkboxes.append(checkbox)

            name_label = QLabel(name)
            name_label.setObjectName("rulesRowText")
            name_label.setFixedWidth(215)

            desc_label = QLabel(desc)
            desc_label.setObjectName("rulesRowDescription")

            state_label = QLabel(
                "활성" if checked else "비활성"
            )
            state_label.setObjectName("rulesRowState")
            state_label.setFixedWidth(70)

            row_layout.addWidget(checkbox)
            row_layout.addWidget(name_label)
            row_layout.addWidget(desc_label, 1)
            row_layout.addWidget(state_label)

            table_layout.addWidget(row)

        layout.addWidget(table)

        # ==================================================
        # 하단
        # ==================================================
        bottom = QHBoxLayout()

        self.selected_count = QLabel()
        self.selected_count.setObjectName("rulesSelectedCount")
        self.update_selected_count()

        for checkbox in self.rule_checkboxes:
            checkbox.stateChanged.connect(
                self.update_selected_count
            )

        cancel = QPushButton("취소")
        cancel.setObjectName("rulesCancelButton")
        cancel.setFixedSize(88, 38)
        cancel.clicked.connect(self.reject)

        confirm = QPushButton("확인")
        confirm.setObjectName("rulesConfirmButton")
        confirm.setFixedSize(88, 38)
        confirm.clicked.connect(self.accept)

        bottom.addWidget(self.selected_count)
        bottom.addStretch()
        bottom.addWidget(cancel)
        bottom.addWidget(confirm)

        layout.addLayout(bottom)

        self.setStyleSheet(
            """
            #rulesDialogPanel {
                background: #101f2c;
                border: 1px solid #64748b;
                border-radius: 12px;
            }

            #rulesDialogTitle {
                color: #f8fafc;
                font-size: 17px;
                font-weight: 700;
            }

            #rulesDialogCount {
                color: #94a3b8;
                font-size: 11px;
            }

            #rulesDialogClose {
                color: #e2e8f0;
                background: transparent;
                border: none;
                font-size: 23px;
            }

            #rulesDialogDescription {
                color: #cbd5e1;
                font-size: 11px;
            }

            #rulesDialogNote {
                color: #3b82f6;
                font-size: 9px;
            }

            #rulesDialogSmallButton,
            #rulesCancelButton {
                color: #e2e8f0;
                background: #172431;
                border: 1px solid #33475a;
                border-radius: 6px;
                font-size: 10px;
            }

            #rulesConfirmButton {
                color: white;
                background: #0866f5;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
            }

            #rulesTable {
                background: #101a25;
                border: 1px solid #26394b;
                border-radius: 7px;
            }

            #rulesTableHeader {
                background: #172431;
                border-bottom: 1px solid #26394b;
            }

            #rulesTableHeaderText {
                color: #aebaca;
                font-size: 9px;
            }

            #rulesTableRow {
                background: transparent;
                border-bottom: 1px solid #223140;
            }

            #rulesRowText {
                color: #e5e7eb;
                font-size: 9px;
            }

            #rulesRowDescription {
                color: #aebaca;
                font-size: 9px;
            }

            #rulesRowState {
                color: #cbd5e1;
                font-size: 9px;
            }

            #rulesSelectedCount {
                color: #e5e7eb;
                font-size: 11px;
                font-weight: 600;
            }

            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }

            QCheckBox::indicator:unchecked {
                background: #0c1721;
                border: 1px solid #64748b;
                border-radius: 3px;
            }

            QCheckBox::indicator:checked {
                background: #0866f5;
                border: 1px solid #3b82f6;
                border-radius: 3px;
            }
            """
        )

    def set_all_checked(self, checked):
        for checkbox in self.rule_checkboxes:
            checkbox.setChecked(checked)

    def update_selected_count(self):
        selected = sum(
            1 for checkbox in self.rule_checkboxes
            if checkbox.isChecked()
        )

        # 현재 샘플 화면에는 8개 규칙만 표시하지만,
        # 원본 카테고리의 전체 규칙 수(32개)를 기준으로 표시한다.
        display_count = max(
            0,
            32 - (len(self.rule_checkboxes) - selected)
        )
        self.selected_count.setText(
            f"선택됨 {display_count} / 32 항목"
        )
