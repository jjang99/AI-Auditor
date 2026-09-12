from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QProgressBar, QScrollArea

DARK_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription { color:#e2e8f0; font-size:11px; font-weight:650; }
#inspectionProgressPercent { color:#60a5fa; font-size:31px; font-weight:800; }
QProgressBar#inspectionProgressBar { background:#2b3b4b; border:none; border-radius:9px; }
QProgressBar#inspectionProgressBar::chunk { background:#3b82f6; border-radius:9px; }
#inspectionCancelButton { color:#ffffff; background:#dc2626; border:1px solid #f87171; border-radius:7px; font-size:13px; font-weight:900; }
#inspectionCancelButton:hover { background:#ef4444; border-color:#fca5a5; }
#inspectionProgressInfoBox { background:#0d1721; border:1px solid #465669; border-radius:7px; }
#inspectionProgressInfoTitle { color:#d1d9e3; font-size:11px; font-weight:700; }
#inspectionProgressInfoValue { color:#ffffff; font-size:14px; font-weight:850; }
#inspectionCompleteCheck { color:#ffffff; background:#168653; border-radius:17px; font-size:21px; font-weight:900; }
#inspectionCompleteMessage { color:#ffffff; font-size:17px; font-weight:900; }
#inspectionCompleteDescription { color:#f1f5f9; font-size:13px; font-weight:750; }
#inspectionCompleteInfoBox { background:#0d1721; border:1px solid #63758a; border-radius:7px; }
#inspectionCompleteInfoTitle { color:#e2e8f0; font-size:12px; font-weight:800; }
#inspectionCompleteInfoValue { color:#ffffff; font-size:17px; font-weight:900; }
#inspectionResultButton { color:#ffffff; background:#2563eb; border:1px solid #60a5fa; border-radius:7px; font-size:14px; font-weight:900; text-align:center; padding:0px; }
#inspectionResultButton:hover { background:#3475f5; border-color:#93c5fd; }
#inspectionCompleteNote { color:#f1f5f9; font-size:11px; font-weight:750; }
#inspectionSummaryIcon { color:#3b82f6; }
'''

LIGHT_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription { color:#334155; font-size:11px; font-weight:650; }
#inspectionProgressPercent { color:#2563eb; font-size:31px; font-weight:800; }
QProgressBar#inspectionProgressBar { background:#d6dee8; border:none; border-radius:9px; }
QProgressBar#inspectionProgressBar::chunk { background:#3b82f6; border-radius:9px; }
#inspectionCancelButton { color:#ffffff; background:#dc2626; border:1px solid #b91c1c; border-radius:7px; font-size:13px; font-weight:900; }
#inspectionCancelButton:hover { background:#b91c1c; border-color:#991b1b; }
#inspectionProgressInfoBox { background:#f8fafc; border:1px solid #aebccc; border-radius:7px; }
#inspectionProgressInfoTitle { color:#334155; font-size:11px; font-weight:700; }
#inspectionProgressInfoValue { color:#0b1220; font-size:14px; font-weight:850; }
#inspectionCompleteCheck { color:#ffffff; background:#168653; border-radius:17px; font-size:21px; font-weight:900; }
#inspectionCompleteMessage { color:#020617; font-size:17px; font-weight:900; }
#inspectionCompleteDescription { color:#1e293b; font-size:13px; font-weight:750; }
#inspectionCompleteInfoBox { background:#ffffff; border:1px solid #91a2b7; border-radius:7px; }
#inspectionCompleteInfoTitle { color:#334155; font-size:12px; font-weight:800; }
#inspectionCompleteInfoValue { color:#020617; font-size:17px; font-weight:900; }
#inspectionResultButton { color:#ffffff; background:#2563eb; border:1px solid #1d4ed8; border-radius:7px; font-size:14px; font-weight:900; text-align:center; padding:0px; }
#inspectionResultButton:hover { background:#1d4ed8; border-color:#1e40af; }
#inspectionCompleteNote { color:#1e293b; font-size:11px; font-weight:750; }
#inspectionSummaryIcon { color:#2563eb; }
'''

def apply_inspection_progress_refinements(inspection_cls):
    if getattr(inspection_cls, '_progress_refined', False): return
    original_init = inspection_cls.__init__
    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        page_scroll = next(iter(self.findChildren(QScrollArea, 'inspectionScroll')), None)
        if page_scroll is not None:
            page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); page_scroll.verticalScrollBar().setEnabled(False); page_scroll.verticalScrollBar().setValue(0)
        if hasattr(self, 'main_layout'):
            self.main_layout.setContentsMargins(14,9,10,10); self.main_layout.setSpacing(10)
        cards=self.findChildren(QFrame,'inspectionCard')
        if len(cards)>=4:
            for card,height in zip(cards[:4],[175,221,204,190]): card.setFixedHeight(height)
        summary_card=getattr(self,'summary_card',None); progress_card=getattr(self,'progress_card',None); complete_card=getattr(self,'complete_card',None)
        for card in (summary_card,progress_card,complete_card):
            if card is not None: card.setFixedHeight(190)
        summary_icons=self.findChildren(QLabel,'inspectionSummaryIcon')
        if len(summary_icons)>=3:
            time_icon=summary_icons[2]; time_icon.setPixmap(QPixmap()); time_icon.setText('◷'); time_icon.setAlignment(Qt.AlignCenter); time_icon.setStyleSheet('font-size:22px; font-weight:700;')
        if progress_card is not None:
            lay=progress_card.layout()
            if lay is not None: lay.setContentsMargins(14,10,14,8); lay.setSpacing(6)
            percent=next(iter(progress_card.findChildren(QLabel,'inspectionProgressPercent')),None)
            if percent is not None: percent.setFixedWidth(72); percent.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            bar=next(iter(progress_card.findChildren(QProgressBar,'inspectionProgressBar')),None)
            if bar is not None: bar.setFixedHeight(18)
            cancel=next(iter(progress_card.findChildren(QPushButton,'inspectionCancelButton')),None)
            if cancel is not None: cancel.setFixedSize(115,46)
            for box in progress_card.findChildren(QFrame,'inspectionProgressInfoBox'):
                box.setFixedHeight(46); bl=box.layout()
                if bl is not None: bl.setContentsMargins(10,3,10,3); bl.setSpacing(0)
                title=next(iter(box.findChildren(QLabel,'inspectionProgressInfoTitle')),None)
                if title is not None:
                    title.setAlignment(Qt.AlignLeft|Qt.AlignVCenter); box.setFixedWidth(250 if title.text()=='현재 검사 항목' else 108)
                value=next(iter(box.findChildren(QLabel,'inspectionProgressInfoValue')),None)
                if value is not None: value.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        if complete_card is not None:
            lay=complete_card.layout()
            if lay is not None:
                lay.setContentsMargins(14,6,14,6)
                lay.setSpacing(4)
                lay.setAlignment(Qt.AlignTop)
            check=next(iter(complete_card.findChildren(QLabel,'inspectionCompleteCheck')),None)
            if check is not None: check.setFixedSize(34,34)
            message=next(iter(complete_card.findChildren(QLabel,'inspectionCompleteMessage')),None)
            if message is not None: message.setFixedHeight(22); message.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            description=next(iter(complete_card.findChildren(QLabel,'inspectionCompleteDescription')),None)
            if description is not None:
                description.setWordWrap(False); description.setMinimumWidth(430); description.setFixedHeight(19); description.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            for box in complete_card.findChildren(QFrame,'inspectionCompleteInfoBox'):
                box.setFixedHeight(52); bl=box.layout()
                if bl is not None: bl.setContentsMargins(10,3,10,3); bl.setSpacing(0)
                title=next(iter(box.findChildren(QLabel,'inspectionCompleteInfoTitle')),None)
                value=next(iter(box.findChildren(QLabel,'inspectionCompleteInfoValue')),None)
                if title is not None: title.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                if value is not None: value.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            result_button=next(iter(complete_card.findChildren(QPushButton,'inspectionResultButton')),None)
            if result_button is not None:
                result_button.setText('검사 결과 보기 →'); result_button.setFixedSize(126,52)
            note=next(iter(complete_card.findChildren(QLabel,'inspectionCompleteNote')),None)
            if note is not None: note.setFixedHeight(18); note.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    inspection_cls.__init__=refined_init; inspection_cls._progress_refined=True
