import sys

from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("AI Auditor")
window.resize(800, 500)

layout = QVBoxLayout(window)

label = QLabel("AI Auditor UI 개발환경 정상 실행")
layout.addWidget(label)

window.show()

sys.exit(app.exec())