import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QFrame,
    QLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def apply_project_detail_refinements(ProjectDetailPage):
    """Apply final UI refinements without changing Project Detail behavior/data."""
    original_init = ProjectDetailPage.__init__

    def refined_init(self):
        original_init(self)

        breadcrumb = self.findChild(QLabel, "detailBreadcrumb")
        if breadcrumb:
            breadcrumb.setMinimumHeight(24)

        grade_value = self.findChild(QLabel, "detailSummaryGrade")
        if grade_value:
            grade_value.setAlignment(Qt.AlignCenter)
            parent = grade_value.parentWidget()
            if parent:
                for label in parent.findChildren(QLabel, "detailSummaryLabel"):
                    if label.text() == "Grade":
                        label.setAlignment(Qt.AlignCenter)

        for label in self.findChildren(QLabel):
            if label.text() == "마지막 검사일":
                label.setObjectName("detailLastInspectionLabel")
            elif "2026.07.25 14:32" in label.text() and label.objectName() == "detailDate":
                label.setObjectName("detailLastInspectionDate")

        body_cards = self.findChildren(QFrame, "detailBodyCard")
        distribution = _card_by_title(body_cards, "Issue Distribution")
        history = _card_by_title(body_cards, "Inspection History")
        issues = _card_by_prefix(body_cards, "Issues (")
        detail = _card_by_title(body_cards, "Issue Detail")

        # Fixed 840px window: reserve more width for Issue Detail.
        # 좌측 145 < 가운데 198 < 우측 280
        if distribution:
            distribution.setFixedWidth(145)
            _refine_distribution(distribution)
        if history:
            history.setFixedWidth(145)
            _refine_history(history)
        if issues:
            issues.setFixedWidth(198)
            scroll = issues.findChild(QScrollArea, "detailIssueScroll")
            if scroll:
                scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        if detail:
            detail.setFixedWidth(280)

        issue_rows = self.findChildren(QFrame, "detailIssueListRow")
        for index, row in enumerate(issue_rows):
            row.setVisible(index < 8)
            _refine_issue_row(row)

        more_buttons = [
            button for button in self.findChildren(QPushButton, "detailHistoryButton")
            if button.text() == "더 보기"
        ]
        for button in more_buttons:
            try:
                button.clicked.disconnect()
            except (RuntimeError, TypeError):
                pass

            def show_remaining(_checked=False, rows=issue_rows, more_button=button, issue_card=issues):
                for row in rows:
                    row.show()
                more_button.hide()
                if issue_card:
                    scroll_area = issue_card.findChild(QScrollArea, "detailIssueScroll")
                    if scroll_area:
                        scroll_area.verticalScrollBar().setValue(0)

            button.clicked.connect(show_remaining)
            button.show()

        for button in self.findChildren(QPushButton, "detailHistoryButton"):
            button.setMinimumHeight(34)
        sort_button = self.findChild(QPushButton, "detailSortButton")
        if sort_button:
            sort_button.setMinimumHeight(30)
            sort_button.setMinimumWidth(78)

        icon_map = {
            "detailStatIcon_purple": "detail_score.svg",
            "detailStatIcon_green": "detail_grade.svg",
        }
        blue_icons = self.findChildren(QLabel, "detailStatIcon_blue")
        if blue_icons:
            if len(blue_icons) >= 1:
                _set_svg_icon(blue_icons[0], "detail_issues.svg", 23)
            if len(blue_icons) >= 2:
                _set_svg_icon(blue_icons[1], "detail_resolved.svg", 23)

        for object_name, filename in icon_map.items():
            label = self.findChild(QLabel, object_name)
            if label:
                _set_svg_icon(label, filename, 23)

        if detail:
            _replace_detail_metadata_rows(detail)
            _refine_detail_header(detail)
            _refine_detail_sections(detail)
            _make_issue_detail_scrollable(detail)

        reinspect = self.findChild(QPushButton, "detailReInspectButton")
        if reinspect:
            reinspect.setText("Re-Inspect")
            reinspect.setIcon(QIcon(_icon_path("reinspect.svg")))
            reinspect.setIconSize(QSize(21, 21))
            reinspect.setFixedHeight(44)

    ProjectDetailPage.__init__ = refined_init


def _card_by_title(cards, text):
    return next((card for card in cards if any(
        label.text() == text for label in card.findChildren(QLabel, "detailBodyTitle")
    )), None)


def _card_by_prefix(cards, prefix):
    return next((card for card in cards if any(
        label.text().startswith(prefix) for label in card.findChildren(QLabel, "detailBodyTitle")
    )), None)


def _refine_distribution(card):
    layout = card.layout()
    if layout:
        layout.setSpacing(13)
    for label in card.findChildren(QLabel, "detailSmallText"):
        label.setMinimumHeight(17)
        if label.text().isdigit():
            label.setMinimumWidth(12)


def _refine_history(card):
    """Narrow history column: wrap long descriptions instead of clipping them."""
    for label in card.findChildren(QLabel, "detailHistoryDate"):
        label.setWordWrap(False)
        label.setMinimumHeight(17)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    for label in card.findChildren(QLabel, "detailHistoryType"):
        label.setWordWrap(True)
        label.setMinimumWidth(0)
        label.setMinimumHeight(30)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)


