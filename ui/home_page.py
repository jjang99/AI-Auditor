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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 28, 0, 14)
        main_layout.setSpacing(0)

        # Hero
        hero_layout = QVBoxLayout()
        hero_layout.setContentsMargins(24, 0, 24, 0)
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
            "<div style='line-height:145%;'>"
            "프로젝트 산출물을 AI가 자동 분석하여<br>"
            "품질을 진단하고 개선 방향을 제공합니다."
            "</div>"
        )
        description.setObjectName("homeDescription")
        description.setTextFormat(Qt.RichText)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet(
            'font-weight: 500; font-family: "Segoe UI Variable", "Malgun Gothic";'
        )

        self.inspection_button = QPushButton("Inspection 시작    →")
        self.inspection_button.setObjectName("inspectionStartButton")
        self.inspection_button.setCursor(Qt.PointingHandCursor)
        self.inspection_button.setFixedSize(205, 46)

        play_icon_path = self.asset_path("icons", "play.svg")
        self.inspection_button.setIcon(QIcon(play_icon_path))
        self.inspection_button.setIconSize(QSize(24, 24))

        hero_layout.addWidget(title)
        hero_layout.addSpacing(10)
        hero_layout.addWidget(subtitle)
        hero_layout.addSpacing(12)
        hero_layout.addWidget(description)
        hero_layout.addSpacing(22)
        hero_layout.addWidget(self.inspection_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(hero_layout)
        main_layout.addSpacing(10)

        # 중앙 물결
        wave_label = QLabel()
        wave_label.setAlignment(Qt.AlignCenter)
        wave_label.setFixedHeight(125)

        wave_path = self.asset_path("icons", "home_wave.svg")
        wave_pixmap = QPixmap(wave_path)
        wave_label.setPixmap(
            wave_pixmap.scaled(
                840,
                125,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        main_layout.addWidget(wave_label)
        main_layout.addSpacing(8)

        # 주요 메뉴 카드
        cards_layout = QGridLayout()
        cards_layout.setHorizontalSpacing(14)
        cards_layout.setVerticalSpacing(0)
        cards_layout.setContentsMargins(24, 0, 24, 0)

        for column in range(4):
            cards_layout.setColumnStretch(column, 1)

        card_data = [
            ("Projects", "프로젝트를 생성하고\n이력 및 결과를 관리합니다."),
            ("Inspection", "산출물을 업로드하고\nAI 검사를 수행합니다."),
            ("Reports", "검사 결과를 확인하고\n보고서를 생성합니다."),
            ("Administration", "검사 기준 및 시스템\n설정을 관리합니다."),
        ]

        for index, (name, text) in enumerate(card_data):
            cards_layout.addWidget(self.create_menu_card(name, text), 0, index)

        main_layout.addLayout(cards_layout)
        main_layout.addSpacing(22)

        # Why AI Auditor
        why_outer_layout = QHBoxLayout()
        why_outer_layout.setContentsMargins(24, 0, 24, 0)
        why_outer_layout.setSpacing(0)

        why_frame = QFrame()
        why_frame.setObjectName("whyFrame")
        why_frame.setFixedHeight(128)

        why_layout = QVBoxLayout(why_frame)
        why_layout.setContentsMargins(16, 10, 16, 10)
        why_layout.setSpacing(0)

        why_title = QLabel("Why AI Auditor?")
        why_title.setObjectName("whyTitle")
        why_title.setStyleSheet(
            'color: #3b82f6; font-size: 16px; font-weight: 600; '
            'font-family: "Segoe UI Variable", "Malgun Gothic";'
        )

        why_layout.addWidget(why_title)
        why_layout.addSpacing(6)

        why_items_layout = QHBoxLayout()
        why_items_layout.setContentsMargins(0, 0, 0, 0)
        why_items_layout.setSpacing(10)

        why_data = [
            ("AI 기반 품질 검사", "산출물을 분석하여\n품질 문제를 자동 탐지합니다.", "why_quality.svg"),
            ("요구사항 정합성 검증", "요구사항과 산출물 간의\n정합성을 확인합니다.", "why_consistency.svg"),
            ("변경 영향도 분석", "변경사항이 관련 산출물에\n미치는 영향을 분석합니다.", "why_impact.svg"),
            ("FP 검증 지원", "기능점수 산정 및 검증을\n지원합니다.", "why_fp.svg"),
        ]

        for index, (title_text, body_text, icon_file) in enumerate(why_data):
            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            item_header = QHBoxLayout()
            item_header.setContentsMargins(0, 0, 0, 0)
            item_header.setSpacing(7)

            icon_label = QLabel()
            icon_label.setFixedSize(28, 28)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_pixmap = QPixmap(self.asset_path("icons", icon_file))
            icon_label.setPixmap(
                icon_pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

            item_title = QLabel(title_text)
            item_title.setObjectName("whyItemTitle")
            item_title.setStyleSheet(
                'font-family: "Segoe UI Variable", "Malgun Gothic";'
            )

            item_header.addWidget(icon_label)
            item_header.addWidget(item_title)
            item_header.addStretch()

            body_row = QHBoxLayout()
            body_row.setContentsMargins(35, 0, 0, 0)
            body_row.setSpacing(0)

            body_html = body_text.replace("\n", "<br>")
            item_body = QLabel(
                "<div style='line-height:140%;'>"
                f"{body_html}"
                "</div>"
            )
            item_body.setObjectName("whyItemBody")
            item_body.setTextFormat(Qt.RichText)
            item_body.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            item_body.setStyleSheet(
                'font-family: "Segoe UI Variable", "Malgun Gothic";'
            )
            body_row.addWidget(item_body)
            body_row.addStretch()

            item_layout.addLayout(item_header)
            item_layout.addLayout(body_row)
            item_layout.addStretch()
            why_items_layout.addLayout(item_layout, 1)

            if index < len(why_data) - 1:
                divider = QFrame()
                divider.setObjectName("whyDivider")
                divider.setFrameShape(QFrame.VLine)
                divider.setFixedWidth(1)
                divider.setFixedHeight(50)
                why_items_layout.addWidget(divider, alignment=Qt.AlignVCenter)

        why_layout.addLayout(why_items_layout)
        why_outer_layout.addWidget(why_frame)
        main_layout.addLayout(why_outer_layout)
        main_layout.addSpacing(10)

        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(28, 0, 28, 0)
        footer_layout.setSpacing(0)

        version_label = QLabel("Version 1.0.0")
        version_label.setObjectName("footerText")
        version_label.setStyleSheet(
            'font-size: 11px; font-family: "Segoe UI Variable", "Malgun Gothic";'
        )

        copyright_label = QLabel("© 2026 AI Auditor. All Rights Reserved.")
        copyright_label.setObjectName("footerText")
        copyright_label.setStyleSheet(
            'font-size: 11px; font-family: "Segoe UI Variable", "Malgun Gothic";'
        )

        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        footer_layout.addWidget(copyright_label)
        main_layout.addLayout(footer_layout)

    def create_menu_card(self, title_text, description_text):
        card = QFrame()
        card.setObjectName("homeCard")
        card.setFixedHeight(220)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(0)

        icon_label = QLabel()
        icon_label.setFixedSize(58, 58)
        icon_label.setAlignment(Qt.AlignCenter)

        icon_backgrounds = {
            "Projects": "rgba(37, 99, 235, 32)",
            "Inspection": "rgba(16, 185, 129, 30)",
            "Reports": "rgba(168, 85, 247, 35)",
            "Administration": "rgba(245, 158, 11, 28)",
        }
        icon_label.setStyleSheet(
            f"background-color: {icon_backgrounds[title_text]}; border-radius: 29px;"
        )

        icon_files = {
            "Projects": "project.svg",
            "Inspection": "inspection.svg",
            "Reports": "reports.svg",
            "Administration": "administration.svg",
        }

        pixmap = QPixmap(self.asset_path("icons", icon_files[title_text]))
        icon_label.setPixmap(
            pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        title = QLabel(title_text)
        title.setObjectName("homeCardTitle")
        title.setAlignment(Qt.AlignCenter)

        description_html = description_text.replace("\n", "<br>")
        description = QLabel(
            "<div style='line-height:145%;'>"
            f"{description_html}"
            "</div>"
        )
        description.setObjectName("homeCardDescription")
        description.setTextFormat(Qt.RichText)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet(
            'font-family: "Segoe UI Variable", "Malgun Gothic";'
        )

        arrow = QLabel("→")
        arrow.setObjectName("homeCardArrow")
        arrow.setAlignment(Qt.AlignRight)

        layout.addWidget(icon_label, alignment=Qt.AlignHCenter)
        layout.addSpacing(14)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addStretch()
        layout.addSpacing(4)
        layout.addWidget(arrow)

        return card

    def asset_path(self, folder_name, file_name):
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            folder_name,
            file_name,
        )
