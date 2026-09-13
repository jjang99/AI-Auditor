from PySide6.QtCore import Qt, QSize, QPointF, QRectF
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QFrame

from ui.inspection_rules_dialog import InspectionRulesDialog


def _category_pixmap(category, size=28):
    """폰트/SVG 플러그인에 의존하지 않고 카테고리 아이콘을 직접 그린다."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    pen = QPen(QColor("#60A5FA"), 2.0)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    s = float(size)

    if category == "보안 취약점":
        # 방패 + 체크
        path = QPainterPath()
        path.moveTo(s * 0.50, s * 0.10)
        path.lineTo(s * 0.79, s * 0.22)
        path.lineTo(s * 0.76, s * 0.56)
        path.cubicTo(s * 0.73, s * 0.74, s * 0.61, s * 0.84, s * 0.50, s * 0.90)
        path.cubicTo(s * 0.39, s * 0.84, s * 0.27, s * 0.74, s * 0.24, s * 0.56)
        path.lineTo(s * 0.21, s * 0.22)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(QPointF(s * 0.35, s * 0.50), QPointF(s * 0.46, s * 0.61))
        painter.drawLine(QPointF(s * 0.46, s * 0.61), QPointF(s * 0.66, s * 0.39))

    elif category == "코드 품질":
        # </> 형태
        painter.drawLine(QPointF(s * 0.36, s * 0.28), QPointF(s * 0.17, s * 0.50))
        painter.drawLine(QPointF(s * 0.17, s * 0.50), QPointF(s * 0.36, s * 0.72))
        painter.drawLine(QPointF(s * 0.64, s * 0.28), QPointF(s * 0.83, s * 0.50))
        painter.drawLine(QPointF(s * 0.83, s * 0.50), QPointF(s * 0.64, s * 0.72))
        painter.drawLine(QPointF(s * 0.57, s * 0.22), QPointF(s * 0.43, s * 0.78))

    elif category == "AI 특화 검증":
        # 칩/AI를 선으로 표현
        painter.drawRoundedRect(QRectF(s * 0.24, s * 0.24, s * 0.52, s * 0.52), s * 0.08, s * 0.08)
        for p in (0.34, 0.50, 0.66):
            painter.drawLine(QPointF(s * p, s * 0.13), QPointF(s * p, s * 0.24))
            painter.drawLine(QPointF(s * p, s * 0.76), QPointF(s * p, s * 0.87))
            painter.drawLine(QPointF(s * 0.13, s * p), QPointF(s * 0.24, s * p))
            painter.drawLine(QPointF(s * 0.76, s * p), QPointF(s * 0.87, s * p))
        painter.drawEllipse(QPointF(s * 0.40, s * 0.46), s * 0.035, s * 0.035)
        painter.drawEllipse(QPointF(s * 0.60, s * 0.46), s * 0.035, s * 0.035)
        painter.drawArc(QRectF(s * 0.39, s * 0.48, s * 0.22, s * 0.16), 200 * 16, 140 * 16)

    elif category == "성능 및 효율성":
        # 속도계
        painter.drawArc(QRectF(s * 0.16, s * 0.22, s * 0.68, s * 0.68), 20 * 16, 140 * 16)
        painter.drawLine(QPointF(s * 0.50, s * 0.58), QPointF(s * 0.69, s * 0.38))
        painter.drawEllipse(QPointF(s * 0.50, s * 0.58), s * 0.045, s * 0.045)
        painter.drawLine(QPointF(s * 0.26, s * 0.70), QPointF(s * 0.74, s * 0.70))

    painter.end()
    return pixmap


def apply_inspection_visual_polish(InspectionPage):
    """Inspection UI의 잔여 시각 보정만 적용한다."""

    original_init = InspectionPage.__init__
    original_refresh_file_table = InspectionPage._refresh_file_table
    original_dialog_show_event = InspectionRulesDialog.showEvent

    import os
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
    trash_icon = QIcon(os.path.join(icon_dir, "trash.svg"))

    def polish_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            if row.layout() is not None:
                row.layout().setSpacing(11)

            count_label = row.findChild(QLabel, "inspectionRuleCount")
            if count_label is not None:
                count_label.setFixedWidth(122)

    def apply_trash_icon(self):
        for button in self.findChildren(QPushButton, "inspectionSmallButton"):
            if button.text() == "전체 삭제":
                button.setIcon(trash_icon)
                button.setIconSize(QSize(15, 15))

        for button in self.findChildren(QPushButton, "inspectionFileDeleteButton"):
            button.setText("")
            button.setIcon(trash_icon)
            button.setIconSize(QSize(16, 16))

    def patched_init(self):
        original_init(self)
        polish_rule_rows(self)
        apply_trash_icon(self)

    def patched_refresh_file_table(self):
        original_refresh_file_table(self)
        apply_trash_icon(self)

    def patched_dialog_show_event(dialog, event):
        # 먼저 원래 showEvent를 처리한 뒤, 마지막에 아이콘을 강제로 그려 넣는다.
        # 이 순서로 하면 다른 초기화/스타일 코드가 아이콘을 다시 지우지 못한다.
        original_dialog_show_event(dialog, event)

        title = dialog.findChild(QLabel, "rulesDialogTitle")
        category = title.text() if title is not None else ""
        icon_label = dialog.findChild(QLabel, "rulesDialogShieldIcon")

        if icon_label is not None:
            icon_label.clear()
            icon_label.setText("")
            icon_label.setFixedSize(34, 34)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setPixmap(_category_pixmap(category, 28))
            icon_label.setVisible(True)
            icon_label.raise_()

        replacement = dialog.findChild(QLabel, "rulesDialogCategoryIcon")
        if replacement is not None:
            replacement.hide()

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_file_table = patched_refresh_file_table
    InspectionRulesDialog.showEvent = patched_dialog_show_event
