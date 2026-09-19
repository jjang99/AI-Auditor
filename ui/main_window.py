import os

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from ui.home_page import HomePage
from ui.projects_page import ProjectsPage
from ui.project_detail_page import ProjectDetailPage
from ui.project_detail_refinements import apply_project_detail_refinements
from ui.project_detail_runtime import apply_project_detail_runtime
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
from ui.theme_overrides import (
    DARK_UI_OVERRIDES, LIGHT_UI_OVERRIDES, LIGHT_TEXT_HIERARCHY_FINAL,
    DARK_SHARED_VISUAL_FINAL, LIGHT_SHARED_VISUAL_FINAL,
    PROJECTS_DARK_FINAL, PROJECTS_LIGHT_FINAL,
)

apply_project_detail_refinements(ProjectDetailPage)
apply_project_detail_runtime(ProjectDetailPage)
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
        self.reports_page.report_selected.connect(self.open_project_detail)
        self.inspection_page.existing_project_selected.connect(self.open_project_detail)
        self.inspection_page.inspection_result_requested.connect(self.open_latest_inspection_result)

        self.home_page.inspection_button.clicked.connect(lambda: self.select_menu("Inspection"))
        for card in self.home_page.findChildren(QFrame, "homeCard"):
            title_label = card.findChild(QLabel, "homeCardTitle")
            if title_label is not None:
                card.setProperty("menuName", title_label.text())
                card.setCursor(Qt.PointingHandCursor)
                card.installEventFilter(self)

        main_layout.addWidget(self.header)
        main_layout.addWidget(content)
        self.page_stack.setCurrentWidget(self.home_page)
        self.apply_theme()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonRelease:
            menu_name = watched.property("menuName")
            if menu_name in {"Projects", "Inspection", "Reports", "Administration"}:
                self.select_menu(menu_name)
                return True
        return super().eventFilter(watched, event)

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
            self.projects_page.refresh_projects()
            self.page_stack.setCurrentWidget(self.projects_page)
        elif selected_name == "Inspection":
            self.header.hide()
            self.inspection_page.prepare_new_inspection()
            self.page_stack.setCurrentWidget(self.inspection_page)
        elif selected_name == "Reports":
            self.header.hide()
            self.reports_page.refresh_reports()
            self.page_stack.setCurrentWidget(self.reports_page)
        elif selected_name == "Administration":
            self.header.hide()
            self.page_stack.setCurrentWidget(self.administration_page)

    def open_latest_inspection_result(self):
        project_id = self.inspection_page.last_project_id
        inspection_id = self.inspection_page.last_inspection_id
        if project_id is None:
            return
        self.open_project_detail({"id": project_id, "inspection_id": inspection_id})

    def open_project_detail(self, project):
        self.header.hide()
        self.update_sidebar_selection("Projects")
        project_id = project.get("id") if isinstance(project, dict) else None
        inspection_id = project.get("inspection_id") if isinstance(project, dict) else None
        if project_id is not None:
            self.project_detail_page.load_project(project_id, inspection_id)
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
                QComboBox::drop-down:hover {
                    background:#23445b;
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
                QComboBox::drop-down:hover {
                    background:#dfeaf2;
                }
            """

        for combo in self.inspection_page.findChildren(QComboBox, "inspectionCombo"):
            combo.setStyleSheet(combo_style)
        for combo in self.administration_page.findChildren(QComboBox, "adminThemeCombo"):
            combo.setStyleSheet(combo_style)

    def apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(DARK_THEME + DARK_UI_OVERRIDES + DETAIL_DARK_REFINEMENTS + DARK_INSPECTION_REFINEMENTS + DARK_INSPECTION_READABILITY_V2 + DARK_INSPECTION_FINAL + DARK_INSPECTION_PROGRESS + DARK_SHARED_VISUAL_FINAL + PROJECTS_DARK_FINAL)
            self.theme_button.setText("☀")
            self.theme_button.setToolTip("Light Mode")
        else:
            self.setStyleSheet(LIGHT_THEME + LIGHT_UI_OVERRIDES + DETAIL_LIGHT_REFINEMENTS + LIGHT_INSPECTION_REFINEMENTS + LIGHT_INSPECTION_READABILITY_V2 + LIGHT_INSPECTION_FINAL + LIGHT_INSPECTION_PROGRESS + LIGHT_TEXT_HIERARCHY_FINAL + LIGHT_SHARED_VISUAL_FINAL + PROJECTS_LIGHT_FINAL)
            self.theme_button.setText("☾")
            self.theme_button.setToolTip("Dark Mode")
        self.projects_page.set_light_mode(not self.is_dark_mode)
        self.home_page.set_wave_theme(self.is_dark_mode)

        # Page-local styles have higher precedence than MainWindow QSS.
        # Inspection's legacy stylesheet is dark-only, so keep it only for the
        # verified dark theme and remove it in light mode.  The approved light
        # Inspection QSS above then becomes the single source of truth.
        if self.is_dark_mode:
            self.inspection_page.setStyleSheet(self.inspection_page.inspection_style())
        else:
            self.inspection_page.setStyleSheet("")

        self.inspection_page.apply_rule_text_theme(self.is_dark_mode)
        self.reports_page.apply_theme(self.is_dark_mode)
        self.administration_page.apply_theme(self.is_dark_mode)
        self._apply_shared_combo_style()
        for sidebar in self.sidebars:
            sidebar.set_theme(self.is_dark_mode)
