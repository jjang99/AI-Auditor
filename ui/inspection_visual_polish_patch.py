import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


CATEGORY_ICONS = {
    "보안 취약점": "♢",
    "코드 품질": "</>",
    "AI 특화 검증": "AI",
    "성능 및 효율성": "◌",
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
                # '32 / 32개 규칙'처럼 문구가 길어진 뒤 설명과 붙어 보이지 않도록
                # 기존 95px보다 여유 폭을 확보한다.
                count_label.setFixedWidth(122)

    def apply_trash_icon(self):
        for button in self.findChildren(QPushButton, "inspectionSmallButton"):
            if button.text() == "전체 삭제":
                button.setIcon(trash_icon)
                button.setIconSize(QSize(11, 11))

        for button in self.findChildren(QPushButton, "inspectionFileDeleteButton"):
            button.setText("")
            button.setIcon(trash_icon)
            button.setIconSize(QSize(11, 11))

    def patched_init(self):
        original_init(self)
        polish_rule_rows(self)
        apply_trash_icon(self)

    def patched_refresh_file_table(self):
        original_refresh_file_table(self)
        apply_trash_icon(self)

    def patched_dialog_show_event(dialog, event):
        title = dialog.findChild(QLabel, "rulesDialogTitle")
        category = title.text() if title is not None else ""
        old_icon = dialog.findChild(QLabel, "rulesDialogShieldIcon")

        # 기존 QLabel의 pixmap/text 전환이 환경에 따라 표시되지 않는 문제가 있어,
        # 실제 표시 직전에 별도 QLabel을 만들어 헤더 레이아웃에 삽입한다.
        if old_icon is not None and dialog.header_drag_area.layout() is not None:
            old_icon.hide()
            replacement = dialog.findChild(QLabel, "rulesDialogCategoryIcon")
            if replacement is None:
                replacement = QLabel(CATEGORY_ICONS.get(category, ""), dialog.header_drag_area)
                replacement.setObjectName("rulesDialogCategoryIcon")
                replacement.setAlignment(Qt.AlignCenter)
                replacement.setFixedSize(30, 30)
                replacement.setStyleSheet(
                    "color:#60a5fa; background:transparent; border:none; "
                    "font-size:13px; font-weight:700;"
                )
                dialog.header_drag_area.layout().insertWidget(0, replacement)
            else:
                replacement.setText(CATEGORY_ICONS.get(category, ""))
                replacement.show()

        original_dialog_show_event(dialog, event)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.showEvent = patched_dialog_show_event
