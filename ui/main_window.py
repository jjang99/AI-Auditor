import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from ui.home_page import HomePage
from ui.projects_page import ProjectsPage
from ui.project_detail_page import ProjectDetailPage
from ui.project_detail_refinements import apply_project_detail_refinements
from ui.project_detail_theme import DETAIL_DARK_REFINEMENTS, DETAIL_LIGHT_REFINEMENTS
from ui.inspection_page import InspectionPage
from ui.inspection_refinements import apply_inspection_refinements, DARK_INSPECTION_REFINEMENTS, LIGHT_INSPECTION_REFINEMENTS
from ui.inspection_readability_v2 import apply_inspection_readability_v2, DARK_INSPECTION_READABILITY_V2, LIGHT_INSPECTION_READABILITY_V2
from ui.inspection_final_refinements import apply_inspection_final_refinements, DARK_INSPECTION_FINAL, LIGHT_INSPECTION_FINAL
from ui.inspection_progress_refinements import apply_inspection_progress_refinements, DARK_INSPECTION_PROGRESS, LIGHT_INSPECTION_PROGRESS
from ui.inspection_runtime import apply_inspection_runtime
from ui.reports_page import ReportsPage
from ui.administration_page import AdministrationPage
from ui.theme import DARK_THEME, LIGHT_THEME
from ui.theme_overrides import DARK_UI_OVERRIDES, LIGHT_UI_OVERRIDES

