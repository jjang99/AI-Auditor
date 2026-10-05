from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


AUDIT_BADGE_STYLES = {
    "필수": ("#ffffff", "#dc2626", "#ef4444"),
    "협의": ("#ffffff", "#d97706", "#f59e0b"),
    "권고": ("#ffffff", "#7c3aed", "#8b5cf6"),
    "단기": ("#ffffff", "#7c3aed", "#8b5cf6"),
    "장기": ("#ffffff", "#0891b2", "#06b6d4"),
    "O": ("#ffffff", "#ef4444", "#fb7185"),
    "-": ("#334155", "#cbd5e1", "#e2e8f0"),
    "판정 없음": ("#ffffff", "#334155", "#64748b"),
}


def _audit_badge_style(value):
    text_color, background, border = AUDIT_BADGE_STYLES.get(
        str(value or "").strip(), AUDIT_BADGE_STYLES["판정 없음"]
    )
    return (
        f"color:{text_color};"
        f"background:{background};"
        f"border:1px solid {border};"
        "border-radius:7px;"
        "font-size:12px;"
        "font-weight:900;"
        "padding:0 7px;"
    )


def _style_audit_result_badges(page):
    """Make actual audit-result badges match the approved audit-help color roles."""
    for badge in page.findChildren(QLabel, "detailAuditResultBadge"):
        value = badge.text().strip() or "판정 없음"
        badge.setMinimumWidth(60)
        badge.setMaximumWidth(74)
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        badge.setStyleSheet(_audit_badge_style(value))


def apply_project_detail_audit_badge_patch(ProjectDetailPage):
    """Restyle audit judgment badges after each Issue Detail refresh."""
    original_update_issue_detail = ProjectDetailPage._runtime_update_issue_detail

    def patched_update_issue_detail(self, issue):
        original_update_issue_detail(self, issue)
        _style_audit_result_badges(self)

    ProjectDetailPage._runtime_update_issue_detail = patched_update_issue_detail
