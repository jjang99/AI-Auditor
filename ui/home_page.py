import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # ==================================================
        # 전체 Home 레이아웃
        # ==================================================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 18, 40, 14)
        main_layout.setSpacing(0)

        # ==================================================
        # Hero 영역
        # ==================================================
        hero_layout = QVBoxLayout()
        hero_layout.setAlignment(Qt.AlignCenter)
        hero_layout.setSpacing(0)

        title = QLabel("AI Auditor")
        title.setObjectName("homeTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setMinimumHeight(66)

        subtitle = QLabel("AI 기반 프로젝트 품질 감사 플랫폼")
        subtitle.setObjectName("homeSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        description = QLabel(
            "프로젝트 산출물을 AI가 자동 분석하여\n"
            "품질을 진단하고 개선 방향을 제공합니다."
        )
        description.setObjectName("homeDescription")
        description.setAlignment(Qt.AlignCenter)

        self.inspection_button = QPushButton("Inspection 시작    →")
        self.inspection_button.setObjectName("inspectionStartButton")
        self.inspection_button.setCursor(Qt.PointingHandCursor)
        self.inspection_button.setFixedSize(205, 46)

        play_icon_path = self.asset_path(
            "icons",
            "play.svg",
        )

        self.inspection_button.setIcon(QIcon(play_icon_path))
        self.inspection_button.setIconSize(
            QSize(24, 24)
        )

        hero_layout.addWidget(title)
        hero_layout.addSpacing(10)

        hero_layout.addWidget(subtitle)
        hero_layout.addSpacing(10)

        hero_layout.addWidget(description)
        hero_layout.addSpacing(16)

        hero_layout.addWidget(
            self.inspection_button,
            alignment=Qt.AlignCenter,
        )

        main_layout.addLayout(hero_layout)
        main_layout.addSpacing(14)

        # ==================================================
        # 중앙 물결 배경
        # ==================================================
        wave_label = QLabel()
        wave_label.setAlignment(Qt.AlignCenter)
        wave_label.setFixedHeight(90)

        wave_path = self.asset_path(
            "icons",
            "home_wave.svg",
        )

        wave_pixmap = QPixmap(wave_path)

        wave_label.setPixmap(
            wave_pixmap.scaled(
                680,
                105,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        main_layout.addWidget(wave_label)
        main_layout.addSpacing(8)

        # ==================================================
        # 주요 메뉴 카드
        # ==================================================
        cards_layout = QGridLayout()
        cards_layout.setHorizontalSpacing(15)
        cards_layout.setVerticalSpacing(0)

        card_data = [
            (
                "Projects",
                "프로젝트를 생성하고\n이력 및 결과를 관리합니다.",
            ),
            (
                "Inspection",
                "산출물을 업로드하고\nAI 검사를 수행합니다.",
            ),
            (
                "Reports",
                "검사 결과를 확인하고\n보고서를 생성합니다.",
            ),
            (
                "Administration",
                "검사 기준 및 시스템\n설정을 관리합니다.",
            ),
        ]

        for index, (name, text) in enumerate(card_data):
            card = self.create_menu_card(name, text)
            cards_layout.addWidget(card, 0, index)

        main_layout.addLayout(cards_layout)
        main_layout.addSpacing(12)

        # ==================================================
        # Why AI Auditor
        # ==================================================
        why_frame = QFrame()
        why_frame.setObjectName("whyFrame")
        why_frame.setFixedHeight(170)

        why_layout = QVBoxLayout(why_frame)
        why_layout.setContentsMargins(20, 12, 20, 12)
        why_layout.setSpacing(0)

        why_title = QLabel("Why AI Auditor?")
        why_title.setObjectName("whyTitle")

        why_layout.addWidget(why_title)
        why_layout.addSpacing(8)

        why_items_layout = QHBoxLayout()
        why_items_layout.setContentsMargins(0, 0, 0, 0)
        why_items_layout.setSpacing(12)

        why_data = [
            (
                "AI 기반 품질 검사",
                "산출물을 분석하여\n품질 문제를 자동 탐지합니다.",
                "why_quality.svg",
            ),
            (
                "요구사항 정합성 검증",
                "요구사항과 산출물 간의\n정합성을 확인합니다.",
                "why_consistency.svg",
            ),
            (
                "변경 영향도 분석",
                "변경사항이 관련 산출물에\n미치는 영향을 분석합니다.",
                "why_impact.svg",
            ),
            (
                "FP 검증 지원",
                "기능점수 산정 및 검증을\n지원합니다.",
                "why_fp.svg",
            ),
        ]

        for index, (
            title_text,
            body_text,
            icon_file,
        ) in enumerate(why_data):

            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            # Why 아이콘
            icon_label = QLabel()
            icon_label.setFixedSize(38, 38)
            icon_label.setAlignment(Qt.AlignCenter)

            icon_path = self.asset_path(
                "icons",
                icon_file,
            )

            icon_pixmap = QPixmap(icon_path)

            icon_label.setPixmap(
                icon_pixmap.scaled(
                    34,
                    34,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

            # 제목
            item_title = QLabel(title_text)
            item_title.setObjectName("whyItemTitle")

            # 설명
            item_body = QLabel(body_text)
            item_body.setObjectName("whyItemBody")

            item_layout.addWidget(icon_label)
            item_layout.addWidget(item_title)
            item_layout.addWidget(item_body)
            item_layout.addStretch()

            why_items_layout.addLayout(item_layout, 1)

            # 항목 사이 세로 구분선
            if index < len(why_data) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.VLine)
                divider.setObjectName("whyDivider")
                why_items_layout.addWidget(divider)

        why_layout.addLayout(why_items_layout)

        main_layout.addWidget(why_frame)
        main_layout.addSpacing(6)

        # ==================================================
        # Footer
        # ==================================================
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(4, 0, 4, 0)
        footer_layout.setSpacing(0)

        version_label = QLabel("Version 1.0.0")
        version_label.setObjectName("footerText")

        copyright_label = QLabel(
            "© 2026 AI Auditor. All Rights Reserved."
        )
        copyright_label.setObjectName("footerText")

        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        footer_layout.addWidget(copyright_label)

        main_layout.addLayout(footer_layout)

    # ======================================================
    # 메뉴 카드 생성
    # ======================================================
    def create_menu_card(self, title_text, description_text):
        card = QFrame()
        card.setObjectName("homeCard")
        card.setFixedHeight(205)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(0)

        # 아이콘 영역
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)

        # Reports 원형 배경
        if title_text == "Reports":
            icon_label.setStyleSheet("""
                background-color: rgba(168, 85, 247, 35);
                border-radius: 24px;
            """)

        icon_files = {
            "Projects": "project.svg",
            "Inspection": "inspection.svg",
            "Reports": "reports.svg",
            "Administration": "administration.svg",
        }

        icon_path = self.asset_path(
            "icons",
            icon_files[title_text],
        )

        pixmap = QPixmap(icon_path)

        icon_label.setPixmap(
            pixmap.scaled(
                42,
                42,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        # 카드 제목
        title = QLabel(title_text)
        title.setObjectName("homeCardTitle")

        # 카드 설명
        description = QLabel(description_text)
        description.setObjectName("homeCardDescription")

        # 화살표
        arrow = QLabel("→")
        arrow.setObjectName("homeCardArrow")
        arrow.setAlignment(Qt.AlignRight)

        layout.addWidget(icon_label)
        layout.addSpacing(7)

        layout.addWidget(title)
        layout.addSpacing(7)

        layout.addWidget(description)

        layout.addStretch()

        layout.addWidget(arrow)

        return card

    # ======================================================
    # assets 경로 생성
    # ======================================================
    def asset_path(self, folder_name, file_name):
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            folder_name,
            file_name,
        )