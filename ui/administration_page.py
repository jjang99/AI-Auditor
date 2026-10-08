import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)

from ui.sidebar import Sidebar
from ui.administration_rules_dialog import AdministrationRulesDialog
from app.database.repositories.data_management_repository import (
    get_data_management_summary,
)
from rules.definitions.document_rule_catalog import (
    get_document_rule_categories,
    get_total_rule_count,
)


class AdministrationPage(QWidget):
    def __init__(self):
        super().__init__()

        categories = get_document_rule_categories()
        total_rules = get_total_rule_count()

        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.sidebar = Sidebar("Administration")
        page_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("projectsContent")
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 12, 20, 10)
        main_layout.setSpacing(0)
        page_layout.addWidget(content, 1)

        title = QLabel("Administration")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)
        main_layout.addSpacing(8)

        summary_label = QLabel("검사 기준 요약")
        summary_label.setObjectName("adminAccentLabel")
        main_layout.addWidget(summary_label)
        main_layout.addSpacing(4)

        summary_frame = QFrame()
        summary_frame.setObjectName("adminSummaryFrame")
        summary_frame.setFixedHeight(72)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(22, 6, 22, 6)
        summary_layout.setSpacing(0)
        self.summary_value_labels = {}
        for value, label, object_name in [
            (str(total_rules), "전체 규칙", "adminSummaryValue"),
            (str(total_rules), "활성 규칙", "adminSummaryActive"),
            ("0", "비활성 규칙", "adminSummaryInactive"),
        ]:
            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 1, 0, 1)
            cell_layout.setSpacing(0)
            value_label = QLabel(value)
            value_label.setObjectName(object_name)
            value_label.setAlignment(Qt.AlignCenter)
            self.summary_value_labels[object_name] = value_label
            text_label = QLabel(label)
            text_label.setObjectName("adminSummaryText")
            text_label.setAlignment(Qt.AlignCenter)
            cell_layout.addWidget(value_label)
            cell_layout.addWidget(text_label)
            summary_layout.addWidget(cell, 1)
        main_layout.addWidget(summary_frame)
        main_layout.addSpacing(10)

        rules_card = QFrame()
        rules_card.setObjectName("adminSectionCard")
        rules_layout = QVBoxLayout(rules_card)
        rules_layout.setContentsMargins(16, 10, 16, 8)
        rules_layout.setSpacing(0)

        section_title = QLabel("1. 검사 기준 관리")
        section_title.setObjectName("adminSectionTitle")
        rules_layout.addWidget(section_title)
        rules_layout.addSpacing(8)

        table = QFrame()
        table.setObjectName("adminRulesTable")
        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("adminRulesHeader")
        header.setFixedHeight(36)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 0, 12, 0)
        header_layout.setSpacing(8)
        for text, width in [("카테고리", 225), ("전체 규칙", 78), ("활성 규칙", 78), ("비활성 규칙", 78), ("관리", 58)]:
            label = QLabel(text)
            label.setObjectName("adminHeaderText")
            label.setFixedWidth(width)
            label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(label)
        table_layout.addWidget(header)

        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        category_icons = {
            "AUD": "rule_aud.svg",
            "REQ": "rule_req.svg",
            "CHG": "rule_chg.svg",
            "FP": "rule_fp.svg",
            "AI": "rule_ai.svg",
        }
        categories = [
            (
                category.name,
                category.total_count,
                category.total_count,
                0,
                category_icons[category.code],
            )
            for category in categories
        ]
        self.category_counts = {}
        self.category_rule_states = {}
        for name, total, active, inactive, icon_file in categories:
            row = QFrame()
            row.setObjectName("adminCategoryRow")
            row.setFixedHeight(50)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 0, 12, 0)
            row_layout.setSpacing(8)

            category = QWidget()
            category.setFixedWidth(225)
            category_layout = QHBoxLayout(category)
            category_layout.setContentsMargins(0, 0, 0, 0)
            category_layout.setSpacing(10)

            icon = QLabel()
            icon.setPixmap(QIcon(os.path.join(icon_dir, icon_file)).pixmap(QSize(24, 24)))
            icon.setFixedSize(28, 28)
            icon.setAlignment(Qt.AlignCenter)

            name_label = QLabel(name)
            name_label.setObjectName("adminCategoryName")
            name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            category_layout.addWidget(icon)
            category_layout.addWidget(name_label, 1)
            row_layout.addWidget(category)

            row_counts = {}
            for value, object_name in [(total, "adminCount"), (active, "adminActiveCount"), (inactive, "adminInactiveCount")]:
                count = QLabel(str(value))
                count.setObjectName(object_name)
                count.setFixedWidth(78)
                count.setAlignment(Qt.AlignCenter)
                row_layout.addWidget(count)
                row_counts[object_name] = count
            self.category_counts[name] = row_counts

            view = QPushButton("보기")
            view.setObjectName("adminViewButton")
            view.setFixedSize(58, 30)
            view.setCursor(Qt.PointingHandCursor)
            view.clicked.connect(
                lambda checked=False, n=name, t=total, a=active, i=inactive, icon_name=icon_file:
                self.open_rules(n, t, a, i, icon_name)
            )
            row_layout.addWidget(view)
            table_layout.addWidget(row)

        rules_layout.addWidget(table)
        rules_layout.addSpacing(6)
        note = QLabel("ⓘ  카테고리별 전체/활성/비활성 규칙 현황을 실시간으로 반영합니다.")
        note.setObjectName("adminNote")
        rules_layout.addWidget(note)
        rules_card.setFixedHeight(365)
        main_layout.addWidget(rules_card)
        main_layout.addSpacing(8)

        settings_card = QFrame()
        settings_card.setObjectName("adminSectionCard")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(16, 8, 16, 8)
        settings_layout.setSpacing(0)

        settings_title = QLabel("2. 환경 설정")
        settings_title.setObjectName("adminSectionTitle")
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(4)

        settings_body = QFrame()
        settings_body.setObjectName("adminSettingsBody")
        body_layout = QVBoxLayout(settings_body)
        body_layout.setContentsMargins(12, 4, 12, 0)
        body_layout.setSpacing(0)

        self.ai_model_combo = QComboBox()
        self.ai_model_combo.setObjectName("adminThemeCombo")
        self.ai_model_combo.setFixedSize(210, 32)
        self.ai_model_combo.addItem("Qwen3-4B (기본)", "qwen3-4b-q4_k_m")
        self.ai_model_combo.setToolTip("AI Auditor에서 검증된 로컬 AI 모델을 선택합니다.")
        body_layout.addLayout(self.setting_row("로컬 AI 모델", self.ai_model_combo, 36))

        save_logs = self.create_toggle(True)
        body_layout.addLayout(self.setting_row("로그 저장", save_logs, 36))

        settings_layout.addWidget(settings_body)
        settings_card.setFixedHeight(130)
        main_layout.addWidget(settings_card)
        main_layout.addSpacing(8)

        data_card = QFrame()
        data_card.setObjectName("adminSectionCard")
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(16, 8, 16, 10)
        data_layout.setSpacing(0)

        data_title = QLabel("3. 데이터 관리")
        data_title.setObjectName("adminSectionTitle")
        data_layout.addWidget(data_title)
        data_layout.addSpacing(4)

        try:
            data_summary = get_data_management_summary()
        except Exception:
            data_summary = {"projects": 0, "inspections": 0, "issues": 0}

        self.data_summary_label = QLabel(
            "현재 데이터  ·  "
            f"프로젝트 {data_summary['projects']}개  /  "
            f"검사 이력 {data_summary['inspections']}건  /  "
            f"이슈 {data_summary['issues']}건"
        )
        self.data_summary_label.setObjectName("adminDataSummary")
        data_layout.addWidget(self.data_summary_label)
        data_layout.addSpacing(4)

        data_body = QFrame()
        data_body.setObjectName("adminDataBody")
        data_body_layout = QVBoxLayout(data_body)
        data_body_layout.setContentsMargins(12, 3, 12, 3)
        data_body_layout.setSpacing(0)

        self.clear_history_button = QPushButton("정리")
        self.clear_history_button.setObjectName("adminDangerButton")
        self.clear_history_button.setFixedSize(74, 30)
        self.clear_history_button.setCursor(Qt.PointingHandCursor)
        data_body_layout.addLayout(
            self.data_management_row(
                "전체 검사 이력 정리",
                "모든 검사 이력과 이슈를 삭제하며 프로젝트 정보는 유지합니다.",
                self.clear_history_button,
            )
        )

        divider = QFrame()
        divider.setObjectName("adminDataDivider")
        divider.setFixedHeight(1)
        data_body_layout.addWidget(divider)

        self.manage_projects_button = QPushButton("관리")
        self.manage_projects_button.setObjectName("adminManageButton")
        self.manage_projects_button.setFixedSize(74, 30)
        self.manage_projects_button.setCursor(Qt.PointingHandCursor)
        data_body_layout.addLayout(
            self.data_management_row(
                "프로젝트 관리",
                "프로젝트별 검사 이력과 이슈 범위를 확인한 뒤 프로젝트를 삭제합니다.",
                self.manage_projects_button,
            )
        )

        data_layout.addWidget(data_body)
        data_card.setFixedHeight(164)
        main_layout.addWidget(data_card)
        main_layout.addStretch()

        self.apply_theme(True)

    def create_toggle(self, checked):
        toggle = QPushButton("ON" if checked else "OFF")
        toggle.setObjectName("adminToggle")
        toggle.setCheckable(True)
        toggle.setChecked(checked)
        toggle.setCursor(Qt.PointingHandCursor)
        toggle.setFixedSize(82, 28)
        toggle.toggled.connect(lambda state, button=toggle: button.setText("ON" if state else "OFF"))
        return toggle

    def setting_row(self, text, control, height):
        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 0, 0)
        label = QLabel(text)
        label.setObjectName("adminSettingLabel")
        label.setFixedHeight(height)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row.addWidget(label)
        row.addStretch()
        row.addWidget(control, 0, Qt.AlignVCenter)
        return row

    def data_management_row(self, title, description, button):
        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 4, 0)
        row.setSpacing(12)

        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 3, 0, 3)
        text_layout.setSpacing(1)

        title_label = QLabel(title)
        title_label.setObjectName("adminDataTitle")
        description_label = QLabel(description)
        description_label.setObjectName("adminDataDescription")
        description_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)
        row.addWidget(text_widget, 1)
        row.addWidget(button, 0, Qt.AlignVCenter)
        return row

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("""
                #adminAccentLabel { color:#46a3ff; font-size:13px; font-weight:800; }
                #adminSummaryFrame { background:#0b1219; border:1px solid #40576b; border-radius:9px; }
                #adminSummaryValue, #adminSummaryActive, #adminSummaryInactive { color:#ffffff; font-size:24px; font-weight:850; }
                #adminSummaryActive { color:#22c55e; }
                #adminSummaryInactive { color:#ff5a36; }
                #adminSummaryText { color:#f8fafc; font-size:13px; font-weight:750; }
                #adminSectionCard { background:#101b25; border:1px solid #2f4659; border-radius:8px; }
                #adminSectionTitle { color:#ffffff; font-size:16px; font-weight:850; }
                #adminRulesTable, #adminSettingsBody, #adminDataBody { background:#0d1b27; border:1px solid #21384a; border-radius:7px; }
                #adminRulesHeader { background:#162b3c; border-bottom:1px solid #476174; }
                #adminHeaderText { color:#ffffff; font-size:12px; font-weight:850; }
                #adminCategoryRow { background:#0d1b27; border-bottom:1px solid #30485a; }
                #adminCategoryRow:hover { background:#132536; }
                #adminRulesBottomSeparator { background:#30485a; border:none; }
                #adminCategoryName { color:#ffffff; font-size:13px; font-weight:850; }
                #adminCount { color:#ffffff; font-size:15px; font-weight:850; }
                #adminActiveCount { color:#28d768; font-size:15px; font-weight:900; }
                #adminInactiveCount { color:#ff613e; font-size:15px; font-weight:900; }
                #adminViewButton, #adminBrowseButton, #adminManageButton { background:#1b3347; color:#ffffff; border:1px solid #46647b; border-radius:6px; font-size:12px; font-weight:850; }
                #adminViewButton:hover, #adminBrowseButton:hover, #adminManageButton:hover { background:#27465e; }
                #adminDangerButton { background:#4a2222; color:#ffdddd; border:1px solid #8f4141; border-radius:6px; font-size:12px; font-weight:850; }
                #adminDangerButton:hover { background:#672929; border-color:#b55454; }
                #adminDataSummary { color:#d7e1eb; font-size:11px; font-weight:750; }
                #adminDataTitle { color:#ffffff; font-size:13px; font-weight:850; }
                #adminDataDescription { color:#bac8d4; font-size:11px; font-weight:650; }
                #adminDataDivider { background:#30485a; border:none; }
                #adminNote { color:#d7e1eb; font-size:11px; font-weight:700; }
                #adminSettingLabel { color:#ffffff; font-size:13px; font-weight:850; }
                #adminPath { background:#102331; color:#ffffff; border:1px solid #476174; border-radius:6px; padding:0 9px; font-size:12px; font-weight:650; }
                QComboBox#adminThemeCombo { background:#102331; color:#ffffff; border:1px solid #557187; border-radius:7px; padding:0 10px; font-size:12px; font-weight:700; }
                QComboBox#adminThemeCombo::drop-down { subcontrol-origin:padding; subcontrol-position:top right; width:30px; border-left:1px solid #405a6e; border-top-right-radius:7px; border-bottom-right-radius:7px; background:#132433; }
                QComboBox#adminThemeCombo::down-arrow { width:9px; height:9px; }
                QComboBox#adminThemeCombo::drop-down:hover { background:#dfeaf2; }
                QPushButton#adminToggle { background:#40566a; color:#edf2f7; border:none; border-radius:14px; font-size:11px; font-weight:900; padding:0; }
                QPushButton#adminToggle:checked { background:#20c967; color:#ffffff; }
            """)
        else:
            self.setStyleSheet("""
                #adminAccentLabel { color:#1d70d6; font-size:13px; font-weight:800; }
                #adminSummaryFrame { background:#ffffff; border:1px solid #9fb0c1; border-radius:9px; }
                #adminSummaryValue { color:#152333; font-size:24px; font-weight:850; }
                #adminSummaryActive { color:#149447; font-size:24px; font-weight:850; }
                #adminSummaryInactive { color:#e2492d; font-size:24px; font-weight:850; }
                #adminSummaryText { color:#26384a; font-size:13px; font-weight:750; }
                #adminSectionCard { background:#ffffff; border:1px solid #c2ced9; border-radius:8px; }
                #adminSectionTitle { color:#142435; font-size:16px; font-weight:850; }
                #adminRulesTable, #adminSettingsBody, #adminDataBody { background:#f8fafc; border:1px solid #b6c4d1; border-radius:7px; }
                #adminRulesHeader { background:#e7eef5; border-bottom:1px solid #aebdcb; }
                #adminHeaderText { color:#243648; font-size:12px; font-weight:850; }
                #adminCategoryRow { background:#ffffff; border-bottom:1px solid #d2dce5; }
                #adminCategoryRow:hover { background:#f1f6fa; }
                #adminRulesBottomSeparator { background:#b6c4d1; border:none; }
                #adminCategoryName { color:#142435; font-size:13px; font-weight:850; }
                #adminCount { color:#142435; font-size:15px; font-weight:850; }
                #adminActiveCount { color:#149447; font-size:15px; font-weight:900; }
                #adminInactiveCount { color:#e2492d; font-size:15px; font-weight:900; }
                #adminViewButton, #adminBrowseButton, #adminManageButton { background:#edf3f8; color:#17324a; border:1px solid #a9bac8; border-radius:6px; font-size:12px; font-weight:850; }
                #adminViewButton:hover, #adminBrowseButton:hover, #adminManageButton:hover { background:#e0eaf2; }
                #adminDangerButton { background:#fff1f0; color:#b42318; border:1px solid #e3a19a; border-radius:6px; font-size:12px; font-weight:850; }
                #adminDangerButton:hover { background:#ffe4e1; border-color:#cf7d74; }
                #adminDataSummary { color:#4a5e72; font-size:11px; font-weight:750; }
                #adminDataTitle { color:#142435; font-size:13px; font-weight:850; }
                #adminDataDescription { color:#607386; font-size:11px; font-weight:650; }
                #adminDataDivider { background:#d2dce5; border:none; }
                #adminNote { color:#4a5e72; font-size:11px; font-weight:700; }
                #adminSettingLabel { color:#142435; font-size:13px; font-weight:850; }
                #adminPath { background:#ffffff; color:#172a3c; border:1px solid #aab9c7; border-radius:6px; padding:0 9px; font-size:12px; font-weight:650; }
                QComboBox#adminThemeCombo { background:#ffffff; color:#172a3c; border:1px solid #97adbd; border-radius:7px; padding:0 10px; font-size:12px; font-weight:700; }
                QComboBox#adminThemeCombo::drop-down { subcontrol-origin:padding; subcontrol-position:top right; width:30px; border-left:1px solid #b3c3cf; border-top-right-radius:7px; border-bottom-right-radius:7px; background:#edf3f7; }
                QComboBox#adminThemeCombo::down-arrow { width:9px; height:9px; }
                QPushButton#adminToggle { background:#aab6c3; color:#ffffff; border:none; border-radius:11px; font-size:9px; font-weight:850; padding:0; }
                QPushButton#adminToggle:checked { background:#20b85f; color:#ffffff; }
            """)

    def open_rules(self, name, total, active, inactive, icon_file):
        counts = self.category_counts.get(name, {})
        current_active = int(counts["adminActiveCount"].text()) if counts else active
        current_inactive = int(counts["adminInactiveCount"].text()) if counts else inactive
        dialog = AdministrationRulesDialog(
            name, total, current_active, current_inactive, self, icon_file,
            self.category_rule_states.get(name),
        )
        dialog.exec()
        self.category_rule_states[name] = dict(dialog.rule_states)
        if counts:
            counts["adminActiveCount"].setText(str(dialog.active_count))
            counts["adminInactiveCount"].setText(str(dialog.inactive_count))
        total_active = sum(int(values["adminActiveCount"].text()) for values in self.category_counts.values())
        total_inactive = sum(int(values["adminInactiveCount"].text()) for values in self.category_counts.values())
        self.summary_value_labels["adminSummaryActive"].setText(str(total_active))
        self.summary_value_labels["adminSummaryInactive"].setText(str(total_inactive))
