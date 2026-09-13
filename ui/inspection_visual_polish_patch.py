import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


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
        # 확정된 휴지통 크기 유지
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
        # 먼저 원래 모달 표시 처리를 끝낸 뒤 최종 표시 상태를 덮어쓴다.
        original_dialog_show_event(dialog, event)

        title = dialog.findChild(QLabel, "rulesDialogTitle")
        category = title.text() if title is not None else ""
        modal_icon = dialog.findChild(QLabel, "rulesDialogShieldIcon")

        # 별도 SVG/임의 아이콘을 사용하지 않고,
        # 검사기준 선택 카드에서 실제로 보이는 아이콘 텍스트를 그대로 복사한다.
        source_icon = None
        page = dialog.parentWidget()
        if page is not None:
            for row in page.findChildren(QFrame, "inspectionRuleRow"):
                if row.property("ruleCategory") == category:
                    source_icon = row.findChild(QLabel, "inspectionRuleIcon")
                    break

        if modal_icon is not None and source_icon is not None:
            modal_icon.clear()
            modal_icon.setPixmap(None)
            modal_icon.setText(source_icon.text())
            modal_icon.setAlignment(Qt.AlignCenter)
            modal_icon.setFixedSize(40, 34)

            # 타이틀(20px)과 비슷한 시각 크기로 맞춘다.
            font = source_icon.font()
            font.setPixelSize(20)
            font.setBold(True)
            modal_icon.setFont(font)
            modal_icon.setStyleSheet(
                "color:#60a5fa; background:transparent; border:none;"
            )
            modal_icon.show()

        # 이전 보정 과정에서 생성된 대체 아이콘이 남아 있다면 숨긴다.
        replacement = dialog.findChild(QLabel, "rulesDialogCategoryIcon")
        if replacement is not None:
            replacement.hide()

        # 모달 표 헤더의 '규칙명 / 설명 / 상태'를 가운데 정렬한다.
        for label in dialog.findChildren(QLabel, "rulesTableHeaderText"):
            label.setAlignment(Qt.AlignCenter)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.showEvent = patched_dialog_show_event
