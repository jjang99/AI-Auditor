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
        """Apply the sidebar palette directly so page-level styles cannot override it."""
        if is_dark_mode:
            self.theme_button.setText("☀  Light Mode")
            self.theme_button.setToolTip("라이트 모드로 전환")
            self.setStyleSheet("""
                QFrame#sidebar {
                    background:#0d1117;
                    border-right:1px solid #1f2937;
                }
                QLabel#sidebarTitle { color:#ffffff; font-size:16px; font-weight:700; }
                QPushButton#sidebarMenuButton {
                    color:#94a3b8; background:transparent; border:none; border-radius:7px;
                    padding:10px 12px; text-align:left; font-size:12px; font-weight:600;
                }
                QPushButton#sidebarMenuButton:hover { color:#ffffff; background:#151b23; }
                QPushButton#sidebarMenuButton:checked {
                    color:#60a5fa; background:#162033; border-left:3px solid #3b82f6;
                }
                QFrame#sidebarHelpFrame { background:#0b131c; border:1px solid #334155; border-radius:8px; }
                QLabel#sidebarHelpTitle { color:#f8fafc; font-size:12px; font-weight:700; }
                QLabel#sidebarGradeText { color:#dbe3ee; font-size:10px; }
                QLabel#sidebarGradeA, QLabel#sidebarGradeB { color:#22c55e; font-size:11px; font-weight:700; }
                QLabel#sidebarGradeC { color:#fbbf24; font-size:11px; font-weight:700; }
                QLabel#sidebarGradeD { color:#f97316; font-size:11px; font-weight:700; }
                QLabel#sidebarGradeE { color:#ef4444; font-size:11px; font-weight:700; }
                QPushButton#sidebarThemeButton {
                    color:#e2e8f0; background:#171c22; border:1px solid #2d3742;
                    border-radius:6px; font-size:11px; font-weight:600;
                }
                QPushButton#sidebarThemeButton:hover { background:#222a33; border-color:#475569; }
                QFrame#sidebarFooterFrame { background:transparent; border-top:1px solid #243041; }
                QLabel#sidebarFooterText { color:#cbd5e1; font-size:10px; }
            """)
        else:
            self.theme_button.setText("☾  Dark Mode")
            self.theme_button.setToolTip("다크 모드로 전환")
            self.setStyleSheet("""
                QFrame#sidebar {
                    background:#f8fafc;
                    border-right:1px solid #d7e0ea;
                }
                QLabel#sidebarTitle { color:#0f172a; font-size:16px; font-weight:700; }
                QPushButton#sidebarMenuButton {
                    color:#64748b; background:transparent; border:none; border-radius:7px;
                    padding:10px 12px; text-align:left; font-size:12px; font-weight:600;
                }
                QPushButton#sidebarMenuButton:hover { color:#0f172a; background:#f1f5f9; }
                QPushButton#sidebarMenuButton:checked {
                    color:#2563eb; background:#eff6ff; border-left:3px solid #2563eb;
                }
                QFrame#sidebarHelpFrame { background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; }
                QLabel#sidebarHelpTitle { color:#0f172a; font-size:12px; font-weight:700; }
                QLabel#sidebarGradeText { color:#334155; font-size:10px; }
                QLabel#sidebarGradeA, QLabel#sidebarGradeB { color:#16a34a; font-size:11px; font-weight:700; }
                QLabel#sidebarGradeC { color:#ca8a04; font-size:11px; font-weight:700; }
                QLabel#sidebarGradeD { color:#ea580c; font-size:11px; font-weight:700; }
                QLabel#sidebarGradeE { color:#dc2626; font-size:11px; font-weight:700; }
                QPushButton#sidebarThemeButton {
                    color:#334155; background:#f8fafc; border:1px solid #cbd5e1;
                    border-radius:6px; font-size:11px; font-weight:600;
                }
                QPushButton#sidebarThemeButton:hover { background:#eef2f7; border-color:#94a3b8; }
                QFrame#sidebarFooterFrame { background:transparent; border-top:1px solid #dbe3ee; }
                QLabel#sidebarFooterText { color:#475569; font-size:10px; }
            """)

    def select_menu(self, selected_name):
        for menu_name, button in self.menu_buttons.items():
            button.setChecked(menu_name == selected_name)
        self.menu_clicked.emit(selected_name)
