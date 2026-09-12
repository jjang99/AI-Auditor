from PySide6.QtWidgets import QFrame, QLabel, QPushButton


DARK_INSPECTION_REFINEMENTS = r'''
#inspectionContent, #inspectionScroll { background:#09090b; border:none; }
#inspectionTitle { color:#fff; font-size:27px; font-weight:700; }
#inspectionDescription { color:#cbd5e1; font-size:12px; }
#inspectionCard { background:#10161c; border:1px solid #334155; border-radius:9px; }
#inspectionSectionTitle { color:#f8fafc; font-size:14px; font-weight:700; }
#inspectionFieldLabel { color:#cbd5e1; font-size:10px; font-weight:500; }
#inspectionInput, #inspectionCombo { color:#f1f5f9; background:#0c141c; border:1px solid #3b4a5d; border-radius:6px; padding:0 10px; font-size:11px; }
#inspectionDuplicate { color:#fbbf24; font-size:9px; font-weight:600; }
#inspectionDuplicateButton { color:#fbbf24; background:transparent; border:none; padding:0; font-size:9px; font-weight:700; text-decoration:underline; }
#inspectionUploadBox { background:#0d1721; border:1px dashed #64748b; border-radius:7px; }
#inspectionUploadText { color:#dbe5f1; font-size:11px; }
#inspectionFileButton { color:#fff; background:#1d4f91; border:1px solid #3b82f6; border-radius:6px; font-size:11px; font-weight:600; }
#inspectionFileCount { color:#f1f5f9; font-size:11px; font-weight:600; }
#inspectionFileTable { background:#0d1721; border:1px solid #334155; border-radius:6px; }
#inspectionFileRow { border-bottom:1px solid #293747; }
#inspectionTableText { color:#e5edf6; font-size:9px; }
#inspectionTableMuted { color:#aebccc; font-size:9px; }
#inspectionBlueNote { color:#60a5fa; font-size:9px; }
#inspectionRuleRow { background:#0d1721; border:1px solid #334155; border-radius:6px; }
#inspectionCheck { color:#fff; background:#0866f5; border-radius:4px; font-size:12px; font-weight:700; }
#inspectionRuleIcon { color:#60a5fa; font-size:14px; }
#inspectionRuleName { color:#f8fafc; font-size:11px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#c0cad6; font-size:10px; }
#inspectionHelpButton, #inspectionSmallButton, #inspectionViewButton { color:#e8eef6; background:#101820; border:1px solid #405166; border-radius:6px; font-size:10px; font-weight:600; }
#inspectionSummaryBox, #inspectionProgressInfoBox, #inspectionCompleteInfoBox { background:#0d1721; border:1px solid #334155; border-radius:7px; }
#inspectionSummaryIcon { color:#60a5fa; font-size:18px; }
#inspectionSummaryTitle, #inspectionProgressInfoTitle, #inspectionCompleteInfoTitle { color:#cbd5e1; font-size:10px; }
#inspectionSummaryValue, #inspectionCompleteInfoValue { color:#fff; font-size:15px; font-weight:700; }
#inspectionSummaryDetail { color:#a8b5c4; font-size:9px; }
#inspectionStartButton { color:#fff; background:#0866f5; border:none; border-radius:7px; font-size:15px; font-weight:700; }
#inspectionInfoBox { background:#0a121a; border:1px solid #334155; border-radius:7px; }
#inspectionInfoTitle { color:#60a5fa; font-size:10px; font-weight:600; }
#inspectionInfoText { color:#b4c0ce; font-size:9px; }
#inspectionProgressDescription, #inspectionCompleteDescription { color:#b4c0ce; font-size:10px; }
#inspectionProgressPercent { color:#60a5fa; font-size:27px; font-weight:600; }
#inspectionProgressInfoValue { color:#f8fafc; font-size:11px; font-weight:600; }
#inspectionCompleteMessage { color:#f8fafc; font-size:14px; font-weight:700; }
#inspectionCompleteCheck { color:#d1fae5; background:#168653; border-radius:16px; font-size:20px; font-weight:700; }
#inspectionCompleteNote { color:#94a3b8; font-size:9px; }
#inspectionResultButton { color:#fff; background:#2f6fed; border:none; border-radius:7px; font-size:12px; font-weight:700; }
#inspectionCancelButton { color:#fca5a5; background:#10161c; border:1px solid #b94a4a; border-radius:7px; font-size:10px; font-weight:600; }
QProgressBar#inspectionProgressBar { background:#263747; border:none; border-radius:9px; }
QProgressBar#inspectionProgressBar::chunk { background:#3478f6; border-radius:9px; }
'''