def _refine_issue_row(row):
    row.setFixedHeight(72)

    badge = next((x for x in row.findChildren(QLabel) if x.objectName().startswith("detailBadge_")), None)
    if badge:
        badge.setFixedWidth(32)
        badge.setFixedHeight(20)
        badge.setAlignment(Qt.AlignCenter)

    status = next((x for x in row.findChildren(QLabel) if x.objectName() in ("detailStatusResolved", "detailStatusOpen")), None)
    if status:
        status.setFixedWidth(31)
        status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    layout = row.layout()
    if layout:
        layout.setContentsMargins(5, 7, 3, 7)
        layout.setSpacing(3)

    for label in row.findChildren(QLabel):
        if label.objectName() == "detailIssueCode":
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            label.setMinimumWidth(0)
        elif label.objectName() == "detailIssueDescription":
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            label.setMinimumWidth(0)
            label.setWordWrap(True)
            label.setMinimumHeight(34)


def _refine_detail_header(detail_card):
    badge = detail_card.findChild(QLabel, "detailBadge_critical")
    status = detail_card.findChild(QLabel, "detailStatusOpen")
    code = detail_card.findChild(QLabel, "detailIssueDetailCode")
    if badge:
        badge.setFixedWidth(58)
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignCenter)
    if status:
        status.setFixedWidth(48)
        status.setMinimumHeight(24)
        status.setAlignment(Qt.AlignCenter)
    if code:
        code.setMinimumHeight(24)
        code.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)


def _refine_detail_sections(detail_card):
    section_titles = {"제목", "설명", "근거", "영향", "AI 권고"}
    for label in detail_card.findChildren(QLabel, "detailTextLabel"):
        if label.text() in section_titles:
            label.setMinimumHeight(22)
            label.setContentsMargins(0, 4, 0, 3)

    for label in detail_card.findChildren(QLabel, "detailTextBody"):
        label.setWordWrap(True)
        label.setContentsMargins(0, 1, 0, 5)
        label.setMinimumHeight(20)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


def _make_issue_detail_scrollable(detail_card):
    """Keep Issue Detail title fixed; scroll the long detail content below it."""
    layout = detail_card.layout()
    if layout is None or detail_card.findChild(QScrollArea, "detailContentScroll"):
        return

    # Keep the first widget (Issue Detail title) fixed and move everything else into scroll content.
    items = []
    while layout.count() > 1:
        item = layout.takeAt(1)
        if item is not None:
            items.append(item)

    scroll = QScrollArea()
    scroll.setObjectName("detailContentScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    content = QWidget()
    content.setObjectName("detailContentContainer")
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 4, 0, 0)
    content_layout.setSpacing(6)
    # Long wrapped labels must keep their calculated minimum height so the
    # scroll area grows vertically instead of compressing/clipping the text.
    content_layout.setSizeConstraint(QLayout.SetMinimumSize)

    for item in items:
        if item.widget() is not None:
            content_layout.addWidget(item.widget())
        elif item.layout() is not None:
            content_layout.addLayout(item.layout())
        elif item.spacerItem() is not None:
            content_layout.addItem(item.spacerItem())

    scroll.setWidget(content)

    # Match the Issues card structure: the outer card has no side padding,
    # while the fixed title and the scroll content own their own padding.
    # This lets the vertical scrollbar sit directly on the card's right edge.
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    title = layout.itemAt(0).widget()
    if title is not None:
        title.setContentsMargins(12, 12, 12, 6)
        title.setMinimumHeight(38)
    content_layout.setContentsMargins(12, 4, 10, 12)
    scroll.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(scroll, 1)


def _replace_detail_metadata_rows(detail_card):
    layout = detail_card.layout()
    if layout is None:
        return
    category = next((x for x in detail_card.findChildren(QLabel) if x.text().startswith("카테고리")), None)
    rule = next((x for x in detail_card.findChildren(QLabel) if x.text().startswith("발견 기준")), None)
    if not category or not rule:
        return
    category_index = layout.indexOf(category)
    rule_index = layout.indexOf(rule)
    insert_at = min(i for i in (category_index, rule_index) if i >= 0)
    layout.removeWidget(category)
    layout.removeWidget(rule)
    category.hide()
    rule.hide()
    layout.insertWidget(insert_at, _metadata_row("카테고리", "요구사항", False))
    layout.insertWidget(insert_at + 1, _metadata_row("발견 기준", "Requirement Consistency Rule", True))


def _metadata_row(label_text, value_text, wrap=False):
    row = QFrame()
    row.setObjectName("detailMetaRow")
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(8, 5, 8, 5)
    row_layout.setSpacing(8)
    label = QLabel(label_text)
    label.setObjectName("detailMetaLabel")
    label.setFixedWidth(50)
    label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    value = QLabel(value_text)
    value.setObjectName("detailMetaValue")
    value.setWordWrap(wrap)
    value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    value.setMinimumWidth(0)
    value.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    row_layout.addWidget(label)
    row_layout.addWidget(value, 1)
    return row


def _icon_path(filename):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", filename)


def _set_svg_icon(label, filename, size):
    label.setText("")
    label.setPixmap(QIcon(_icon_path(filename)).pixmap(QSize(size, size)))
    label.setAlignment(Qt.AlignCenter)
