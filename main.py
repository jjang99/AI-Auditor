import sys

from PySide6.QtWidgets import QApplication

from app.database.database import initialize_database
from ui.main_window import MainWindow
from ui.inspection_page import InspectionPage
from ui.inspection_rule_ui_patch import apply_inspection_rule_ui_patch


initialize_database()
apply_inspection_rule_ui_patch(InspectionPage)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
