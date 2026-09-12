from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.sidebar import Sidebar
from ui.reinspect_dialog import ReInspectDialog

class ProjectDetailPage(QWidget):
    def __init__(self):
        super().__init__()

        # =====================================================
        # 전체
        # =====================================================
        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.sidebar = Sidebar("Projects")
        page_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("projectDetailContent")

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(10)

        page_layout.addWidget(content, 1)

        # =====================================================
        # Breadcrumb
        # =====================================================
        breadcrumb = QLabel(
            "Projects   ›   국방 건축행정시스템 재구축"
        )
        breadcrumb.setObjectName("detailBreadcrumb")
        main_layout.addWidget(breadcrumb)

        # =====================================================
        # 프로젝트 요약 대형 카드
        # =====================================================
        summary_card = QFrame()
        summary_card.setObjectName("detailSummaryCard")
        summary_card.setFixedHeight(112)

        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(18, 13, 18, 13)
        summary_layout.setSpacing(18)

        project_area = QVBoxLayout()
        project_area.setSpacing(5)

        project_name = QLabel("국방 건축행정시스템 재구축")
        project_name.setObjectName("detailProjectName")

        last_label = QLabel("마지막 검사일")
        last_label.setObjectName("detailMuted")

        last_date = QLabel("▣   2026.07.25 14:32")
        last_date.setObjectName("detailDate")

        project_area.addWidget(project_name)
        project_area.addWidget(last_label)
        project_area.addWidget(last_date)

        summary_layout.addLayout(project_area, 1)

        score_area = QVBoxLayout()
        score_area.setSpacing(0)

        score_label = QLabel("Score")
        score_label.setObjectName("detailSummaryLabel")

        score_row = QHBoxLayout()
        score_row.setSpacing(3)

        score_value = QLabel("82")
        score_value.setObjectName("detailSummaryScore")

        score_max = QLabel("/100")
        score_max.setObjectName("detailMuted")

        score_row.addWidget(score_value)
        score_row.addWidget(score_max, 0, Qt.AlignBottom)
        score_row.addStretch()

        score_area.addWidget(score_label)
        score_area.addLayout(score_row)

        summary_layout.addLayout(score_area)

        divider = QFrame()
        divider.setObjectName("detailVerticalDivider")
        divider.setFixedWidth(1)
        divider.setFixedHeight(60)
        summary_layout.addWidget(divider)

        grade_area = QVBoxLayout()
        grade_area.setSpacing(0)

        grade_label = QLabel("Grade")
        grade_label.setObjectName("detailSummaryLabel")

        grade_value = QLabel("B")
        grade_value.setObjectName("detailSummaryGrade")

        grade_area.addWidget(grade_label)
        grade_area.addWidget(grade_value)

        summary_layout.addLayout(grade_area)

        main_layout.addWidget(summary_card)

        # =====================================================
        # 4개 요약 카드
        # =====================================================
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)

        stats_layout.addWidget(
            self.create_stat_card(
                "◈",
                "Score",
                "82",
                "/100",
                "purple",
            ),
            1,
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "▤",
                "Issues",
                "14",
                "",
                "blue",
            ),
            1,
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "♢",
                "Grade",
                "B",
                "",
                "green",
            ),
            1,
        )

        stats_layout.addWidget(
            self.create_resolved_card(),
            1,
        )

        main_layout.addLayout(stats_layout)

        # =====================================================
        # 본문 3열
        # 최종 비율: 좌측 < 가운데 < 우측
        # - 좌측: 분포/이력 중심이라 가장 작게
        # - 가운데: 이슈 목록 가독성 확보
        # - 우측: 설명형 정보가 많아 가장 넓게
        # =====================================================
        body_layout = QHBoxLayout()
        body_layout.setSpacing(8)

        left_column = QVBoxLayout()
        left_column.setSpacing(8)

        distribution_card = self.create_distribution_card()
        history_card = self.create_history_card()

        left_column.addWidget(distribution_card)
        left_column.addWidget(history_card, 1)

        body_layout.addLayout(left_column, 3)

        issues_card = self.create_issues_card()
        body_layout.addWidget(issues_card, 4)

        detail_card = self.create_issue_detail_card()
        body_layout.addWidget(detail_card, 5)

        main_layout.addLayout(body_layout, 1)

        # =====================================================
        # 하단 액션 버튼
        # =====================================================
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        action_layout.setContentsMargins(28, 2, 28, 0)

        re_inspect = QPushButton("⟳   Re-Inspect")
        re_inspect.setObjectName("detailReInspectButton")
        re_inspect.clicked.connect(self.open_reinspect_dialog)

        new_inspection = QPushButton("New Inspection")
        new_inspection.setObjectName("detailActionButton")

        export_report = QPushButton("Export Report")
        export_report.setObjectName("detailActionButton")

        for button in (
            re_inspect,
            new_inspection,
            export_report,
        ):
            button.setFixedHeight(42)
            button.setCursor(Qt.PointingHandCursor)

        action_layout.addWidget(re_inspect)
        action_layout.addWidget(new_inspection)
        action_layout.addWidget(export_report)

        main_layout.addLayout(action_layout)

    # =========================================================
    # 일반 통계 카드
    # =========================================================
    def create_stat_card(
        self,
        icon,
        title,
        value,
        suffix,
        color_name,
    ):
        card = QFrame()
        card.setObjectName("detailStatCard")
        card.setFixedHeight(82)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setObjectName(
            f"detailStatIcon_{color_name}"
        )
        icon_label.setFixedSize(36, 36)
        icon_label.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        title_label = QLabel(title)
        title_label.setObjectName("detailStatTitle")

        value_row = QHBoxLayout()
        value_row.setSpacing(3)

        value_label = QLabel(value)
        value_label.setObjectName("detailStatValue")

        suffix_label = QLabel(suffix)
        suffix_label.setObjectName("detailMuted")

        value_row.addWidget(value_label)
        value_row.addWidget(
            suffix_label,
            0,
            Qt.AlignBottom,
        )
        value_row.addStretch()

        text_layout.addWidget(title_label)
        text_layout.addLayout(value_row)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)

        return card

    # =========================================================
    # Resolved 카드
    # =========================================================
    def create_resolved_card(self):
        card = QFrame()
        card.setObjectName("detailStatCard")
        card.setFixedHeight(82)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(9)

        icon = QLabel("✓")
        icon.setObjectName("detailStatIcon_blue")
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignCenter)

        right = QVBoxLayout()
        right.setSpacing(3)

        title = QLabel("Resolved")
        title.setObjectName("detailStatTitle")

        value = QLabel("9 / 14")
        value.setObjectName("detailResolvedValue")

        progress_row = QHBoxLayout()
        progress_row.setSpacing(5)

        progress = QProgressBar()
        progress.setObjectName("detailProgress")
        progress.setRange(0, 100)
        progress.setValue(64)
        progress.setTextVisible(False)
        progress.setFixedHeight(6)

        percent = QLabel("64%")
        percent.setObjectName("detailSmallText")

        progress_row.addWidget(progress, 1)
        progress_row.addWidget(percent)

        right.addWidget(title)
        right.addWidget(value)
        right.addLayout(progress_row)

        layout.addWidget(icon)
        layout.addLayout(right, 1)

        return card

    # =========================================================
    # Issue Distribution
    # =========================================================
    def create_distribution_card(self):
        card = QFrame()
        card.setObjectName("detailBodyCard")
        card.setFixedHeight(188)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Issue Distribution")
        title.setObjectName("detailBodyTitle")
        layout.addWidget(title)

        rows = [
            ("Critical", 1, "critical"),
            ("High", 3, "high"),
            ("Medium", 5, "medium"),
            ("Low", 5, "low"),
        ]

        for level, count, key in rows:
            row = QHBoxLayout()
            row.setSpacing(5)

            dot = QLabel("●")
            dot.setObjectName(f"detailLevel_{key}")
            dot.setFixedWidth(10)

            label = QLabel(level)
            label.setObjectName("detailSmallText")
            label.setFixedWidth(52)

            bar = QProgressBar()
            bar.setRange(0, 5)
            bar.setValue(count)
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            bar.setObjectName(f"detailDistribution_{key}")

            count_label = QLabel(str(count))
            count_label.setObjectName("detailSmallText")
            count_label.setFixedWidth(12)
            count_label.setAlignment(Qt.AlignRight)

            row.addWidget(dot)
            row.addWidget(label)
            row.addWidget(bar, 1)
            row.addWidget(count_label)

            layout.addLayout(row)

        layout.addStretch()
        return card

    # =========================================================
    # Inspection History
    # =========================================================
    def create_history_card(self):
        card = QFrame()
        card.setObjectName("detailBodyCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Inspection History")
        title.setObjectName("detailBodyTitle")
        layout.addWidget(title)

        history_data = [
            ("2026.07.25 14:32", "전체 검사 · 100 Rules", True),
            ("2026.07.18 10:15", "요구사항 검사 · 25 Rules", False),
            ("2026.06.28 09:20", "보안 검사 · 20 Rules", False),
        ]

        for date, inspection_type, active in history_data:
            row = QHBoxLayout()
            row.setSpacing(7)

            marker = QLabel("●")
            marker.setObjectName(
                "detailHistoryActive" if active else "detailHistoryInactive"
            )
            marker.setFixedWidth(12)

            text = QVBoxLayout()
            text.setSpacing(1)

            date_label = QLabel(date)
            date_label.setObjectName("detailHistoryDate")

            type_label = QLabel(inspection_type)
            type_label.setObjectName("detailHistoryType")

            text.addWidget(date_label)
            text.addWidget(type_label)

            row.addWidget(marker, 0, Qt.AlignTop)
            row.addLayout(text, 1)
            layout.addLayout(row)

        layout.addStretch()

        history_button = QPushButton("전체 이력 보기   ›")
        history_button.setObjectName("detailHistoryButton")
        history_button.setCursor(Qt.PointingHandCursor)
        history_button.setFixedHeight(34)

        layout.addWidget(history_button)
        return card

    # =========================================================
    # Issues 목록
    # =========================================================
    def create_issues_card(self):
        card = QFrame()
        card.setObjectName("detailBodyCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("detailIssuesHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 9, 8, 9)

        title = QLabel("Issues (14)")
        title.setObjectName("detailBodyTitle")

        sort_button = QPushButton("Sort : Severity⌄")
        sort_button.setObjectName("detailSortButton")
        sort_button.setFixedHeight(28)
        sort_button.setCursor(Qt.PointingHandCursor)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(sort_button)

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setObjectName("detailIssueScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("detailIssueContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 0, 8, 0)
        container_layout.setSpacing(0)

        issues = [
            ("Critical", "REQ-021", "요구사항 누락", "미조치"),
            ("High", "SEC-011", "입력값 검증 부족", "조치완료"),
            ("High", "ARCH-007", "권한 관리 미흡", "조치완료"),
            ("Medium", "DATA-015", "데이터 형식 불일치", "미조치"),
            ("Medium", "UI-003", "예외 처리 누락", "미조치"),
            ("Low", "PERF-008", "비효율적 쿼리 사용", "조치완료"),
            ("Low", "LOG-002", "로그 레벨 부적절", "조치완료"),
            ("Low", "DOC-001", "주석/문서화 부족", "미조치"),
            ("Medium", "REQ-034", "요구사항 추적성 부족", "미조치"),
            ("High", "SEC-018", "접근권한 검증 누락", "조치완료"),
            ("Medium", "DATA-022", "참조 데이터 불일치", "미조치"),
            ("Low", "UI-011", "화면 메시지 기준 불일치", "조치완료"),
            ("Low", "DOC-014", "설계 근거 문서 누락", "미조치"),
            ("Medium", "TEST-009", "테스트 케이스 누락", "조치완료"),
        ]

        for index, issue in enumerate(issues):
            row = self.create_issue_row(*issue)
            if index >= 8:
                row.hide()
            container_layout.addWidget(row)

        more_button = QPushButton("더 보기")
        more_button.setObjectName("detailHistoryButton")
        more_button.setCursor(Qt.PointingHandCursor)
        more_button.clicked.connect(
            lambda: self.show_all_issue_rows(container, more_button)
        )

        container_layout.addWidget(more_button)
        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)
        return card

    def create_issue_row(self, severity, code, description, status):
        row = QFrame()
        row.setObjectName("detailIssueListRow")
        row.setFixedHeight(62)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(2, 6, 2, 6)
        layout.setSpacing(8)

        badge = QLabel(severity)
        badge.setObjectName(f"detailBadge_{severity.lower()}")
        badge.setFixedWidth(52)
        badge.setAlignment(Qt.AlignCenter)

        text = QVBoxLayout()
        text.setSpacing(2)

        code_label = QLabel(code)
        code_label.setObjectName("detailIssueCode")

        desc_label = QLabel(description)
        desc_label.setObjectName("detailIssueDescription")

        text.addWidget(code_label)
        text.addWidget(desc_label)

        status_label = QLabel(status)
        status_label.setObjectName(
            "detailStatusResolved" if status == "조치완료" else "detailStatusOpen"
        )
        status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(badge)
        layout.addLayout(text, 1)
        layout.addWidget(status_label)
        return row

    def show_all_issue_rows(self, container, button):
        for child in container.findChildren(QFrame, "detailIssueListRow"):
            child.show()
        button.hide()

    # =========================================================
    # Issue Detail
    # =========================================================
    def create_issue_detail_card(self):
        card = QFrame()
        card.setObjectName("detailBodyCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QLabel("Issue Detail")
        title.setObjectName("detailBodyTitle")
        layout.addWidget(title)

        header = QHBoxLayout()
        header.setSpacing(7)

        badge = QLabel("Critical")
        badge.setObjectName("detailBadge_critical")
        badge.setFixedWidth(54)
        badge.setAlignment(Qt.AlignCenter)

        code = QLabel("REQ-021")
        code.setObjectName("detailIssueDetailCode")

        status = QLabel("미조치")
        status.setObjectName("detailStatusOpen")
        status.setAlignment(Qt.AlignRight)

        header.addWidget(badge)
        header.addWidget(code)
        header.addStretch()
        header.addWidget(status)

        layout.addLayout(header)

        self.add_detail_section(layout, "제목", "요구사항 누락")
        self.add_detail_section(
            layout,
            "설명",
            "요구사항 정의서와 설계서 간 정합성 불일치가 발견되었습니다.",
        )
        self.add_detail_section(
            layout,
            "근거",
            "• 요구사항 정의서 : 3.2.1, 3.2.4\n• 설계서(기능 정의) : 관련 항목 누락",
        )
        self.add_detail_section(
            layout,
            "영향",
            "• 관련 기능 구현 오류 가능성\n• 시스템 요구사항 충족 불가 위험",
        )

        ai_title = QLabel("AI 권고")
        ai_title.setObjectName("detailTextLabel")
        layout.addWidget(ai_title)

        ai_box = QFrame()
        ai_box.setObjectName("detailAIBox")
        ai_layout = QHBoxLayout(ai_box)
        ai_layout.setContentsMargins(10, 9, 10, 9)
        ai_layout.setSpacing(7)

        ai_icon = QLabel("♙")
        ai_icon.setObjectName("detailAIIcon")
        ai_icon.setFixedWidth(16)

        ai_text = QLabel(
            "누락된 요구사항을 설계서에 반영하고,\n"
            "관련 구현 모듈을 검토 후 재검사를 권장합니다."
        )
        ai_text.setObjectName("detailAIText")
        ai_text.setWordWrap(True)

        ai_layout.addWidget(ai_icon, 0, Qt.AlignTop)
        ai_layout.addWidget(ai_text, 1)

        layout.addWidget(ai_box)
        layout.addStretch()

        category = QLabel("카테고리    요구사항")
        category.setObjectName("detailTagText")

        rule = QLabel("발견 기준    Requirement Consistency Rule")
        rule.setObjectName("detailTagText")

        layout.addWidget(category)
        layout.addWidget(rule)

        return card

    def add_detail_section(self, layout, title, text):
        title_label = QLabel(title)
        title_label.setObjectName("detailTextLabel")

        body = QLabel(text)
        body.setObjectName("detailTextBody")
        body.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(body)

    # =========================================================
    # ReInspect 팝업
    # =========================================================
    def open_reinspect_dialog(self):
        dialog = ReInspectDialog(self)
        dialog.exec()