apply_project_detail_refinements(ProjectDetailPage)
apply_inspection_refinements(InspectionPage)
apply_inspection_readability_v2(InspectionPage)
apply_inspection_final_refinements(InspectionPage)
apply_inspection_progress_refinements(InspectionPage)
apply_inspection_runtime(InspectionPage)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = True
        self.setWindowTitle("AI Auditor")
        window_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "logo.svg")
        self.setWindowIcon(QIcon(window_icon_path))
        self.setFixedSize(840, 900)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.header = QFrame()
        self.header.setObjectName("header")
        self.header.setFixedHeight(56)
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(0)
        menu_row = QHBoxLayout()
        menu_row.setSpacing(4)
        menu_row.addStretch()
        menu_names = ["Home", "Projects", "Inspection", "Reports", "Administration"]
        self.menu_buttons = {}
        for menu_name in menu_names:
            button = QPushButton(menu_name)
            button.setObjectName("topMenuButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setCheckable(True)
            if menu_name == "Home":
                button.setChecked(True)
            button.clicked.connect(lambda checked, name=menu_name: self.select_menu(name))
            self.menu_buttons[menu_name] = button
            menu_row.addWidget(button)
        self.theme_button = QPushButton("☀")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setToolTip("Light Mode")
        self.theme_button.setFixedSize(32, 28)
        self.theme_button.clicked.connect(self.toggle_theme)
        menu_row.addSpacing(4)
        menu_row.addWidget(self.theme_button)
        header_layout.addLayout(menu_row)
        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.page_stack = QStackedWidget()
        self.home_page = HomePage()
        self.projects_page = ProjectsPage()
        self.project_detail_page = ProjectDetailPage()
        self.inspection_page = InspectionPage()
        self.reports_page = ReportsPage()
        self.administration_page = AdministrationPage()
        for page in [self.home_page, self.projects_page, self.project_detail_page, self.inspection_page, self.reports_page, self.administration_page]:
            self.page_stack.addWidget(page)
        content_layout.addWidget(self.page_stack)
        self.sidebars = [self.projects_page.sidebar, self.project_detail_page.sidebar, self.inspection_page.sidebar, self.reports_page.sidebar, self.administration_page.sidebar]
        for sidebar in self.sidebars:
            sidebar.menu_clicked.connect(self.select_menu)
            sidebar.theme_toggle_requested.connect(self.toggle_theme)
        self.projects_page.project_selected.connect(self.open_project_detail)
        self.inspection_page.existing_project_selected.connect(self.open_project_detail)
        self.inspection_page.inspection_result_requested.connect(lambda: self.open_project_detail({}))
        main_layout.addWidget(self.header)
        main_layout.addWidget(content)
        self.page_stack.setCurrentWidget(self.home_page)
        self.apply_theme()

    def update_sidebar_selection(self, selected_name):
        for sidebar in self.sidebars:
            for menu_name, button in sidebar.menu_buttons.items():
                button.setChecked(menu_name == selected_name)

    def select_menu(self, selected_name):
        for menu_name, button in self.menu_buttons.items():
            button.setChecked(menu_name == selected_name)
        self.update_sidebar_selection(selected_name)
        if selected_name == "Home":
            self.header.show()
            self.page_stack.setCurrentWidget(self.home_page)
        elif selected_name == "Projects":
            self.header.hide()
            self.page_stack.setCurrentWidget(self.projects_page)
        elif selected_name == "Inspection":
            self.header.hide()
            self.page_stack.setCurrentWidget(self.inspection_page)
        elif selected_name == "Reports":
            self.header.hide()
            self.page_stack.setCurrentWidget(self.reports_page)
        elif selected_name == "Administration":
            self.header.hide()
            self.page_stack.setCurrentWidget(self.administration_page)

    def open_project_detail(self, project):
        self.header.hide()
        self.update_sidebar_selection("Projects")
        self.page_stack.setCurrentWidget(self.project_detail_page)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def _apply_shared_combo_style(self):
        if self.is_dark_mode:
            combo_style = """
                QComboBox {
                    background:#0d1822;
                    color:#f8fbfd;
                    border:1px solid #557187;
                    border-radius:7px;
                    padding:0 10px;
                    font-size:12px;
                    font-weight:700;
                }
                QComboBox::drop-down {
                    subcontrol-origin:padding;
                    subcontrol-position:top right;
                    width:30px;
                    border-left:1px solid #405a6e;
                    border-top-right-radius:7px;
                    border-bottom-right-radius:7px;
                    background:#132433;
                }
                QComboBox::down-arrow {
                    width:9px;
                    height:9px;
                }
            """
        else:
            combo_style = """
                QComboBox {
                    background:#ffffff;
                    color:#203648;
                    border:1px solid #97adbd;
                    border-radius:7px;
                    padding:0 10px;
                    font-size:12px;
                    font-weight:700;
                }
                QComboBox::drop-down {
                    subcontrol-origin:padding;
                    subcontrol-position:top right;
                    width:30px;
                    border-left:1px solid #b3c3cf;
                    border-top-right-radius:7px;
                    border-bottom-right-radius:7px;
                    background:#edf3f7;
                }
                QComboBox::down-arrow {
                    width:9px;
                    height:9px;
                }
            """

        for combo in self.inspection_page.findChildren(QComboBox, "inspectionCombo"):
            combo.setStyleSheet(combo_style)
        for combo in self.administration_page.findChildren(QComboBox, "adminThemeCombo"):
            combo.setStyleSheet(combo_style)

    def apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(DARK_THEME + DARK_UI_OVERRIDES + DETAIL_DARK_REFINEMENTS + DARK_INSPECTION_REFINEMENTS + DARK_INSPECTION_READABILITY_V2 + DARK_INSPECTION_FINAL + DARK_INSPECTION_PROGRESS)
            self.theme_button.setText("☀")
            self.theme_button.setToolTip("Light Mode")
        else:
            self.setStyleSheet(LIGHT_THEME + LIGHT_UI_OVERRIDES + DETAIL_LIGHT_REFINEMENTS + LIGHT_INSPECTION_REFINEMENTS + LIGHT_INSPECTION_READABILITY_V2 + LIGHT_INSPECTION_FINAL + LIGHT_INSPECTION_PROGRESS)
            self.theme_button.setText("☾")
            self.theme_button.setToolTip("Dark Mode")
        self.home_page.set_wave_theme(self.is_dark_mode)
        self.reports_page.apply_theme(self.is_dark_mode)
        self.administration_page.apply_theme(self.is_dark_mode)
        self._apply_shared_combo_style()
        for sidebar in self.sidebars:
            sidebar.set_theme(self.is_dark_mode)
