from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QScrollArea, QVBoxLayout,
)

DARK_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription { color:#f1f5f9; font-size:11px; font-weight:700; }
#inspectionProgressPercent { color:#60a5fa; font-size:31px; font-weight:850; }
QProgressBar#inspectionProgressBar { background:#2b3b4b; border:none; border-radius:9px; }
QProgressBar#inspectionProgressBar::chunk { background:#3b82f6; border-radius:9px; }
#inspectionCancelButton { color:#ffffff; background:#dc2626; border:1px solid #f87171; border-radius:7px; font-size:13px; font-weight:900; }
#inspectionCancelButton:hover { background:#ef4444; border-color:#fca5a5; }
#inspectionProgressInfoBox { background:#0d1721; border:1px solid #526477; border-radius:7px; }
#inspectionProgressInfoTitle { color:#dbe4ee; font-size:11px; font-weight:750; }
#inspectionProgressInfoValue { color:#ffffff; font-size:14px; font-weight:900; }
#inspectionCompleteCheck { color:#ffffff; background:#168653; border-radius:17px; font-size:21px; font-weight:900; }
#inspectionCompleteMessage { color:#ffffff; font-size:17px; font-weight:900; }
#inspectionCompleteDescription { color:#f1f5f9; font-size:12px; font-weight:750; }
#inspectionCompleteInfoBox { background:#0d1721; border:1px solid #63758a; border-radius:7px; }
#inspectionCompleteInfoTitle { color:#e2e8f0; font-size:11px; font-weight:800; }
#inspectionCompleteInfoValue { color:#ffffff; font-size:16px; font-weight:900; }
#inspectionResultButton { color:#ffffff; background:#2563eb; border:1px solid #60a5fa; border-radius:7px; font-size:14px; font-weight:900; text-align:center; padding:0px; }
#inspectionResultButton:hover { background:#3475f5; border-color:#93c5fd; }
#inspectionCompleteNote { color:#ffffff; font-size:11px; font-weight:800; }
#inspectionSummaryIcon { color:#3b82f6; }
'''

LIGHT_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription { color:#1e293b; font-size:11px; font-weight:700; }
#inspectionProgressPercent { color:#2563eb; font-size:31px; font-weight:850; }
QProgressBar#inspectionProgressBar { background:#d6dee8; border:none; border-radius:9px; }
QProgressBar#inspectionProgressBar::chunk { background:#3b82f6; border-radius:9px; }
#inspectionCancelButton { color:#ffffff; background:#dc2626; border:1px solid #b91c1c; border-radius:7px; font-size:13px; font-weight:900; }
#inspectionCancelButton:hover { background:#b91c1c; border-color:#991b1b; }
#inspectionProgressInfoBox { background:#ffffff; border:1px solid #9fadc0; border-radius:7px; }
#inspectionProgressInfoTitle { color:#334155; font-size:11px; font-weight:750; }
#inspectionProgressInfoValue { color:#020617; font-size:14px; font-weight:900; }
#inspectionCompleteCheck { color:#ffffff; background:#168653; border-radius:17px; font-size:21px; font-weight:900; }
#inspectionCompleteMessage { color:#020617; font-size:17px; font-weight:900; }
#inspectionCompleteDescription { color:#1e293b; font-size:12px; font-weight:750; }
#inspectionCompleteInfoBox { background:#ffffff; border:1px solid #91a2b7; border-radius:7px; }
#inspectionCompleteInfoTitle { color:#334155; font-size:11px; font-weight:800; }
#inspectionCompleteInfoValue { color:#020617; font-size:16px; font-weight:900; }
#inspectionResultButton { color:#ffffff; background:#2563eb; border:1px solid #1d4ed8; border-radius:7px; font-size:14px; font-weight:900; text-align:center; padding:0px; }
#inspectionResultButton:hover { background:#1d4ed8; border-color:#1e40af; }
#inspectionCompleteNote { color:#0f172a; font-size:11px; font-weight:800; }
#inspectionSummaryIcon { color:#2563eb; }
'''


def _build_progress_card(self):
    card = self.create_card()
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 8, 14, 7)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignTop)

    layout.addWidget(self.section_title('4. 검사 진행'))
    layout.addSpacing(7)

    description = QLabel('AI Auditor가 등록된 산출물을 검사하고 있습니다.')
    description.setObjectName('inspectionProgressDescription')
    description.setFixedHeight(16)
    layout.addWidget(description)
    layout.addSpacing(5)

    progress_row = QHBoxLayout()
    progress_row.setSpacing(12)
    percent = QLabel('42%')
    percent.setObjectName('inspectionProgressPercent')
    percent.setFixedSize(74, 40)
    percent.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    bar = QProgressBar()
    bar.setObjectName('inspectionProgressBar')
    bar.setRange(0, 100)
    bar.setValue(42)
    bar.setTextVisible(False)
    bar.setFixedHeight(18)

    cancel = QPushButton('검사 취소')
    cancel.setObjectName('inspectionCancelButton')
    cancel.setFixedSize(115, 46)
    cancel.setCursor(Qt.PointingHandCursor)
    cancel.clicked.connect(self.cancel_progress)

    progress_row.addWidget(percent)
    progress_row.addWidget(bar, 1, Qt.AlignVCenter)
    progress_row.addWidget(cancel)
    layout.addLayout(progress_row)
    layout.addSpacing(5)

    status_row = QHBoxLayout()
    status_row.setSpacing(10)
    specs = [
        ('완료 규칙', '43 / 102개', 108),
        ('현재 검사 항목', 'SEC-011 입력값 검증', 250),
        ('예상 남은 시간', '약 1분 15초', 108),
        ('처리 상태', '검사 진행 중', 108),
    ]
    for title, value, width in specs:
        box = self.create_progress_info_box(title, value)
        box.setFixedSize(width, 46)
        bl = box.layout()
        if bl is not None:
            bl.setContentsMargins(10, 3, 10, 3)
            bl.setSpacing(0)
        status_row.addWidget(box)
    layout.addLayout(status_row)
    layout.addStretch(1)
    return card


