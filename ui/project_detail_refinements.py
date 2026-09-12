import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy


def apply_project_detail_refinements(ProjectDetailPage):
    """Apply final UI refinements without changing Project Detail behavior/data."""
    original_init = ProjectDetailPage.__init__

    def refined_init(self):
        original_init(self)

        # Breadcrumb: stronger hierarchy while keeping it secondary to the project title.
        breadcrumb = self.findChild(QLabel, "detailBreadcrumb")
        if breadcrumb:
            breadcrumb.setMinimumHeight(24)

        # Summary: center Grade and give the inspection date its own readable style hooks.
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

        # Identify body cards.
        body_cards = self.findChildren(QFrame, "detailBodyCard")
        distribution = _card_by_title(body_cards, "Issue Distribution")
        history = _card_by_title(body_cards, "Inspection History")
        issues = _card_by_prefix(body_cards, "Issues (")
        detail = _card_by_title(body_cards, "Issue Detail")

        # Keep analytics compact, but don't starve Issues. Let Issue Detail stay readable too.
        if distribution:
            distribution.setMaximumWidth(178)
        if history:
            history.setMaximumWidth(178)
        if issues:
            issues.setMinimumWidth(218)
            issues.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if detail:
            detail.setMinimumWidth(220)
            detail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Default view shows exactly 8 issues; remaining items are exposed by More.
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

            def show_remaining(_checked=False, rows=issue_rows, more_button=button):
                for row in rows:
                    row.show()
                more_button.hide()

            button.clicked.connect(show_remaining)
            button.show()

        # Replace glyph-like stat icons with simple outline SVG icons.
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

        # Issue Detail: preserve original structure but make metadata rows match the final mock-up.
        if detail:
            _replace_detail_metadata_rows(detail)

        # Re-Inspect: modern refresh icon and stronger action presence.
        reinspect = self.findChild(QPushButton, "detailReInspectButton")
        if reinspect:
            reinspect.setText("Re-Inspect")
            reinspect.setIcon(QIcon(_icon_path("reinspect.svg")))
            reinspect.setIconSize(QSize(21, 21))
            reinspect.setFixedHeight(44)

    ProjectDetailPage.__init__ = refined_init


def _card_by_title(cards, text):
    return next(
        (card for card in cards if any(
            label.text() == text for label in card.findChildren(QLabel, "detailBodyTitle")
        )),
        None,
    )


def _card_by_prefix(cards, prefix):
    return next(
        (card for card in cards if any(
            label.text().startswith(prefix) for label in card.findChildren(QLabel, "detailBodyTitle")
        )),
        None,
    )


def _refine_issue_row(row):
    """Give the issue title/description more usable width without changing the data."""
    badge = next((x for x in row.findChildren(QLabel) if x.objectName().startswith("detailBadge_")), None)
    if badge:
        badge.setFixedWidth(46)

    status = next(
        (x for x in row.findChildren(QLabel)
         if x.objectName() in ("detailStatusResolved", "detailStatusOpen")),
        None,
    )
    if status:
        status.setFixedWidth(36)
        status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    # Prevent code/description labels from reserving unnecessary width.
    for label in row.findChildren(QLabel):
        if label.objectName() in ("detailIssueCode", "detailIssueDescription"):
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            label.setMinimumWidth(0)


def _replace_detail_metadata_rows(detail_card):
    layout = detail_card.layout()
    if layout is None:
        return

    category = next(
        (x for x in detail_card.findChildren(QLabel) if x.text().startswith("카테고리")),
        None,
    )
    rule = next(
        (x for x in detail_card.findChildren(QLabel) if x.text().startswith("발견 기준")),
        None,
    )

    if not category or not rule:
        return

    category_index = layout.indexOf(category)
    rule_index = layout.indexOf(rule)
    insert_at = min(i for i in (category_index, rule_index) if i >= 0)

    layout.removeWidget(category)
    layout.removeWidget(rule)
    category.hide()
    rule.hide()

    category_row = _metadata_row("카테고리", "요구사항")
    rule_row = _metadata_row("발견 기준", "Requirement Consistency Rule")
    layout.insertWidget(insert_at, category_row)
    layout.insertWidget(insert_at + 1, rule_row)


def _metadata_row(label_text, value_text):
    row = QFrame()
    row.setObjectName("detailMetaRow")
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(8, 4, 8, 4)
    row_layout.setSpacing(8)

    label = QLabel(label_text)
    label.setObjectName("detailMetaLabel")
    label.setFixedWidth(50)

    value = QLabel(value_text)
    value.setObjectName("detailMetaValue")
    value.setWordWrap(False)

    row_layout.addWidget(label)
    row_layout.addWidget(value, 1)
    return row


def _icon_path(filename):
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets",
        "icons",
        filename,
    )


def _set_svg_icon(label, filename, size):
    label.setText("")
    label.setPixmap(QIcon(_icon_path(filename)).pixmap(QSize(size, size)))
    label.setAlignment(Qt.AlignCenter)
