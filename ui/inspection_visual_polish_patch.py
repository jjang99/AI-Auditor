import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


def apply_inspection_visual_polish(InspectionPage):
    """Inspection UI의 잔여 시각 보정만 적용한다."""

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table
    original_dialog_exec = InspectionRulesDialog.exec

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
        # 휴지통은 현재 확정된 크기를 유지한다.
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

    def patched_dialog_exec(dialog):
        """모달이 실제 표시되기 직전에 아이콘과 표 헤더 정렬을 확정한다."""
        title = dialog.findChild(QLabel, "rulesDialogTitle")
        category = title.text() if title is not None else ""
        modal_icon = dialog.findChild(QLabel, "rulesDialogShieldIcon")

        # 검사기준 선택 카드에서 실제로 보이는 아이콘 QLabel의 텍스트/폰트를 그대로 가져온다.
        source_icon = None
        page = dialog.parentWidget()
        if page is not None:
            for row in page.findChildren(QFrame, "inspectionRuleRow"):
                if row.property("ruleCategory") == category:
                    source_icon = row.findChild(QLabel, "inspectionRuleIcon")
                    break

        if modal_icon is not None and source_icon is not None:
            modal_icon.clear()
            modal_icon.setText(source_icon.text())
            modal_icon.setAlignment(Qt.AlignCenter)
            modal_icon.setFixedSize(42, 34)

            source_font = source_icon.font()
            source_font.setPixelSize(20)
            source_font.setBold(True)
            modal_icon.setFont(source_font)
            modal_icon.setStyleSheet(
                "color:#60a5fa; background:transparent; border:none;"
            )
            modal_icon.show()

        # 이전 시도에서 생성된 대체 아이콘이 있으면 숨긴다.
        replacement = dialog.findChild(QLabel, "rulesDialogCategoryIcon")
        if replacement is not None:
            replacement.hide()

        # 규칙명 / 설명 / 상태 헤더를 실제 표시 직전에 가운데 정렬한다.
        for label in dialog.findChildren(QLabel, "rulesTableHeaderText"):
            label.setAlignment(Qt.AlignCenter)

        return original_dialog_exec(dialog)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.exec = patched_dialog_exec
