import os

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
)


class Sidebar(QFrame):
    menu_clicked = Signal(str)
    theme_toggle_requested = Signal()

    def __init__(self, selected_menu="Projects", show_grade_help=False):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(165)

        base_path = os.path.dirname(os.path.dirname(__file__))
        self.icon_path = os.path.join(base_path, "assets", "icons")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 18, 12, 12)
        main_layout.setSpacing(0)

        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(4, 0, 0, 0)
        logo_row.setSpacing(8)

        logo_label = QLabel()
        logo_icon = QIcon(os.path.join(self.icon_path, "logo.svg"))
        logo_label.setPixmap(logo_icon.pixmap(QSize(24, 24)))
        logo_label.setFixedSize(26, 26)

        title = QLabel("AI Auditor")
        title.setObjectName("sidebarTitle")

        logo_row.addWidget(logo_label)
        logo_row.addWidget(title)
        logo_row.addStretch()
        main_layout.addLayout(logo_row)
        main_layout.addSpacing(22)

        self.menu_buttons = {}
        menu_items = [
            ("Home", None),
            ("Projects", "project.svg"),
            ("Inspection", "inspection.svg"),
            ("Reports", "reports.svg"),
            ("Administration", "administration.svg"),
        ]

        for menu_name, icon_file in menu_items:
            button = QPushButton(menu_name)
            button.setObjectName("sidebarMenuButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setCheckable(True)
            button.setFixedHeight(40)

            if icon_file:
                button.setIcon(QIcon(os.path.join(self.icon_path, icon_file)))
            else:
                button.setIcon(self.style().standardIcon(QStyle.SP_DirHomeIcon))

            button.setIconSize(QSize(15, 15))
            if menu_name == selected_menu:
                button.setChecked(True)

            button.clicked.connect(lambda checked, name=menu_name: self.select_menu(name))
            self.menu_buttons[menu_name] = button
            main_layout.addWidget(button)
            main_layout.addSpacing(3)

        main_layout.addStretch()

        if show_grade_help:
            help_frame = QFrame()
            help_frame.setObjectName("sidebarHelpFrame")
            help_layout = QVBoxLayout(help_frame)
            help_layout.setContentsMargins(10, 11, 10, 11)
            help_layout.setSpacing(7)

            help_title = QLabel("❓  등급 기준 (Help)")
            help_title.setObjectName("sidebarHelpTitle")
            help_layout.addWidget(help_title)
            help_layout.addSpacing(2)

            grade_data = [
                ("A", "우수", "90 ~ 100", "sidebarGradeA"),
                ("B", "양호", "80 ~ 89", "sidebarGradeB"),
                ("C", "보통", "70 ~ 79", "sidebarGradeC"),
                ("D", "미흡", "60 ~ 69", "sidebarGradeD"),
                ("E", "불량", "0 ~ 59", "sidebarGradeE"),
            ]

            for grade, text, score, object_name in grade_data:
                row = QHBoxLayout()
                row.setSpacing(3)
                grade_label = QLabel(grade)
                grade_label.setObjectName(object_name)
                grade_label.setFixedWidth(16)
                description = QLabel(f"({text}) : {score}")
                description.setObjectName("sidebarGradeText")
                row.addWidget(grade_label)
                row.addWidget(description)
                row.addStretch()
                help_layout.addLayout(row)

            main_layout.addWidget(help_frame)
            main_layout.addSpacing(8)

        self.theme_button = QPushButton("☀  Light Mode")
        self.theme_button.setObjectName("sidebarThemeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setFixedHeight(34)
        self.theme_button.clicked.connect(self.theme_toggle_requested.emit)
        main_layout.addWidget(self.theme_button)
        main_layout.addSpacing(8)

        footer_frame = QFrame()
        footer_frame.setObjectName("sidebarFooterFrame")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 8, 10, 8)
        footer_layout.setSpacing(5)

        version = QLabel("Version 1.0.0")
        version.setObjectName("sidebarFooterText")
        copyright_text = QLabel("© 2026 AI Auditor.")
        copyright_text.setObjectName("sidebarFooterText")
        rights = QLabel("All rights reserved.")
        rights.setObjectName("sidebarFooterText")

        footer_layout.addWidget(version)
        footer_layout.addWidget(copyright_text)
        footer_layout.addWidget(rights)
        main_layout.addWidget(footer_frame)

    def set_theme(self, is_dark_mode):
        if is_dark_mode:
            self.theme_button.setText("☀  Light Mode")
            self.theme_button.setToolTip("라이트 모드로 전환")
        else:
            self.theme_button.setText("☾  Dark Mode")
            self.theme_button.setToolTip("다크 모드로 전환")

    def select_menu(self, selected_name):
        for menu_name, button in self.menu_buttons.items():
            button.setChecked(menu_name == selected_name)
        self.menu_clicked.emit(selected_name)
