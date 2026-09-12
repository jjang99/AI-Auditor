from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QScrollArea, QVBoxLayout, QWidget,
)

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
#inspectionCompleteCheck { color:#ffffff; background:#168653; border-radius:12px; font-size:16px; font-weight:900; }
#inspectionCompleteMessage { color:#ffffff; font-size:17px; font-weight:900; }
#inspectionCompleteDescription { color:#f1f5f9; font-size:13px; font-weight:750; }
#inspectionCompleteInfoBox { background:#0d1721; border:1px solid #63758a; border-radius:7px; }
#inspectionCompleteInfoTitle { color:#dbe4ee; font-size:11px; font-weight:750; }
#inspectionCompleteInfoValue { color:#ffffff; font-size:16px; font-weight:850; }
#inspectionResultButton { color:#ffffff; background:#2563eb; border:1px solid #93c5fd; border-radius:7px; font-size:15px; font-weight:900; text-align:center; padding:0px; }
#inspectionResultButton:hover { background:#3475f5; border-color:#bfdbfe; }
#inspectionCompleteNote { color:#f8fafc; font-size:11px; font-weight:800; }
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
#inspectionCompleteCheck { color:#ffffff; background:#168653; border-radius:12px; font-size:16px; font-weight:900; }
#inspectionCompleteMessage { color:#020617; font-size:17px; font-weight:900; }
#inspectionCompleteDescription { color:#1e293b; font-size:13px; font-weight:750; }
#inspectionCompleteInfoBox { background:#ffffff; border:1px solid #91a2b7; border-radius:7px; }
#inspectionCompleteInfoTitle { color:#475569; font-size:11px; font-weight:750; }
#inspectionCompleteInfoValue { color:#020617; font-size:16px; font-weight:850; }
#inspectionResultButton { color:#ffffff; background:#2563eb; border:1px solid #1d4ed8; border-radius:7px; font-size:15px; font-weight:900; text-align:center; padding:0px; }
#inspectionResultButton:hover { background:#1d4ed8; border-color:#1e40af; }
#inspectionCompleteNote { color:#0f172a; font-size:11px; font-weight:800; }
#inspectionSummaryIcon { color:#2563eb; }
'''


def _progress_row_widget(parent):
    row_widget = QWidget(parent)
    row_widget.setFixedHeight(46)
    row = QHBoxLayout(row_widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(14)

    percent = QLabel('42%')
    percent.setObjectName('inspectionProgressPercent')
    percent.setFixedSize(72, 46)
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
    cancel.clicked.connect(parent.cancel_progress)

    row.addWidget(percent)
    row.addWidget(bar, 1, Qt.AlignVCenter)
    row.addWidget(cancel)
    return row_widget


def _progress_status_widget(parent):
    row_widget = QWidget(parent)
    row_widget.setFixedHeight(46)
    row = QHBoxLayout(row_widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)

    items = [
        ('완료 규칙', '43 / 102개', 108),
        ('현재 검사 항목', 'SEC-011 입력값 검증', 250),
        ('예상 남은 시간', '약 1분 15초', 108),
        ('처리 상태', '검사 진행 중', 108),
    ]
    for title, value, width in items:
        box = parent.create_progress_info_box(title, value)
        box.setFixedSize(width, 46)
        box_layout = box.layout()
        if box_layout is not None:
            box_layout.setContentsMargins(10, 3, 10, 3)
            box_layout.setSpacing(0)
        row.addWidget(box)
    return row_widget


def _build_progress_card(self):
    card = self.create_card()
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 8, 14, 8)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignTop)

    title = self.section_title('4. 검사 진행')
    title.setFixedHeight(20)
    layout.addWidget(title)
    layout.addSpacing(10)

    description = QLabel('AI Auditor가 등록된 산출물을 검사하고 있습니다.')
    description.setObjectName('inspectionProgressDescription')
    description.setFixedHeight(17)
    description.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    layout.addWidget(description)
    layout.addSpacing(10)

    layout.addWidget(_progress_row_widget(self))
    layout.addStretch(1)
    layout.addWidget(_progress_status_widget(self))
    return card


def _complete_result_box(parent, title, value):
    box = parent.create_complete_info_box(title, value)
    box.setFixedSize(110, 54)
    box_layout = box.layout()
    if box_layout is not None:
        box_layout.setContentsMargins(10, 4, 10, 4)
        box_layout.setSpacing(3)
    title_label = next(iter(box.findChildren(QLabel, 'inspectionCompleteInfoTitle')), None)
    value_label = next(iter(box.findChildren(QLabel, 'inspectionCompleteInfoValue')), None)
    if title_label is not None:
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    if value_label is not None:
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    return box


def _build_complete_card(self):
    card = self.create_card()
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 7, 14, 7)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignTop)

    title = self.section_title('4. 검사 완료')
    title.setFixedHeight(20)
    layout.addWidget(title)
    layout.addSpacing(8)

    success_row_widget = QWidget(card)
    success_row_widget.setFixedHeight(26)
    success_row = QHBoxLayout(success_row_widget)
    success_row.setContentsMargins(0, 0, 0, 0)
    success_row.setSpacing(8)
    check = QLabel('✓')
    check.setObjectName('inspectionCompleteCheck')
    check.setAlignment(Qt.AlignCenter)
    check.setFixedSize(24, 24)
    message = QLabel('검사가 성공적으로 완료되었습니다.')
    message.setObjectName('inspectionCompleteMessage')
    message.setFixedHeight(22)
    message.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    success_row.addWidget(check)
    success_row.addWidget(message)
    success_row.addStretch(1)
    layout.addWidget(success_row_widget)
    layout.addSpacing(1)

    description_row_widget = QWidget(card)
    description_row_widget.setFixedHeight(18)
    description_row = QHBoxLayout(description_row_widget)
    description_row.setContentsMargins(32, 0, 0, 0)
    description_row.setSpacing(0)
    description = QLabel('검사 결과를 확인하거나 Project Detail로 이동할 수 있습니다.')
    description.setObjectName('inspectionCompleteDescription')
    description.setWordWrap(False)
    description.setMinimumWidth(500)
    description.setFixedHeight(18)
    description.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    description_row.addWidget(description)
    description_row.addStretch(1)
    layout.addWidget(description_row_widget)

    layout.addSpacing(12)

    result_row_widget = QWidget(card)
    result_row_widget.setFixedHeight(54)
    result_row = QHBoxLayout(result_row_widget)
    result_row.setContentsMargins(0, 0, 0, 0)
    result_row.setSpacing(0)

    result_widgets = []
    for result_title, result_value in [
        ('적용 규칙', '100 / 100개'),
        ('발견 Issues', '14개'),
        ('소요 시간', '2분 18초'),
        ('검사 파일', '18개'),
    ]:
        result_widgets.append(_complete_result_box(self, result_title, result_value))

    result_button = QPushButton('검사 결과 보기 →')
    result_button.setObjectName('inspectionResultButton')
    result_button.setFixedSize(120, 54)
    result_button.setCursor(Qt.PointingHandCursor)
    result_button.clicked.connect(self.inspection_result_requested.emit)
    result_widgets.append(result_button)

    for index, widget in enumerate(result_widgets):
        result_row.addWidget(widget)
        if index < len(result_widgets) - 1:
            result_row.addStretch(1)

    layout.addWidget(result_row_widget)
    layout.addStretch(1)

    note = QLabel('※ 완료된 결과는 해당 Project의 Inspection History에 자동으로 저장됩니다.')
    note.setObjectName('inspectionCompleteNote')
    note.setFixedHeight(17)
    note.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    layout.addWidget(note)
    return card


def apply_inspection_progress_refinements(inspection_cls):
    if getattr(inspection_cls, '_progress_refined', False):
        return

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

        for state_card in (
            getattr(self, 'summary_card', None),
            getattr(self, 'progress_card', None),
            getattr(self, 'complete_card', None),
        ):
            if state_card is not None:
                state_card.setFixedHeight(190)

        summary_icons = self.findChildren(QLabel, 'inspectionSummaryIcon')
        if len(summary_icons) >= 3:
            time_icon = summary_icons[2]
            time_icon.setPixmap(QPixmap())
            time_icon.setText('◷')
            time_icon.setAlignment(Qt.AlignCenter)
            time_icon.setStyleSheet('font-size:22px; font-weight:700;')

    inspection_cls.__init__ = refined_init
    inspection_cls._progress_refined = True
