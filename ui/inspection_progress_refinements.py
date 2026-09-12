from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QProgressBar


DARK_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription {
    color:#cbd5e1;
    font-size:10px;
    font-weight:550;
}
#inspectionProgressPercent {
    color:#60a5fa;
    font-size:30px;
    font-weight:700;
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
    color:#f87171;
    background:#10161c;
    border:1px solid #d35b5b;
    border-radius:7px;
    font-size:11px;
    font-weight:700;
}
#inspectionCancelButton:hover {
    background:#241619;
}
#inspectionProgressInfoBox {
    background:#0d1721;
    border:1px solid #3a4758;
    border-radius:7px;
}
#inspectionProgressInfoTitle {
    color:#aebaca;
    font-size:10px;
    font-weight:600;
}
#inspectionProgressInfoValue {
    color:#ffffff;
    font-size:11px;
    font-weight:650;
}
'''


LIGHT_INSPECTION_PROGRESS = r'''
#inspectionProgressDescription {
    color:#475569;
    font-size:10px;
    font-weight:600;
}
#inspectionProgressPercent {
    color:#2563eb;
    font-size:30px;
    font-weight:750;
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
    background:#ffffff;
    border:1px solid #dc6b6b;
    border-radius:7px;
    font-size:11px;
    font-weight:700;
}
#inspectionCancelButton:hover {
    background:#fff1f2;
}
#inspectionProgressInfoBox {
    background:#f8fafc;
    border:1px solid #b8c4d2;
    border-radius:7px;
}
#inspectionProgressInfoTitle {
    color:#475569;
    font-size:10px;
    font-weight:650;
}
#inspectionProgressInfoValue {
    color:#0b1220;
    font-size:11px;
    font-weight:700;
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

        for box in progress_card.findChildren(QFrame, 'inspectionProgressInfoBox'):
            box.setFixedHeight(70)
            box_layout = box.layout()
            if box_layout is not None:
                box_layout.setContentsMargins(10, 9, 10, 9)
                box_layout.setSpacing(5)

    inspection_cls.__init__ = refined_init
    inspection_cls._progress_refined = True
