from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)


class ExistingProjectDialog(QDialog):
    project_selected = Signal(dict)

    def __init__(self, parent=None, projects=None):
        super().__init__(parent)
        self.setWindowTitle("기존 프로젝트 확인")
        self.setModal(True)
        self.setFixedSize(700, 440)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_offset = None

        self.projects = projects or [
            {"name": "AI Auditor Backend", "department": "개발본부", "type": "신규 구축", "date": "2026.08.01"},
            {"name": "AI Auditor Backend", "department": "정보화기획실", "type": "고도화", "date": "2026.07.25"},
            {"name": "AI Auditor Backend", "department": "운영본부", "type": "유지보수", "date": "2026.07.10"},
        ]
        self.radio_group = QButtonGroup(self)
        self.radio_group.setExclusive(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        panel = QFrame()
        panel.setObjectName("existingProjectPanel")
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(9)

        self.header_drag_area = QFrame()
        self.header_drag_area.setObjectName("existingProjectHeaderArea")
        self.header_drag_area.setFixedHeight(34)
        self.header_drag_area.installEventFilter(self)
        header = QHBoxLayout(self.header_drag_area)
        header.setContentsMargins(0, 0, 0, 0)

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

        description = QLabel("동일한 프로젝트명이 존재합니다. 신규 등록 전에 기존 프로젝트인지 확인하세요.")
        description.setObjectName("existingProjectDescription")
        layout.addWidget(description)
        layout.addSpacing(5)

        table_header = QHBoxLayout()
        table_header.setContentsMargins(4, 0, 12, 0)
        table_header.setSpacing(12)
        project_header = QLabel("프로젝트명")
        department_header = QLabel("부서명(기관명)")
        type_header = QLabel("프로젝트 구분")
        date_header = QLabel("최근 검사일")
        for label in (project_header, department_header, type_header, date_header):
            label.setObjectName("existingProjectHeader")
            label.setAlignment(Qt.AlignCenter)
        project_header.setFixedWidth(210)
        department_header.setFixedWidth(140)
        type_header.setFixedWidth(115)
        date_header.setFixedWidth(110)
        table_header.addWidget(project_header)
        table_header.addWidget(department_header)
        table_header.addWidget(type_header)
        table_header.addWidget(date_header)
        table_header.addStretch()
        layout.addLayout(table_header)

        scroll = QScrollArea()
        scroll.setObjectName("existingProjectScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFixedHeight(180)

        list_content = QWidget()
        list_content.setObjectName("existingProjectListContent")
        list_layout = QVBoxLayout(list_content)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(8)
        for index, project in enumerate(self.projects):
            list_layout.addWidget(self.create_project_row(index, project))
        list_layout.addStretch()
        scroll.setWidget(list_content)
        layout.addWidget(scroll)

        layout.addSpacing(3)
        guide1 = QLabel("같은 프로젝트라면 선택 후 기존 프로젝트로 이동하세요.")
        guide1.setObjectName("existingProjectGuide")
        guide2 = QLabel("다른 프로젝트라면 닫고 현재 입력 내용을 그대로 이어서 작성할 수 있습니다.")
        guide2.setObjectName("existingProjectGuideBlue")
        layout.addWidget(guide1)
        layout.addWidget(guide2)
        layout.addSpacing(4)

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
        row.setFixedHeight(54)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(6, 5, 14, 5)
        row_layout.setSpacing(12)

        selector = QPushButton("✓")
        selector.setObjectName("existingProjectSelector")
        selector.setCheckable(True)
        selector.setCursor(Qt.PointingHandCursor)
        selector.setFixedSize(15, 15)
        self.radio_group.addButton(selector, index)

        name = QLabel(project["name"])
        department = QLabel(project["department"])
        project_type = QLabel(project["type"])
        date = QLabel(project["date"])
        for label in (name, department, project_type, date):
            label.setObjectName("existingProjectText")
            label.setAlignment(Qt.AlignCenter)

        selector_cell = QWidget()
        selector_cell.setObjectName("existingProjectSelectorCell")
        selector_layout = QHBoxLayout(selector_cell)
        selector_layout.setContentsMargins(0, 0, 0, 0)
        selector_layout.setSpacing(0)
        selector_layout.addStretch()
        selector_layout.addWidget(selector)
        selector_layout.addSpacing(12)
        selector_layout.addWidget(name)
        selector_layout.addStretch()
        selector_cell.setFixedWidth(210)

        department.setFixedWidth(140)
        project_type.setFixedWidth(115)
        date.setFixedWidth(110)

        row_layout.addWidget(selector_cell)
        row_layout.addWidget(department)
        row_layout.addWidget(project_type)
        row_layout.addWidget(date)
        row_layout.addStretch()
        return row

    def apply_theme(self):
        host = self.parentWidget().window() if self.parentWidget() is not None else None
        is_dark = getattr(host, "is_dark_mode", True)
        if is_dark:
            self.setStyleSheet("""
                #existingProjectPanel { background:#101f2c; border:1px solid #64748b; border-radius:12px; }
                #existingProjectHeaderArea, #existingProjectListContent, #existingProjectSelectorCell { background:transparent; }
                #existingProjectTitle { color:#ffffff; font-size:22px; font-weight:800; }
                #existingProjectClose { color:#ffffff; background:transparent; border:none; font-size:24px; font-weight:650; }
                #existingProjectClose:hover { background:#1d3142; border-radius:6px; }
                #existingProjectDescription { color:#ffffff; font-size:13px; font-weight:650; }
                #existingProjectHeader { color:#d6e0ea; font-size:12px; font-weight:800; }
                #existingProjectRow { background:#142635; border:1px solid #40586c; border-radius:9px; }
                #existingProjectRow:hover { background:#182d3e; border-color:#638099; }
                #existingProjectText { color:#ffffff; font-size:12px; font-weight:700; }
                #existingProjectGuide { color:#ffffff; font-size:12px; font-weight:650; }
                #existingProjectGuideBlue { color:#7fc0ff; font-size:12px; font-weight:700; }
                #existingProjectCancel { color:#ffffff; background:#253b4f; border:1px solid #3a5369; border-radius:8px; font-size:13px; font-weight:750; }
                #existingProjectCancel:hover { background:#30495f; }
                #existingProjectMove { color:#ffffff; background:#2563eb; border:none; border-radius:8px; font-size:13px; font-weight:800; }
                #existingProjectMove:hover { background:#3475f5; }
                #existingProjectScroll { background:transparent; border:none; }
                #existingProjectScroll QWidget { background:transparent; }
                #existingProjectScroll QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                #existingProjectScroll QScrollBar::handle:vertical { background:#60758a; min-height:28px; border-radius:4px; }
                #existingProjectScroll QScrollBar::add-line:vertical, #existingProjectScroll QScrollBar::sub-line:vertical { height:0px; }
                QPushButton#existingProjectSelector {
                    color:transparent; background:transparent;
                    border:1px solid #64748b; border-radius:3px;
                    font-family:'Segoe UI Symbol'; font-size:12px; font-weight:900; padding:0;
                    min-width:15px; max-width:15px; min-height:15px; max-height:15px;
                }
                QPushButton#existingProjectSelector:hover { border:1px solid #3b82f6; }
                QPushButton#existingProjectSelector:checked {
                    color:#ffffff; background:#2563eb;
                    border:1px solid #2563eb;
                }
            """)
        else:
            self.setStyleSheet("""
                #existingProjectPanel { background:#ffffff; border:1px solid #a8b6c7; border-radius:12px; }
                #existingProjectHeaderArea, #existingProjectListContent, #existingProjectSelectorCell { background:transparent; }
                #existingProjectTitle { color:#050b16; font-size:22px; font-weight:800; }
                #existingProjectClose { color:#0f172a; background:transparent; border:none; font-size:24px; font-weight:650; }
                #existingProjectClose:hover { background:#eef2f6; border-radius:6px; }
                #existingProjectDescription { color:#111827; font-size:13px; font-weight:650; }
                #existingProjectHeader { color:#263548; font-size:12px; font-weight:800; }
                #existingProjectRow { background:#ffffff; border:1px solid #bdcad8; border-radius:9px; }
                #existingProjectRow:hover { background:#f8fafc; border-color:#8197ad; }
                #existingProjectText { color:#0b1220; font-size:12px; font-weight:700; }
                #existingProjectGuide { color:#172033; font-size:12px; font-weight:650; }
                #existingProjectGuideBlue { color:#1d4ed8; font-size:12px; font-weight:700; }
                #existingProjectCancel { color:#0f172a; background:#e7edf4; border:1px solid #bdc9d6; border-radius:8px; font-size:13px; font-weight:750; }
                #existingProjectCancel:hover { background:#dce5ee; }
                #existingProjectMove { color:#ffffff; background:#2563eb; border:none; border-radius:8px; font-size:13px; font-weight:800; }
                #existingProjectMove:hover { background:#3475f5; }
                #existingProjectScroll { background:transparent; border:none; }
                #existingProjectScroll QWidget { background:transparent; }
                #existingProjectScroll QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                #existingProjectScroll QScrollBar::handle:vertical { background:#8998aa; min-height:28px; border-radius:4px; }
                #existingProjectScroll QScrollBar::add-line:vertical, #existingProjectScroll QScrollBar::sub-line:vertical { height:0px; }
                QPushButton#existingProjectSelector {
                    color:transparent; background:transparent;
                    border:1px solid #8296aa; border-radius:3px;
                    font-family:'Segoe UI Symbol'; font-size:12px; font-weight:900; padding:0;
                    min-width:15px; max-width:15px; min-height:15px; max-height:15px;
                }
                QPushButton#existingProjectSelector:hover { border:1px solid #3b82f6; }
                QPushButton#existingProjectSelector:checked {
                    color:#ffffff; background:#2563eb;
                    border:1px solid #2563eb;
                }
            """)

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
