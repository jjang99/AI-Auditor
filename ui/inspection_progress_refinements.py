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
    background:#b4232c;
    border:1px solid #ef5961;
    border-radius:7px;
    font-size:12px;
    font-weight:850;
}
#inspectionCancelButton:hover {
    background:#c92b35;
    border-color:#ff7379;
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
    font-size:12px;
    font-weight:750;
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
    background:#c62832;
    border:1px solid #a91520;
    border-radius:7px;
    font-size:12px;
    font-weight:850;
}
#inspectionCancelButton:hover {
    background:#ae1f28;
    border-color:#8f1620;
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
    font-size:12px;
    font-weight:750;
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

        # Restore the already-approved Inspection geometry.  Previous progress
        # tuning made sections 1~3 smaller, which reduced readability and left
        # unused space at the bottom of the fixed window.
        if hasattr(self, 'main_layout'):
            self.main_layout.setContentsMargins(14, 9, 10, 10)
            self.main_layout.setSpacing(10)

        cards = self.findChildren(QFrame, 'inspectionCard')
        if len(cards) >= 4:
            for card, height in zip(cards[:4], [175, 221, 204, 190]):
                card.setFixedHeight(height)

        # Summary / Progress / Complete are one fixed 4th-area container whose
        # contents change by state, so all three must keep the same size.
        common_action_card_height = 190
        summary_card = getattr(self, 'summary_card', None)
        progress_card = getattr(self, 'progress_card', None)
        complete_card = getattr(self, 'complete_card', None)
        for card in (summary_card, progress_card, complete_card):
            if card is not None:
                card.setFixedHeight(common_action_card_height)

        # The SVG used for the time summary can disappear on the light theme.
        # Replace only that third summary icon with a theme-safe text clock.
        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        if len(summary_icons) >= 3:
            time_icon = summary_icons[2]
            time_icon.setPixmap(QPixmap())
            time_icon.setText('◷')
            time_icon.setAlignment(Qt.AlignCenter)
            time_icon.setStyleSheet('font-size:22px; font-weight:700;')

        if progress_card is None:
            return

        progress_layout = progress_card.layout()
        if progress_layout is not None:
            progress_layout.setContentsMargins(14, 10, 14, 8)
            progress_layout.setSpacing(7)

        percent = next(iter(progress_card.findChildren(QLabel, 'inspectionProgressPercent')), None)
        if percent is not None:
            percent.setFixedWidth(72)
            percent.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        bar = next(iter(progress_card.findChildren(QProgressBar, 'inspectionProgressBar')), None)
        if bar is not None:
            bar.setFixedHeight(18)

        cancel = next(iter(progress_card.findChildren(QPushButton, 'inspectionCancelButton')), None)
        if cancel is not None:
            cancel.setFixedSize(115, 44)

        info_boxes = progress_card.findChildren(QFrame, 'inspectionProgressInfoBox')
        for box in info_boxes:
            box.setFixedHeight(54)
            box_layout = box.layout()
            if box_layout is not None:
                box_layout.setContentsMargins(10, 5, 10, 5)
                box_layout.setSpacing(1)

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

    inspection_cls.__init__ = refined_init
    inspection_cls._progress_refined = True
