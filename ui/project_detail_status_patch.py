from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel

ISSUE_STATUS_WIDTH = 50


def _fix_issue_status_columns(page):
    """Apply final status-column sizing after runtime has created issue rows."""
    for row in page.findChildren(QFrame, "detailIssueListRow"):
        status = next(
            (
                label
                for label in row.findChildren(QLabel)
                if label.objectName() in ("detailStatusResolved", "detailStatusOpen")
            ),
            None,
        )
        if status is None:
            continue
        status.setContentsMargins(0, 0, 0, 0)
        status.setFixedWidth(ISSUE_STATUS_WIDTH)
        status.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)


def apply_project_detail_status_patch(ProjectDetailPage):
    """Patch runtime issue refresh once, then fix status columns afterwards."""
    original_update_issues = ProjectDetailPage._runtime_update_issues

    def patched_update_issues(self, issues):
        original_update_issues(self, issues)
        _fix_issue_status_columns(self)

    ProjectDetailPage._runtime_update_issues = patched_update_issues
