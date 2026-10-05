import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from ui.project_detail_status_patch import (
    ISSUE_ROW_BODY_SPACING,
    ISSUE_ROW_MIN_HEIGHT,
    ISSUE_ROW_VERTICAL_MARGIN,
    ISSUE_STATUS_WIDTH,
    _build_issue_row,
    _required_description_height,
)


def _app():
    return QApplication.instance() or QApplication([])


def test_issue_row_uses_independent_header_status_column():
    _app()
    row = _build_issue_row(
        "Medium",
        "CHG-001",
        "SFR-043-ID-02 및 SFR-044-ID-01 등 요구사항 분리 및 취합됨",
        "미조치",
    )

    status = row.findChild(QLabel, "detailStatusOpen")
    description = row.findChild(QLabel, "detailIssueDescription")
    code = row.findChild(QLabel, "detailIssueCode")

    assert ISSUE_STATUS_WIDTH == 38
    assert status is not None
    assert status.minimumWidth() == ISSUE_STATUS_WIDTH
    assert status.maximumWidth() == ISSUE_STATUS_WIDTH
    assert status.contentsMargins().right() == 0

    assert description is not None
    assert description.wordWrap() is True
    assert description.toolTip() == description.text()
    assert "font-size:12px" in description.styleSheet()
    assert "font-weight:800" in description.styleSheet()

    assert code is not None and code.text() == "CHG-001"
    assert "font-size:12px" in code.styleSheet()
    assert "font-weight:900" in code.styleSheet()


def test_long_description_requires_more_than_legacy_row_height():
    _app()
    row = _build_issue_row(
        "Low",
        "CHG-001",
        "현재 문서에 이용기관·보유기관 서비스 이용현황 대시보드 기능과 기관 담당자 서비스 제공 기능이 추가됨",
        "미조치",
    )
    description = row.findChild(QLabel, "detailIssueDescription")
    description_height = _required_description_height(description)

    calculated_row_height = (
        ISSUE_ROW_VERTICAL_MARGIN * 2
        + 20
        + ISSUE_ROW_BODY_SPACING
        + description_height
    )
    assert ISSUE_ROW_MIN_HEIGHT == 82
    assert description_height > 18
    assert calculated_row_height > 78
