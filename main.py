import sys

from PySide6.QtWidgets import QApplication

from app.database.database import initialize_database
from app.services.local_ai_runtime import LocalAIRuntimeManager
from ui.main_window import MainWindow
from ui.inspection_page import InspectionPage
from ui.inspection_rule_ui_patch import apply_inspection_rule_ui_patch
from ui.inspection_visual_polish_patch import apply_inspection_visual_polish


initialize_database()
apply_inspection_rule_ui_patch(InspectionPage)
apply_inspection_visual_polish(InspectionPage)

app = QApplication(sys.argv)

local_ai_runtime = LocalAIRuntimeManager()
app.aboutToQuit.connect(local_ai_runtime.stop)

window = MainWindow()
window.show()

sys.exit(app.exec())
