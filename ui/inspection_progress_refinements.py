from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QProgressBar, QScrollArea


DARK_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription {
    color:#e2e8f0;
    font-size:11px;
    font-weight:650;
}
#inspectionProgressPercent {
    color:#60a5fa;
    font-size:31px;
    font-weight:800;
}
QProgressBar#inspectionProgressBar {
    background:#2b3b4b;
    border:none;
    border-radius:9px;
}
QProgressBar#inspectionProgressBar::chunk {
    background:#3b82f6;
    border-radius:9px;
}
#inspectionCancelButton {
    color:#ffffff;
    background:#dc2626;
    border:1px solid #f87171;
    border-radius:7px;
    font-size:13px;
    font-weight:900;
}
#inspectionCancelButton:hover {
    background:#ef4444;
    border-color:#fca5a5;
}
#inspectionProgressInfoBox {
    background:#0d1721;
    border:1px solid #465669;
    border-radius:7px;
}
#inspectionProgressInfoTitle {
    color:#d1d9e3;
    font-size:11px;
    font-weight:700;
}
#inspectionProgressInfoValue {
    color:#ffffff;
    font-size:14px;
    font-weight:850;
}
#inspectionCompleteCheck {
    color:#ffffff;
    background:#168653;
    border-radius:16px;
    font-size:20px;
    font-weight:800;
}
#inspectionCompleteMessage {
    color:#ffffff;
    font-size:15px;
    font-weight:800;
}
#inspectionCompleteDescription {
    color:#d6dee8;
    font-size:11px;
    font-weight:600;
}
#inspectionCompleteInfoBox {
    background:#0d1721;
    border:1px solid #465669;
    border-radius:7px;
}
#inspectionCompleteInfoTitle {
    color:#cbd5e1;
    font-size:11px;
    font-weight:700;
}
#inspectionCompleteInfoValue {
    color:#ffffff;
    font-size:14px;
    font-weight:850;
}
#inspectionResultButton {
    color:#ffffff;
    background:#2563eb;
    border:none;
    border-radius:7px;
    font-size:13px;
    font-weight:850;
    text-align:center;
    padding:0px;
}
#inspectionResultButton:hover {
    background:#3475f5;
}
#inspectionCompleteNote {
    color:#c0cad6;
    font-size:10px;
    font-weight:600;
}
#inspectionSummaryIcon {
    color:#3b82f6;
}
'''


LIGHT_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription {
    color:#334155;
    font-size:11px;
    font-weight:650;
}
#inspectionProgressPercent {
    color:#2563eb;
    font-size:31px;
    font-weight:800;
}
QProgressBar#inspectionProgressBar {
    background:#d6dee8;
    border:none;
    border-radius:9px;
}
QProgressBar#inspectionProgressBar::chunk {
    background:#3b82f6;
    border-radius:9px;
}
#inspectionCancelButton {
    color:#ffffff;
    background:#dc2626;
    border:1px solid #b91c1c;
    border-radius:7px;
    font-size:13px;
    font-weight:900;
}
#inspectionCancelButton:hover {
    background:#b91c1c;
    border-color:#991b1b;
}
#inspectionProgressInfoBox {
    background:#f8fafc;
    border:1px solid #aebccc;
    border-radius:7px;
}
#inspectionProgressInfoTitle {
    color:#334155;
    font-size:11px;
    font-weight:700;
}
#inspectionProgressInfoValue {
    color:#0b1220;
    font-size:14px;
    font-weight:850;
}
#inspectionCompleteCheck {
    color:#ffffff;
    background:#168653;
    border-radius:16px;
    font-size:20px;
    font-weight:800;
}
#inspectionCompleteMessage {
    color:#0b1220;
    font-size:15px;
    font-weight:800;
}
#inspectionCompleteDescription {
    color:#334155;
    font-size:11px;
    font-weight:650;
}
#inspectionCompleteInfoBox {
    background:#f8fafc;
    border:1px solid #aebccc;
    border-radius:7px;
}
#inspectionCompleteInfoTitle {
    color:#475569;
    font-size:11px;
    font-weight:700;
}
#inspectionCompleteInfoValue {
    color:#0b1220;
    font-size:14px;
    font-weight:850;
}
#inspectionResultButton {
    color:#ffffff;
    background:#2563eb;
    border:none;
    border-radius:7px;
    font-size:13px;
    font-weight:850;
    text-align:center;
    padding:0px;
}
#inspectionResultButton:hover {
    background:#1d4ed8;
}
#inspectionCompleteNote {
    color:#475569;
    font-size:10px;
    font-weight:600;
}
#inspectionSummaryIcon {
    color:#2563eb;
}
'''


