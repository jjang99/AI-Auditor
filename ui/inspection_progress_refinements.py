from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QProgressBar


DARK_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription {
    color:#e2e8f0;
    font-size:11px;
    font-weight:650;
}
#inspectionProgressPercent {
    color:#60a5fa;
    font-size:32px;
    font-weight:800;
}
QProgressBar#inspectionProgressBar {
    background:#2b3b4b;
    border:none;
    border-radius:10px;
}
QProgressBar#inspectionProgressBar::chunk {
    background:#3b82f6;
    border-radius:10px;
}
#inspectionCancelButton {
    color:#fecaca;
    background:#2a171a;
    border:1px solid #dc6262;
    border-radius:7px;
    font-size:11px;
    font-weight:750;
}
#inspectionCancelButton:hover {
    color:#ffffff;
    background:#3a1c20;
    border-color:#f87171;
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
'''


LIGHT_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription {
    color:#334155;
    font-size:11px;
    font-weight:650;
}
#inspectionProgressPercent {
    color:#2563eb;
    font-size:32px;
    font-weight:800;
}
QProgressBar#inspectionProgressBar {
    background:#d6dee8;
    border:none;
    border-radius:10px;
}
QProgressBar#inspectionProgressBar::chunk {
    background:#3b82f6;
    border-radius:10px;
}
#inspectionCancelButton {
    color:#b91c1c;
    background:#fff1f2;
    border:1px solid #e57a7a;
    border-radius:7px;
    font-size:11px;
    font-weight:750;
}
#inspectionCancelButton:hover {
    color:#991b1b;
    background:#ffe4e6;
    border-color:#dc2626;
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
'''


def apply_inspection_progress_refinements(inspection_cls):
    if getattr(inspection_cls, '_progress_refined', False):
        return

    original_init = inspection_cls.__init__

    def refined_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        progress_card = getattr(self, 'progress_card', None)
        if progress_card is None:
            return

        progress_layout = progress_card.layout()
        if progress_layout is not None:
            progress_layout.setContentsMargins(14, 13, 14, 13)
            progress_layout.setSpacing(11)

        percent = next(iter(progress_card.findChildren(QLabel, 'inspectionProgressPercent')), None)
        if percent is not None:
            percent.setFixedWidth(72)
            percent.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        bar = next(iter(progress_card.findChildren(QProgressBar, 'inspectionProgressBar')), None)
        if bar is not None:
            bar.setFixedHeight(20)

        cancel = next(iter(progress_card.findChildren(QPushButton, 'inspectionCancelButton')), None)
        if cancel is not None:
            cancel.setFixedSize(115, 46)

        info_boxes = progress_card.findChildren(QFrame, 'inspectionProgressInfoBox')
        for box in info_boxes:
            box.setFixedHeight(74)
            box_layout = box.layout()
            if box_layout is not None:
                box_layout.setContentsMargins(11, 9, 11, 9)
                box_layout.setSpacing(5)

            title = next(iter(box.findChildren(QLabel, 'inspectionProgressInfoTitle')), None)
            if title is not None:
                title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                title_text = title.text()
                if title_text == '현재 검사 항목':
                    box.setFixedWidth(250)
                else:
                    box.setFixedWidth(108)

            value = next(iter(box.findChildren(QLabel, 'inspectionProgressInfoValue')), None)
            if value is not None:
                value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    inspection_cls.__init__ = refined_init
    inspection_cls._progress_refined = True
