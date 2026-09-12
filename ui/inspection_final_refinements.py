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
#inspectionFileCount { color:#ffffff; font-size:12px; font-weight:700; }
#inspectionTableText { color:#f8fafc; font-size:11px; font-weight:600; }
#inspectionTableMuted { color:#dbe4ee; font-size:10px; font-weight:500; }
#inspectionBlueNote { color:#93c5fd; font-size:10px; font-weight:500; }
#inspectionRuleName { color:#ffffff; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#e8eef6; font-size:10px; font-weight:500; }
#inspectionSummaryTitle { color:#e8eef6; font-size:11px; font-weight:600; }
#inspectionSummaryValue { color:#ffffff; font-size:16px; font-weight:700; }
#inspectionSummaryDetail { color:#d1d9e4; font-size:9px; }
#inspectionInfoTitle { color:#93c5fd; font-size:10px; font-weight:700; }
#inspectionInfoText { color:#dbe4ee; font-size:9px; }
#inspectionSmallButton, #inspectionViewButton { color:#ffffff; font-size:10px; font-weight:650; }
#inspectionStartButton { color:#ffffff; font-size:14px; font-weight:700; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#0b1219; width:9px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#64748b; min-height:28px; border-radius:4px; }
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
#inspectionFileCount { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionTableText { color:#0f172a; font-size:11px; font-weight:600; }
#inspectionTableMuted { color:#334155; font-size:10px; font-weight:500; }
#inspectionBlueNote { color:#1d4ed8; font-size:10px; font-weight:500; }
#inspectionRuleName { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#334155; font-size:10px; font-weight:500; }
#inspectionSummaryTitle { color:#334155; font-size:11px; font-weight:600; }
#inspectionSummaryValue { color:#0f172a; font-size:16px; font-weight:700; }
#inspectionSummaryDetail { color:#475569; font-size:9px; }
#inspectionInfoTitle { color:#1d4ed8; font-size:10px; font-weight:700; }
#inspectionInfoText { color:#334155; font-size:9px; }
#inspectionSmallButton, #inspectionViewButton { color:#0f172a; font-size:10px; font-weight:650; }
#inspectionStartButton { color:#ffffff; font-size:14px; font-weight:700; }
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

        # 이 화면은 고정 창 안에서 완결되며, 페이지 자체에는 스크롤을 허용하지 않는다.
        page_scroll = self.findChild(QScrollArea, 'inspectionScroll')
        if page_scroll is not None:
            page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 고정 840x900 창에 맞춰 전체 여백/세로 높이를 잠근다.
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

        cards = self.findChildren(QFrame, 'inspectionCard')
        if len(cards) >= 4:
            cards[0].setFixedHeight(148)
            cards[1].setFixedHeight(245)
            cards[2].setFixedHeight(220)
            cards[3].setFixedHeight(178)

        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons')
        file_icon = QIcon(os.path.join(icon_dir, 'file.svg'))
        trash_icon = QIcon(os.path.join(icon_dir, 'trash.svg'))

        # 등록 파일 영역만 독립 스크롤. 4줄을 고정 표시하고 그 이상만 스크롤한다.
        file_rows = self.findChildren(QFrame, 'inspectionFileRow')
        for row in file_rows:
            row.setFixedHeight(31)
            labels = row.findChildren(QLabel)
            if len(labels) >= 4:
                name_label, path_label, size_label, delete_label = labels[:4]
                raw_name = name_label.text()
                if '  ' in raw_name:
                    raw_name = raw_name.split('  ', 1)[1]
                name_label.setText(raw_name)
                name_label.setFixedWidth(155)

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
            if parent_layout is not None and page_scroll is not table.parentWidget():
                idx = parent_layout.indexOf(table)
                if idx >= 0:
                    parent_layout.removeWidget(table)
                    visible_rows = 4
                    row_height = 31
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

        # 검사기준: 고정 폭을 줄여 우측 버튼이 다시는 잘리지 않도록 한다.
        rule_icons = self.findChildren(QLabel, 'inspectionRuleIcon')
        rule_icon_files = ['detail_grade.svg', 'detail_issues.svg', 'inspection.svg', 'reports.svg']
        for label, filename in zip(rule_icons, rule_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(18, 18)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(26)

        for label in self.findChildren(QLabel, 'inspectionRuleName'):
            label.setFixedWidth(125)
        for label in self.findChildren(QLabel, 'inspectionRuleCount'):
            label.setFixedWidth(75)
        for row in self.findChildren(QFrame, 'inspectionRuleRow'):
            row.setFixedHeight(42)
        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(66, 28)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setFixedHeight(28)

        # 요약 3개 박스 + 검사 시작 버튼이 고정 폭 안에 반드시 들어오도록 제한한다.
        summary_icon_files = ['project.svg', 'detail_issues.svg', 'play.svg']
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        for label, filename in zip(summary_icons, summary_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(24, 24)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(30, 30)

        start = next(iter(self.findChildren(QPushButton, 'inspectionStartButton')), None)
        if start is not None:
            start.setFixedSize(120, 72)

    inspection_cls.__init__ = refined_init
    inspection_cls._final_refined = True
