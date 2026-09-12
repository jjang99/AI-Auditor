from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ExistingProjectDialog(QDialog):
    project_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("기존 프로젝트 확인")
        self.setModal(True)
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._drag_offset = None

        self.projects = [
            {"name": "AI Auditor Backend", "department": "개발본부", "type": "신규 구축", "date": "2026.08.01"},
            {"name": "AI Auditor Backend", "department": "정보화기획실", "type": "고도화", "date": "2026.07.25"},
            {"name": "AI Auditor Backend", "department": "운영본부", "type": "유지보수", "date": "2026.07.10"},
        ]

        self.radio_group = QButtonGroup(self)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("existingProjectPanel")
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(11)

        # Header / drag area
        self.header_drag_area = QFrame()
        self.header_drag_area.setObjectName("existingProjectHeaderArea")
        self.header_drag_area.setFixedHeight(34)
        self.header_drag_area.installEventFilter(self)

        header = QHBoxLayout(self.header_drag_area)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel("기존 프로젝트 확인")
        title.setObjectName("existingProjectTitle")
        title.installEventFilter(self)

        close_button = QPushButton("×")
        close_button.setObjectName("existingProjectClose")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addWidget(self.header_drag_area)

        description = QLabel(
            "동일한 프로젝트명이 존재합니다. 신규 등록 전에 기존 프로젝트인지 확인하세요."
        )
        description.setObjectName("existingProjectDescription")
        layout.addWidget(description)
        layout.addSpacing(7)

        # Column header
        table_header = QHBoxLayout()
        table_header.setContentsMargins(12, 0, 12, 0)
        table_header.setSpacing(8)

        project_header = QLabel("프로젝트명")
        department_header = QLabel("부서명(기관명)")
        type_header = QLabel("프로젝트 구분")
        date_header = QLabel("최근 검사일")

        for label in (project_header, department_header, type_header, date_header):
            label.setObjectName("existingProjectHeader")

        project_header.setFixedWidth(220)
        department_header.setFixedWidth(150)
        type_header.setFixedWidth(122)

        table_header.addWidget(project_header)
        table_header.addWidget(department_header)
        table_header.addWidget(type_header)
        table_header.addWidget(date_header, 1)
        layout.addLayout(table_header)

        # Only the project list scrolls when the result set grows.
        scroll = QScrollArea()
        scroll.setObjectName("existingProjectScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFixedHeight(190)

        list_content = QWidget()
        list_content.setObjectName("existingProjectListContent")
        list_layout = QVBoxLayout(list_content)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(10)

        for index, project in enumerate(self.projects):
            list_layout.addWidget(self.create_project_row(index, project))

        list_layout.addStretch()
        scroll.setWidget(list_content)
        layout.addWidget(scroll)

        layout.addStretch()

        guide1 = QLabel("같은 프로젝트라면 선택 후 기존 프로젝트로 이동하세요.")
        guide1.setObjectName("existingProjectGuide")

        guide2 = QLabel(
            "다른 프로젝트라면 닫고 현재 입력 내용을 그대로 이어서 작성할 수 있습니다."
        )
        guide2.setObjectName("existingProjectGuideBlue")

        layout.addWidget(guide1)
        layout.addWidget(guide2)
        layout.addSpacing(5)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addStretch()

        close = QPushButton("닫기")
        close.setObjectName("existingProjectCancel")
        close.setCursor(Qt.PointingHandCursor)
        close.setFixedSize(130, 42)
        close.clicked.connect(self.reject)

        move = QPushButton("기존 프로젝트로 이동")
        move.setObjectName("existingProjectMove")
        move.setCursor(Qt.PointingHandCursor)
        move.setFixedSize(170, 42)
        move.clicked.connect(self.move_to_project)

        button_row.addWidget(close)
        button_row.addWidget(move)
        layout.addLayout(button_row)

        first_button = self.radio_group.button(0)
        if first_button:
            first_button.setChecked(True)

        self.apply_theme()

    def create_project_row(self, index, project):
        row = QFrame()
        row.setObjectName("existingProjectRow")
        row.setFixedHeight(56)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(14, 5, 14, 5)
        row_layout.setSpacing(10)

        radio = QRadioButton()
        radio.setCursor(Qt.PointingHandCursor)
        self.radio_group.addButton(radio, index)

        name = QLabel(project["name"])
        department = QLabel(project["department"])
        project_type = QLabel(project["type"])
        date = QLabel(project["date"])

        for label in (name, department, project_type, date):
            label.setObjectName("existingProjectText")
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        name.setFixedWidth(178)
        department.setFixedWidth(150)
        project_type.setFixedWidth(122)

        row_layout.addWidget(radio)
        row_layout.addWidget(name)
        row_layout.addWidget(department)
        row_layout.addWidget(project_type)
        row_layout.addWidget(date, 1)
        return row

    def apply_theme(self):
        host = self.parentWidget().window() if self.parentWidget() is not None else None
        is_dark = getattr(host, "is_dark_mode", True)

        if is_dark:
            self.setStyleSheet(
                """
                #existingProjectPanel { background:#101f2c; border:1px solid #64748b; border-radius:12px; }
                #existingProjectHeaderArea, #existingProjectListContent { background:transparent; }
                #existingProjectTitle { color:#f8fafc; font-size:22px; font-weight:800; }
                #existingProjectClose { color:#e2e8f0; background:transparent; border:none; font-size:24px; font-weight:500; }
                #existingProjectClose:hover { color:#ffffff; }
                #existingProjectDescription { color:#d4dde7; font-size:12px; font-weight:500; }
                #existingProjectHeader { color:#aab7c7; font-size:11px; font-weight:650; }
                #existingProjectRow { background:#162837; border:1px solid #365064; border-radius:8px; }
                #existingProjectRow:hover { border-color:#52718a; }
                #existingProjectText { color:#edf2f7; font-size:11px; font-weight:550; }
                #existingProjectGuide { color:#b7c2cf; font-size:11px; font-weight:500; }
                #existingProjectGuideBlue { color:#6fb2ff; font-size:11px; font-weight:550; }
                #existingProjectCancel { color:#f1f5f9; background:#223548; border:1px solid #2e4357; border-radius:7px; font-size:12px; font-weight:650; }
                #existingProjectCancel:hover { background:#2b4155; }
                #existingProjectMove { color:#ffffff; background:#2563eb; border:none; border-radius:7px; font-size:12px; font-weight:700; }
                #existingProjectMove:hover { background:#3171f2; }
                #existingProjectScroll { background:transparent; border:none; }
                #existingProjectScroll QWidget { background:transparent; }
                #existingProjectScroll QScrollBar:vertical { background:#0d1721; width:9px; margin:2px; }
                #existingProjectScroll QScrollBar::handle:vertical { background:#60758a; min-height:28px; border-radius:4px; }
                #existingProjectScroll QScrollBar::add-line:vertical, #existingProjectScroll QScrollBar::sub-line:vertical { height:0px; }
                QRadioButton { spacing:8px; }
                QRadioButton::indicator { width:17px; height:17px; }
                QRadioButton::indicator:unchecked { background:transparent; border:1px solid #82a7c5; border-radius:8px; }
                QRadioButton::indicator:checked { background:#2563eb; border:3px solid #8bc1e8; border-radius:8px; }
                """
            )
        else:
            self.setStyleSheet(
                """
                #existingProjectPanel { background:#ffffff; border:1px solid #a8b6c7; border-radius:12px; }
                #existingProjectHeaderArea, #existingProjectListContent { background:transparent; }
                #existingProjectTitle { color:#0b1220; font-size:22px; font-weight:800; }
                #existingProjectClose { color:#334155; background:transparent; border:none; font-size:24px; font-weight:500; }
                #existingProjectClose:hover { color:#0b1220; }
                #existingProjectDescription { color:#334155; font-size:12px; font-weight:550; }
                #existingProjectHeader { color:#526174; font-size:11px; font-weight:700; }
                #existingProjectRow { background:#f8fafc; border:1px solid #c4cfdb; border-radius:8px; }
                #existingProjectRow:hover { border-color:#8ca0b5; }
                #existingProjectText { color:#162033; font-size:11px; font-weight:600; }
                #existingProjectGuide { color:#475569; font-size:11px; font-weight:550; }
                #existingProjectGuideBlue { color:#1d4ed8; font-size:11px; font-weight:600; }
                #existingProjectCancel { color:#172033; background:#e8edf3; border:1px solid #c5cfda; border-radius:7px; font-size:12px; font-weight:650; }
                #existingProjectCancel:hover { background:#dde5ee; }
                #existingProjectMove { color:#ffffff; background:#2563eb; border:none; border-radius:7px; font-size:12px; font-weight:700; }
                #existingProjectMove:hover { background:#3171f2; }
                #existingProjectScroll { background:transparent; border:none; }
                #existingProjectScroll QWidget { background:transparent; }
                #existingProjectScroll QScrollBar:vertical { background:#edf1f5; width:9px; margin:2px; }
                #existingProjectScroll QScrollBar::handle:vertical { background:#8998aa; min-height:28px; border-radius:4px; }
                #existingProjectScroll QScrollBar::add-line:vertical, #existingProjectScroll QScrollBar::sub-line:vertical { height:0px; }
                QRadioButton { spacing:8px; }
                QRadioButton::indicator { width:17px; height:17px; }
                QRadioButton::indicator:unchecked { background:#ffffff; border:1px solid #7891aa; border-radius:8px; }
                QRadioButton::indicator:checked { background:#2563eb; border:3px solid #93c5fd; border-radius:8px; }
                """
            )

    def eventFilter(self, watched, event):
        if watched in (self.header_drag_area, self.header_drag_area.findChild(QLabel, "existingProjectTitle")):
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

    def move_to_project(self):
        selected_id = self.radio_group.checkedId()
        if selected_id < 0:
            return

        project = self.projects[selected_id]
        self.project_selected.emit(project)
        self.accept()
