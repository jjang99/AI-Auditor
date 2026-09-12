from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.sidebar import Sidebar


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()

        # ==================================================
        # 전체 Layout
        # ==================================================
        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar("Reports")
        page_layout.addWidget(self.sidebar)

        # 오른쪽 Content
        content = QWidget()
        content.setObjectName("projectsContent")

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 16)
        main_layout.setSpacing(0)

        page_layout.addWidget(content, 1)

        # ==================================================
        # 1. Header
        # ==================================================
        title = QLabel("Reports")
        title.setObjectName("pageTitle")

        description = QLabel(
            "프로젝트별 AI 검사 결과와 보고서를 확인하고 "
            "내보낼 수 있습니다."
        )
        description.setObjectName("pageDescription")

        main_layout.addWidget(title)
        main_layout.addSpacing(3)
        main_layout.addWidget(description)
        main_layout.addSpacing(18)

        # ==================================================
        # 2. Filter
        # ==================================================
        filter_frame = QFrame()
        filter_frame.setObjectName("projectCard")

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(10)

        project_label = QLabel("프로젝트")
        project_label.setObjectName("projectResultTitle")

        self.project_combo = QComboBox()
        self.project_combo.addItems(
            [
                "전체 프로젝트",
                "국방 건축행정시스템 재구축",
                "차세대 업무시스템",
                "통합관리시스템",
            ]
        )
        self.project_combo.setFixedWidth(210)

        period_label = QLabel("기간")
        period_label.setObjectName("projectResultTitle")

        self.period_combo = QComboBox()
        self.period_combo.addItems(
            [
                "전체 기간",
                "최근 1개월",
                "최근 3개월",
                "최근 6개월",
            ]
        )
        self.period_combo.setFixedWidth(130)

        search_button = QPushButton("조회")
        search_button.setObjectName("newProjectButton")
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setFixedSize(78, 36)

        filter_layout.addWidget(project_label)
        filter_layout.addWidget(self.project_combo)
        filter_layout.addSpacing(6)
        filter_layout.addWidget(period_label)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(search_button)

        main_layout.addWidget(filter_frame)
        main_layout.addSpacing(14)

        # ==================================================
        # 3. Summary
        # ==================================================
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)

        summary_data = [
            ("전체 검사", "12건"),
            ("평균 Score", "84점"),
            ("발견 Issues", "96건"),
            ("조치 완료", "71건"),
        ]

        for label_text, value_text in summary_data:
            card = QFrame()
            card.setObjectName("projectCard")
            card.setFixedHeight(88)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            card_layout.setSpacing(5)

            label = QLabel(label_text)
            label.setObjectName("projectResultTitle")

            value = QLabel(value_text)
            value.setObjectName("projectName")

            card_layout.addWidget(label)
            card_layout.addWidget(value)
            card_layout.addStretch()

            summary_layout.addWidget(card)

        main_layout.addLayout(summary_layout)
        main_layout.addSpacing(16)

        # ==================================================
        # 4. Report List Title
        # ==================================================
        list_header = QHBoxLayout()

        list_title = QLabel("검사 보고서")
        list_title.setObjectName("projectName")

        export_all_button = QPushButton("Export")
        export_all_button.setCursor(Qt.PointingHandCursor)
        export_all_button.setFixedSize(88, 34)

        list_header.addWidget(list_title)
        list_header.addStretch()
        list_header.addWidget(export_all_button)

        main_layout.addLayout(list_header)
        main_layout.addSpacing(8)

        # ==================================================
        # 5. Report Table
        # ==================================================
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(6)

        self.report_table.setHorizontalHeaderLabels(
            [
                "프로젝트",
                "검사일시",
                "Score",
                "Grade",
                "Issues",
                "상태",
            ]
        )

        self.report_table.setRowCount(5)

        sample_reports = [
            (
                "국방 건축행정시스템 재구축",
                "2026.07.25 14:32",
                "82",
                "B",
                "14",
                "검사 완료",
            ),
            (
                "차세대 업무시스템",
                "2026.07.18 10:15",
                "91",
                "A",
                "6",
                "검사 완료",
            ),
            (
                "데이터 분석 플랫폼",
                "2026.07.10 16:05",
                "73",
                "C",
                "21",
                "검사 완료",
            ),
            (
                "모바일 서비스 플랫폼",
                "2026.06.28 09:40",
                "88",
                "B",
                "9",
                "검사 완료",
            ),
            (
                "통합관리시스템",
                "-",
                "-",
                "-",
                "-",
                "검사 실패",
            ),
        ]

        for row, report in enumerate(sample_reports):
            for column, value in enumerate(report):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)

                if column == 0:
                    item.setTextAlignment(
                        Qt.AlignLeft | Qt.AlignVCenter
                    )

                self.report_table.setItem(
                    row,
                    column,
                    item,
                )

        self.report_table.setColumnWidth(0, 220)
        self.report_table.setColumnWidth(1, 135)
        self.report_table.setColumnWidth(2, 65)
        self.report_table.setColumnWidth(3, 65)
        self.report_table.setColumnWidth(4, 70)
        self.report_table.setColumnWidth(5, 90)

        self.report_table.setFixedHeight(270)
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.report_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        main_layout.addWidget(self.report_table)
        main_layout.addSpacing(14)

        # ==================================================
        # 6. Bottom
        # ==================================================
        bottom_frame = QFrame()
        bottom_frame.setObjectName("projectCard")

        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(14, 12, 14, 12)

        info = QLabel(
            "검사 결과를 선택하면 상세 결과 및 보고서 "
            "내보내기 기능을 사용할 수 있습니다."
        )
        info.setObjectName("projectDescription")

        detail_button = QPushButton("상세보기")
        detail_button.setCursor(Qt.PointingHandCursor)
        detail_button.setFixedSize(90, 34)

        export_button = QPushButton("Export Report")
        export_button.setObjectName("newProjectButton")
        export_button.setCursor(Qt.PointingHandCursor)
        export_button.setFixedSize(118, 34)

        bottom_layout.addWidget(info)
        bottom_layout.addStretch()
        bottom_layout.addWidget(detail_button)
        bottom_layout.addSpacing(6)
        bottom_layout.addWidget(export_button)

        main_layout.addWidget(bottom_frame)
        main_layout.addStretch(1)