from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class ProjectsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("Projects")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignLeft)

        description = QLabel(
            "프로젝트 목록 화면을 준비 중입니다."
        )
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()