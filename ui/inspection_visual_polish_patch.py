import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


def apply_inspection_visual_polish(InspectionPage):
    """Inspection UI의 확정된 잔여 시각 보정만 적용한다."""

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table
    original_dialog_init = InspectionRulesDialog.__init__

    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
    trash_icon = QIcon(os.path.join(icon_dir, "trash.svg"))

    def polish_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            if row.layout() is not None:
                row.layout().setSpacing(11)

            name_label = row.findChild(QLabel, "inspectionRuleName")
            count_label = row.findChild(QLabel, "inspectionRuleCount")
            desc_label = row.findChild(QLabel, "inspectionRuleDescription")

            if count_label is not None:
                count_label.setFixedWidth(122)

            # 규칙수/설명은 QSS 숫자로 추정하지 않고,
            # 실제 구분명 QLabel의 폰트를 그대로 복사해 크기를 완전히 동일하게 맞춘다.
            if name_label is not None:
                name_font = QFont(name_label.font())
                if count_label is not None:
                    count_font = QFont(name_font)
                    count_font.setWeight(QFont.Medium)
                    count_label.setFont(count_font)
                if desc_label is not None:
                    desc_font = QFont(name_font)
                    desc_font.setWeight(QFont.Medium)
                    desc_label.setFont(desc_font)

            toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle is not None:
                # 작은 박스는 유지하고, 더 굵은 체크 문자(✔)를 사용해 식별성을 높인다.
                toggle.setFixedSize(14, 14)
                toggle.setText("✔" if toggle.isChecked() else "")
                check_font = QFont(toggle.font())
                check_font.setPixelSize(10)
                check_font.setWeight(QFont.Black)
                toggle.setFont(check_font)
                toggle.setStyleSheet(
                    "QPushButton#inspectionCheck {"
                    "padding:0; min-width:14px; max-width:14px; min-height:14px; max-height:14px;"
                    "border-radius:3px;"
                    "}"
                    "QPushButton#inspectionCheck:checked {"
                    "color:#ffffff; background:#2563eb; border:1px solid #2563eb;"
                    "}"
                    "QPushButton#inspectionCheck:!checked {"
                    "color:transparent; background:transparent; border:1px solid #64748b;"
                    "}"
                )

    def apply_trash_icon(self):
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

    def patched_dialog_init(dialog, *args, **kwargs):
        original_dialog_init(dialog, *args, **kwargs)

        table_header = dialog.findChild(QFrame, "rulesTableHeader")
        if table_header is not None and table_header.layout() is not None:
            table_header.layout().setContentsMargins(12, 0, 20, 0)

        for label in dialog.findChildren(QLabel, "rulesRowState"):
            label.setAlignment(Qt.AlignCenter)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.__init__ = patched_dialog_init
