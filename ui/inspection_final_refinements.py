import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton, QScrollArea

DARK_INSPECTION_FINAL = r'''
#inspectionTitle { color:#ffffff; font-size:26px; font-weight:800; }
#inspectionDescription { color:#dbe4ee; font-size:12px; font-weight:500; }
#inspectionCard { border:1px solid #3a4758; border-radius:9px; }
#inspectionSectionTitle { color:#ffffff; font-size:16px; font-weight:750; }
#inspectionFieldLabel { color:#f1f5f9; font-size:12px; font-weight:650; }
#inspectionInput, #inspectionCombo { color:#ffffff; font-size:12px; font-weight:500; border-color:#475569; min-height:30px; max-height:30px; }
#inspectionCombo { padding-top:0px; padding-bottom:0px; }
#inspectionDuplicate { color:#fbbf24; font-size:10px; font-weight:700; }
#inspectionDuplicateButton { color:#fbbf24; font-size:10px; font-weight:700; }
#inspectionUploadBox { border-color:#526274; }
#inspectionUploadText { color:#f8fafc; font-size:12px; font-weight:600; }
#inspectionFileButton { color:#ffffff; font-size:11px; font-weight:700; }
#inspectionFileCount { color:#ffffff; font-size:12px; font-weight:750; }
#inspectionFileTable { border:none; border-radius:0px; background:transparent; }
#inspectionFileRow { border-bottom:1px solid #2f3c4c; }
#inspectionTableText { color:#ffffff; font-size:11px; font-weight:650; }
#inspectionTableMuted { color:#d7e0ea; font-size:11px; font-weight:550; }
#inspectionBlueNote { color:#7db7ff; font-size:10px; font-weight:600; }
#inspectionRuleRow { border-color:#3a4758; }
#inspectionRuleName { color:#ffffff; font-size:12px; font-weight:750; }
#inspectionRuleCount, #inspectionRuleDescription { color:#e2e8f0; font-size:10px; font-weight:550; }
#inspectionSummaryBox { border-color:#3a4758; }
#inspectionSummaryTitle { color:#e8eef6; font-size:11px; font-weight:650; }
#inspectionSummaryValue { color:#ffffff; font-size:16px; font-weight:750; }
#inspectionSummaryDetail { color:#cbd5e1; font-size:9px; font-weight:500; }
#inspectionInfoBox { border-color:#3a4758; }
#inspectionInfoTitle { color:#7db7ff; font-size:11px; font-weight:700; }
#inspectionInfoText { color:#e2e8f0; font-size:10px; font-weight:550; }
#inspectionSmallButton, #inspectionViewButton { color:#f8fafc; font-size:10px; font-weight:650; border-color:#475569; }
#inspectionStartButton { color:#ffffff; font-size:16px; font-weight:800; }
#inspectionFileScroll { background:#0d1721; border:1px solid #3a4758; border-radius:7px; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#0b1219; width:9px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#64748b; min-height:28px; border-radius:4px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
'''

LIGHT_INSPECTION_FINAL = r'''
#inspectionTitle { color:#0b1220; font-size:26px; font-weight:800; }
#inspectionDescription { color:#263548; font-size:12px; font-weight:600; }
#inspectionCard { background:#ffffff; border:1px solid #b6c3d2; border-radius:9px; }
#inspectionSectionTitle { color:#0b1220; font-size:16px; font-weight:800; }
#inspectionFieldLabel { color:#162033; font-size:12px; font-weight:700; }
#inspectionInput, #inspectionCombo { color:#0b1220; background:#ffffff; font-size:12px; font-weight:550; border:1px solid #9eacbd; min-height:30px; max-height:30px; }
#inspectionCombo { padding-top:0px; padding-bottom:0px; }
#inspectionDuplicate { color:#9a3412; font-size:10px; font-weight:750; }
#inspectionDuplicateButton { color:#9a3412; font-size:10px; font-weight:750; }
#inspectionUploadBox { background:#f8fafc; border-color:#8fa0b4; }
#inspectionUploadText { color:#162033; font-size:12px; font-weight:650; }
#inspectionFileButton { color:#ffffff; font-size:11px; font-weight:700; }
#inspectionFileCount { color:#0b1220; font-size:12px; font-weight:800; }
#inspectionFileTable { border:none; border-radius:0px; background:transparent; }
#inspectionFileRow { border-bottom:1px solid #d6dee8; }
#inspectionTableText { color:#0b1220; font-size:11px; font-weight:700; }
#inspectionTableMuted { color:#263548; font-size:11px; font-weight:600; }
#inspectionBlueNote { color:#1e40af; font-size:10px; font-weight:650; }
#inspectionRuleRow { background:#ffffff; border-color:#b8c4d2; }
#inspectionRuleName { color:#0b1220; font-size:12px; font-weight:800; }
#inspectionRuleCount, #inspectionRuleDescription { color:#243247; font-size:10px; font-weight:600; }
#inspectionSummaryBox { background:#f8fafc; border-color:#b8c4d2; }
#inspectionSummaryTitle { color:#253247; font-size:11px; font-weight:700; }
#inspectionSummaryValue { color:#0b1220; font-size:16px; font-weight:800; }
#inspectionSummaryDetail { color:#334155; font-size:9px; font-weight:600; }
#inspectionInfoBox { background:#f8fafc; border-color:#b8c4d2; }
#inspectionInfoTitle { color:#1e40af; font-size:11px; font-weight:750; }
#inspectionInfoText { color:#263548; font-size:10px; font-weight:600; }
#inspectionSmallButton, #inspectionViewButton { color:#111827; background:#ffffff; font-size:10px; font-weight:700; border:1px solid #9eacbd; }
#inspectionStartButton { color:#ffffff; font-size:16px; font-weight:800; }
#inspectionFileScroll { background:#ffffff; border:1px solid #b7c4d3; border-radius:7px; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#edf1f6; width:9px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#7f8da0; min-height:28px; border-radius:4px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
'''