def _build_complete_card(self):
    card = self.create_card()
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 7, 14, 6)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignTop)

    layout.addWidget(self.section_title('4. 검사 완료'))
    layout.addSpacing(7)

    message_row = QHBoxLayout()
    message_row.setSpacing(10)
    check = QLabel('✓')
    check.setObjectName('inspectionCompleteCheck')
    check.setAlignment(Qt.AlignCenter)
    check.setFixedSize(34, 34)

    message_area = QVBoxLayout()
    message_area.setContentsMargins(0, 0, 0, 0)
    message_area.setSpacing(0)
    message = QLabel('검사가 성공적으로 완료되었습니다.')
    message.setObjectName('inspectionCompleteMessage')
    message.setFixedHeight(20)
    description = QLabel('검사 결과를 확인하거나 Project Detail로 이동할 수 있습니다.')
    description.setObjectName('inspectionCompleteDescription')
    description.setFixedHeight(17)
    description.setWordWrap(False)
    message_area.addWidget(message)
    message_area.addWidget(description)

    message_row.addWidget(check, 0, Qt.AlignVCenter)
    message_row.addLayout(message_area)
    message_row.addStretch(1)
    layout.addLayout(message_row)
    layout.addSpacing(7)

    result_row = QHBoxLayout()
    result_row.setSpacing(8)
    results = [
        ('적용 규칙', '100 / 100개'),
        ('발견 Issues', '14개'),
        ('소요 시간', '2분 18초'),
        ('검사 파일', '18개'),
    ]
    for title, value in results:
        box = self.create_complete_info_box(title, value)
        box.setFixedSize(102, 50)
        bl = box.layout()
        if bl is not None:
            bl.setContentsMargins(9, 3, 9, 3)
            bl.setSpacing(0)
        result_row.addWidget(box)

    result_button = QPushButton('검사 결과 보기 →')
    result_button.setObjectName('inspectionResultButton')
    result_button.setFixedSize(150, 50)
    result_button.setCursor(Qt.PointingHandCursor)
    result_button.clicked.connect(self.inspection_result_requested.emit)
    result_row.addWidget(result_button)
    layout.addLayout(result_row)
    layout.addSpacing(6)

    note = QLabel('※ 완료된 결과는 해당 Project의 Inspection History에 자동으로 저장됩니다.')
    note.setObjectName('inspectionCompleteNote')
    note.setFixedHeight(17)
    note.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    layout.addWidget(note)
    layout.addStretch(1)
    return card


def apply_inspection_progress_refinements(inspection_cls):
    if getattr(inspection_cls, '_progress_refined', False):
        return

    # Replace the two state cards themselves so spacing is deterministic.
    # This avoids relying on after-the-fact layout tweaks that Qt may redistribute.
    inspection_cls.create_progress_card = _build_progress_card
    inspection_cls.create_complete_card = _build_complete_card

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

        for card in (
            getattr(self, 'summary_card', None),
            getattr(self, 'progress_card', None),
            getattr(self, 'complete_card', None),
        ):
            if card is not None:
                card.setFixedHeight(190)

        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        if len(summary_icons) >= 3:
            time_icon = summary_icons[2]
            time_icon.setPixmap(QPixmap())
            time_icon.setText('◷')
            time_icon.setAlignment(Qt.AlignCenter)
            time_icon.setStyleSheet('font-size:22px; font-weight:700;')

    inspection_cls.__init__ = refined_init
    inspection_cls._progress_refined = True
