import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QPushButton


def apply_project_detail_refinements(ProjectDetailPage):
    """Apply final UI refinements without changing Project Detail behavior/data."""
    original_init = ProjectDetailPage.__init__

    def refined_init(self):
        original_init(self)

        # Breadcrumb: stronger hierarchy while keeping it secondary to the project title.
        breadcrumb = self.findChild(QLabel, "detailBreadcrumb")
        if breadcrumb:
            breadcrumb.setMinimumHeight(22)

        # Center Grade label/value in the summary area.
        grade_value = self.findChild(QLabel, "detailSummaryGrade")
        if grade_value:
            grade_value.setAlignment(Qt.AlignCenter)
            parent = grade_value.parentWidget()
            if parent:
                for label in parent.findChildren(QLabel, "detailSummaryLabel"):
                    if label.text() == "Grade":
                        label.setAlignment(Qt.AlignCenter)

        # Keep the left analytics column compact so the Issues list has enough width.
        body_cards = self.findChildren(QFrame, "detailBodyCard")
        distribution = next(
            (card for card in body_cards if any(
                label.text() == "Issue Distribution"
                for label in card.findChildren(QLabel, "detailBodyTitle")
            )),
            None,
        )
        history = next(
            (card for card in body_cards if any(
                label.text() == "Inspection History"
                for label in card.findChildren(QLabel, "detailBodyTitle")
            )),
            None,
        )
        issues = next(
            (card for card in body_cards if any(
                label.text().startswith("Issues (")
                for label in card.findChildren(QLabel, "detailBodyTitle")
            )),
            None,
        )
        detail = next(
            (card for card in body_cards if any(
                label.text() == "Issue Detail"
                for label in card.findChildren(QLabel, "detailBodyTitle")
            )),
            None,
        )

        if distribution:
            distribution.setMaximumWidth(188)
        if history:
            history.setMaximumWidth(188)
        if issues:
            issues.setMinimumWidth(205)
        if detail:
            detail.setMinimumWidth(225)

        # Default view shows exactly 8 issues; remaining items are exposed by More.
        issue_rows = self.findChildren(QFrame, "detailIssueListRow")
        for index, row in enumerate(issue_rows):
            row.setVisible(index < 8)

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
            # First blue icon = Issues, second = Resolved.
            if len(blue_icons) >= 1:
                _set_svg_icon(blue_icons[0], "detail_issues.svg", 23)
            if len(blue_icons) >= 2:
                _set_svg_icon(blue_icons[1], "detail_resolved.svg", 23)

        for object_name, filename in icon_map.items():
            label = self.findChild(QLabel, object_name)
            if label:
                _set_svg_icon(label, filename, 23)

        # Re-Inspect: modern refresh icon and stronger action presence.
        reinspect = self.findChild(QPushButton, "detailReInspectButton")
        if reinspect:
            reinspect.setText("Re-Inspect")
            reinspect.setIcon(QIcon(_icon_path("reinspect.svg")))
            reinspect.setIconSize(QSize(20, 20))
            reinspect.setFixedHeight(44)

    ProjectDetailPage.__init__ = refined_init


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
