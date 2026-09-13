import os

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


CATEGORY_ICON_FILES = {
    "보안 취약점": "rule_security.svg",
    "코드 품질": "rule_quality.svg",
    "AI 특화 검증": "rule_ai.svg",
    "성능 및 효율성": "rule_performance.svg",
}


def apply_inspection_visual_polish(InspectionPage):
    """Inspection UI의 잔여 시각 보정만 적용한다."""

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table
    original_dialog_show_event = InspectionRulesDialog.showEvent

    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
    trash_icon = QIcon(os.path.join(icon_dir, "trash.svg"))

    def polish_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            if row.layout() is not None:
                row.layout().setSpacing(11)

            count_label = row.findChild(QLabel, "inspectionRuleCount")
            if count_label is not None:
                count_label.setFixedWidth(122)

    def apply_trash_icon(self):
        # 글자 크기와 균형이 맞도록 이전 11px보다 한 단계 키운다.
        for button in self.findChildren(QPushButton, "inspectionSmallButton"):
            if button.text() == "전체 삭제":
                button.setIcon(trash_icon)
                button.setIconSize(QSize(15, 15))

        for button in self.findChildren(QPushButton, "inspectionFileDeleteButton"):
            button.setText("")
            button.setIcon(trash_icon)
            button.setIconSize(QSize(16, 16))

    def patched_init(self):
        original_init(self)
        polish_rule_rows(self)
        apply_trash_icon(self)

    def patched_refresh_file_table(self):
        original_refresh_file_table(self)
        apply_trash_icon(self)

    def patched_dialog_show_event(dialog, event):
        # 문자 아이콘은 Windows 글꼴/렌더링에 따라 사라질 수 있으므로
        # 모달 표시 직전에 실제 SVG pixmap을 기존 아이콘 QLabel에 직접 넣는다.
        title = dialog.findChild(QLabel, "rulesDialogTitle")
        category = title.text() if title is not None else ""
        icon_label = dialog.findChild(QLabel, "rulesDialogShieldIcon")
        icon_file = CATEGORY_ICON_FILES.get(category)

        if icon_label is not None and icon_file:
            icon_label.show()
            icon_label.clear()
            icon_label.setText("")
            icon_label.setFixedSize(30, 30)
            icon_label.setPixmap(QIcon(os.path.join(icon_dir, icon_file)).pixmap(QSize(22, 22)))

        # 이전 패치에서 만들어졌을 수 있는 대체 문자 아이콘은 숨긴다.
        replacement = dialog.findChild(QLabel, "rulesDialogCategoryIcon")
        if replacement is not None:
            replacement.hide()

        original_dialog_show_event(dialog, event)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.showEvent = patched_dialog_show_event
