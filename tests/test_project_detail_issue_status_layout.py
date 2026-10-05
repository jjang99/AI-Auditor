import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QWidget

from ui.project_detail_status_patch import (
    ISSUE_STATUS_WIDTH,
    _fix_issue_status_columns,
)


def _app():
    return QApplication.instance() or QApplication([])


def test_issue_status_width_is_locked_to_unclipped_column():
    _app()
    assert ISSUE_STATUS_WIDTH == 50


def test_issue_status_column_has_no_padding_and_keeps_full_text_space():
    _app()
    page = QWidget()
    row = QFrame(page)
    row.setObjectName("detailIssueListRow")
    layout = QHBoxLayout(row)

    description = QLabel("설명")
    description.setObjectName("detailIssueDescription")
    status = QLabel("미조치")
    status.setObjectName("detailStatusOpen")
    status.setFixedWidth(38)
    status.setContentsMargins(0, 0, 10, 0)
    layout.addWidget(description)
    layout.addWidget(status)

    _fix_issue_status_columns(page)

    assert status.width() == ISSUE_STATUS_WIDTH
    assert status.minimumWidth() == ISSUE_STATUS_WIDTH
    assert status.maximumWidth() == ISSUE_STATUS_WIDTH
    assert status.contentsMargins().right() == 0
    assert status.alignment() == (Qt.AlignCenter | Qt.AlignVCenter)
    assert description.contentsMargins().right() == 0