LIGHT_INSPECTION_REFINEMENTS = r'''
#inspectionContent, #inspectionScroll { background:#f8fafc; border:none; }
#inspectionTitle { color:#0f172a; font-size:27px; font-weight:700; }
#inspectionDescription { color:#475569; font-size:12px; }
#inspectionCard { background:#fff; border:1px solid #cbd5e1; border-radius:9px; }
#inspectionSectionTitle { color:#0f172a; font-size:14px; font-weight:700; }
#inspectionFieldLabel { color:#475569; font-size:10px; font-weight:500; }
#inspectionInput, #inspectionCombo { color:#0f172a; background:#fff; border:1px solid #cbd5e1; border-radius:6px; padding:0 10px; font-size:11px; }
#inspectionDuplicate { color:#b45309; font-size:9px; font-weight:600; }
#inspectionDuplicateButton { color:#b45309; background:transparent; border:none; padding:0; font-size:9px; font-weight:700; text-decoration:underline; }
#inspectionUploadBox { background:#f8fafc; border:1px dashed #94a3b8; border-radius:7px; }
#inspectionUploadText { color:#334155; font-size:11px; }
#inspectionFileButton { color:#fff; background:#2563eb; border:1px solid #2563eb; border-radius:6px; font-size:11px; font-weight:600; }
#inspectionFileCount { color:#0f172a; font-size:11px; font-weight:600; }
#inspectionFileTable { background:#fff; border:1px solid #d7e0ea; border-radius:6px; }
#inspectionFileRow { border-bottom:1px solid #e2e8f0; }
#inspectionTableText { color:#1e293b; font-size:9px; }
#inspectionTableMuted { color:#64748b; font-size:9px; }
#inspectionBlueNote { color:#2563eb; font-size:9px; }
#inspectionRuleRow { background:#fff; border:1px solid #d7e0ea; border-radius:6px; }
#inspectionCheck { color:#fff; background:#2563eb; border-radius:4px; font-size:12px; font-weight:700; }
#inspectionRuleIcon { color:#2563eb; font-size:14px; }
#inspectionRuleName { color:#0f172a; font-size:11px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#475569; font-size:10px; }
#inspectionHelpButton, #inspectionSmallButton, #inspectionViewButton { color:#334155; background:#fff; border:1px solid #cbd5e1; border-radius:6px; font-size:10px; font-weight:600; }
#inspectionSummaryBox, #inspectionProgressInfoBox, #inspectionCompleteInfoBox { background:#f8fafc; border:1px solid #d7e0ea; border-radius:7px; }
#inspectionSummaryIcon { color:#2563eb; font-size:18px; }
#inspectionSummaryTitle, #inspectionProgressInfoTitle, #inspectionCompleteInfoTitle { color:#475569; font-size:10px; }
#inspectionSummaryValue, #inspectionCompleteInfoValue { color:#0f172a; font-size:15px; font-weight:700; }
#inspectionSummaryDetail { color:#64748b; font-size:9px; }
#inspectionStartButton { color:#fff; background:#2563eb; border:none; border-radius:7px; font-size:15px; font-weight:700; }
#inspectionInfoBox { background:#f8fafc; border:1px solid #d7e0ea; border-radius:7px; }
#inspectionInfoTitle { color:#2563eb; font-size:10px; font-weight:600; }
#inspectionInfoText { color:#64748b; font-size:9px; }
#inspectionProgressDescription, #inspectionCompleteDescription { color:#64748b; font-size:10px; }
#inspectionProgressPercent { color:#2563eb; font-size:27px; font-weight:600; }
#inspectionProgressInfoValue { color:#0f172a; font-size:11px; font-weight:600; }
#inspectionCompleteMessage { color:#0f172a; font-size:14px; font-weight:700; }
#inspectionCompleteCheck { color:#fff; background:#16a34a; border-radius:16px; font-size:20px; font-weight:700; }
#inspectionCompleteNote { color:#64748b; font-size:9px; }
#inspectionResultButton { color:#fff; background:#2563eb; border:none; border-radius:7px; font-size:12px; font-weight:700; }
#inspectionCancelButton { color:#dc2626; background:#fff; border:1px solid #ef4444; border-radius:7px; font-size:10px; font-weight:600; }
QProgressBar#inspectionProgressBar { background:#e2e8f0; border:none; border-radius:9px; }
QProgressBar#inspectionProgressBar::chunk { background:#2563eb; border-radius:9px; }
'''


def apply_inspection_refinements(inspection_cls):
    if getattr(inspection_cls, '_readability_refined', False):
        return

    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # The page previously owned a hard-coded dark stylesheet. Clear it so
        # MainWindow's dark/light theme can style Inspection consistently.
        self.setStyleSheet('')

        cards = self.findChildren(QFrame, 'inspectionCard')
        if len(cards) >= 4:
            cards[0].setMinimumHeight(158)   # project information
            cards[1].setMinimumHeight(280)   # files
            cards[2].setMinimumHeight(205)   # rules
            cards[3].setMinimumHeight(190)   # summary

        # Readability first: avoid tiny fixed rows and give text breathing room.
        for row in self.findChildren(QFrame, 'inspectionFileRow'):
            row.setFixedHeight(28)
        for row in self.findChildren(QFrame, 'inspectionRuleRow'):
            row.setFixedHeight(42)

        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(72, 29)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setMinimumHeight(29)

        # Long explanatory text must wrap instead of being clipped.
        for name in ('inspectionDescription', 'inspectionInfoText',
                     'inspectionRuleDescription', 'inspectionCompleteDescription',
                     'inspectionProgressDescription'):
            for label in self.findChildren(QLabel, name):
                label.setWordWrap(True)

    inspection_cls.__init__ = refined_init
    inspection_cls._readability_refined = True
