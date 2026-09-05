from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ReInspectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Re-Inspect")
        self.setModal(True)
        self.setFixedSize(620, 565)

        # 기본 윈도우 프레임 제거
        self.setWindowFlags(
            Qt.Dialog |
            Qt.FramelessWindowHint
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        # =====================================================
        # 전체 외곽
        # =====================================================
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("reinspectPanel")

        outer_layout.addWidget(panel)

        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(24, 20, 24, 18)
        main_layout.setSpacing(13)

        # =====================================================
        # Header
        # =====================================================
        header = QHBoxLayout()

        title_area = QVBoxLayout()
        title_area.setSpacing(2)

        title = QLabel("Re-Inspect")
        title.setObjectName("reinspectTitle")

        description = QLabel(
            "수정된 산출물을 등록하고 기존 검사 기준으로 "
            "재검사를 수행합니다."
        )
        description.setObjectName(
            "reinspectDescription"
        )

        title_area.addWidget(title)
        title_area.addWidget(description)

        close_button = QPushButton("×")
        close_button.setObjectName(
            "reinspectCloseButton"
        )
        close_button.setFixedSize(28, 28)
        close_button.setCursor(
            Qt.PointingHandCursor
        )
        close_button.clicked.connect(
            self.reject
        )

        header.addLayout(title_area)
        header.addStretch()
        header.addWidget(
            close_button,
            0,
            Qt.AlignTop,
        )

        main_layout.addLayout(header)

        # =====================================================
        # 1. 수정 산출물 등록
        # =====================================================
        section1_title = QLabel(
            "1. 수정 산출물 등록"
        )
        section1_title.setObjectName(
            "reinspectSectionTitle"
        )

        main_layout.addWidget(section1_title)

        upload_box = QFrame()
        upload_box.setObjectName(
            "reinspectUploadBox"
        )
        upload_box.setFixedHeight(80)

        upload_layout = QHBoxLayout(
            upload_box
        )
        upload_layout.setContentsMargins(
            16, 10, 16, 10
        )

        upload_text = QLabel(
            "파일을 드래그 앤 드롭하거나"
        )
        upload_text.setObjectName(
            "reinspectMutedText"
        )

        select_button = QPushButton(
            "파일 선택"
        )
        select_button.setObjectName(
            "reinspectFileButton"
        )
        select_button.setFixedSize(
            135, 46
        )
        select_button.setCursor(
            Qt.PointingHandCursor
        )
        select_button.clicked.connect(
            self.select_files
        )

        upload_layout.addStretch()
        upload_layout.addWidget(upload_text)
        upload_layout.addSpacing(25)
        upload_layout.addWidget(select_button)
        upload_layout.addStretch()

        main_layout.addWidget(upload_box)

        # =====================================================
        # 2. 업로드 상태
        # =====================================================
        section2_title = QLabel(
            "2. 업로드 상태"
        )
        section2_title.setObjectName(
            "reinspectSectionTitle"
        )

        main_layout.addWidget(section2_title)

        self.upload_status_layout = (
            QVBoxLayout()
        )
        self.upload_status_layout.setSpacing(
            6
        )

        self.add_uploaded_file(
            "요구사항기술서.xlsx",
            "12.4 MB",
        )

        self.add_uploaded_file(
            "요구사항추적표.xlsx",
            "4.8 MB",
        )

        main_layout.addLayout(
            self.upload_status_layout
        )

        # =====================================================
        # 3. 검사 기준
        # =====================================================
        section3_title = QLabel(
            "3. 검사 기준"
        )
        section3_title.setObjectName(
            "reinspectSectionTitle"
        )

        main_layout.addWidget(section3_title)

        rule_box = QFrame()
        rule_box.setObjectName(
            "reinspectRuleBox"
        )
        rule_box.setFixedHeight(66)

        rule_layout = QVBoxLayout(rule_box)
        rule_layout.setContentsMargins(
            15, 8, 15, 8
        )
        rule_layout.setSpacing(3)

        rule_row = QHBoxLayout()

        rule_label = QLabel(
            "기존 Inspection 검사기준"
        )
        rule_label.setObjectName(
            "reinspectMutedText"
        )

        rule_value = QLabel(
            "전체 검사 · 100 Rules"
        )
        rule_value.setObjectName(
            "reinspectRuleValue"
        )

        rule_row.addWidget(rule_label)
        rule_row.addStretch()
        rule_row.addWidget(rule_value)

        rule_note = QLabel(
            "※ Administration 변경과 관계없이 "
            "당시 검사규칙을 그대로 사용합니다."
        )
        rule_note.setObjectName(
            "reinspectRuleNote"
        )

        rule_layout.addLayout(rule_row)
        rule_layout.addWidget(rule_note)

        main_layout.addWidget(rule_box)

        # =====================================================
        # 4. 검사 준비 요약
        # =====================================================
        section4_title = QLabel(
            "4. 검사 준비 요약"
        )
        section4_title.setObjectName(
            "reinspectSectionTitle"
        )

        main_layout.addWidget(section4_title)

        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(
            15, 0, 15, 0
        )

        summary_layout.addLayout(
            self.create_summary_item(
                "등록 파일",
                "18개",
            )
        )

        summary_layout.addStretch()

        summary_layout.addLayout(
            self.create_summary_item(
                "적용 규칙",
                "100개",
            )
        )

        summary_layout.addStretch()

        summary_layout.addLayout(
            self.create_summary_item(
                "예상 검사 시간",
                "약 2분 20초",
            )
        )

        main_layout.addLayout(
            summary_layout
        )

        main_layout.addStretch()

        # =====================================================
        # 하단 버튼
        # =====================================================
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        button_layout.addStretch()

        cancel_button = QPushButton(
            "취소"
        )
        cancel_button.setObjectName(
            "reinspectCancelButton"
        )
        cancel_button.setFixedSize(
            104, 42
        )
        cancel_button.setCursor(
            Qt.PointingHandCursor
        )
        cancel_button.clicked.connect(
            self.reject
        )

        start_button = QPushButton(
            "재검사 시작"
        )
        start_button.setObjectName(
            "reinspectStartButton"
        )
        start_button.setFixedSize(
            130, 42
        )
        start_button.setCursor(
            Qt.PointingHandCursor
        )
        start_button.clicked.connect(
            self.accept
        )

        button_layout.addWidget(
            cancel_button
        )
        button_layout.addWidget(
            start_button
        )

        main_layout.addLayout(
            button_layout
        )

        # =====================================================
        # Modal 전용 스타일
        # theme.py를 건드리지 않도록 여기서 적용
        # =====================================================
        self.setStyleSheet(
            """
            #reinspectPanel {
                background-color: #101f2c;
                border: 1px solid #64748b;
                border-radius: 14px;
            }

            #reinspectTitle {
                color: #f8fafc;
                font-size: 22px;
                font-weight: 600;
            }

            #reinspectDescription {
                color: #aebaca;
                font-size: 11px;
            }

            #reinspectSectionTitle {
                color: #f1f5f9;
                font-size: 14px;
                font-weight: 600;
            }

            #reinspectCloseButton {
                color: #e2e8f0;
                background: transparent;
                border: none;
                font-size: 25px;
                font-weight: 300;
            }

            #reinspectCloseButton:hover {
                color: #ffffff;
                background-color: #1e293b;
                border-radius: 5px;
            }

            #reinspectUploadBox {
                background-color: #102231;
                border: 1px solid #64748b;
                border-radius: 9px;
            }

            #reinspectMutedText {
                color: #9eacbd;
                font-size: 11px;
            }

            #reinspectFileButton {
                color: #ffffff;
                background-color: #2c5da8;
                border: none;
                border-radius: 7px;
                font-size: 12px;
                font-weight: 600;
            }

            #reinspectFileButton:hover {
                background-color: #356bbd;
            }

            #reinspectUploadedFile {
                color: #4ade80;
                font-size: 11px;
            }

            #reinspectFileSize {
                color: #94a3b8;
                font-size: 10px;
            }

            #reinspectRuleBox {
                background-color: #132534;
                border: 1px solid #405368;
                border-radius: 7px;
            }

            #reinspectRuleValue {
                color: #f1f5f9;
                font-size: 11px;
                font-weight: 600;
            }

            #reinspectRuleNote {
                color: #60a5fa;
                font-size: 9px;
            }

            #reinspectSummaryLabel {
                color: #94a3b8;
                font-size: 10px;
            }

            #reinspectSummaryValue {
                color: #f1f5f9;
                font-size: 16px;
                font-weight: 500;
            }

            #reinspectCancelButton {
                color: #f1f5f9;
                background-color: #243748;
                border: none;
                border-radius: 8px;
                font-size: 11px;
            }

            #reinspectCancelButton:hover {
                background-color: #30485d;
            }

            #reinspectStartButton {
                color: #ffffff;
                background-color: #5b2daf;
                border: none;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 600;
            }

            #reinspectStartButton:hover {
                background-color: #6d38c6;
            }
            """
        )

    # =========================================================
    # 업로드 파일 한 줄
    # =========================================================
    def add_uploaded_file(
        self,
        file_name,
        file_size,
    ):
        row = QHBoxLayout()

        file_label = QLabel(
            f"✓ {file_name}"
        )
        file_label.setObjectName(
            "reinspectUploadedFile"
        )

        size_label = QLabel(file_size)
        size_label.setObjectName(
            "reinspectFileSize"
        )

        row.addWidget(file_label)
        row.addStretch()
        row.addWidget(size_label)

        self.upload_status_layout.addLayout(
            row
        )

    # =========================================================
    # 검사 준비 요약 항목
    # =========================================================
    def create_summary_item(
        self,
        title,
        value,
    ):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setObjectName(
            "reinspectSummaryLabel"
        )

        value_label = QLabel(value)
        value_label.setObjectName(
            "reinspectSummaryValue"
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return layout

    # =========================================================
    # 파일 선택
    # =========================================================
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "수정 산출물 선택",
            "",
            (
                "지원 파일 "
                "(*.xlsx *.xls *.docx *.doc "
                "*.pdf *.hwp *.hwpx);;"
                "모든 파일 (*.*)"
            ),
        )

        # 현재 단계에서는 실제 분석 전에
        # 선택 기능까지만 연결
        if files:
            pass