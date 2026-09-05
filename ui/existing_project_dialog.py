from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class ExistingProjectDialog(QDialog):
    project_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("기존 프로젝트 확인")
        self.setModal(True)
        self.setFixedSize(650, 455)

        self.setWindowFlags(
            Qt.Dialog | Qt.FramelessWindowHint
        )
        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.projects = [
            {
                "name": "AI Auditor Backend",
                "department": "개발본부",
                "type": "신규 구축",
                "date": "2026.08.01",
            },
            {
                "name": "AI Auditor Backend",
                "department": "정보화기획실",
                "type": "고도화",
                "date": "2026.07.25",
            },
            {
                "name": "AI Auditor Backend",
                "department": "운영본부",
                "type": "유지보수",
                "date": "2026.07.10",
            },
        ]

        self.radio_group = QButtonGroup(self)

        # ==================================================
        # 전체 배경
        # ==================================================
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("existingProjectPanel")

        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            24, 20, 24, 20
        )
        layout.setSpacing(10)

        # ==================================================
        # Header
        # ==================================================
        header = QHBoxLayout()

        title = QLabel("기존 프로젝트 확인")
        title.setObjectName(
            "existingProjectTitle"
        )

        close_button = QPushButton("×")
        close_button.setObjectName(
            "existingProjectClose"
        )
        close_button.setCursor(
            Qt.PointingHandCursor
        )
        close_button.setFixedSize(28, 28)
        close_button.clicked.connect(
            self.reject
        )

        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)

        layout.addLayout(header)

        description = QLabel(
            "동일한 프로젝트명이 존재합니다. "
            "신규 등록 전에 기존 프로젝트인지 확인하세요."
        )
        description.setObjectName(
            "existingProjectDescription"
        )

        layout.addWidget(description)

        layout.addSpacing(8)

        # ==================================================
        # 목록 Header
        # ==================================================
        table_header = QHBoxLayout()
        table_header.setContentsMargins(
            10, 0, 10, 0
        )

        project_header = QLabel("프로젝트명")
        department_header = QLabel(
            "부서명(기관명)"
        )
        type_header = QLabel("프로젝트 구분")
        date_header = QLabel("최근 검사일")

        headers = [
            project_header,
            department_header,
            type_header,
            date_header,
        ]

        for label in headers:
            label.setObjectName(
                "existingProjectHeader"
            )

        project_header.setFixedWidth(205)
        department_header.setFixedWidth(145)
        type_header.setFixedWidth(120)

        table_header.addWidget(
            project_header
        )
        table_header.addWidget(
            department_header
        )
        table_header.addWidget(type_header)
        table_header.addWidget(
            date_header
        )

        layout.addLayout(table_header)

        # ==================================================
        # 프로젝트 목록
        # ==================================================
        for index, project in enumerate(
            self.projects
        ):
            row = self.create_project_row(
                index,
                project,
            )
            layout.addWidget(row)

        layout.addStretch()

        # ==================================================
        # 안내
        # ==================================================
        guide1 = QLabel(
            "같은 프로젝트라면 선택 후 "
            "기존 프로젝트로 이동하세요."
        )
        guide1.setObjectName(
            "existingProjectGuide"
        )

        guide2 = QLabel(
            "다른 프로젝트라면 닫고 현재 입력 내용을 "
            "그대로 이어서 작성할 수 있습니다."
        )
        guide2.setObjectName(
            "existingProjectGuideBlue"
        )

        layout.addWidget(guide1)
        layout.addWidget(guide2)

        layout.addSpacing(6)

        # ==================================================
        # 버튼
        # ==================================================
        button_row = QHBoxLayout()
        button_row.addStretch()

        close = QPushButton("닫기")
        close.setObjectName(
            "existingProjectCancel"
        )
        close.setCursor(
            Qt.PointingHandCursor
        )
        close.setFixedSize(120, 40)
        close.clicked.connect(
            self.reject
        )

        move = QPushButton(
            "기존 프로젝트로 이동"
        )
        move.setObjectName(
            "existingProjectMove"
        )
        move.setCursor(
            Qt.PointingHandCursor
        )
        move.setFixedSize(150, 40)
        move.clicked.connect(
            self.move_to_project
        )

        button_row.addWidget(close)
        button_row.addWidget(move)

        layout.addLayout(button_row)

        # 첫 번째 프로젝트 기본 선택
        first_button = self.radio_group.button(
            0
        )

        if first_button:
            first_button.setChecked(True)

        # ==================================================
        # Modal 전용 스타일
        # ==================================================
        self.setStyleSheet(
            """
            #existingProjectPanel {
                background: #101f2c;
                border: 1px solid #64748b;
                border-radius: 12px;
            }

            #existingProjectTitle {
                color: #f8fafc;
                font-size: 20px;
                font-weight: 700;
            }

            #existingProjectClose {
                color: #e2e8f0;
                background: transparent;
                border: none;
                font-size: 24px;
            }

            #existingProjectClose:hover {
                color: #ffffff;
            }

            #existingProjectDescription {
                color: #cbd5e1;
                font-size: 11px;
            }

            #existingProjectHeader {
                color: #94a3b8;
                font-size: 10px;
            }

            #existingProjectRow {
                background: #162837;
                border: 1px solid #334b5e;
                border-radius: 8px;
            }

            #existingProjectRow:hover {
                border: 1px solid #4b6a82;
            }

            #existingProjectText {
                color: #e2e8f0;
                font-size: 10px;
            }

            #existingProjectGuide {
                color: #94a3b8;
                font-size: 10px;
            }

            #existingProjectGuideBlue {
                color: #60a5fa;
                font-size: 10px;
            }

            #existingProjectCancel {
                color: #e2e8f0;
                background: #223548;
                border: none;
                border-radius: 7px;
                font-size: 11px;
            }

            #existingProjectCancel:hover {
                background: #2b4155;
            }

            #existingProjectMove {
                color: #ffffff;
                background: #2563eb;
                border: none;
                border-radius: 7px;
                font-size: 11px;
                font-weight: 600;
            }

            #existingProjectMove:hover {
                background: #3171f2;
            }

            QRadioButton {
                color: #e2e8f0;
                spacing: 8px;
            }

            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }

            QRadioButton::indicator:unchecked {
                background: transparent;
                border: 1px solid #7da2c1;
                border-radius: 8px;
            }

            QRadioButton::indicator:checked {
                background: #2563eb;
                border: 3px solid #8bc1e8;
                border-radius: 8px;
            }
            """
        )

    # ======================================================
    # 프로젝트 한 줄
    # ======================================================
    def create_project_row(
        self,
        index,
        project,
    ):
        row = QFrame()
        row.setObjectName(
            "existingProjectRow"
        )
        row.setFixedHeight(52)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(
            12, 4, 12, 4
        )
        row_layout.setSpacing(8)

        radio = QRadioButton()
        self.radio_group.addButton(
            radio,
            index,
        )

        name = QLabel(project["name"])
        department = QLabel(
            project["department"]
        )
        project_type = QLabel(
            project["type"]
        )
        date = QLabel(project["date"])

        for label in (
            name,
            department,
            project_type,
            date,
        ):
            label.setObjectName(
                "existingProjectText"
            )

        name.setFixedWidth(175)
        department.setFixedWidth(145)
        project_type.setFixedWidth(120)

        row_layout.addWidget(radio)
        row_layout.addWidget(name)
        row_layout.addWidget(department)
        row_layout.addWidget(project_type)
        row_layout.addWidget(date, 1)

        return row

    # ======================================================
    # 기존 프로젝트로 이동
    # ======================================================
    def move_to_project(self):
        selected_id = (
            self.radio_group.checkedId()
        )

        if selected_id < 0:
            return

        project = self.projects[selected_id]

        self.project_selected.emit(project)

        self.accept()