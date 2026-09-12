import os

from PySide6.QtCore import QEvent, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)


class InspectionRulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("보안 취약점")
        self.setModal(True)
        self.setFixedSize(720, 500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_offset = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        panel = QFrame()
        panel.setObjectName("rulesDialogPanel")
        outer.addWidget(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(8)

        self.header_drag_area = QFrame()
        self.header_drag_area.setObjectName("rulesDialogHeaderArea")
        self.header_drag_area.setFixedHeight(34)
        self.header_drag_area.installEventFilter(self)
        header = QHBoxLayout(self.header_drag_area)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        icon = QLabel()
        icon.setObjectName("rulesDialogShieldIcon")
        icon.setPixmap(QIcon(os.path.join(icon_dir, "detail_grade.svg")).pixmap(QSize(18, 18)))
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(26, 26)
        icon.installEventFilter(self)
        title = QLabel("보안 취약점")
        title.setObjectName("rulesDialogTitle")
        title.installEventFilter(self)
        count = QLabel("32개 항목")
        count.setObjectName("rulesDialogCount")
        count.installEventFilter(self)
        close_button = QPushButton("×")
        close_button.setObjectName("rulesDialogClose")
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        header.addWidget(icon)
        header.addWidget(title)
        header.addWidget(count)
        header.addStretch()
        header.addWidget(close_button)
        layout.addWidget(self.header_drag_area)

        description = QLabel("적용할 항목을 선택하거나 제외할 수 있습니다.")
        description.setObjectName("rulesDialogDescription")
        layout.addWidget(description)
        note = QLabel("※ 변경 사항은 이번 검사에만 적용됩니다.")
        note.setObjectName("rulesDialogNote")
        layout.addWidget(note)

        select_row = QHBoxLayout()
        select_row.setSpacing(8)
        select_row.addStretch()
        select_all = QPushButton("전체 선택")
        select_all.setObjectName("rulesDialogSmallButton")
        select_all.setFixedSize(88, 32)
        select_all.setCursor(Qt.PointingHandCursor)
        select_all.clicked.connect(lambda: self.set_all_checked(True))
        clear_all = QPushButton("전체 해제")
        clear_all.setObjectName("rulesDialogSmallButton")
        clear_all.setFixedSize(88, 32)
        clear_all.setCursor(Qt.PointingHandCursor)
        clear_all.clicked.connect(lambda: self.set_all_checked(False))
        select_row.addWidget(select_all)
        select_row.addWidget(clear_all)
        layout.addLayout(select_row)

        table = QFrame()
        table.setObjectName("rulesTable")
        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_header = QFrame()
        table_header.setObjectName("rulesTableHeader")
        table_header.setFixedHeight(34)
        header_layout = QHBoxLayout(table_header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(8)
        check_header = QLabel("")
        check_header.setFixedWidth(22)
        h1, h2, h3 = QLabel("항목명"), QLabel("설명"), QLabel("상태")
        for label in (h1, h2, h3):
            label.setObjectName("rulesTableHeaderText")
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        h1.setFixedWidth(215)
        h3.setFixedWidth(58)
        header_layout.addWidget(check_header)
        header_layout.addWidget(h1)
        header_layout.addWidget(h2, 1)
        header_layout.addWidget(h3)
        table_layout.addWidget(table_header)

        scroll = QScrollArea()
        scroll.setObjectName("rulesTableScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFixedHeight(270)
        list_content = QWidget()
        list_content.setObjectName("rulesListContent")
        list_layout = QVBoxLayout(list_content)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        self.rule_checkboxes = []
        self.state_labels = []
        rules = [
            ("SQL Injection", "사용자 입력값에 대한 SQL 삽입 취약점 검사", True),
            ("Cross Site Scripting (XSS)", "웹 페이지 내 스크립트 삽입 취약점 검사", True),
            ("Cross Site Request Forgery (CSRF)", "요청 위조 공격 가능성 검사", False),
            ("Hard Coding (민감정보)", "소스코드 내 하드코딩된 민감정보 검사", True),
            ("Weak Password Usage", "약한 암호 사용 여부 검사", False),
            ("Insufficient Authentication", "인증 로직 부재 또는 우회 가능성 검사", True),
            ("Broken Access Control", "접근 권한 검증 누락 검사", True),
            ("Sensitive Data Exposure", "민감 데이터 노출 가능성 검사", True),
        ]
        for name, desc, checked in rules:
            row = QFrame()
            row.setObjectName("rulesTableRow")
            row.setFixedHeight(36)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 0, 12, 0)
            row_layout.setSpacing(8)
            checkbox = QCheckBox()
            checkbox.setObjectName("rulesCheckbox")
            checkbox.setChecked(checked)
            checkbox.setCursor(Qt.PointingHandCursor)
            checkbox.setFixedWidth(22)
            self.rule_checkboxes.append(checkbox)
            name_label = QLabel(name)
            name_label.setObjectName("rulesRowText")
            name_label.setFixedWidth(215)
            name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            desc_label = QLabel(desc)
            desc_label.setObjectName("rulesRowDescription")
            desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            state_label = QLabel("활성" if checked else "비활성")
            state_label.setObjectName("rulesRowState")
            state_label.setFixedWidth(58)
            state_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.state_labels.append(state_label)
            checkbox.stateChanged.connect(lambda state, label=state_label: label.setText("활성" if state == Qt.Checked.value else "비활성"))
            checkbox.stateChanged.connect(self.update_selected_count)
            row_layout.addWidget(checkbox)
            row_layout.addWidget(name_label)
            row_layout.addWidget(desc_label, 1)
            row_layout.addWidget(state_label)
            list_layout.addWidget(row)
        list_layout.addStretch()
        scroll.setWidget(list_content)
        table_layout.addWidget(scroll)
        layout.addWidget(table)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        self.selected_count = QLabel()
        self.selected_count.setObjectName("rulesSelectedCount")
        self.update_selected_count()
        cancel = QPushButton("취소")
        cancel.setObjectName("rulesCancelButton")
        cancel.setFixedSize(96, 32)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        confirm = QPushButton("확인")
        confirm.setObjectName("rulesConfirmButton")
        confirm.setFixedSize(96, 32)
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.clicked.connect(self.accept)
        bottom.addWidget(self.selected_count)
        bottom.addStretch()
        bottom.addWidget(cancel)
        bottom.addWidget(confirm)
        layout.addLayout(bottom)
        self.apply_theme()

    def set_all_checked(self, checked):
        for checkbox in self.rule_checkboxes:
            checkbox.setChecked(checked)

    def update_selected_count(self):
        selected = sum(1 for checkbox in self.rule_checkboxes if checkbox.isChecked())
        display_count = max(0, 32 - (len(self.rule_checkboxes) - selected))
        self.selected_count.setText(f"선택됨 {display_count} / 32 항목")

    def eventFilter(self, watched, event):
        draggable = watched is self.header_drag_area or watched.objectName() in {"rulesDialogShieldIcon", "rulesDialogTitle", "rulesDialogCount"}
        if draggable:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            if event.type() == QEvent.MouseMove and self._drag_offset is not None and event.buttons() & Qt.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                return True
            if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._drag_offset = None
                return True
        return super().eventFilter(watched, event)

    def apply_theme(self):
        host = self.parentWidget().window() if self.parentWidget() is not None else None
        is_dark = getattr(host, "is_dark_mode", True)
        if is_dark:
            self.setStyleSheet("""
                #rulesDialogPanel { background:#101f2c; border:1px solid #64748b; border-radius:12px; }
                #rulesDialogHeaderArea, #rulesListContent { background:transparent; }
                #rulesDialogShieldIcon { background:transparent; border:none; }
                #rulesDialogTitle { color:#ffffff; font-size:20px; font-weight:800; }
                #rulesDialogCount { color:#b8c5d4; font-size:12px; font-weight:700; }
                #rulesDialogClose { color:#ffffff; background:transparent; border:none; font-size:24px; font-weight:650; }
                #rulesDialogClose:hover { background:#1d3142; border-radius:6px; }
                #rulesDialogDescription { color:#f1f5f9; font-size:12px; font-weight:650; }
                #rulesDialogNote { color:#60a5fa; font-size:11px; font-weight:750; }
                #rulesDialogSmallButton, #rulesCancelButton { color:#ffffff; background:#253b4f; border:1px solid #476079; border-radius:7px; font-size:12px; font-weight:750; }
                #rulesDialogSmallButton:hover, #rulesCancelButton:hover { background:#30495f; }
                #rulesConfirmButton { color:#ffffff; background:#2563eb; border:none; border-radius:7px; font-size:12px; font-weight:850; }
                #rulesConfirmButton:hover { background:#3475f5; }
                #rulesTable { background:#0d1721; border:1px solid #40586c; border-radius:8px; }
                #rulesTableHeader { background:#17293a; border-bottom:1px solid #40586c; }
                #rulesTableHeaderText { color:#d9e3ee; font-size:11px; font-weight:800; }
                #rulesTableRow { background:#0d1721; border-bottom:1px solid #293d50; }
                #rulesTableRow:hover { background:#142536; }
                #rulesRowText { color:#ffffff; font-size:11px; font-weight:750; }
                #rulesRowDescription { color:#d7e0e9; font-size:11px; font-weight:600; }
                #rulesRowState { color:#ffffff; font-size:11px; font-weight:750; }
                #rulesSelectedCount { color:#ffffff; font-size:12px; font-weight:800; }
                #rulesTableScroll { background:transparent; border:none; }
                #rulesTableScroll QWidget { background:transparent; }
                #rulesTableScroll QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                #rulesTableScroll QScrollBar::handle:vertical { background:#60758a; min-height:28px; border-radius:4px; }
                #rulesTableScroll QScrollBar::add-line:vertical, #rulesTableScroll QScrollBar::sub-line:vertical { height:0px; }
                QCheckBox#rulesCheckbox { background:transparent; spacing:0px; }
                QCheckBox#rulesCheckbox::indicator { width:18px; height:18px; }
                QCheckBox#rulesCheckbox::indicator:unchecked { background:#0d1721; border:1px solid #64748b; border-radius:4px; }
                QCheckBox#rulesCheckbox::indicator:checked { background:#0878f9; border:1px solid #3194ff; border-radius:4px; }
            """)
        else:
            self.setStyleSheet("""
                #rulesDialogPanel { background:#ffffff; border:1px solid #a8b6c7; border-radius:12px; }
                #rulesDialogHeaderArea, #rulesListContent { background:transparent; }
                #rulesDialogShieldIcon { background:transparent; border:none; }
                #rulesDialogTitle { color:#050b16; font-size:20px; font-weight:800; }
                #rulesDialogCount { color:#475569; font-size:12px; font-weight:700; }
                #rulesDialogClose { color:#0f172a; background:transparent; border:none; font-size:24px; font-weight:650; }
                #rulesDialogClose:hover { background:#eef2f6; border-radius:6px; }
                #rulesDialogDescription { color:#111827; font-size:12px; font-weight:650; }
                #rulesDialogNote { color:#1d4ed8; font-size:11px; font-weight:750; }
                #rulesDialogSmallButton, #rulesCancelButton { color:#0f172a; background:#e7edf4; border:1px solid #bdc9d6; border-radius:7px; font-size:12px; font-weight:750; }
                #rulesDialogSmallButton:hover, #rulesCancelButton:hover { background:#dce5ee; }
                #rulesConfirmButton { color:#ffffff; background:#2563eb; border:none; border-radius:7px; font-size:12px; font-weight:850; }
                #rulesConfirmButton:hover { background:#1d4ed8; }
                #rulesTable { background:#ffffff; border:1px solid #b9c6d5; border-radius:8px; }
                #rulesTableHeader { background:#eef3f8; border-bottom:1px solid #b9c6d5; }
                #rulesTableHeaderText { color:#263548; font-size:11px; font-weight:800; }
                #rulesTableRow { background:#ffffff; border-bottom:1px solid #d9e1ea; }
                #rulesTableRow:hover { background:#f6f9fc; }
                #rulesRowText { color:#0b1220; font-size:11px; font-weight:750; }
                #rulesRowDescription { color:#334155; font-size:11px; font-weight:600; }
                #rulesRowState { color:#0f172a; font-size:11px; font-weight:750; }
                #rulesSelectedCount { color:#0f172a; font-size:12px; font-weight:800; }
                #rulesTableScroll { background:transparent; border:none; }
                #rulesTableScroll QWidget { background:transparent; }
                #rulesTableScroll QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                #rulesTableScroll QScrollBar::handle:vertical { background:#8998aa; min-height:28px; border-radius:4px; }
                #rulesTableScroll QScrollBar::add-line:vertical, #rulesTableScroll QScrollBar::sub-line:vertical { height:0px; }
                QCheckBox#rulesCheckbox { background:transparent; spacing:0px; }
                QCheckBox#rulesCheckbox::indicator { width:18px; height:18px; }
                QCheckBox#rulesCheckbox::indicator:unchecked { background:#ffffff; border:1px solid #8296aa; border-radius:4px; }
                QCheckBox#rulesCheckbox::indicator:checked { background:#0878f9; border:1px solid #2563eb; border-radius:4px; }
            """)