import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


def apply_inspection_visual_polish(InspectionPage):
    """Inspection UI의 확정된 잔여 시각 보정만 적용한다."""

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table
    original_refresh_rule_summary = InspectionPage._refresh_rule_summary
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

            # 규칙 행의 색상/폰트는 InspectionPage.apply_rule_text_theme()에서
            # 현재 Dark/Light 테마에 맞춰 관리한다. 여기서 색상을 다시 지정하면
            # 선택 상태 갱신 후 Light Mode가 어두운 테마 색으로 되돌아갈 수 있다.
            toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle is not None:
                # 선택 상태가 바뀐 뒤에도 동일한 크기/체크 표시가 유지되도록 항상 재적용한다.
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

    def patched_refresh_rule_summary(self):
        # inspection_rule_ui_patch가 선택 변경 시 14px로 다시 지정하므로,
        # 원래 상태 갱신이 끝난 직후 최종 시각값(15px)을 다시 적용한다.
        original_refresh_rule_summary(self)
        polish_rule_rows(self)

    def patched_dialog_init(dialog, *args, **kwargs):
        original_dialog_init(dialog, *args, **kwargs)

        table_header = dialog.findChild(QFrame, "rulesTableHeader")
        if table_header is not None and table_header.layout() is not None:
            table_header.layout().setContentsMargins(12, 0, 20, 0)

        for label in dialog.findChildren(QLabel, "rulesRowState"):
            label.setAlignment(Qt.AlignCenter)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionPage._refresh_rule_summary = patched_refresh_rule_summary
    InspectionRulesDialog.__init__ = patched_dialog_init
