import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

from ui.sidebar import Sidebar
from ui.administration_rules_dialog import AdministrationRulesDialog


class AdministrationPage(QWidget):
    def __init__(self):
        super().__init__()

        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.sidebar = Sidebar("Administration")
        page_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("projectsContent")
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 18, 20, 14)
        main_layout.setSpacing(0)
        page_layout.addWidget(content, 1)

        title = QLabel("Administration")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)
        main_layout.addSpacing(14)

        summary_label = QLabel("검사 기준 요약")
        summary_label.setObjectName("adminAccentLabel")
        main_layout.addWidget(summary_label)
        main_layout.addSpacing(7)

        summary_frame = QFrame()
        summary_frame.setObjectName("adminSummaryFrame")
        summary_frame.setFixedHeight(88)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(22, 10, 22, 10)
        summary_layout.setSpacing(0)
        self.summary_value_labels = {}
        for value, label, object_name in [
            ("100", "전체 규칙", "adminSummaryValue"),
            ("92", "활성 규칙", "adminSummaryActive"),
            ("8", "비활성 규칙", "adminSummaryInactive"),
        ]:
            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 3, 0, 3)
            cell_layout.setSpacing(2)
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
        main_layout.addSpacing(16)

        rules_card = QFrame()
        rules_card.setObjectName("adminSectionCard")
        rules_layout = QVBoxLayout(rules_card)
        rules_layout.setContentsMargins(16, 14, 16, 12)
        rules_layout.setSpacing(0)

        section_title = QLabel("1. 검사 기준 관리")
        section_title.setObjectName("adminSectionTitle")
        rules_layout.addWidget(section_title)
        rules_layout.addSpacing(12)

        table = QFrame()
        table.setObjectName("adminRulesTable")
        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("adminRulesHeader")
        header.setFixedHeight(42)
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
        categories = [
            ("요구사항 정합성", 24, 22, 2, "detail_grade.svg"),
            ("설계 품질", 18, 18, 0, "detail_score.svg"),
            ("보안 취약점", 32, 30, 2, "detail_issues.svg"),
            ("코드 품질", 16, 14, 2, "detail_resolved.svg"),
            ("AI 특화 검증", 10, 8, 2, "administration.svg"),
        ]
        self.category_counts = {}
        self.category_rule_states = {}
        for name, total, active, inactive, icon_file in categories:
            row = QFrame()
            row.setObjectName("adminCategoryRow")
            row.setFixedHeight(66)
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
            view.setFixedSize(58, 34)
            view.setCursor(Qt.PointingHandCursor)
            view.clicked.connect(
                lambda checked=False, n=name, t=total, a=active, i=inactive, icon_name=icon_file:
                self.open_rules(n, t, a, i, icon_name)
            )
            row_layout.addWidget(view)
            table_layout.addWidget(row)

        rules_layout.addWidget(table)
        rules_layout.addSpacing(9)
        note = QLabel("ⓘ  카테고리별 전체/활성/비활성 규칙 현황을 실시간으로 반영합니다.")
        note.setObjectName("adminNote")
        rules_layout.addWidget(note)
        main_layout.addWidget(rules_card)
        main_layout.addSpacing(14)

        settings_card = QFrame()
        settings_card.setObjectName("adminSectionCard")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(16, 10, 16, 12)
        settings_layout.setSpacing(0)

        settings_title = QLabel("2. 환경 설정")
        settings_title.setObjectName("adminSectionTitle")
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(6)

        settings_body = QFrame()
        settings_body.setObjectName("adminSettingsBody")
        body_layout = QVBoxLayout(settings_body)
        body_layout.setContentsMargins(12, 8, 12, 0)
        body_layout.setSpacing(0)

        path_controls = QWidget()
        path_controls.setFixedWidth(400)
        path_layout = QHBoxLayout(path_controls)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(7)
        self.result_path = QLineEdit(r"C:\AI_Auditor\Results")
        self.result_path.setObjectName("adminPath")
        self.result_path.setFixedHeight(34)
        browse = QPushButton("찾아보기")
        browse.setObjectName("adminBrowseButton")
        browse.setFixedSize(82, 34)
        browse.setCursor(Qt.PointingHandCursor)
        browse.clicked.connect(self.browse_result_path)
        path_layout.addWidget(self.result_path, 1)
        path_layout.addWidget(browse)
        body_layout.addLayout(self.setting_row("결과 저장 경로", path_controls, 48))

        save_logs = self.create_toggle(True)
        body_layout.addLayout(self.setting_row("로그 저장", save_logs, 48))

        auto_save = self.create_toggle(True)
        body_layout.addLayout(self.setting_row("검사 결과 자동 저장", auto_save, 48))

        settings_layout.addWidget(settings_body)
        main_layout.addWidget(settings_card, 1)

        self.apply_theme(True)

    def browse_result_path(self):
        current_path = self.result_path.text().strip()
        start_path = current_path if current_path and os.path.isdir(current_path) else os.path.expanduser("~")
        selected_path = QFileDialog.getExistingDirectory(
            self,
            "결과 저장 경로 선택",
            start_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if selected_path:
            self.result_path.setText(os.path.normpath(selected_path))

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
                #adminRulesTable, #adminSettingsBody { background:#0d1b27; border:1px solid #21384a; border-radius:7px; }
                #adminRulesHeader { background:#162b3c; border-bottom:1px solid #476174; }
                #adminHeaderText { color:#ffffff; font-size:12px; font-weight:850; }
                #adminCategoryRow { background:#0d1b27; border-bottom:1px solid #30485a; }
                #adminCategoryRow:hover { background:#132536; }
                #adminRulesBottomSeparator { background:#30485a; border:none; }
                #adminCategoryName { color:#ffffff; font-size:13px; font-weight:850; }
                #adminCount { color:#ffffff; font-size:15px; font-weight:850; }
                #adminActiveCount { color:#28d768; font-size:15px; font-weight:900; }
                #adminInactiveCount { color:#ff613e; font-size:15px; font-weight:900; }
                #adminViewButton, #adminBrowseButton { background:#1b3347; color:#ffffff; border:1px solid #46647b; border-radius:6px; font-size:12px; font-weight:850; }
                #adminViewButton:hover, #adminBrowseButton:hover { background:#27465e; }
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
                #adminRulesTable, #adminSettingsBody { background:#f8fafc; border:1px solid #b6c4d1; border-radius:7px; }
                #adminRulesHeader { background:#e7eef5; border-bottom:1px solid #aebdcb; }
                #adminHeaderText { color:#243648; font-size:12px; font-weight:850; }
                #adminCategoryRow { background:#ffffff; border-bottom:1px solid #d2dce5; }
                #adminCategoryRow:hover { background:#f1f6fa; }
                #adminRulesBottomSeparator { background:#b6c4d1; border:none; }
                #adminCategoryName { color:#142435; font-size:13px; font-weight:850; }
                #adminCount { color:#142435; font-size:15px; font-weight:850; }
                #adminActiveCount { color:#149447; font-size:15px; font-weight:900; }
                #adminInactiveCount { color:#e2492d; font-size:15px; font-weight:900; }
                #adminViewButton, #adminBrowseButton { background:#edf3f8; color:#17324a; border:1px solid #a9bac8; border-radius:6px; font-size:12px; font-weight:850; }
                #adminViewButton:hover, #adminBrowseButton:hover { background:#e0eaf2; }
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