def apply_inspection_final_refinements(inspection_cls):
    if getattr(inspection_cls, '_final_refined', False):
        return
    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        page_scroll = self.findChild(QScrollArea, 'inspectionScroll')
        if page_scroll is not None:
            page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        if hasattr(self, 'main_layout'):
            self.main_layout.setContentsMargins(14, 9, 10, 10)
            self.main_layout.setSpacing(10)
        for button in self.findChildren(QPushButton, 'inspectionHelpButton'):
            button.hide()
        titles = self.findChildren(QLabel, 'inspectionSectionTitle')
        for i, text in enumerate(['1. 프로젝트 정보', '2. 검사 대상 파일', '3. 검사 기준 선택', '4. 검사 준비 요약']):
            if i < len(titles):
                titles[i].setText(text)
        cards = self.findChildren(QFrame, 'inspectionCard')
        if len(cards) >= 4:
            # Keep the overall page height stable: give the five rule rows more
            # breathing room and recover the same space from the summary card.
            for card, height in zip(cards[:4], [175, 221, 234, 160]):
                card.setFixedHeight(height)
        for label in self.findChildren(QLabel, 'inspectionFieldLabel'):
            label.setFixedHeight(17)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            if label.text().startswith('Project Name'):
                label.setText('Project Name <span style="color:#ef4444;font-weight:700;">*</span>')
                label.setTextFormat(Qt.RichText)
        for edit in self.findChildren(QLineEdit, 'inspectionInput'):
            edit.setMinimumHeight(30)
            edit.setMaximumHeight(30)
            edit.setFixedHeight(30)
        for combo in self.findChildren(QComboBox, 'inspectionCombo'):
            combo.setMinimumHeight(30)
            combo.setMaximumHeight(30)
            combo.setFixedHeight(30)
            combo.setContentsMargins(0, 0, 0, 0)
        if cards and cards[0].layout() is not None:
            project_layout = cards[0].layout()
            project_layout.setContentsMargins(14, 8, 14, 12)
            project_layout.setSpacing(7)
            project_layout.setAlignment(Qt.AlignTop)
            if project_layout.count() > 1 and project_layout.itemAt(1).layout() is not None:
                form_row = project_layout.itemAt(1).layout()
                form_row.setSpacing(16)
                form_row.setAlignment(Qt.AlignTop)
                left_col = form_row.itemAt(0).layout() if form_row.count() > 0 else None
                right_col = form_row.itemAt(1).layout() if form_row.count() > 1 else None
                for col in (left_col, right_col):
                    if col is not None:
                        col.setContentsMargins(0, 0, 0, 0)
                        col.setSpacing(5)
                        col.setAlignment(Qt.AlignTop)
                if right_col is not None and right_col.count() > 2:
                    item = right_col.itemAt(2)
                    if item.spacerItem() is not None:
                        item.spacerItem().changeSize(0, 24)
                    elif item.widget() is not None:
                        item.widget().setFixedHeight(24)
                    right_col.invalidate()
                    right_col.activate()
        for label in self.findChildren(QLabel, 'inspectionDuplicate'):
            label.setFixedHeight(24)
            label.setContentsMargins(0, 5, 0, 1)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for button in self.findChildren(QPushButton, 'inspectionDuplicateButton'):
            button.setFixedHeight(24)
        if len(cards) >= 2 and cards[1].layout() is not None:
            lay = cards[1].layout()
            lay.setContentsMargins(14, 7, 14, 11)
            lay.setSpacing(5)
            lay.setAlignment(Qt.AlignTop)
        for box in self.findChildren(QFrame, 'inspectionUploadBox'):
            box.setFixedHeight(44)
            if box.layout() is not None:
                box.layout().setContentsMargins(0, 0, 0, 0)
                box.layout().setSpacing(16)
                box.layout().setAlignment(Qt.AlignCenter)
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons')
        file_icon = QIcon(os.path.join(icon_dir, 'file.svg'))
        trash_icon = QIcon(os.path.join(icon_dir, 'trash.svg'))
        file_rows = self.findChildren(QFrame, 'inspectionFileRow')
        for row in file_rows:
            row.setFixedHeight(30)
            labels = row.findChildren(QLabel)
            if len(labels) >= 4:
                name_label, path_label, size_label, delete_label = labels[:4]
                raw_name = name_label.text()
                if '  ' in raw_name:
                    raw_name = raw_name.split('  ', 1)[1]
                name_label.setText(raw_name)
                name_label.setFixedWidth(150)
                layout = row.layout()
                if layout is not None:
                    file_label = QLabel()
                    file_label.setObjectName('inspectionFileIcon')
                    file_label.setPixmap(file_icon.pixmap(QSize(16, 16)))
                    file_label.setAlignment(Qt.AlignCenter)
                    file_label.setFixedWidth(20)
                    layout.insertWidget(0, file_label)
                path_label.setMinimumHeight(18)
                path_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                size_label.setFixedWidth(50)
                delete_label.setText('')
                delete_label.setPixmap(trash_icon.pixmap(QSize(16, 16)))
                delete_label.setAlignment(Qt.AlignCenter)
                delete_label.setFixedWidth(24)
        table = next(iter(self.findChildren(QFrame, 'inspectionFileTable')), None)
        if table is not None and table.parentWidget() is not None:
            parent_layout = table.parentWidget().layout()
            if parent_layout is not None:
                idx = parent_layout.indexOf(table)
                if idx >= 0:
                    parent_layout.removeWidget(table)
                    row_height = 30
                    viewport_height = 92
                    table.setMinimumHeight(max(viewport_height, len(file_rows) * row_height))
                    scroll = QScrollArea()
                    scroll.setObjectName('inspectionFileScroll')
                    scroll.setWidgetResizable(True)
                    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    scroll.setFixedHeight(viewport_height)
                    scroll.setWidget(table)
                    parent_layout.insertWidget(idx, scroll)
        for label in self.findChildren(QLabel):
            if label.text() in ('외 14개 파일', '총 12.3 MB'):
                label.hide()
                label.setFixedHeight(0)
        rule_icon_files = [
            'inspection.svg',
            'why_consistency.svg',
            'why_impact.svg',
            'why_fp.svg',
            'rule_ai.svg',
        ]
        rule_icons = self.findChildren(QLabel, 'inspectionRuleIcon')
        for label, filename in zip(rule_icons, rule_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(18, 18)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(26)
        for label in self.findChildren(QLabel, 'inspectionRuleName'):
            label.setFixedWidth(120)
        for label in self.findChildren(QLabel, 'inspectionRuleCount'):
            label.setFixedWidth(70)
        for row in self.findChildren(QFrame, 'inspectionRuleRow'):
            row.setFixedHeight(40)
        if len(cards) >= 3 and cards[2].layout() is not None:
            cards[2].layout().setSpacing(6)
        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(66, 27)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setFixedHeight(27)
        summary_icon_files = ['project.svg', 'detail_issues.svg', 'play.svg']
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        for label, filename in zip(summary_icons, summary_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(24, 24)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(30, 30)
        for box in self.findChildren(QFrame, 'inspectionSummaryBox'):
            box.setFixedHeight(54)
        start = next(iter(self.findChildren(QPushButton, 'inspectionStartButton')), None)
        if start is not None:
            start.setFixedSize(118, 54)
        if len(cards) >= 4 and cards[3].layout() is not None:
            cards[3].layout().setContentsMargins(14, 8, 14, 8)
            cards[3].layout().setSpacing(6)
        for box in self.findChildren(QFrame, 'inspectionInfoBox'):
            box.setFixedHeight(50)
            if box.layout() is not None:
                lay = box.layout()
                lay.setContentsMargins(12, 4, 12, 4)
                lay.setSpacing(1)
                lay.setAlignment(Qt.AlignVCenter)
        for label in self.findChildren(QLabel, 'inspectionInfoTitle'):
            label.setFixedHeight(14)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for label in self.findChildren(QLabel, 'inspectionInfoText'):
            label.setWordWrap(True)
            label.setFixedHeight(28)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    inspection_cls.__init__ = refined_init
    inspection_cls._final_refined = True
