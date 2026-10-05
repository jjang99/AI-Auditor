import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QWidget

from ui.project_detail_audit_badge_patch import (
    AUDIT_BADGE_STYLES,
    _audit_badge_style,
    _style_audit_result_badges,
)


def _app():
    return QApplication.instance() or QApplication([])


def test_audit_result_palette_matches_help_roles():
    assert AUDIT_BADGE_STYLES["필수"][1] == "#dc2626"
    assert AUDIT_BADGE_STYLES["협의"][1] == "#d97706"
    assert AUDIT_BADGE_STYLES["권고"][1] == "#7c3aed"
    assert AUDIT_BADGE_STYLES["단기"][1] == "#7c3aed"
    assert AUDIT_BADGE_STYLES["장기"][1] == "#0891b2"
    assert AUDIT_BADGE_STYLES["O"][1] == "#ef4444"
    assert AUDIT_BADGE_STYLES["-"][1] == "#cbd5e1"


def test_pending_badge_is_readable_and_result_badges_are_styled():
    _app()
    page = QWidget()
    values = ["판정 없음", "필수", "협의", "권고", "단기", "장기", "O", "-"]
    labels = []
    for value in values:
        label = QLabel(value, page)
        label.setObjectName("detailAuditResultBadge")
        labels.append(label)

    _style_audit_result_badges(page)

    for label in labels:
        assert label.minimumWidth() == 60
        assert label.maximumWidth() == 74
        assert label.height() == 24
        style = label.styleSheet()
        assert "font-size:12px" in style
        assert "font-weight:900" in style

    assert "background:#334155" in _audit_badge_style("판정 없음")
    assert "background:#dc2626" in _audit_badge_style("필수")
    assert "background:#d97706" in _audit_badge_style("협의")
