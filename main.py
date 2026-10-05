import sys

from PySide6.QtWidgets import QApplication

from app.database.database import initialize_database
from app.services.local_ai_runtime import get_local_ai_runtime
from ui.main_window import MainWindow
from ui.inspection_page import InspectionPage
from ui.inspection_rule_ui_patch import apply_inspection_rule_ui_patch
from ui.inspection_visual_polish_patch import apply_inspection_visual_polish
from ui.project_detail_page import ProjectDetailPage
from ui.project_detail_status_patch import apply_project_detail_status_patch
from ui.project_detail_audit_badge_patch import apply_project_detail_audit_badge_patch


initialize_database()
apply_inspection_rule_ui_patch(InspectionPage)
apply_inspection_visual_polish(InspectionPage)
apply_project_detail_status_patch(ProjectDetailPage)
apply_project_detail_audit_badge_patch(ProjectDetailPage)

app = QApplication(sys.argv)

local_ai_runtime = get_local_ai_runtime()
app.aboutToQuit.connect(local_ai_runtime.stop)

window = MainWindow()
window.show()

sys.exit(app.exec())
