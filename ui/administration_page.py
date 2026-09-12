import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
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
        header.setFixedHeight(40)
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

        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        categories = [
            ("요구사항 정합성", 24, 22, 2, "detail_grade.svg"),
            ("설계 품질", 18, 18, 0, "detail_score.svg"),
            ("보안 취약점", 32, 30, 2, "detail_issues.svg"),
            ("코드 품질", 16, 14, 2, "detail_resolved.svg"),
            ("AI 특화 검증", 10, 8, 2, "administration.svg"),
        ]
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

        settings_title = QLabel("2. 환경 설정")
        settings_title.setObjectName("adminSectionTitle")
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(10)

        settings_body = QFrame()
        settings_body.setObjectName("adminSettingsBody")
        body_layout = QVBoxLayout(settings_body)
        body_layout.setContentsMargins(12, 2, 12, 2)
        body_layout.setSpacing(0)

        theme_combo = QComboBox()
        theme_combo.addItems(["다크", "라이트"])
        theme_combo.setFixedSize(240, 34)
        body_layout.addLayout(self.setting_row("테마", theme_combo, 44))

        path_controls = QWidget()
        path_controls.setFixedWidth(240)
        path_layout = QHBoxLayout(path_controls)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(7)
        path = QLineEdit(r"C:\AI_Auditor\Results")
        path.setObjectName("adminPath")
        path.setFixedHeight(34)
        browse = QPushButton("찾아보기")
        browse.setObjectName("adminBrowseButton")
        browse.setFixedSize(74, 34)
        path_layout.addWidget(path, 1)
        path_layout.addWidget(browse)
        body_layout.addLayout(self.setting_row("결과 저장 경로", path_controls, 44))

        save_logs = self.create_toggle(True)
        body_layout.addLayout(self.setting_row("로그 저장", save_logs, 44))

        auto_save = self.create_toggle(True)
        body_layout.addLayout(self.setting_row("검사 결과 자동 저장", auto_save, 44))

        settings_layout.addWidget(settings_body)
        main_layout.addWidget(settings_card)
        main_layout.addStretch(1)

        self.setStyleSheet("""
            #adminAccentLabel { color:#46a3ff; font-size:13px; font-weight:800; }
            #adminSummaryFrame { background:transparent; border:1px solid #40576b; border-radius:9px; }
            #adminSummaryValue, #adminSummaryActive, #adminSummaryInactive { color:#ffffff; font-size:24px; font-weight:850; }
            #adminSummaryActive { color:#22c55e; }
            #adminSummaryInactive { color:#ff5a36; }
            #adminSummaryText { color:#f1f5f9; font-size:13px; font-weight:700; }
            #adminSectionCard { background:#172636; border-radius:8px; }
            #adminSectionTitle { color:#ffffff; font-size:16px; font-weight:850; }
            #adminRulesTable, #adminSettingsBody { background:#0e1b27; border-radius:7px; }
            #adminRulesHeader { background:#132332; border-bottom:1px solid #2b4052; }
            #adminHeaderText { color:#f1f5f9; font-size:12px; font-weight:800; }
            #adminCategoryRow { background:#0e1b27; border-bottom:1px solid #263a4b; }
            #adminCategoryName { color:#ffffff; font-size:13px; font-weight:800; }
            #adminCount { color:#ffffff; font-size:14px; font-weight:800; }
            #adminActiveCount { color:#22c55e; font-size:14px; font-weight:850; }
            #adminInactiveCount { color:#ff5a36; font-size:14px; font-weight:850; }
            #adminViewButton, #adminBrowseButton { background:#182b3d; color:#ffffff; border:1px solid #36536a; border-radius:6px; font-size:12px; font-weight:800; }
            #adminViewButton:hover, #adminBrowseButton:hover { background:#22394d; }
            #adminNote { color:#cbd5e1; font-size:11px; font-weight:650; }
            #adminSettingLabel { color:#f1f5f9; font-size:12px; font-weight:750; }
            #adminPath, QComboBox { background:#10202e; color:#ffffff; border:1px solid #3a5368; border-radius:6px; padding:0 9px; font-size:12px; }
            QPushButton#adminToggle { background:#31465a; color:#dbe4ed; border:none; border-radius:11px; font-size:9px; font-weight:850; padding:0; }
            QPushButton#adminToggle:checked { background:#22c55e; color:#ffffff; }
        """)

    def create_toggle(self, checked):
        toggle = QPushButton("ON" if checked else "OFF")
        toggle.setObjectName("adminToggle")
        toggle.setCheckable(True)
        toggle.setChecked(checked)
        toggle.setCursor(Qt.PointingHandCursor)
        toggle.setFixedSize(44, 22)
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

    def open_rules(self, name, total, active, inactive):
        dialog = AdministrationRulesDialog(name, total, active, inactive, self)
        dialog.exec()
