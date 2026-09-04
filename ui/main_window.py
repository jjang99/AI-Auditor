import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.home_page import HomePage
from ui.projects_page import ProjectsPage
from ui.theme import DARK_THEME, LIGHT_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_dark_mode = True

        # ==================================================
        # 기본 창 설정
        # ==================================================
        self.setWindowTitle("AI Auditor")

        window_icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "icons",
            "logo.svg",
        )

        self.setWindowIcon(QIcon(window_icon_path))

        # 최종 시안 기준 세로형 창 비율
        self.resize(760, 980)
        self.setMinimumSize(720, 900)

        # ==================================================
        # 전체 화면
        # ==================================================
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================================================
        # 상단 Header
        # ==================================================
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(56)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(0)

        # --------------------------------------------------
        # 상단 메뉴 한 줄
        # --------------------------------------------------
        menu_row = QHBoxLayout()
        menu_row.setSpacing(4)
        menu_row.addStretch()

        menu_names = [
            "Home",
            "Projects",
            "Inspection",
            "Reports",
            "Administration",
        ]

        self.menu_buttons = {}

        for menu_name in menu_names:
            button = QPushButton(menu_name)
            button.setObjectName("topMenuButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setCheckable(True)

            if menu_name == "Home":
                button.setChecked(True)

            # 메뉴를 클릭하면 선택 메뉴 변경
            button.clicked.connect(
                lambda checked, name=menu_name: self.select_menu(name)
            )

            self.menu_buttons[menu_name] = button
            menu_row.addWidget(button)

        # --------------------------------------------------
        # 테마 전환 버튼
        # --------------------------------------------------
        self.theme_button = QPushButton("☀")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setToolTip("Light Mode")
        self.theme_button.setFixedSize(32, 28)
        self.theme_button.clicked.connect(self.toggle_theme)

        menu_row.addSpacing(4)
        menu_row.addWidget(self.theme_button)

        header_layout.addLayout(menu_row)

        # ==================================================
        # Home 콘텐츠
        # ==================================================
        content = QFrame()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.page_stack = QStackedWidget()

        self.home_page = HomePage()
        self.projects_page = ProjectsPage()

        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.projects_page)

        content_layout.addWidget(self.page_stack)

        # ==================================================
        # 전체 화면 배치
        # ==================================================
        main_layout.addWidget(header)
        main_layout.addWidget(content)

        # 기본 Dark Mode 적용
        self.apply_theme()

    # ======================================================
    # 메뉴 선택
    # ======================================================
    def select_menu(self, selected_name):
        for menu_name, button in self.menu_buttons.items():
            button.setChecked(menu_name == selected_name)

        if selected_name == "Home":
            self.page_stack.setCurrentWidget(self.home_page)

        elif selected_name == "Projects":
            self.page_stack.setCurrentWidget(self.projects_page)

    # ======================================================
    # Dark / Light Mode 전환
    # ======================================================
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    # ======================================================
    # 테마 적용
    # ======================================================
    def apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(DARK_THEME)
            self.theme_button.setText("☀")
            self.theme_button.setToolTip("Light Mode")
        else:
            self.setStyleSheet(LIGHT_THEME)
            self.theme_button.setText("☾")
            self.theme_button.setToolTip("Dark Mode")