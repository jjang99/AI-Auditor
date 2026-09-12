import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea

DARK_INSPECTION_FINAL = r'''
#inspectionSectionTitle { color:#ffffff; font-size:16px; font-weight:700; }
#inspectionFieldLabel { color:#f1f5f9; font-size:12px; font-weight:600; }
#inspectionInput, #inspectionCombo { color:#ffffff; font-size:12px; }
#inspectionFileCount { color:#ffffff; font-size:12px; font-weight:700; }
#inspectionTableText { color:#ffffff; font-size:11px; font-weight:500; }
#inspectionTableMuted { color:#d7e0ea; font-size:10px; }
#inspectionBlueNote { color:#7db7ff; font-size:10px; font-weight:500; }
#inspectionRuleName { color:#ffffff; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#e2e8f0; font-size:11px; }
#inspectionSummaryTitle { color:#e2e8f0; font-size:11px; font-weight:600; }
#inspectionSummaryValue { color:#ffffff; font-size:17px; font-weight:700; }
#inspectionSummaryDetail { color:#cbd5e1; font-size:10px; }
#inspectionInfoTitle { color:#7db7ff; font-size:11px; font-weight:700; }
#inspectionInfoText { color:#d2dbe6; font-size:10px; }
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
#inspectionFileCount { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionTableText { color:#0f172a; font-size:11px; font-weight:500; }
#inspectionTableMuted { color:#475569; font-size:10px; }
#inspectionBlueNote { color:#1d4ed8; font-size:10px; font-weight:500; }
#inspectionRuleName { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#334155; font-size:11px; }
#inspectionSummaryTitle { color:#334155; font-size:11px; font-weight:600; }
#inspectionSummaryValue { color:#0f172a; font-size:17px; font-weight:700; }
#inspectionSummaryDetail { color:#475569; font-size:10px; }
#inspectionInfoTitle { color:#1d4ed8; font-size:11px; font-weight:700; }
#inspectionInfoText { color:#475569; font-size:10px; }
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

        # 1) 도움말 제거
        for button in self.findChildren(QPushButton, 'inspectionHelpButton'):
            button.hide()

        # 2) 모든 번호 섹션에 동일한 안정적인 아이콘 사용
        titles = self.findChildren(QLabel, 'inspectionSectionTitle')
        clean_titles = ['1. 프로젝트 정보', '2. 검사 대상 파일', '3. 검사 기준 선택', '4. 검사 준비 요약']
        for i, title in enumerate(titles[:4]):
            title.setText(f'◆  {clean_titles[i]}')

        # 3) Project Name 필수 별표만 빨간색
        for label in self.findChildren(QLabel, 'inspectionFieldLabel'):
            if label.text().startswith('Project Name'):
                label.setText('Project Name <span style="color:#ef4444;font-weight:700;">*</span>')
                label.setTextFormat(Qt.RichText)

        # 4) 등록 파일 목록 내부에만 자동 스크롤
        table = next(iter(self.findChildren(QFrame, 'inspectionFileTable')), None)
        if table is not None and table.parentWidget() is not None:
            parent_layout = table.parentWidget().layout()
            if parent_layout is not None:
                idx = parent_layout.indexOf(table)
                parent_layout.removeWidget(table)

                file_rows = self.findChildren(QFrame, 'inspectionFileRow')
                content_height = max(150, len(file_rows) * 31 + 4)
                table.setMinimumHeight(content_height)

                scroll = QScrollArea()
                scroll.setObjectName('inspectionFileScroll')
                scroll.setWidgetResizable(True)
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll.setFixedHeight(160)
                scroll.setWidget(table)
                parent_layout.insertWidget(idx, scroll)

        # 파일 행 가독성
        for row in self.findChildren(QFrame, 'inspectionFileRow'):
            row.setFixedHeight(31)

        # 5) 검사 기준 아이콘: 기존 SVG 자산을 사용해 문자 아이콘 깨짐 방지
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons')
        rule_icon_files = ['detail_grade.svg', 'detail_issues.svg', 'inspection.svg', 'reports.svg']
        rule_icons = self.findChildren(QLabel, 'inspectionRuleIcon')
        for label, filename in zip(rule_icons, rule_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(19, 19)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(30)

        # 6) 검사 준비 요약 아이콘
        summary_icon_files = ['project.svg', 'detail_issues.svg', 'play.svg']
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        for label, filename in zip(summary_icons, summary_icon_files):
            label.setText('')
            label.setPixmap(QIcon(os.path.join(icon_dir, filename)).pixmap(QSize(21, 21)))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(32)

        # 7) 검사 시작 버튼이 옆 요약 박스와 같은 높이/비슷한 폭을 갖도록 고정.
        # 초기 layout 전 width() 값을 사용하면 수백 px로 잡혀 전체 화면이 잘리는 문제가 생긴다.
        start = next(iter(self.findChildren(QPushButton, 'inspectionStartButton')), None)
        if start is not None:
            start.setFixedSize(145, 72)

        # 8) 일반 텍스트와 행 자체 높이도 같이 확대
        for row in self.findChildren(QFrame, 'inspectionRuleRow'):
            row.setFixedHeight(44)
        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(74, 30)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setMinimumHeight(30)

    inspection_cls.__init__ = refined_init
    inspection_cls._final_refined = True
