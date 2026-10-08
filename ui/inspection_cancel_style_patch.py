from PySide6.QtWidgets import QPushButton


def apply_inspection_cancel_style_patch(InspectionPage):
    if getattr(InspectionPage, "_cancel_style_patch_applied", False):
        return

    original_apply_rule_text_theme = InspectionPage.apply_rule_text_theme

    def apply_cancel_button_theme(self, is_dark):
        button = self.progress_card.findChild(
            QPushButton,
            "inspectionCancelButton",
        )
        if button is None:
            return

        if is_dark:
            button.setStyleSheet(
                """
                QPushButton#inspectionCancelButton {
                    color:#fecaca;
                    background:#2b161a;
                    border:1px solid #a94a55;
                    border-radius:7px;
                    font-size:13px;
                    font-weight:800;
                }
                QPushButton#inspectionCancelButton:hover {
                    color:#ffffff;
                    background:#442025;
                    border-color:#d46670;
                }
                QPushButton#inspectionCancelButton:disabled {
                    color:#94a3b8;
                    background:#1f2937;
                    border-color:#475569;
                }
                """
            )
        else:
            button.setStyleSheet(
                """
                QPushButton#inspectionCancelButton {
                    color:#b4232b;
                    background:#fffafa;
                    border:1px solid #d6a0a5;
                    border-radius:7px;
                    font-size:13px;
                    font-weight:800;
                }
                QPushButton#inspectionCancelButton:hover {
                    color:#991b1b;
                    background:#fff1f2;
                    border-color:#c85d66;
                }
                QPushButton#inspectionCancelButton:disabled {
                    color:#94a3b8;
                    background:#f1f5f9;
                    border-color:#cbd5e1;
                }
                """
            )

    def patched_apply_rule_text_theme(self, is_dark):
        original_apply_rule_text_theme(self, is_dark)
        apply_cancel_button_theme(self, is_dark)

    InspectionPage.apply_rule_text_theme = patched_apply_rule_text_theme
    InspectionPage._apply_cancel_button_theme = apply_cancel_button_theme
    InspectionPage._cancel_style_patch_applied = True
