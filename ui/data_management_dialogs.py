from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)


class DeleteConfirmDialog(QDialog):
    def __init__(self, title, message, impact_lines, confirm_text="삭제", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(520, 305)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("deleteConfirmPanel")
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(9)

        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("deleteConfirmTitle")
        close_button = QPushButton("×")
        close_button.setObjectName("deleteConfirmClose")
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        message_label = QLabel(message)
        message_label.setObjectName("deleteConfirmMessage")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        impact_frame = QFrame()
        impact_frame.setObjectName("deleteConfirmImpact")
        impact_layout = QVBoxLayout(impact_frame)
        impact_layout.setContentsMargins(14, 9, 14, 9)
        impact_layout.setSpacing(4)
        for line in impact_lines:
            display_line = line
            if title == "전체 검사 이력 정리" and line.startswith("프로젝트:"):
                display_line = line.replace("프로젝트:", "프로젝트 정보:", 1)
            label = QLabel(display_line)
            label.setObjectName("deleteConfirmImpactText")
            impact_layout.addWidget(label)
        layout.addWidget(impact_frame)

        warning = QLabel("삭제된 데이터는 복구할 수 없습니다.")
        warning.setObjectName("deleteConfirmWarning")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        layout.addSpacing(3)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch()
        cancel = QPushButton("취소")
        cancel.setObjectName("deleteConfirmCancel")
        cancel.setFixedSize(105, 40)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        confirm = QPushButton(confirm_text)
        confirm.setObjectName("deleteConfirmDelete")
        confirm.setFixedSize(112, 40)
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addLayout(buttons)

        self.apply_theme()

    def apply_theme(self):
        host = self.parentWidget().window() if self.parentWidget() is not None else None
        is_dark = getattr(host, "is_dark_mode", True)
        if is_dark:
            self.setStyleSheet("""
                #deleteConfirmPanel { background:#101f2c; border:1px solid #64748b; border-radius:12px; }
                #deleteConfirmTitle { color:#ffffff; font-size:22px; font-weight:850; }
                #deleteConfirmClose { color:#ffffff; background:transparent; border:none; font-size:24px; }
                #deleteConfirmClose:hover { background:#1d3142; border-radius:6px; }
                #deleteConfirmMessage { color:#f8fafc; font-size:15px; font-weight:800; }
                #deleteConfirmImpact { background:#142635; border:1px solid #40586c; border-radius:8px; }
                #deleteConfirmImpactText { color:#ffffff; font-size:14px; font-weight:850; }
                #deleteConfirmWarning { color:#ff8d82; font-size:14px; font-weight:900; }
                #deleteConfirmCancel { color:#ffffff; background:#253b4f; border:1px solid #3a5369; border-radius:7px; font-size:13px; font-weight:800; }
                #deleteConfirmCancel:hover { background:#30495f; }
                #deleteConfirmDelete { color:#ffffff; background:#b42318; border:none; border-radius:7px; font-size:13px; font-weight:900; }
                #deleteConfirmDelete:hover { background:#d92d20; }
            """)
        else:
            self.setStyleSheet("""
                #deleteConfirmPanel { background:#ffffff; border:1px solid #a8b6c7; border-radius:12px; }
                #deleteConfirmTitle { color:#0b1220; font-size:22px; font-weight:850; }
                #deleteConfirmClose { color:#0f172a; background:transparent; border:none; font-size:24px; }
                #deleteConfirmClose:hover { background:#eef2f6; border-radius:6px; }
                #deleteConfirmMessage { color:#111827; font-size:15px; font-weight:800; }
                #deleteConfirmImpact { background:#f8fafc; border:1px solid #bdcad8; border-radius:8px; }
                #deleteConfirmImpactText { color:#0b1220; font-size:14px; font-weight:850; }
                #deleteConfirmWarning { color:#b42318; font-size:14px; font-weight:900; }
                #deleteConfirmCancel { color:#0f172a; background:#e7edf4; border:1px solid #bdc9d6; border-radius:7px; font-size:13px; font-weight:800; }
                #deleteConfirmCancel:hover { background:#dce5ee; }
                #deleteConfirmDelete { color:#ffffff; background:#b42318; border:none; border-radius:7px; font-size:13px; font-weight:900; }
                #deleteConfirmDelete:hover { background:#d92d20; }
            """)


class ProjectManagementDialog(QDialog):
    def __init__(self, projects, delete_callback, parent=None):
        super().__init__(parent)
        self.projects = list(projects)
        self.delete_callback = delete_callback
        self.setWindowTitle("프로젝트 관리")
        self.setModal(True)
        self.setFixedSize(700, 490)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        panel = QFrame()
        panel.setObjectName("projectManagePanel")
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(26, 20, 26, 20)
        layout.setSpacing(11)

        header = QHBoxLayout()
        title = QLabel("프로젝트 관리")
        title.setObjectName("projectManageTitle")
        close_button = QPushButton("×")
        close_button.setObjectName("projectManageClose")
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        description = QLabel("프로젝트 삭제 시 해당 프로젝트의 검사 이력과 이슈도 함께 삭제됩니다.")
        description.setObjectName("projectManageDescription")
        layout.addWidget(description)

        scroll = QScrollArea()
        scroll.setObjectName("projectManageScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("projectManageContent")
        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(5)
        self.refresh_rows()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        close = QPushButton("닫기")
        close.setObjectName("projectManageCancel")
        close.setFixedSize(112, 40)
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.reject)
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(close)
        layout.addLayout(button_row)

        self.apply_theme()

    def refresh_rows(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self.projects:
            empty = QLabel("등록된 프로젝트가 없습니다.")
            empty.setObjectName("projectManageEmpty")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)
            self.list_layout.addStretch()
            return

        for project in self.projects:
            row = QFrame()
            row.setObjectName("projectManageRow")
            row.setFixedHeight(66)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 5, 12, 5)
            row_layout.setSpacing(10)

            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(1)
            name = QLabel(project.get("project_name") or "-")
            name.setObjectName("projectManageName")
            meta = QLabel(
                f"부서: {project.get('department') or '-'}   ·   "
                f"검사 이력 {project.get('inspections', 0)}건   ·   "
                f"이슈 {project.get('issues', 0)}건"
            )
            meta.setObjectName("projectManageMeta")
            text_layout.addWidget(name)
            text_layout.addWidget(meta)

            delete_button = QPushButton("삭제")
            delete_button.setObjectName("projectManageDelete")
            delete_button.setFixedSize(76, 34)
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.clicked.connect(
                lambda checked=False, p=dict(project): self.delete_project(p)
            )

            row_layout.addWidget(text_widget, 1)
            row_layout.addWidget(delete_button)
            self.list_layout.addWidget(row)
        self.list_layout.addStretch()

    def delete_project(self, project):
        deleted = self.delete_callback(project)
        if not deleted:
            return
        project_id = project.get("project_id")
        self.projects = [p for p in self.projects if p.get("project_id") != project_id]
        self.refresh_rows()

    def apply_theme(self):
        host = self.parentWidget().window() if self.parentWidget() is not None else None
        is_dark = getattr(host, "is_dark_mode", True)
        if is_dark:
            self.setStyleSheet("""
                #projectManagePanel { background:#101f2c; border:1px solid #64748b; border-radius:12px; }
                QWidget#projectManageContent { background:transparent; }
                #projectManageTitle { color:#ffffff; font-size:22px; font-weight:850; }
                #projectManageClose { color:#ffffff; background:transparent; border:none; font-size:24px; }
                #projectManageClose:hover { background:#1d3142; border-radius:6px; }
                #projectManageDescription { color:#f8fafc; font-size:14px; font-weight:750; }
                #projectManageRow { background:#142635; border:1px solid #40586c; border-radius:8px; }
                #projectManageRow:hover { background:#182d3e; border-color:#638099; }
                #projectManageName { color:#ffffff; font-size:15px; font-weight:900; }
                #projectManageMeta { color:#e2e8f0; font-size:14px; font-weight:780; }
                QPushButton#projectManageDelete { color:#ff9b91; background:transparent; border:1px solid #d92d20; border-radius:6px; font-size:13px; font-weight:900; }
                QPushButton#projectManageDelete:hover { color:#ffffff; background:#b42318; border-color:#b42318; }
                #projectManageCancel { color:#ffffff; background:#253b4f; border:1px solid #3a5369; border-radius:7px; font-size:13px; font-weight:800; }
                #projectManageCancel:hover { background:#30495f; }
                #projectManageEmpty { color:#d6e0ea; font-size:14px; font-weight:750; }
                #projectManageScroll { background:transparent; border:none; }
                #projectManageScroll QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                #projectManageScroll QScrollBar::handle:vertical { background:#60758a; min-height:28px; border-radius:4px; }
                #projectManageScroll QScrollBar::add-line:vertical, #projectManageScroll QScrollBar::sub-line:vertical { height:0px; }
            """)
        else:
            self.setStyleSheet("""
                #projectManagePanel { background:#ffffff; border:1px solid #a8b6c7; border-radius:12px; }
                QWidget#projectManageContent { background:transparent; }
                #projectManageTitle { color:#0b1220; font-size:22px; font-weight:850; }
                #projectManageClose { color:#0f172a; background:transparent; border:none; font-size:24px; }
                #projectManageClose:hover { background:#eef2f6; border-radius:6px; }
                #projectManageDescription { color:#111827; font-size:14px; font-weight:750; }
                #projectManageRow { background:#ffffff; border:1px solid #bdcad8; border-radius:8px; }
                #projectManageRow:hover { background:#f8fafc; border-color:#8197ad; }
                #projectManageName { color:#0b1220; font-size:15px; font-weight:900; }
                #projectManageMeta { color:#263548; font-size:14px; font-weight:780; }
                QPushButton#projectManageDelete { color:#b42318; background:#ffffff; border:1px solid #d92d20; border-radius:6px; font-size:13px; font-weight:900; }
                QPushButton#projectManageDelete:hover { color:#ffffff; background:#b42318; border-color:#b42318; }
                #projectManageCancel { color:#0f172a; background:#e7edf4; border:1px solid #bdc9d6; border-radius:7px; font-size:13px; font-weight:800; }
                #projectManageCancel:hover { background:#dce5ee; }
                #projectManageEmpty { color:#334155; font-size:14px; font-weight:750; }
                #projectManageScroll { background:transparent; border:none; }
                #projectManageScroll QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
                #projectManageScroll QScrollBar::handle:vertical { background:#8998aa; min-height:28px; border-radius:4px; }
                #projectManageScroll QScrollBar::add-line:vertical, #projectManageScroll QScrollBar::sub-line:vertical { height:0px; }
            """)
