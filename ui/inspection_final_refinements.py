import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea

DARK_INSPECTION_FINAL = r'''
#inspectionTitle { color:#ffffff; font-size:26px; font-weight:800; }
#inspectionDescription { color:#dbe4ee; font-size:12px; font-weight:500; }
#inspectionCard { border:1px solid #3a4758; border-radius:9px; }
#inspectionSectionTitle { color:#ffffff; font-size:16px; font-weight:750; }
#inspectionFieldLabel { color:#f1f5f9; font-size:12px; font-weight:650; }
#inspectionInput, #inspectionCombo { color:#ffffff; font-size:12px; font-weight:500; border-color:#475569; }
#inspectionDuplicate { color:#fbbf24; font-size:10px; font-weight:700; }
#inspectionDuplicateButton { color:#fbbf24; font-size:10px; font-weight:700; }
#inspectionUploadBox { border-color:#526274; }
#inspectionUploadText { color:#f8fafc; font-size:12px; font-weight:600; }
#inspectionFileButton { color:#ffffff; font-size:11px; font-weight:700; }
#inspectionFileCount { color:#ffffff; font-size:12px; font-weight:750; }
#inspectionFileTable { border-color:#3a4758; }
#inspectionFileRow { border-bottom:1px solid #2f3c4c; }
#inspectionTableText { color:#ffffff; font-size:11px; font-weight:650; }
#inspectionTableMuted { color:#cbd5e1; font-size:10px; font-weight:500; }
#inspectionBlueNote { color:#7db7ff; font-size:10px; font-weight:600; }
#inspectionRuleRow { border-color:#3a4758; }
#inspectionRuleName { color:#ffffff; font-size:12px; font-weight:750; }
#inspectionRuleCount, #inspectionRuleDescription { color:#e2e8f0; font-size:10px; font-weight:550; }
#inspectionSummaryBox { border-color:#3a4758; }
#inspectionSummaryTitle { color:#e8eef6; font-size:11px; font-weight:650; }
#inspectionSummaryValue { color:#ffffff; font-size:16px; font-weight:750; }
#inspectionSummaryDetail { color:#cbd5e1; font-size:9px; font-weight:500; }
#inspectionInfoBox { border-color:#3a4758; }
#inspectionInfoTitle { color:#7db7ff; font-size:10px; font-weight:700; }
#inspectionInfoText { color:#cbd5e1; font-size:9px; font-weight:500; }
#inspectionSmallButton, #inspectionViewButton { color:#f8fafc; font-size:10px; font-weight:650; border-color:#475569; }
#inspectionStartButton { color:#ffffff; font-size:14px; font-weight:750; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#0b1219; width:9px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#64748b; min-height:28px; border-radius:4px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
'''

LIGHT_INSPECTION_FINAL = r'''
#inspectionTitle { color:#0f172a; font-size:26px; font-weight:800; }
#inspectionDescription { color:#334155; font-size:12px; font-weight:500; }
#inspectionCard { border:1px solid #cbd5e1; border-radius:9px; }
#inspectionSectionTitle { color:#0f172a; font-size:16px; font-weight:750; }
#inspectionFieldLabel { color:#1e293b; font-size:12px; font-weight:650; }
#inspectionInput, #inspectionCombo { color:#0f172a; font-size:12px; font-weight:500; border-color:#b8c4d3; }
#inspectionDuplicate { color:#b45309; font-size:10px; font-weight:700; }
#inspectionDuplicateButton { color:#b45309; font-size:10px; font-weight:700; }
#inspectionUploadBox { border-color:#94a3b8; }
#inspectionUploadText { color:#172033; font-size:12px; font-weight:600; }
#inspectionFileButton { color:#ffffff; font-size:11px; font-weight:700; }
#inspectionFileCount { color:#0f172a; font-size:12px; font-weight:750; }
#inspectionFileTable { border-color:#cbd5e1; }
#inspectionFileRow { border-bottom:1px solid #e2e8f0; }
#inspectionTableText { color:#0f172a; font-size:11px; font-weight:650; }
#inspectionTableMuted { color:#475569; font-size:10px; font-weight:500; }
#inspectionBlueNote { color:#1d4ed8; font-size:10px; font-weight:600; }
#inspectionRuleRow { border-color:#cbd5e1; }
#inspectionRuleName { color:#0f172a; font-size:12px; font-weight:750; }
#inspectionRuleCount, #inspectionRuleDescription { color:#334155; font-size:10px; font-weight:550; }
#inspectionSummaryBox { border-color:#cbd5e1; }
#inspectionSummaryTitle { color:#334155; font-size:11px; font-weight:650; }
#inspectionSummaryValue { color:#0f172a; font-size:16px; font-weight:750; }
#inspectionSummaryDetail { color:#475569; font-size:9px; font-weight:500; }
#inspectionInfoBox { border-color:#cbd5e1; }
#inspectionInfoTitle { color:#1d4ed8; font-size:10px; font-weight:700; }
#inspectionInfoText { color:#475569; font-size:9px; font-weight:500; }
#inspectionSmallButton, #inspectionViewButton { color:#0f172a; font-size:10px; font-weight:650; border-color:#b8c4d3; }
#inspectionStartButton { color:#ffffff; font-size:14px; font-weight:750; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#eef2f7; width:9px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#94a3b8; min-height:28px; border-radius:4px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
'''


