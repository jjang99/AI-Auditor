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

            # 검사기준 행 체크박스는 주변 아이콘/텍스트와 균형이 맞도록 축소한다.
            toggle = row.findChild(QPushButton, "inspectionCheck")
            if toggle is not None:
                toggle.setFixedSize(17, 17)

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

        # 본문에는 세로 스크롤바(8px)가 있으므로 헤더의 오른쪽 여백도
        # 그만큼 더 확보해야 '상태' 헤더 중심과 활성/비활성 값의 중심이 일치한다.
        table_header = dialog.findChild(QFrame, "rulesTableHeader")
        if table_header is not None and table_header.layout() is not None:
            table_header.layout().setContentsMargins(12, 0, 20, 0)

        for label in dialog.findChildren(QLabel, "rulesRowState"):
            label.setAlignment(Qt.AlignCenter)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.__init__ = patched_dialog_init
