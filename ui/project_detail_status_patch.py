from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)


ISSUE_STATUS_WIDTH = 38
ISSUE_ROW_TEXT_WIDTH = 150
ISSUE_ROW_MIN_HEIGHT = 82
ISSUE_ROW_HORIZONTAL_MARGIN = 9
ISSUE_ROW_RIGHT_MARGIN = 10
ISSUE_ROW_VERTICAL_MARGIN = 7
ISSUE_ROW_HEADER_SPACING = 6
ISSUE_ROW_BODY_SPACING = 5


def _strengthen_issue_text(code_label, description_label):
    """Use widget-local font rules so global theme QSS cannot shrink issue text."""
    if code_label is not None:
        code_label.setStyleSheet("font-size:12px; font-weight:900;")
    if description_label is not None:
        description_label.setStyleSheet("font-size:12px; font-weight:800;")


def _build_issue_row(severity, code, description, status):
    """Build a readable issue row without competing text/status columns."""
    row = QFrame()
    row.setObjectName("detailIssueListRow")
    row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    outer = QVBoxLayout(row)
    outer.setContentsMargins(
        ISSUE_ROW_HORIZONTAL_MARGIN,
        ISSUE_ROW_VERTICAL_MARGIN,
        ISSUE_ROW_RIGHT_MARGIN,
        ISSUE_ROW_VERTICAL_MARGIN,
    )
    outer.setSpacing(ISSUE_ROW_BODY_SPACING)

    header = QHBoxLayout()
    header.setContentsMargins(0, 0, 0, 0)
    header.setSpacing(ISSUE_ROW_HEADER_SPACING)

    badge = QLabel(severity)
    badge.setObjectName(f"detailBadge_{str(severity).lower()}")
    badge.setFixedSize(48, 20)
    badge.setAlignment(Qt.AlignCenter)

    code_label = QLabel(str(code or ""))
    code_label.setObjectName("detailIssueCode")
    code_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

    status_label = QLabel(str(status or ""))
    status_label.setObjectName(
        "detailStatusResolved" if status == "조치완료" else "detailStatusOpen"
    )
    status_label.setFixedWidth(ISSUE_STATUS_WIDTH)
    status_label.setContentsMargins(0, 0, 0, 0)
    status_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    header.addWidget(badge)
    header.addWidget(code_label)
    header.addStretch(1)
    header.addWidget(status_label)

    description_label = QLabel(str(description or ""))
    description_label.setObjectName("detailIssueDescription")
    description_label.setWordWrap(True)
    description_label.setMinimumWidth(0)
    description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    description_label.setToolTip(str(description or ""))

    _strengthen_issue_text(code_label, description_label)

    outer.addLayout(header)
    outer.addWidget(description_label)
    return row


def _required_description_height(label, width=ISSUE_ROW_TEXT_WIDTH):
    """Calculate wrapped text height for the frozen Issues-card width."""
    metrics = label.fontMetrics()
    rect = metrics.boundingRect(
        QRect(0, 0, width, 2400),
        Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop,
        label.text(),
    )
    return max(20, rect.height() + 4)


def _finalize_issue_rows(page):
    """Undo runtime's legacy row lock and fit each real finding completely."""
    for row in page.findChildren(QFrame, "detailIssueListRow"):
        status = next(
            (
                label
                for label in row.findChildren(QLabel)
                if label.objectName() in ("detailStatusResolved", "detailStatusOpen")
            ),
            None,
        )
        description = row.findChild(QLabel, "detailIssueDescription")
        code_label = row.findChild(QLabel, "detailIssueCode")

        if status is not None:
            status.setContentsMargins(0, 0, 0, 0)
            status.setFixedWidth(ISSUE_STATUS_WIDTH)
            status.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        _strengthen_issue_text(code_label, description)

        if description is None:
            continue

        description.setWordWrap(True)
        description.setMinimumWidth(0)
        description_height = _required_description_height(description)
        description.setMinimumHeight(description_height)

        required_height = max(
            ISSUE_ROW_MIN_HEIGHT,
            ISSUE_ROW_VERTICAL_MARGIN * 2
            + 20
            + ISSUE_ROW_BODY_SPACING
            + description_height,
        )
        row.setMinimumHeight(required_height)
        row.setMaximumHeight(required_height)


def apply_project_detail_status_patch(ProjectDetailPage):
    """Keep frozen Project Detail columns but make real issue rows readable."""
    original_update_issues = ProjectDetailPage._runtime_update_issues

    def patched_create_issue_row(self, severity, code, description, status):
        return _build_issue_row(severity, code, description, status)

    def patched_update_issues(self, issues):
        original_update_issues(self, issues)
        _finalize_issue_rows(self)

    ProjectDetailPage.create_issue_row = patched_create_issue_row
    ProjectDetailPage._runtime_update_issues = patched_update_issues
