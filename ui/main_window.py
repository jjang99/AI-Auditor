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
from ui.project_detail_page import ProjectDetailPage
from ui.inspection_page import InspectionPage
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

        # 최종 확정 공통 창 크기
        self.setFixedSize(840, 900)

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
        # Home에서만 표시
        # ==================================================
        self.header = QFrame()
        self.header.setObjectName("header")
        self.header.setFixedHeight(56)

        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(0)

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

            button.clicked.connect(
                lambda checked, name=menu_name:
                self.select_menu(name)
            )

            self.menu_buttons[menu_name] = button
            menu_row.addWidget(button)

        # ==================================================
        # 테마 전환 버튼
        # ==================================================
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
        # 콘텐츠 영역
        # ==================================================
        content = QFrame()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.page_stack = QStackedWidget()

        # ==================================================
        # 페이지 생성
        # ==================================================
        self.home_page = HomePage()
        self.projects_page = ProjectsPage()
        self.project_detail_page = ProjectDetailPage()
        self.inspection_page = InspectionPage()

        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.projects_page)
        self.page_stack.addWidget(self.project_detail_page)
        self.page_stack.addWidget(self.inspection_page)

        content_layout.addWidget(self.page_stack)

        # ==================================================
        # Sidebar 메뉴 신호 연결
        # ==================================================
        self.projects_page.sidebar.menu_clicked.connect(
            self.select_menu
        )

        self.project_detail_page.sidebar.menu_clicked.connect(
            self.select_menu
        )

        self.inspection_page.sidebar.menu_clicked.connect(
            self.select_menu
        )

        self.projects_page.project_selected.connect(
            self.open_project_detail
        )

        self.inspection_page.existing_project_selected.connect(
            self.open_project_detail
        )

        self.inspection_page.inspection_result_requested.connect(
            lambda: self.open_project_detail({})
        )

        # ==================================================
        # 전체 화면 배치
        # ==================================================
        main_layout.addWidget(self.header)
        main_layout.addWidget(content)

        # ==================================================
        # 기본 화면
        # ==================================================
        self.page_stack.setCurrentWidget(self.home_page)

        # ==================================================
        # 기본 Dark Mode 적용
        # ==================================================
        self.apply_theme()

    # ======================================================
    # Sidebar 선택 상태 동기화
    # ======================================================
    def update_sidebar_selection(self, selected_name):

        sidebars = [
            self.projects_page.sidebar,
            self.project_detail_page.sidebar,
            self.inspection_page.sidebar,
        ]

        for sidebar in sidebars:
            for menu_name, button in (
                sidebar.menu_buttons.items()
            ):
                button.setChecked(
                    menu_name == selected_name
                )

    # ======================================================
    # 메뉴 선택 / 페이지 전환
    # ======================================================
    def select_menu(self, selected_name):

        # 상단 메뉴
        for menu_name, button in self.menu_buttons.items():
            button.setChecked(
                menu_name == selected_name
            )

        # Sidebar
        self.update_sidebar_selection(
            selected_name
        )

        # --------------------------------------------------
        # Home
        # --------------------------------------------------
        if selected_name == "Home":
            self.header.show()

            self.page_stack.setCurrentWidget(
                self.home_page
            )

        # --------------------------------------------------
        # Projects
        # --------------------------------------------------
        elif selected_name == "Projects":
            self.header.hide()

            self.page_stack.setCurrentWidget(
                self.projects_page
            )

        # --------------------------------------------------
        # Inspection
        # --------------------------------------------------
        elif selected_name == "Inspection":
            self.header.hide()

            self.page_stack.setCurrentWidget(
                self.inspection_page
            )

        # --------------------------------------------------
        # Reports
        # --------------------------------------------------
        elif selected_name == "Reports":
            pass

        # --------------------------------------------------
        # Administration
        # --------------------------------------------------
        elif selected_name == "Administration":
            pass

    # ======================================================
    # Project Detail
    # ======================================================
    def open_project_detail(self, project):
        self.header.hide()

        self.update_sidebar_selection(
            "Projects"
        )

        self.page_stack.setCurrentWidget(
            self.project_detail_page
        )

    # ======================================================
    # Dark / Light Mode
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
            self.theme_button.setToolTip(
                "Light Mode"
            )

        else:
            self.setStyleSheet(LIGHT_THEME)

            self.theme_button.setText("☾")
            self.theme_button.setToolTip(
                "Dark Mode"
            )