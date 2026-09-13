import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


def apply_inspection_visual_polish(InspectionPage):
    """Inspection UI의 확정된 잔여 시각 보정만 적용한다.

    모달 아이콘은 inspection_rule_ui_patch에서 처리하고,
    여기서는 휴지통, 검사기준 행 간격/체크박스 크기,
    모달 표의 실제 컬럼 정렬 보정을 유지한다.
    """

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table
    original_dialog_init = InspectionRulesDialog.__init__

    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
    trash_icon = QIcon(os.path.join(icon_dir, "trash.svg"))

    def polish_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            if row.layout() is not None:
                row.layout().setSpacing(11)

            count_label = row.findChild(QLabel, "inspectionRuleCount")
            if count_label is not None:
                count_label.setFixedWidth(122)

            toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle is not None:
                # 박스 크기는 작게 유지하되, 체크 표시는 더 굵고 선명하게 보이도록 한다.
                toggle.setFixedSize(14, 14)
                toggle.setStyleSheet(
                    "QPushButton#inspectionCheck {"
                    "font-size:10px; font-weight:900; padding:0;"
                    "min-width:14px; max-width:14px; min-height:14px; max-height:14px;"
                    "border-radius:3px;"
                    "}"
                    "QPushButton#inspectionCheck:checked {"
                    "color:#ffffff; background:#2563eb; border:1px solid #2563eb;"
                    "}"
                    "QPushButton#inspectionCheck:!checked {"
                    "color:transparent; background:transparent; border:1px solid #64748b;"
                    "}"
                )

        # 구분명 / 규칙수 / 설명의 실제 글자 크기를 동일하게 맞춘다.
        # 구분명은 굵기만 더 높이고, 크기는 세 항목 모두 11px로 통일한다.
        self.setStyleSheet(
            self.styleSheet()
            + """
            #inspectionRuleName,
            #inspectionRuleCount,
            #inspectionRuleDescription {
                font-size: 11px;
            }
            #inspectionRuleName {
                font-weight: 600;
            }
            #inspectionRuleCount,
            #inspectionRuleDescription {
                font-weight: 500;
            }
            """
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
