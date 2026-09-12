from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from ui.sidebar import Sidebar


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.sidebar = Sidebar("Reports")
        page_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("projectsContent")
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 18)
        main_layout.setSpacing(0)
        page_layout.addWidget(content, 1)

        title = QLabel("Reports")
        title.setObjectName("pageTitle")
        description = QLabel("프로젝트별 AI 검사 결과를 조회하고 상세 결과와 보고서를 관리합니다.")
        description.setObjectName("pageDescription")
        main_layout.addWidget(title)
        main_layout.addSpacing(4)
        main_layout.addWidget(description)
        main_layout.addSpacing(16)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)
        summary_data = [
            ("전체 검사", "12", "건", "reportMetricBlue"),
            ("평균 점수", "84", "점", "reportMetricGreen"),
            ("발견 이슈", "96", "건", "reportMetricOrange"),
            ("조치 완료", "71", "건", "reportMetricPurple"),
        ]
        for label_text, value_text, suffix, object_name in summary_data:
            card = QFrame()
            card.setObjectName("reportSummaryCard")
            card.setFixedHeight(94)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 11)
            card_layout.setSpacing(3)
            label = QLabel(label_text)
            label.setObjectName("reportMetricLabel")
            value_row = QHBoxLayout()
            value_row.setSpacing(4)
            value = QLabel(value_text)
            value.setObjectName(object_name)
            unit = QLabel(suffix)
            unit.setObjectName("reportMetricUnit")
            value_row.addWidget(value)
            value_row.addWidget(unit, 0, Qt.AlignBottom)
            value_row.addStretch()
            card_layout.addWidget(label)
            card_layout.addLayout(value_row)
            summary_layout.addWidget(card, 1)
        main_layout.addLayout(summary_layout)
        main_layout.addSpacing(12)

        filter_frame = QFrame()
        filter_frame.setObjectName("reportFilterCard")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(14, 10, 14, 10)
        filter_layout.setSpacing(9)
        filter_title = QLabel("조회 조건")
        filter_title.setObjectName("reportFilterTitle")
        self.project_combo = QComboBox()
        self.project_combo.setObjectName("reportCombo")
        self.project_combo.addItems(["전체 프로젝트", "국방 건축행정시스템 재구축", "차세대 업무시스템", "통합관리시스템"])
        self.project_combo.setFixedWidth(210)
        self.period_combo = QComboBox()
        self.period_combo.setObjectName("reportCombo")
        self.period_combo.addItems(["전체 기간", "최근 1개월", "최근 3개월", "최근 6개월"])
        self.period_combo.setFixedWidth(128)
        self.status_combo = QComboBox()
        self.status_combo.setObjectName("reportCombo")
        self.status_combo.addItems(["전체 상태", "검사 완료", "검사 실패"])
        self.status_combo.setFixedWidth(112)
        search_button = QPushButton("조회")
        search_button.setObjectName("reportSearchButton")
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setFixedSize(72, 34)
        filter_layout.addWidget(filter_title)
        filter_layout.addSpacing(4)
        filter_layout.addWidget(self.project_combo)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(search_button)
        main_layout.addWidget(filter_frame)
        main_layout.addSpacing(14)

        report_card = QFrame()
        report_card.setObjectName("reportListCard")
        report_layout = QVBoxLayout(report_card)
        report_layout.setContentsMargins(14, 13, 14, 13)
        report_layout.setSpacing(0)
        list_header = QHBoxLayout()
        list_title_area = QVBoxLayout()
        list_title_area.setSpacing(2)
        list_title = QLabel("검사 보고서")
        list_title.setObjectName("reportSectionTitle")
        list_subtitle = QLabel("검사 결과를 선택하여 상세 내용을 확인하거나 보고서로 내보낼 수 있습니다.")
        list_subtitle.setObjectName("reportSectionDescription")
        list_title_area.addWidget(list_title)
        list_title_area.addWidget(list_subtitle)
        list_header.addLayout(list_title_area)
        list_header.addStretch()
        report_layout.addLayout(list_header)
        report_layout.addSpacing(11)

        self.report_table = QTableWidget()
        self.report_table.setObjectName("reportTable")
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels(["프로젝트", "검사일시", "Score", "Grade", "Issues", "상태"])
        sample_reports = [
            ("국방 건축행정시스템 재구축", "2026.07.25 14:32", "82", "B", "14", "검사 완료"),
            ("차세대 업무시스템", "2026.07.18 10:15", "91", "A", "6", "검사 완료"),
            ("데이터 분석 플랫폼", "2026.07.10 16:05", "73", "C", "21", "검사 완료"),
            ("모바일 서비스 플랫폼", "2026.06.28 09:40", "88", "B", "9", "검사 완료"),
            ("통합관리시스템", "-", "-", "-", "-", "검사 실패"),
        ]
        self.report_table.setRowCount(len(sample_reports))
        for row, report in enumerate(sample_reports):
            for column, value in enumerate(report):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter if column == 0 else Qt.AlignCenter)
                if column == 2:
                    item.setData(Qt.UserRole, "score")
                elif column == 3:
                    item.setData(Qt.UserRole, f"grade-{value}")
                elif column == 4:
                    item.setData(Qt.UserRole, "issues")
                elif column == 5:
                    item.setData(Qt.UserRole, "failed" if value == "검사 실패" else "complete")
                self.report_table.setItem(row, column, item)
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.verticalHeader().setDefaultSectionSize(46)
        self.report_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.report_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.report_table.setShowGrid(False)
        self.report_table.setAlternatingRowColors(False)
        self.report_table.setFixedHeight(278)
        header = self.report_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.report_table.setColumnWidth(1, 128)
        self.report_table.setColumnWidth(2, 58)
        self.report_table.setColumnWidth(3, 58)
        self.report_table.setColumnWidth(4, 62)
        self.report_table.setColumnWidth(5, 86)
        self.report_table.selectRow(0)
        self.report_table.itemSelectionChanged.connect(self.update_selected_report)
        report_layout.addWidget(self.report_table)
        main_layout.addWidget(report_card)
        main_layout.addSpacing(12)

        action_frame = QFrame()
        action_frame.setObjectName("reportActionCard")
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(14, 10, 14, 10)
        selected_area = QVBoxLayout()
        selected_area.setSpacing(2)
        selected_caption = QLabel("선택한 검사 결과")
        selected_caption.setObjectName("reportSelectedCaption")
        self.selected_project = QLabel(sample_reports[0][0])
        self.selected_project.setObjectName("reportSelectedProject")
        selected_area.addWidget(selected_caption)
        selected_area.addWidget(self.selected_project)
        detail_button = QPushButton("상세보기")
        detail_button.setObjectName("reportSecondaryButton")
        detail_button.setCursor(Qt.PointingHandCursor)
        detail_button.setFixedSize(92, 36)
        export_button = QPushButton("보고서 내보내기")
        export_button.setObjectName("reportPrimaryButton")
        export_button.setCursor(Qt.PointingHandCursor)
        export_button.setFixedSize(126, 36)
        action_layout.addLayout(selected_area)
        action_layout.addStretch()
        action_layout.addWidget(detail_button)
        action_layout.addSpacing(6)
        action_layout.addWidget(export_button)
        main_layout.addWidget(action_frame)
        main_layout.addStretch(1)

        self.apply_theme(True)

    def update_selected_report(self):
        selected = self.report_table.selectionModel().selectedRows()
        if selected:
            item = self.report_table.item(selected[0].row(), 0)
            if item:
                self.selected_project.setText(item.text())

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("""
                #reportSummaryCard, #reportFilterCard, #reportListCard, #reportActionCard { background:#101d29; border:1px solid #2e4558; border-radius:8px; }
                #reportMetricLabel { color:#b8c7d6; font-size:11px; font-weight:750; }
                #reportMetricBlue, #reportMetricGreen, #reportMetricOrange, #reportMetricPurple { color:#55a7ff; font-size:24px; font-weight:900; }
                #reportMetricGreen { color:#2bd46f; } #reportMetricOrange { color:#ff9b45; } #reportMetricPurple { color:#b985ff; }
                #reportMetricUnit { color:#dce6ef; font-size:11px; font-weight:750; padding-bottom:3px; }
                #reportFilterTitle { color:#ffffff; font-size:12px; font-weight:850; }
                QComboBox#reportCombo { background:#0d1822; color:#eef5fb; border:1px solid #40586b; border-radius:6px; padding:0 9px; min-height:32px; font-size:11px; font-weight:650; }
                #reportSearchButton, #reportPrimaryButton { background:#1672ef; color:#ffffff; border:none; border-radius:7px; font-size:12px; font-weight:850; }
                #reportSearchButton:hover, #reportPrimaryButton:hover { background:#2c82f3; }
                #reportSectionTitle { color:#ffffff; font-size:16px; font-weight:900; }
                #reportSectionDescription { color:#9fb0c0; font-size:10px; font-weight:650; }
                QTableWidget#reportTable { background:#0b1620; color:#eaf1f7; border:1px solid #30495d; border-radius:6px; selection-background-color:#183b57; selection-color:#ffffff; font-size:11px; font-weight:650; outline:0; }
                QTableWidget#reportTable::item { border-bottom:1px solid #263c4e; padding:5px; }
                QTableWidget#reportTable::item:selected { background:#183b57; color:#ffffff; }
                QHeaderView::section { background:#1a3144; color:#ffffff; border:none; border-bottom:1px solid #50677a; padding:7px; font-size:11px; font-weight:850; }
                #reportSelectedCaption { color:#8fa4b7; font-size:10px; font-weight:700; }
                #reportSelectedProject { color:#ffffff; font-size:13px; font-weight:850; }
                #reportSecondaryButton { background:#1a2d3d; color:#e8f0f7; border:1px solid #405a6f; border-radius:7px; font-size:11px; font-weight:800; }
                #reportSecondaryButton:hover { background:#263e51; }
            """)
        else:
            self.setStyleSheet("""
                #reportSummaryCard, #reportFilterCard, #reportListCard, #reportActionCard { background:#ffffff; border:1px solid #bdcbd7; border-radius:8px; }
                #reportMetricLabel { color:#52677a; font-size:11px; font-weight:750; }
                #reportMetricBlue, #reportMetricGreen, #reportMetricOrange, #reportMetricPurple { color:#176bc6; font-size:24px; font-weight:900; }
                #reportMetricGreen { color:#15934a; } #reportMetricOrange { color:#d96a18; } #reportMetricPurple { color:#7b4ec2; }
                #reportMetricUnit { color:#4a6073; font-size:11px; font-weight:750; padding-bottom:3px; }
                #reportFilterTitle { color:#1c3042; font-size:12px; font-weight:850; }
                QComboBox#reportCombo { background:#ffffff; color:#24384a; border:1px solid #a9b9c7; border-radius:6px; padding:0 9px; min-height:32px; font-size:11px; font-weight:650; }
                #reportSearchButton, #reportPrimaryButton { background:#1672ef; color:#ffffff; border:none; border-radius:7px; font-size:12px; font-weight:850; }
                #reportSearchButton:hover, #reportPrimaryButton:hover { background:#0f63d6; }
                #reportSectionTitle { color:#16293a; font-size:16px; font-weight:900; }
                #reportSectionDescription { color:#64788a; font-size:10px; font-weight:650; }
                QTableWidget#reportTable { background:#ffffff; color:#25394b; border:1px solid #b8c7d3; border-radius:6px; selection-background-color:#e5f1ff; selection-color:#142b40; font-size:11px; font-weight:650; outline:0; }
                QTableWidget#reportTable::item { border-bottom:1px solid #d8e1e8; padding:5px; }
                QTableWidget#reportTable::item:selected { background:#e5f1ff; color:#142b40; }
                QHeaderView::section { background:#e5edf4; color:#24394b; border:none; border-bottom:1px solid #a9bbc9; padding:7px; font-size:11px; font-weight:850; }
                #reportSelectedCaption { color:#667b8d; font-size:10px; font-weight:700; }
                #reportSelectedProject { color:#172b3c; font-size:13px; font-weight:850; }
                #reportSecondaryButton { background:#eef3f7; color:#244057; border:1px solid #aabac7; border-radius:7px; font-size:11px; font-weight:800; }
                #reportSecondaryButton:hover { background:#e2ebf2; }
            """)
