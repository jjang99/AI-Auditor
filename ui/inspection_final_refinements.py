from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout

DARK_INSPECTION_FINAL = r'''
#inspectionSectionTitle { color:#ffffff; font-size:15px; font-weight:700; }
#inspectionFieldLabel { color:#e2e8f0; font-size:11px; font-weight:600; }
#inspectionInput, #inspectionCombo { color:#ffffff; font-size:12px; }
#inspectionFileCount { color:#ffffff; font-size:12px; font-weight:700; }
#inspectionTableText { color:#f8fafc; font-size:10px; }
#inspectionTableMuted { color:#cbd5e1; font-size:10px; }
#inspectionRuleName { color:#ffffff; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#dbe4ee; font-size:10px; }
#inspectionSummaryTitle { color:#dbe4ee; font-size:11px; font-weight:600; }
#inspectionSummaryValue { color:#ffffff; font-size:16px; font-weight:700; }
#inspectionSummaryDetail { color:#b9c6d4; font-size:10px; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#0b1219; width:8px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#526274; min-height:28px; border-radius:4px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
#inspectionSectionIcon { color:#60a5fa; font-size:15px; font-weight:700; }
#inspectionRuleIcon { color:#60a5fa; font-size:16px; font-weight:700; }
'''

LIGHT_INSPECTION_FINAL = r'''
#inspectionSectionTitle { color:#0f172a; font-size:15px; font-weight:700; }
#inspectionFieldLabel { color:#334155; font-size:11px; font-weight:600; }
#inspectionInput, #inspectionCombo { color:#0f172a; font-size:12px; }
#inspectionFileCount { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionTableText { color:#0f172a; font-size:10px; }
#inspectionTableMuted { color:#475569; font-size:10px; }
#inspectionRuleName { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#334155; font-size:10px; }
#inspectionSummaryTitle { color:#334155; font-size:11px; font-weight:600; }
#inspectionSummaryValue { color:#0f172a; font-size:16px; font-weight:700; }
#inspectionSummaryDetail { color:#475569; font-size:10px; }
#inspectionFileScroll { background:transparent; border:none; }
#inspectionFileScroll QWidget { background:transparent; }
#inspectionFileScroll QScrollBar:vertical { background:#eef2f7; width:8px; margin:2px; }
#inspectionFileScroll QScrollBar::handle:vertical { background:#94a3b8; min-height:28px; border-radius:4px; }
#inspectionFileScroll QScrollBar::add-line:vertical, #inspectionFileScroll QScrollBar::sub-line:vertical { height:0px; }
#inspectionSectionIcon { color:#2563eb; font-size:15px; font-weight:700; }
#inspectionRuleIcon { color:#2563eb; font-size:16px; font-weight:700; }
'''


def apply_inspection_final_refinements(inspection_cls):
    if getattr(inspection_cls, '_final_refined', False):
        return
    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # Help was not part of the approved workflow and duplicates contextual guidance.
        for button in self.findChildren(QPushButton, 'inspectionHelpButton'):
            button.hide()

        # Use one consistent lightweight icon language for all numbered sections.
        titles = self.findChildren(QLabel, 'inspectionSectionTitle')
        section_icons = ['▤', '▧', '✓', '◈']
        clean_titles = ['1. 프로젝트 정보', '2. 검사 대상 파일', '3. 검사 기준 선택', '4. 검사 준비 요약']
        for i, title in enumerate(titles[:4]):
            title.setText(f'{section_icons[i]}   {clean_titles[i]}')

        # Make the required marker unmistakable without making the whole label red.
        for label in self.findChildren(QLabel, 'inspectionFieldLabel'):
            if label.text().startswith('Project Name'):
                label.setText('Project Name <span style="color:#ef4444;font-weight:700;">*</span>')
                label.setTextFormat(Qt.RichText)

        # File list gets its OWN vertical scroll area. The page itself does not grow
        # merely because more files were registered.
        table = next(iter(self.findChildren(QFrame, 'inspectionFileTable')), None)
        if table is not None and table.parentWidget() is not None:
            parent_layout = table.parentWidget().layout()
            if parent_layout is not None:
                idx = parent_layout.indexOf(table)
                parent_layout.removeWidget(table)
                scroll = QScrollArea()
                scroll.setObjectName('inspectionFileScroll')
                scroll.setWidgetResizable(True)
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll.setFixedHeight(160)
                table.setMinimumHeight(table.sizeHint().height())
                scroll.setWidget(table)
                parent_layout.insertWidget(idx, scroll)

        # Modern, simple category glyphs; avoid decorative/ambiguous symbols.
        rule_icons = self.findChildren(QLabel, 'inspectionRuleIcon')
        for icon, glyph in zip(rule_icons, ['♢', '</>', 'AI', '◴']):
            icon.setText(glyph)
            icon.setAlignment(Qt.AlignCenter)
            icon.setMinimumWidth(28)

        # Summary icons should be visually distinct and easy to scan.
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        for icon, glyph in zip(summary_icons, ['▤', '☷', '◷']):
            icon.setText(glyph)
            icon.setAlignment(Qt.AlignCenter)
            icon.setMinimumWidth(30)

        # Start button must occupy the same visual box size as the three summaries.
        boxes = self.findChildren(QFrame, 'inspectionSummaryBox')
        start = next(iter(self.findChildren(QPushButton, 'inspectionStartButton')), None)
        if start is not None and boxes:
            start.setFixedWidth(boxes[0].width() if boxes[0].width() > 100 else 145)
            start.setMinimumHeight(72)

    inspection_cls.__init__ = refined_init
    inspection_cls._final_refined = True
