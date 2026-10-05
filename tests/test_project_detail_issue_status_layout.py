import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel

from ui.project_detail_refinements import (
    ISSUE_STATUS_RIGHT_CONTENT_PADDING,
    _apply_issue_status_inset,
)


def _app():
    return QApplication.instance() or QApplication([])


def test_issue_status_inset_is_locked_to_five_pixel_visual_shift():
    _app()
    assert ISSUE_STATUS_RIGHT_CONTENT_PADDING == 10


def test_issue_status_inset_applies_only_to_status_label():
    _app()
    row = QFrame()
    layout = QHBoxLayout(row)

    description = QLabel("설명")
    description.setObjectName("detailIssueDescription")
    status = QLabel("미조치")
    status.setObjectName("detailStatusOpen")
    layout.addWidget(description)
    layout.addWidget(status)

    result = _apply_issue_status_inset(row)

    assert result is status
    assert status.contentsMargins().right() == 10
    assert description.contentsMargins().right() == 0
