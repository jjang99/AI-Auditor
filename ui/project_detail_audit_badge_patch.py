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
}

AUDIT_PENDING_DARK = ("#ffffff", "#334155", "#64748b")
AUDIT_PENDING_LIGHT = ("#334155", "#e2e8f0", "#94a3b8")


def _audit_badge_colors(value, is_dark_mode=True):
    normalized = str(value or "").strip() or "판정 없음"
    if normalized == "판정 없음":
        return AUDIT_PENDING_DARK if is_dark_mode else AUDIT_PENDING_LIGHT
    return AUDIT_BADGE_STYLES.get(normalized, AUDIT_PENDING_DARK if is_dark_mode else AUDIT_PENDING_LIGHT)


def _audit_badge_style(value, is_dark_mode=True):
    text_color, background, border = _audit_badge_colors(value, is_dark_mode)
    return (
        f"color:{text_color};"
        f"background:{background};"
        f"border:1px solid {border};"
        "border-radius:7px;"
        "font-size:12px;"
        "font-weight:900;"
        "padding:0 7px;"
    )


def _style_audit_result_badges(page, is_dark_mode=None):
    """Match actual audit-result badges to the approved help colors and active theme."""
    if is_dark_mode is None:
        window = page.window() if hasattr(page, "window") else None
        is_dark_mode = bool(getattr(window, "is_dark_mode", True))

    for badge in page.findChildren(QLabel, "detailAuditResultBadge"):
        value = badge.text().strip() or "판정 없음"
        badge.setMinimumWidth(60)
        badge.setMaximumWidth(74)
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        badge.setStyleSheet(_audit_badge_style(value, is_dark_mode))

        # Give the audit mini-card a little more breathing room between
        # its title and result badge without changing the 3-column layout.
        card = badge.parentWidget()
        if card is not None:
            layout = card.layout()
            if layout is not None:
                layout.setSpacing(8)
            card.setMinimumHeight(58)
            card.setMaximumHeight(58)


def apply_project_detail_audit_badge_patch(ProjectDetailPage, MainWindow=None):
    """Restyle audit judgment badges after detail refresh and theme switches."""
    original_update_issue_detail = ProjectDetailPage._runtime_update_issue_detail

    def patched_update_issue_detail(self, issue):
        original_update_issue_detail(self, issue)
        _style_audit_result_badges(self)

    ProjectDetailPage._runtime_update_issue_detail = patched_update_issue_detail

    if MainWindow is None or getattr(MainWindow, "_audit_badge_theme_patch_applied", False):
        return

    original_apply_theme = MainWindow.apply_theme

    def patched_apply_theme(self):
        original_apply_theme(self)
        page = getattr(self, "project_detail_page", None)
        if page is not None:
            _style_audit_result_badges(page, self.is_dark_mode)

    MainWindow.apply_theme = patched_apply_theme
    MainWindow._audit_badge_theme_patch_applied = True