def apply_inspection_progress_refinements(inspection_cls):
    if getattr(inspection_cls, '_progress_refined', False):
        return

    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        page_scroll = next(iter(self.findChildren(QScrollArea, 'inspectionScroll')), None)
        if page_scroll is not None:
            page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            page_scroll.verticalScrollBar().setEnabled(False)
            page_scroll.verticalScrollBar().setValue(0)

        if hasattr(self, 'main_layout'):
            self.main_layout.setContentsMargins(14, 9, 10, 10)
            self.main_layout.setSpacing(10)

        cards = self.findChildren(QFrame, 'inspectionCard')
        if len(cards) >= 4:
            for card, height in zip(cards[:4], [175, 221, 204, 190]):
                card.setFixedHeight(height)

        common_action_card_height = 190
        summary_card = getattr(self, 'summary_card', None)
        progress_card = getattr(self, 'progress_card', None)
        complete_card = getattr(self, 'complete_card', None)
        for card in (summary_card, progress_card, complete_card):
            if card is not None:
                card.setFixedHeight(common_action_card_height)

        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        if len(summary_icons) >= 3:
            time_icon = summary_icons[2]
            time_icon.setPixmap(QPixmap())
            time_icon.setText('◷')
            time_icon.setAlignment(Qt.AlignCenter)
            time_icon.setStyleSheet('font-size:22px; font-weight:700;')

        if progress_card is not None:
            progress_layout = progress_card.layout()
            if progress_layout is not None:
                progress_layout.setContentsMargins(14, 10, 14, 8)
                progress_layout.setSpacing(6)

            percent = next(iter(progress_card.findChildren(QLabel, 'inspectionProgressPercent')), None)
            if percent is not None:
                percent.setFixedWidth(72)
                percent.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            bar = next(iter(progress_card.findChildren(QProgressBar, 'inspectionProgressBar')), None)
            if bar is not None:
                bar.setFixedHeight(18)

            cancel = next(iter(progress_card.findChildren(QPushButton, 'inspectionCancelButton')), None)
            if cancel is not None:
                cancel.setFixedSize(115, 46)

            info_boxes = progress_card.findChildren(QFrame, 'inspectionProgressInfoBox')
            for box in info_boxes:
                box.setFixedHeight(46)
                box_layout = box.layout()
                if box_layout is not None:
                    box_layout.setContentsMargins(10, 3, 10, 3)
                    box_layout.setSpacing(0)

                title = next(iter(box.findChildren(QLabel, 'inspectionProgressInfoTitle')), None)
                if title is not None:
                    title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    if title.text() == '현재 검사 항목':
                        box.setFixedWidth(250)
                    else:
                        box.setFixedWidth(108)

                value = next(iter(box.findChildren(QLabel, 'inspectionProgressInfoValue')), None)
                if value is not None:
                    value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        if complete_card is not None:
            complete_layout = complete_card.layout()
            if complete_layout is not None:
                complete_layout.setContentsMargins(14, 9, 14, 8)
                complete_layout.setSpacing(6)

            check = next(iter(complete_card.findChildren(QLabel, 'inspectionCompleteCheck')), None)
            if check is not None:
                check.setFixedSize(32, 32)

            for box in complete_card.findChildren(QFrame, 'inspectionCompleteInfoBox'):
                box.setFixedHeight(56)
                lay = box.layout()
                if lay is not None:
                    lay.setContentsMargins(10, 5, 10, 5)
                    lay.setSpacing(1)

            result_button = next(iter(complete_card.findChildren(QPushButton, 'inspectionResultButton')), None)
            if result_button is not None:
                result_button.setFixedSize(116, 56)

            note = next(iter(complete_card.findChildren(QLabel, 'inspectionCompleteNote')), None)
            if note is not None:
                note.setFixedHeight(16)
                note.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    inspection_cls.__init__ = refined_init
    inspection_cls._progress_refined = True
