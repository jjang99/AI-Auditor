import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon
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
        main_layout.setContentsMargins(20, 18, 20, 16)
        main_layout.setSpacing(0)
        page_layout.addWidget(content, 1)

        self.icon_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "icons"
        )

        title = QLabel("Reports")
        title.setObjectName("pageTitle")
        description = QLabel("프로젝트별 AI 검사 결과를 조회하고 상세 결과와 보고서를 관리합니다.")
        description.setObjectName("pageDescription")
        main_layout.addWidget(title)
        main_layout.addSpacing(4)
        main_layout.addWidget(description)
        main_layout.addSpacing(15)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)
        summary_data = [
            ("inspection.svg", "전체 검사", "12", "건", "reportMetricBlue"),
            ("detail_score.svg", "평균 점수", "84", "점", "reportMetricGreen"),
            ("detail_issues.svg", "발견 이슈", "96", "건", "reportMetricOrange"),
            ("detail_resolved.svg", "조치 완료", "71", "건", "reportMetricPurple"),
        ]
        for icon_file, label_text, value_text, suffix, value_object in summary_data:
            card = QFrame()
            card.setObjectName("reportSummaryCard")
            card.setFixedHeight(102)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 11, 15, 11)
            card_layout.setSpacing(5)

            label_row = QHBoxLayout()
            label_row.setSpacing(7)
            icon = QLabel()
            icon.setObjectName("reportMetricIcon")
            icon.setPixmap(QIcon(os.path.join(self.icon_dir, icon_file)).pixmap(QSize(22, 22)))
            icon.setFixedSize(24, 24)
            icon.setAlignment(Qt.AlignCenter)
            label = QLabel(label_text)
            label.setObjectName("reportMetricLabel")
            label_row.addWidget(icon)
            label_row.addWidget(label)
            label_row.addStretch()

            value_row = QHBoxLayout()
            value_row.setSpacing(5)
            value = QLabel(value_text)
            value.setObjectName(value_object)
            unit = QLabel(suffix)
            unit.setObjectName("reportMetricUnit")
            value_row.addWidget(value)
            value_row.addWidget(unit, 0, Qt.AlignBottom)
            value_row.addStretch()

            card_layout.addLayout(label_row)
            card_layout.addLayout(value_row)
            summary_layout.addWidget(card, 1)

        main_layout.addLayout(summary_layout)
        main_layout.addSpacing(12)

        filter_frame = QFrame()
        filter_frame.setObjectName("reportFilterCard")
        filter_frame.setFixedHeight(60)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(14, 10, 14, 10)
        filter_layout.setSpacing(9)
        filter_title = QLabel("조회 조건")
        filter_title.setObjectName("reportFilterTitle")

        self.project_combo = QComboBox()
        self.project_combo.setObjectName("reportCombo")
        self.project_combo.addItems([
            "전체 프로젝트",
            "국방 건축행정시스템 재구축",
            "차세대 업무시스템",
            "통합관리시스템",
        ])
        self.project_combo.setFixedWidth(196)

        self.period_combo = QComboBox()
        self.period_combo.setObjectName("reportCombo")
        self.period_combo.addItems(["전체 기간", "최근 1개월", "최근 3개월", "최근 6개월"])
        self.period_combo.setFixedWidth(122)

        self.status_combo = QComboBox()
        self.status_combo.setObjectName("reportCombo")
        self.status_combo.addItems(["전체 상태", "검사 완료", "검사 실패"])
        self.status_combo.setFixedWidth(108)

        search_button = QPushButton("조회")
        search_button.setObjectName("reportSearchButton")
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setFixedSize(72, 38)

        filter_layout.addWidget(filter_title)
        filter_layout.addSpacing(2)
        filter_layout.addWidget(self.project_combo)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(search_button)
        main_layout.addWidget(filter_frame)
        main_layout.addSpacing(13)

        report_card = QFrame()
        report_card.setObjectName("reportListCard")
        report_layout = QVBoxLayout(report_card)
        report_layout.setContentsMargins(14, 14, 14, 14)
        report_layout.setSpacing(0)

        list_title = QLabel("검사 보고서")
        list_title.setObjectName("reportSectionTitle")
        list_subtitle = QLabel("검사 결과를 선택하여 상세 내용을 확인하거나 보고서로 내보낼 수 있습니다.")
        list_subtitle.setObjectName("reportSectionDescription")
        report_layout.addWidget(list_title)
        report_layout.addSpacing(4)
        report_layout.addWidget(list_subtitle)
        report_layout.addSpacing(12)

        self.report_table = QTableWidget()
        self.report_table.setObjectName("reportTable")
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "프로젝트", "검사일시", "Score", "Grade", "Issues", "상태"
        ])
        self.sample_reports = [
            ("국방 건축행정시스템 재구축", "2026.07.25 14:32", "82", "B", "14", "검사 완료"),
            ("차세대 업무시스템", "2026.07.18 10:15", "91", "A", "6", "검사 완료"),
            ("데이터 분석 플랫폼", "2026.07.10 16:05", "73", "C", "21", "검사 완료"),
            ("모바일 서비스 플랫폼", "2026.06.28 09:40", "88", "B", "9", "검사 완료"),
            ("통합관리시스템", "-", "-", "-", "-", "검사 실패"),
        ]
        self.report_table.setRowCount(len(self.sample_reports))

        for row, report in enumerate(self.sample_reports):
            for column, value in enumerate(report):
                item = QTableWidgetItem(value)
                item.setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter if column == 0 else Qt.AlignCenter
                )
                self.report_table.setItem(row, column, item)

        self.report_table.verticalHeader().setVisible(False)
        self.report_table.verticalHeader().setDefaultSectionSize(54)
        self.report_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.report_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.report_table.setShowGrid(False)
        self.report_table.setAlternatingRowColors(False)
        self.report_table.setFixedHeight(336)

        header = self.report_table.horizontalHeader()
        header.setFixedHeight(42)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for column in range(1, 6):
            header.setSectionResizeMode(column, QHeaderView.Fixed)
        self.report_table.setColumnWidth(1, 128)
        self.report_table.setColumnWidth(2, 58)
        self.report_table.setColumnWidth(3, 58)
        self.report_table.setColumnWidth(4, 64)
        self.report_table.setColumnWidth(5, 90)

        self.report_table.selectRow(0)
        self.report_table.itemSelectionChanged.connect(self.update_selected_report)
        report_layout.addWidget(self.report_table)
        main_layout.addWidget(report_card)
        main_layout.addSpacing(12)

        action_frame = QFrame()
        action_frame.setObjectName("reportActionCard")
        action_frame.setFixedHeight(100)
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(15, 11, 14, 11)

        selected_area = QVBoxLayout()
        selected_area.setSpacing(3)
        selected_caption = QLabel("선택한 검사 결과")
        selected_caption.setObjectName("reportSelectedCaption")
        self.selected_project = QLabel(self.sample_reports[0][0])
        self.selected_project.setObjectName("reportSelectedProject")
        self.selected_meta = QLabel(
            "2026.07.25 14:32   ·   Score 82   ·   Grade B   ·   Issues 14"
        )
        self.selected_meta.setObjectName("reportSelectedMeta")
        selected_area.addWidget(selected_caption)
        selected_area.addWidget(self.selected_project)
        selected_area.addWidget(self.selected_meta)

        detail_button = QPushButton("상세보기")
        detail_button.setObjectName("reportSecondaryButton")
        detail_button.setCursor(Qt.PointingHandCursor)
        detail_button.setFixedSize(92, 40)

        export_button = QPushButton("보고서 내보내기")
        export_button.setObjectName("reportPrimaryButton")
        export_button.setCursor(Qt.PointingHandCursor)
        export_button.setFixedSize(126, 40)

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
        if not selected:
            return
        row = selected[0].row()
        report = self.sample_reports[row]
        self.selected_project.setText(report[0])
        if report[2] == "-":
            self.selected_meta.setText("검사 실패   ·   결과 정보 없음")
        else:
            self.selected_meta.setText(
                f"{report[1]}   ·   Score {report[2]}   ·   Grade {report[3]}   ·   Issues {report[4]}"
            )

    def _apply_item_colors(self, is_dark):
        score_colors = {
            "A": "#22c55e",
            "B": "#55a7ff",
            "C": "#f5b942",
            "D": "#f97316",
            "E": "#ef4444",
        }
        normal = QColor("#f3f7fb" if is_dark else "#22384a")
        muted = QColor("#91a3b4" if is_dark else "#738596")

        for row, report in enumerate(self.sample_reports):
            for column in range(6):
                item = self.report_table.item(row, column)
                if item:
                    item.setForeground(normal if report[5] != "검사 실패" else muted)

            if report[2] != "-":
                self.report_table.item(row, 2).setForeground(
                    QColor("#6bb5ff" if is_dark else "#176bc6")
                )
                self.report_table.item(row, 3).setForeground(
                    QColor(score_colors.get(report[3], "#ffffff"))
                )
                issues = int(report[4])
                issue_color = "#ff9b45" if issues >= 10 else "#2bd46f"
                self.report_table.item(row, 4).setForeground(QColor(issue_color))
                self.report_table.item(row, 5).setForeground(
                    QColor("#2bd46f" if is_dark else "#15934a")
                )
            else:
                self.report_table.item(row, 5).setForeground(
                    QColor("#ff6464" if is_dark else "#c93636")
                )

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("""
                #reportSummaryCard, #reportFilterCard, #reportListCard, #reportActionCard {
                    background:#101d29;
                    border:1px solid #395266;
                    border-radius:9px;
                }
                #reportSummaryCard:hover { background:#132433; border-color:#4c6b82; }
                #reportMetricIcon { background:transparent; border:none; }
                #reportMetricLabel { color:#eef4f9; font-size:12px; font-weight:850; }
                #reportMetricBlue, #reportMetricGreen, #reportMetricOrange, #reportMetricPurple {
                    color:#55a7ff; font-size:27px; font-weight:900;
                }
                #reportMetricGreen { color:#2bd46f; }
                #reportMetricOrange { color:#ff9b45; }
                #reportMetricPurple { color:#b985ff; }
                #reportMetricUnit { color:#e4edf5; font-size:12px; font-weight:850; padding-bottom:4px; }
                #reportFilterTitle { color:#ffffff; font-size:13px; font-weight:900; }
                QComboBox#reportCombo {
                    background:#0d1822; color:#f6f9fc; border:1px solid #506a7f;
                    border-radius:6px; padding:0 9px; min-height:36px;
                    font-size:12px; font-weight:750;
                }
                #reportSearchButton, #reportPrimaryButton {
                    background:#1672ef; color:#ffffff; border:none; border-radius:7px;
                    font-size:12px; font-weight:900;
                }
                #reportSearchButton:hover, #reportPrimaryButton:hover { background:#2c82f3; }
                #reportSectionTitle { color:#ffffff; font-size:18px; font-weight:900; }
                #reportSectionDescription { color:#bdcad6; font-size:11px; font-weight:700; }
                QTableWidget#reportTable {
                    background:#0b1620; color:#f3f7fb; border:1px solid #405a6e;
                    border-radius:6px; selection-background-color:#173149;
                    selection-color:#ffffff; font-size:12px; font-weight:750; outline:0;
                }
                QTableWidget#reportTable::item {
                    border-bottom:1px solid #334a5c; padding:6px;
                }
                QTableWidget#reportTable::item:selected { background:#173149; }
                QHeaderView::section {
                    background:#1c3549; color:#ffffff; border:none;
                    border-bottom:1px solid #61798d; padding:8px;
                    font-size:12px; font-weight:900;
                }
                #reportSelectedCaption { color:#a7b8c7; font-size:11px; font-weight:800; }
                #reportSelectedProject { color:#ffffff; font-size:15px; font-weight:900; }
                #reportSelectedMeta { color:#c4d0db; font-size:11px; font-weight:750; }
                #reportSecondaryButton {
                    background:#1a2d3d; color:#f2f6fa; border:1px solid #506a7f;
                    border-radius:7px; font-size:12px; font-weight:850;
                }
                #reportSecondaryButton:hover { background:#263e51; }
            """)
        else:
            self.setStyleSheet("""
                #reportSummaryCard, #reportFilterCard, #reportListCard, #reportActionCard {
                    background:#ffffff;
                    border:1px solid #b5c5d2;
                    border-radius:9px;
                }
                #reportSummaryCard:hover { background:#f6f9fc; border-color:#91a8ba; }
                #reportMetricIcon { background:transparent; border:none; }
                #reportMetricLabel { color:#334b5f; font-size:12px; font-weight:850; }
                #reportMetricBlue, #reportMetricGreen, #reportMetricOrange, #reportMetricPurple {
                    color:#176bc6; font-size:27px; font-weight:900;
                }
                #reportMetricGreen { color:#15934a; }
                #reportMetricOrange { color:#d96a18; }
                #reportMetricPurple { color:#7b4ec2; }
                #reportMetricUnit { color:#465f72; font-size:12px; font-weight:850; padding-bottom:4px; }
                #reportFilterTitle { color:#1c3042; font-size:13px; font-weight:900; }
                QComboBox#reportCombo {
                    background:#ffffff; color:#22384a; border:1px solid #9fb2c3;
                    border-radius:6px; padding:0 9px; min-height:36px;
                    font-size:12px; font-weight:750;
                }
                #reportSearchButton, #reportPrimaryButton {
                    background:#1672ef; color:#ffffff; border:none; border-radius:7px;
                    font-size:12px; font-weight:900;
                }
                #reportSearchButton:hover, #reportPrimaryButton:hover { background:#0f63d6; }
                #reportSectionTitle { color:#16293a; font-size:18px; font-weight:900; }
                #reportSectionDescription { color:#536b7e; font-size:11px; font-weight:700; }
                QTableWidget#reportTable {
                    background:#ffffff; color:#22384a; border:1px solid #aebfce;
                    border-radius:6px; selection-background-color:#e7f1fa;
                    selection-color:#142b40; font-size:12px; font-weight:750; outline:0;
                }
                QTableWidget#reportTable::item {
                    border-bottom:1px solid #ccd8e2; padding:6px;
                }
                QTableWidget#reportTable::item:selected { background:#e7f1fa; }
                QHeaderView::section {
                    background:#dfeaf2; color:#20374a; border:none;
                    border-bottom:1px solid #9db1c1; padding:8px;
                    font-size:12px; font-weight:900;
                }
                #reportSelectedCaption { color:#5d7487; font-size:11px; font-weight:800; }
                #reportSelectedProject { color:#172b3c; font-size:15px; font-weight:900; }
                #reportSelectedMeta { color:#425a6d; font-size:11px; font-weight:750; }
                #reportSecondaryButton {
                    background:#eef3f7; color:#244057; border:1px solid #9fb2c3;
                    border-radius:7px; font-size:12px; font-weight:850;
                }
                #reportSecondaryButton:hover { background:#e2ebf2; }
            """)

        self._apply_item_colors(is_dark)
