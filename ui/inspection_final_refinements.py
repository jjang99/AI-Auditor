import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea

DARK_INSPECTION_FINAL = r'''
#inspectionSectionTitle { color:#ffffff; font-size:16px; font-weight:700; }
#inspectionFieldLabel { color:#f8fafc; font-size:12px; font-weight:600; }
#inspectionInput, #inspectionCombo { color:#ffffff; font-size:12px; }
#inspectionDuplicate { color:#fbbf24; font-size:11px; font-weight:700; }
#inspectionDuplicateButton { color:#fbbf24; font-size:11px; font-weight:700; }
#inspectionUploadText { color:#f8fafc; font-size:12px; font-weight:600; }
#inspectionFileButton { color:#ffffff; font-size:11px; font-weight:700; }
#inspectionFileCount { color:#ffffff; font-size:13px; font-weight:700; }
#inspectionTableText { color:#f8fafc; font-size:12px; font-weight:600; }
#inspectionTableMuted { color:#dbe4ee; font-size:11px; font-weight:500; }
#inspectionBlueNote { color:#93c5fd; font-size:11px; font-weight:500; }
#inspectionRuleName { color:#ffffff; font-size:13px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#e8eef6; font-size:11px; font-weight:500; }
#inspectionSummaryTitle { color:#e8eef6; font-size:12px; font-weight:600; }
#inspectionSummaryValue { color:#ffffff; font-size:17px; font-weight:700; }
#inspectionSummaryDetail { color:#d1d9e4; font-size:11px; }
#inspectionInfoTitle { color:#93c5fd; font-size:11px; font-weight:700; }
#inspectionInfoText { color:#dbe4ee; font-size:11px; }
#inspectionSmallButton, #inspectionViewButton { color:#ffffff; font-size:10px; font-weight:650; }
#inspectionStartButton { color:#ffffff; font-size:15px; font-weight:700; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#0b1219; width:10px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#64748b; min-height:30px; border-radius:5px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
'''

LIGHT_INSPECTION_FINAL = r'''
#inspectionSectionTitle { color:#0f172a; font-size:16px; font-weight:700; }
#inspectionFieldLabel { color:#1e293b; font-size:12px; font-weight:600; }
#inspectionInput, #inspectionCombo { color:#0f172a; font-size:12px; }
#inspectionDuplicate { color:#b45309; font-size:11px; font-weight:700; }
#inspectionDuplicateButton { color:#b45309; font-size:11px; font-weight:700; }
#inspectionUploadText { color:#172033; font-size:12px; font-weight:600; }
#inspectionFileButton { color:#ffffff; font-size:11px; font-weight:700; }
#inspectionFileCount { color:#0f172a; font-size:13px; font-weight:700; }
#inspectionTableText { color:#0f172a; font-size:12px; font-weight:600; }
#inspectionTableMuted { color:#334155; font-size:11px; font-weight:500; }
#inspectionBlueNote { color:#1d4ed8; font-size:11px; font-weight:500; }
#inspectionRuleName { color:#0f172a; font-size:13px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#334155; font-size:11px; font-weight:500; }
#inspectionSummaryTitle { color:#334155; font-size:12px; font-weight:600; }
#inspectionSummaryValue { color:#0f172a; font-size:17px; font-weight:700; }
#inspectionSummaryDetail { color:#475569; font-size:11px; }
#inspectionInfoTitle { color:#1d4ed8; font-size:11px; font-weight:700; }
#inspectionInfoText { color:#334155; font-size:11px; }
#inspectionSmallButton, #inspectionViewButton { color:#0f172a; font-size:10px; font-weight:650; }
#inspectionStartButton { color:#ffffff; font-size:15px; font-weight:700; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#eef2f7; width:10px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#94a3b8; min-height:30px; border-radius:5px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
'''


def apply_inspection_final_refinements(inspection_cls):
    if getattr(inspection_cls, '_final_refined', False):
        return
    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

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

        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons')
        file_icon = QIcon(os.path.join(icon_dir, 'file.svg'))
        trash_icon = QIcon(os.path.join(icon_dir, 'trash.svg'))

        file_rows = self.findChildren(QFrame, 'inspectionFileRow')
        for row in file_rows:
            row.setFixedHeight(34)
            labels = row.findChildren(QLabel)
            if len(labels) >= 4:
                name_label, path_label, size_label, delete_label = labels[:4]
                raw_name = name_label.text()
                if '  ' in raw_name:
                    raw_name = raw_name.split('  ', 1)[1]
                name_label.setText(raw_name)
                name_label.setFixedWidth(175)

                layout = row.layout()
                if layout is not None:
                    file_label = QLabel()
                    file_label.setObjectName('inspectionFileIcon')
                    file_label.setPixmap(file_icon.pixmap(QSize(17, 17)))
                    file_label.setAlignment(Qt.AlignCenter)
                    file_label.setFixedWidth(22)
                    layout.insertWidget(0, file_label)

                delete_label.setText('')
                delete_label.setPixmap(trash_icon.pixmap(QSize(17, 17)))
                delete_label.setAlignment(Qt.AlignCenter)
                delete_label.setFixedWidth(26)

        table = next(iter(self.findChildren(QFrame, 'inspectionFileTable')), None)
        if table is not None and table.parentWidget() is not None:
            parent_layout = table.parentWidget().layout()
            if parent_layout is not None:
                idx = parent_layout.indexOf(table)
                parent_layout.removeWidget(table)
                visible_rows = 5
                row_height = 34
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

        rule_icon_files = ['detail_grade.svg', 'detail_issues.svg', 'inspection.svg', 'reports.svg']
        rule_icons = self.findChildren(QLabel, 'inspectionRuleIcon')
        for label, filename in zip(rule_icons, rule_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(19, 19)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(30)

        # 요약 아이콘만 적당히 확대. 폭은 고정 창 레이아웃을 밀지 않도록 제한한다.
        summary_icon_files = ['project.svg', 'detail_issues.svg', 'play.svg']
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        for label, filename in zip(summary_icons, summary_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(28, 28)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(36, 36)

        start = next(iter(self.findChildren(QPushButton, 'inspectionStartButton')), None)
        if start is not None:
            start.setFixedSize(145, 72)

        for row in self.findChildren(QFrame, 'inspectionRuleRow'):
            row.setFixedHeight(46)
        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(74, 30)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setMinimumHeight(30)

    inspection_cls.__init__ = refined_init
    inspection_cls._final_refined = True