def apply_inspection_final_refinements(inspection_cls):
    if getattr(inspection_cls, '_final_refined', False):
        return
    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # Freeze principle: Inspection is a one-screen page.
        # Only the registered-file list may scroll.
        page_scroll = self.findChild(QScrollArea, 'inspectionScroll')
        if page_scroll is not None:
            page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        if hasattr(self, 'main_layout'):
            self.main_layout.setContentsMargins(14, 10, 10, 10)
            self.main_layout.setSpacing(7)

        for button in self.findChildren(QPushButton, 'inspectionHelpButton'):
            button.hide()

        titles = self.findChildren(QLabel, 'inspectionSectionTitle')
        clean_titles = ['1. 프로젝트 정보', '2. 검사 대상 파일', '3. 검사 기준 선택', '4. 검사 준비 요약']
        for i, title in enumerate(titles[:4]):
            title.setText(clean_titles[i])

        for label in self.findChildren(QLabel, 'inspectionFieldLabel'):
            if label.text().startswith('Project Name'):
                label.setText('Project Name <span style="color:#ef4444;font-weight:700;">*</span>')
                label.setTextFormat(Qt.RichText)

        # Balanced card heights inside the fixed 840x900 application window.
        cards = self.findChildren(QFrame, 'inspectionCard')
        if len(cards) >= 4:
            cards[0].setFixedHeight(145)
            cards[1].setFixedHeight(240)
            cards[2].setFixedHeight(214)
            cards[3].setFixedHeight(174)

        # Make inner containers visually consistent and compact.
        upload_boxes = self.findChildren(QFrame, 'inspectionUploadBox')
        for box in upload_boxes:
            box.setFixedHeight(48)

        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons')
        file_icon = QIcon(os.path.join(icon_dir, 'file.svg'))
        trash_icon = QIcon(os.path.join(icon_dir, 'trash.svg'))

        # Registered files: dedicated scroll only here.
        # Show 3 rows cleanly; extra files scroll without overlapping footer text.
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
                    visible_rows = 3
                    row_height = 30
                    viewport_height = visible_rows * row_height + 2
                    table.setMinimumHeight(max(viewport_height, len(file_rows) * row_height))
                    scroll = QScrollArea()
                    scroll.setObjectName('inspectionFileScroll')
                    scroll.setWidgetResizable(True)
                    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    scroll.setFixedHeight(viewport_height)
                    scroll.setWidget(table)
                    parent_layout.insertWidget(idx, scroll)

        # Rule rows: preserve readability while locking the right edge.
        rule_icon_files = ['detail_grade.svg', 'detail_issues.svg', 'inspection.svg', 'reports.svg']
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
        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(66, 28)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setFixedHeight(28)

        # Summary row: keep all four boxes completely inside the viewport.
        summary_icon_files = ['project.svg', 'detail_issues.svg', 'play.svg']
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        for label, filename in zip(summary_icons, summary_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(24, 24)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(30, 30)

        for box in self.findChildren(QFrame, 'inspectionSummaryBox'):
            box.setFixedHeight(68)

        start = next(iter(self.findChildren(QPushButton, 'inspectionStartButton')), None)
        if start is not None:
            start.setFixedSize(118, 68)

        info_boxes = self.findChildren(QFrame, 'inspectionInfoBox')
        for box in info_boxes:
            box.setFixedHeight(52)

    inspection_cls.__init__ = refined_init
    inspection_cls._final_refined = True
