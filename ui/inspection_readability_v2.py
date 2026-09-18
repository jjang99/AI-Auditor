from PySide6.QtWidgets import QFrame, QLabel, QPushButton

# Final-pass overrides for the fixed 840px application window.
# Do not shrink typography to force the whole page into one viewport;
# vertical scrolling is intentional and readability has priority.
DARK_INSPECTION_READABILITY_V2 = r'''
#inspectionTitle { font-size:27px; font-weight:700; }
#inspectionDescription { color:#d7e0ea; font-size:12px; }
#inspectionSectionTitle { font-size:15px; font-weight:700; }
#inspectionFieldLabel { font-size:11px; }
#inspectionInput, #inspectionCombo { font-size:12px; }
#inspectionDuplicate, #inspectionDuplicateButton { font-size:10px; }
#inspectionUploadText { font-size:12px; }
#inspectionFileButton { font-size:11px; font-weight:700; }
#inspectionFileCount { font-size:11px; font-weight:700; }
#inspectionTableText { color:#f1f5f9; font-size:10px; }
#inspectionTableMuted { color:#b9c5d3; font-size:10px; }
#inspectionBlueNote { color:#60a5fa; font-size:10px; }
#inspectionRuleName { color:#fff; font-size:12px; font-weight:700; }
#inspectionRuleCount, #inspectionRuleDescription { color:#d0d8e3; font-size:10px; }
#inspectionHelpButton, #inspectionSmallButton, #inspectionViewButton { font-size:10px; font-weight:700; }
#inspectionSummaryTitle, #inspectionProgressInfoTitle, #inspectionCompleteInfoTitle { font-size:11px; }
#inspectionSummaryValue, #inspectionCompleteInfoValue { font-size:16px; font-weight:700; }
#inspectionSummaryDetail { font-size:9px; }
#inspectionInfoTitle { font-size:11px; font-weight:700; }
#inspectionInfoText { color:#c3ceda; font-size:10px; }
'''

LIGHT_INSPECTION_READABILITY_V2 = r'''
#inspectionTitle { font-size:27px; font-weight:700; }
#inspectionDescription { color:#334155; font-size:12px; }
#inspectionSectionTitle { color:#0f172a; font-size:15px; font-weight:700; }
#inspectionFieldLabel { color:#334155; font-size:11px; }
#inspectionInput, #inspectionCombo { color:#0f172a; font-size:12px; }
#inspectionDuplicate, #inspectionDuplicateButton { font-size:10px; }
#inspectionUploadText { color:#1e293b; font-size:12px; }
#inspectionFileButton { font-size:11px; font-weight:700; }
#inspectionFileCount { color:#0f172a; font-size:11px; font-weight:700; }
#inspectionTableText { color:#0f172a; font-size:10px; }
#inspectionTableMuted { color:#475569; font-size:10px; }
#inspectionBlueNote { color:#1d4ed8; font-size:10px; }
#inspectionRuleName { color:#0f172a; font-size:12px; font-weight:700; }
#inspectionRuleCount { color:#1e293b; font-size:10px; font-weight:600; }
#inspectionRuleDescription { color:#334155; font-size:10px; font-weight:500; }
#inspectionHelpButton, #inspectionSmallButton, #inspectionViewButton { color:#1e293b; font-size:10px; font-weight:700; }
#inspectionSummaryTitle, #inspectionProgressInfoTitle, #inspectionCompleteInfoTitle { color:#334155; font-size:11px; }
#inspectionSummaryValue, #inspectionCompleteInfoValue { color:#0f172a; font-size:16px; font-weight:700; }
#inspectionSummaryDetail { color:#475569; font-size:9px; }
#inspectionInfoTitle { font-size:11px; font-weight:700; }
#inspectionInfoText { color:#475569; font-size:10px; }
'''


def apply_inspection_readability_v2(inspection_cls):
    if getattr(inspection_cls, '_readability_v2', False):
        return
    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # Header must remain a single readable line as in the approved mockup.
        for label in self.findChildren(QLabel, 'inspectionDescription'):
            label.setWordWrap(False)
            label.setMinimumWidth(430)

        # Increase real row height together with font size so text never clips.
        for row in self.findChildren(QFrame, 'inspectionFileRow'):
            row.setFixedHeight(31)
        for row in self.findChildren(QFrame, 'inspectionRuleRow'):
            row.setFixedHeight(44)

        # Keep controls comfortably clickable/readable.
        for button in self.findChildren(QPushButton, 'inspectionViewButton'):
            button.setFixedSize(74, 30)
        for button in self.findChildren(QPushButton, 'inspectionSmallButton'):
            button.setMinimumHeight(30)

        # Long body text may wrap; headings and compact metadata should not.
        for name in ('inspectionInfoText', 'inspectionRuleDescription',
                     'inspectionCompleteDescription', 'inspectionProgressDescription'):
            for label in self.findChildren(QLabel, name):
                label.setWordWrap(True)

    inspection_cls.__init__ = refined_init
    inspection_cls._readability_v2 = True
