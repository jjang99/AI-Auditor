from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
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

        summary_label = QLabel("Inspection Rules Summary")
        summary_label.setObjectName("adminAccentLabel")
        main_layout.addWidget(summary_label)
        main_layout.addSpacing(7)

        summary_frame = QFrame()
        summary_frame.setObjectName("adminSummaryFrame")
        summary_frame.setFixedHeight(88)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(22, 10, 22, 10)
        summary_layout.setSpacing(0)
        for value, label, object_name in [
            ("100", "Total Rules", "adminSummaryValue"),
            ("92", "Active Rules", "adminSummaryActive"),
            ("8", "Inactive Rules", "adminSummaryInactive"),
        ]:
            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 3, 0, 3)
            cell_layout.setSpacing(2)
            value_label = QLabel(value)
            value_label.setObjectName(object_name)
            value_label.setAlignment(Qt.AlignCenter)
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

        section_title = QLabel("1. 검사 기준 관리 (Inspection Rules Management)")
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
        header.setFixedHeight(38)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 0, 12, 0)
        header_layout.setSpacing(8)
        for text, width in [("카테고리", 225), ("전체 규칙", 78), ("활성 규칙", 78), ("비활성 규칙", 78), ("관리", 58)]:
            label = QLabel(text)
            label.setObjectName("adminHeaderText")
            label.setFixedWidth(width)
            label.setAlignment(Qt.AlignCenter if text != "카테고리" else Qt.AlignLeft | Qt.AlignVCenter)
            header_layout.addWidget(label)
        table_layout.addWidget(header)

        categories = [
            ("요구사항 정합성", "Requirement Consistency", 24, 22, 2),
            ("설계 품질", "Design Quality", 18, 18, 0),
            ("보안 취약점", "Security Vulnerability", 32, 30, 2),
            ("코드 품질", "Code Quality", 16, 14, 2),
            ("AI 특화 검증", "AI-Specific Validation", 10, 8, 2),
        ]
        for index, (name, english, total, active, inactive) in enumerate(categories):
            row = QFrame()
            row.setObjectName("adminCategoryRow")
            row.setFixedHeight(66)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 0, 12, 0)
            row_layout.setSpacing(8)

            category = QWidget()
            category.setFixedWidth(225)
            category_layout = QVBoxLayout(category)
            category_layout.setContentsMargins(0, 8, 0, 7)
            category_layout.setSpacing(1)
            name_label = QLabel(name)
            name_label.setObjectName("adminCategoryName")
            english_label = QLabel(english)
            english_label.setObjectName("adminCategoryEnglish")
            category_layout.addWidget(name_label)
            category_layout.addWidget(english_label)
            row_layout.addWidget(category)

            for value, object_name in [(total, "adminCount"), (active, "adminActiveCount"), (inactive, "adminInactiveCount")]:
                count = QLabel(str(value))
                count.setObjectName(object_name)
                count.setFixedWidth(78)
                count.setAlignment(Qt.AlignCenter)
                row_layout.addWidget(count)

            view = QPushButton("보기")
            view.setObjectName("adminViewButton")
            view.setFixedSize(58, 34)
            view.setCursor(Qt.PointingHandCursor)
            view.clicked.connect(lambda checked=False, n=name, t=total, a=active, i=inactive: self.open_rules(n, t, a, i))
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
        settings_layout.setContentsMargins(16, 13, 16, 12)
        settings_layout.setSpacing(0)

        settings_title = QLabel("2. 환경 설정 (Environment Settings)")
        settings_title.setObjectName("adminSectionTitle")
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(10)

        settings_body = QFrame()
        settings_body.setObjectName("adminSettingsBody")
        body_layout = QVBoxLayout(settings_body)
        body_layout.setContentsMargins(12, 0, 12, 0)
        body_layout.setSpacing(0)

        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light"])
        theme_combo.setFixedWidth(240)
        body_layout.addLayout(self.setting_row("Theme", theme_combo, 44))

        path_controls = QWidget()
        path_layout = QHBoxLayout(path_controls)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(7)
        path = QLineEdit(r"C:\AI_Auditor\Results")
        path.setObjectName("adminPath")
        browse = QPushButton("찾아보기")
        browse.setObjectName("adminBrowseButton")
        browse.setFixedSize(74, 32)
        path_layout.addWidget(path, 1)
        path_layout.addWidget(browse)
        body_layout.addLayout(self.setting_row("결과 저장 경로 (Result Save Path)", path_controls, 44))

        save_logs = QCheckBox()
        save_logs.setChecked(True)
        save_logs.setObjectName("adminToggle")
        body_layout.addLayout(self.setting_row("로그 저장 (Save Logs)", save_logs, 44))

        auto_save = QCheckBox()
        auto_save.setChecked(True)
        auto_save.setObjectName("adminToggle")
        body_layout.addLayout(self.setting_row("검사 결과 자동 저장 (Auto Save Results)", auto_save, 44))

        settings_layout.addWidget(settings_body)
        main_layout.addWidget(settings_card)
        main_layout.addStretch(1)

        self.setStyleSheet("""
            #adminAccentLabel { color:#3b9cff; font-size:12px; font-weight:700; }
            #adminSummaryFrame { background:transparent; border:1px solid #40576b; border-radius:9px; }
            #adminSummaryValue, #adminSummaryActive, #adminSummaryInactive { color:#ffffff; font-size:23px; font-weight:800; }
            #adminSummaryActive { color:#22c55e; }
            #adminSummaryInactive { color:#ff5a36; }
            #adminSummaryText { color:#d5dee8; font-size:12px; }
            #adminSectionCard { background:#172636; border-radius:8px; }
            #adminSectionTitle { color:#ffffff; font-size:15px; font-weight:800; }
            #adminRulesTable, #adminSettingsBody { background:#0e1b27; border-radius:7px; }
            #adminRulesHeader { background:#132332; border-bottom:1px solid #2b4052; }
            #adminHeaderText { color:#cbd5e1; font-size:10px; font-weight:700; }
            #adminCategoryRow { background:#0e1b27; border-bottom:1px solid #263a4b; }
            #adminCategoryName { color:#ffffff; font-size:12px; font-weight:800; }
            #adminCategoryEnglish { color:#aebdcc; font-size:10px; }
            #adminCount { color:#ffffff; font-size:13px; font-weight:700; }
            #adminActiveCount { color:#22c55e; font-size:13px; font-weight:800; }
            #adminInactiveCount { color:#ff5a36; font-size:13px; font-weight:800; }
            #adminViewButton, #adminBrowseButton { background:#182b3d; color:#ffffff; border:1px solid #30485c; border-radius:6px; font-weight:700; }
            #adminViewButton:hover, #adminBrowseButton:hover { background:#22394d; }
            #adminNote { color:#b8c5d2; font-size:10px; }
            #adminSettingLabel { color:#e2e8f0; font-size:11px; }
            #adminPath, QComboBox { background:#10202e; color:#ffffff; border:1px solid #31485b; border-radius:6px; padding:0 9px; min-height:30px; }
            QCheckBox#adminToggle { spacing:0px; }
            QCheckBox#adminToggle::indicator { width:36px; height:20px; }
        """)

    def setting_row(self, text, control, height):
        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 0, 0)
        label = QLabel(text)
        label.setObjectName("adminSettingLabel")
        label.setFixedHeight(height)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row.addWidget(label)
        row.addStretch()
        row.addWidget(control)
        return row

    def open_rules(self, name, total, active, inactive):
        dialog = AdministrationRulesDialog(name, total, active, inactive, self)
        dialog.exec()
