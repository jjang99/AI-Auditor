import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
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

            # 부모 QSS의 기존 font-size가 setFont보다 우선 적용될 수 있으므로,
            # 세 텍스트에 인라인 QSS를 직접 지정해 실제 렌더링 크기를 확실히 통일한다.
            if name_label is not None:
                name_label.setStyleSheet(
                    "color:#f1f5f9; font-size:11px; font-weight:600;"
                )
            if count_label is not None:
                count_label.setStyleSheet(
                    "color:#aebaca; font-size:11px; font-weight:600;"
                )
            if desc_label is not None:
                desc_label.setStyleSheet(
                    "color:#aebaca; font-size:11px; font-weight:600;"
                )

            toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle is not None:
                # 박스는 기존 17px보다 작게 유지하되, 체크 문자는 거의 박스를 채우도록 키운다.
                toggle.setFixedSize(15, 15)
                toggle.setText("✓" if toggle.isChecked() else "")
                toggle.setStyleSheet(
                    "QPushButton#inspectionCheck {"
                    "padding:0; min-width:15px; max-width:15px; min-height:15px; max-height:15px;"
                    "border-radius:3px; font-family:'Segoe UI Symbol'; font-size:12px; font-weight:900;"
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
