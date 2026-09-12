from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
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


class AdministrationPage(QWidget):
    def __init__(self):
        super().__init__()

        # ==================================================
        # 전체 Layout
        # ==================================================
        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar("Administration")
        page_layout.addWidget(self.sidebar)

        # 오른쪽 Content
        content = QWidget()
        content.setObjectName("projectsContent")

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 16)
        main_layout.setSpacing(0)

        page_layout.addWidget(content, 1)

        # ==================================================
        # Header
        # ==================================================
        title = QLabel("Administration")
        title.setObjectName("pageTitle")

        description = QLabel(
            "AI Auditor의 검사 기준과 Rule을 관리합니다."
        )
        description.setObjectName("pageDescription")

        main_layout.addWidget(title)
        main_layout.addSpacing(3)
        main_layout.addWidget(description)
        main_layout.addSpacing(18)

        # ==================================================
        # 검사 기준 관리 제목
        # ==================================================
        section_title = QLabel(
            "검사 기준 관리 (Inspection Rules Management)"
        )
        section_title.setObjectName("projectName")

        main_layout.addWidget(section_title)
        main_layout.addSpacing(10)

        # ==================================================
        # 상단 요약 카드
        # ==================================================
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)

        summary_data = [
            ("전체 Rule", "100"),
            ("활성 Rule", "92"),
            ("비활성 Rule", "8"),
            ("카테고리", "6"),
        ]

        for label_text, value_text in summary_data:
            card = QFrame()
            card.setObjectName("projectCard")
            card.setFixedHeight(82)

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
        # Rule 목록 헤더
        # ==================================================
        rule_header = QHBoxLayout()

        rule_title = QLabel("Inspection Rules")
        rule_title.setObjectName("projectName")

        add_rule_button = QPushButton("+ New Rule")
        add_rule_button.setObjectName("newProjectButton")
        add_rule_button.setCursor(Qt.PointingHandCursor)
        add_rule_button.setFixedSize(100, 34)

        rule_header.addWidget(rule_title)
        rule_header.addStretch()
        rule_header.addWidget(add_rule_button)

        main_layout.addLayout(rule_header)
        main_layout.addSpacing(8)

        # ==================================================
        # Rule Table
        # ==================================================
        self.rule_table = QTableWidget()
        self.rule_table.setColumnCount(5)

        self.rule_table.setHorizontalHeaderLabels(
            [
                "Rule ID",
                "Category",
                "검사 기준",
                "Severity",
                "상태",
            ]
        )

        sample_rules = [
            ("REQ-001", "요구사항", "요구사항 누락 여부", "High", "활성"),
            ("REQ-021", "요구사항", "요구사항 모호성 검사", "Critical", "활성"),
            ("SEC-018", "보안", "접근권한 검증 여부", "High", "활성"),
            ("DATA-022", "데이터", "참조 데이터 일관성", "Medium", "활성"),
            ("UI-011", "UI/UX", "화면 메시지 기준", "Low", "비활성"),
            ("TEST-009", "테스트", "테스트 케이스 누락", "Medium", "활성"),
        ]

        self.rule_table.setRowCount(len(sample_rules))

        for row, rule in enumerate(sample_rules):
            for column, value in enumerate(rule):
                item = QTableWidgetItem(value)

                if column in (0, 3, 4):
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(
                        Qt.AlignLeft | Qt.AlignVCenter
                    )

                self.rule_table.setItem(
                    row,
                    column,
                    item,
                )

        self.rule_table.setColumnWidth(0, 85)
        self.rule_table.setColumnWidth(1, 90)
        self.rule_table.setColumnWidth(2, 250)
        self.rule_table.setColumnWidth(3, 85)
        self.rule_table.setColumnWidth(4, 80)

        self.rule_table.setFixedHeight(255)
        self.rule_table.verticalHeader().setVisible(False)
        self.rule_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.rule_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        main_layout.addWidget(self.rule_table)
        main_layout.addSpacing(14)

        # ==================================================
        # Rule Detail
        # ==================================================
        detail_frame = QFrame()
        detail_frame.setObjectName("projectCard")

        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(16, 14, 16, 14)
        detail_layout.setSpacing(8)

        detail_header = QHBoxLayout()

        detail_title = QLabel("Rule Detail")
        detail_title.setObjectName("projectName")

        self.active_checkbox = QCheckBox("활성")
        self.active_checkbox.setChecked(True)

        detail_header.addWidget(detail_title)
        detail_header.addStretch()
        detail_header.addWidget(self.active_checkbox)

        detail_layout.addLayout(detail_header)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        detail_layout.addWidget(separator)

        rule_id = QLabel("Rule ID    REQ-021")
        rule_id.setObjectName("projectDescription")

        category = QLabel("Category   요구사항")
        category.setObjectName("projectDescription")

        severity = QLabel("Severity   Critical")
        severity.setObjectName("projectDescription")

        rule_name = QLabel(
            "검사 기준   요구사항이 명확하고 검증 가능한 형태로 "
            "작성되었는지 확인"
        )
        rule_name.setObjectName("projectDescription")
        rule_name.setWordWrap(True)

        detail_layout.addWidget(rule_id)
        detail_layout.addWidget(category)
        detail_layout.addWidget(severity)
        detail_layout.addWidget(rule_name)

        # 안내 + 닫기 버튼은 같은 줄에 정렬
        bottom_row = QHBoxLayout()

        notice = QLabel(
            "※ 규칙을 비활성화하면 기본 검사에서 제외됩니다."
        )
        notice.setObjectName("projectDescription")

        close_button = QPushButton("닫기")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setFixedSize(74, 32)

        bottom_row.addWidget(notice)
        bottom_row.addStretch()
        bottom_row.addWidget(close_button)

        detail_layout.addSpacing(3)
        detail_layout.addLayout(bottom_row)

        main_layout.addWidget(detail_frame)
        main_layout.addStretch(1)