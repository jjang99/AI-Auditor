from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ReInspectDialog(QDialog):
    def __init__(self, parent=None, rule_count=None):
        super().__init__(parent)
        self.rule_count = rule_count

        self._drag_position = QPoint()
        self._dragging = False
        self.selected_files = []

        self.setWindowTitle("Re-Inspect")
        self.setModal(True)
        self.setFixedSize(700, 680)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("reinspectPanel")
        outer_layout.addWidget(panel)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(26, 22, 26, 20)
        panel_layout.setSpacing(0)

        # =====================================================
        # Header - 다크/라이트 공통 드래그 영역
        # =====================================================
        self.header_frame = QFrame()
        self.header_frame.setObjectName("reinspectHeader")
        header = QHBoxLayout(self.header_frame)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)

        title_area = QVBoxLayout()
        title_area.setSpacing(6)

        self.title_label = QLabel("Re-Inspect")
        self.title_label.setObjectName("reinspectTitle")

        self.description_label = QLabel(
            "수정된 산출물을 등록하고 기존 검사 기준으로 재검사를 수행합니다."
        )
        self.description_label.setObjectName("reinspectDescription")
        self.description_label.setWordWrap(True)

        title_area.addWidget(self.title_label)
        title_area.addWidget(self.description_label)

        close_button = QPushButton("×")
        close_button.setObjectName("reinspectCloseButton")
        close_button.setFixedSize(32, 32)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)

        header.addLayout(title_area, 1)
        header.addWidget(close_button, 0, Qt.AlignTop)
        panel_layout.addWidget(self.header_frame)
        panel_layout.addSpacing(22)

        # Frameless 창은 자식 위젯이 마우스 이벤트를 가져갈 수 있으므로
        # 헤더와 헤더의 텍스트에 동일한 eventFilter를 설치한다.
        self.header_frame.installEventFilter(self)
        self.title_label.installEventFilter(self)
        self.description_label.installEventFilter(self)

        # =====================================================
        # 본문
        # 전체 모달에는 스크롤을 두지 않는다.
        # 스크롤은 2. 업로드 상태 영역에서만 발생한다.
        # =====================================================
        content = QWidget()
        content.setObjectName("reinspectContent")
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =====================================================
        # 1. 수정 산출물 등록
        # =====================================================
        section1_title = QLabel("1. 수정 산출물 등록")
        section1_title.setObjectName("reinspectSectionTitle")
        main_layout.addWidget(section1_title)
        main_layout.addSpacing(12)

        upload_box = QFrame()
        upload_box.setObjectName("reinspectUploadBox")
        upload_box.setFixedHeight(92)

        upload_layout = QHBoxLayout(upload_box)
        upload_layout.setContentsMargins(24, 15, 24, 15)
        upload_layout.setSpacing(22)

        upload_text = QLabel("파일을 드래그 앤 드롭하거나")
        upload_text.setObjectName("reinspectMutedText")
        upload_text.setWordWrap(False)
        upload_text.setMinimumWidth(210)

        select_button = QPushButton("파일 선택")
        select_button.setObjectName("reinspectFileButton")
        select_button.setFixedSize(150, 44)
        select_button.setCursor(Qt.PointingHandCursor)
        select_button.clicked.connect(self.select_files)

        upload_layout.addStretch()
        upload_layout.addWidget(upload_text)
        upload_layout.addWidget(select_button)
        upload_layout.addStretch()

        main_layout.addWidget(upload_box)
        main_layout.addSpacing(28)

        # =====================================================
        # 2. 업로드 상태
        # =====================================================
        section2_title = QLabel("2. 업로드 상태")
        section2_title.setObjectName("reinspectSectionTitle")
        main_layout.addWidget(section2_title)
        main_layout.addSpacing(12)

        self.upload_scroll = QScrollArea()
        self.upload_scroll.setObjectName("reinspectUploadScroll")
        self.upload_scroll.setWidgetResizable(True)
        self.upload_scroll.setFrameShape(QFrame.NoFrame)
        self.upload_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.upload_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.upload_scroll.setFixedHeight(88)

        upload_container = QWidget()
        upload_container.setObjectName("reinspectUploadContainer")
        self.upload_status_layout = QVBoxLayout(upload_container)
        self.upload_status_layout.setContentsMargins(0, 0, 4, 0)
        self.upload_status_layout.setSpacing(10)

        self.upload_status_layout.addStretch()

        self.upload_scroll.setWidget(upload_container)
        main_layout.addWidget(self.upload_scroll)
        main_layout.addSpacing(28)

        # =====================================================
        # 3. 검사 기준
        # =====================================================
        section3_title = QLabel("3. 검사 기준")
        section3_title.setObjectName("reinspectSectionTitle")
        main_layout.addWidget(section3_title)
        main_layout.addSpacing(12)

        rule_box = QFrame()
        rule_box.setObjectName("reinspectRuleBox")
        rule_box.setFixedHeight(84)

        rule_layout = QVBoxLayout(rule_box)
        rule_layout.setContentsMargins(16, 12, 16, 12)
        rule_layout.setSpacing(8)

        rule_row = QHBoxLayout()
        rule_row.setSpacing(12)

        rule_label = QLabel("기존 Inspection 검사기준")
        rule_label.setObjectName("reinspectMutedText")
        rule_label.setWordWrap(True)

        self.rule_value = QLabel(f"전체 검사 · {self.rule_count if self.rule_count is not None else '-'} Rules")
        self.rule_value.setObjectName("reinspectRuleValue")
        self.rule_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        rule_row.addWidget(rule_label, 1)
        rule_row.addWidget(self.rule_value)

        rule_note = QLabel(
            "※ Administration 변경과 관계없이 당시 검사규칙을 그대로 사용합니다."
        )
        rule_note.setObjectName("reinspectRuleNote")
        rule_note.setWordWrap(True)
        rule_note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        rule_layout.addLayout(rule_row)
        rule_layout.addWidget(rule_note)

        main_layout.addWidget(rule_box)
        main_layout.addSpacing(28)

        # =====================================================
        # 4. 검사 준비 요약
        # =====================================================
        section4_title = QLabel("4. 검사 준비 요약")
        section4_title.setObjectName("reinspectSectionTitle")
        main_layout.addWidget(section4_title)
        main_layout.addSpacing(14)

        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(14, 0, 14, 0)
        summary_layout.setSpacing(24)
        self.file_summary_value = self.create_summary_item("등록 파일", "0개")
        summary_layout.addLayout(self.file_summary_value, 1)
        summary_layout.addLayout(self.create_summary_item("적용 규칙", f"{self.rule_count if self.rule_count is not None else '-'}개"), 1)
        self.time_summary_value = self.create_summary_item("예상 검사 시간", "-")
        summary_layout.addLayout(self.time_summary_value, 1)

        main_layout.addLayout(summary_layout)
        panel_layout.addWidget(content, 1)
        panel_layout.addSpacing(18)

        # =====================================================
        # 하단 버튼
        # =====================================================
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        cancel_button = QPushButton("취소")
        cancel_button.setObjectName("reinspectCancelButton")
        cancel_button.setFixedSize(116, 46)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)

        start_button = QPushButton("재검사 시작")
        start_button.setObjectName("reinspectStartButton")
        start_button.setFixedSize(142, 46)
        start_button.setCursor(Qt.PointingHandCursor)
        start_button.clicked.connect(self.accept)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(start_button)
        panel_layout.addLayout(button_layout)

        self.apply_theme()

    # =========================================================
    # Frameless modal dragging
    # =========================================================
    def eventFilter(self, watched, event):
        if watched in (self.header_frame, self.title_label, self.description_label):
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._dragging = True
                self._drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()
                return True

            if event.type() == QEvent.MouseMove and self._dragging:
                if event.buttons() & Qt.LeftButton:
                    self.move(event.globalPosition().toPoint() - self._drag_position)
                    event.accept()
                    return True

            if event.type() == QEvent.MouseButtonRelease:
                self._dragging = False
                event.accept()
                return True

        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            local_point = event.position().toPoint()
            if self.header_frame.geometry().contains(local_point):
                self._dragging = True
                self._drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)

    # =========================================================
    # Theme
    # =========================================================
    def apply_theme(self):
        self.setStyleSheet(self._dark_style() if self._is_dark_mode() else self._light_style())

    def _is_dark_mode(self):
        current = self.parent()
        while current is not None:
            if hasattr(current, "is_dark_mode"):
                return bool(current.is_dark_mode)
            current = current.parent() if hasattr(current, "parent") else None
        return True

    def _dark_style(self):
        return """
        #reinspectPanel { background-color:#101f2c; border:1px solid #64748b; border-radius:14px; }
        #reinspectHeader, #reinspectContent, #reinspectUploadContainer, #reinspectUploadScroll { background:transparent; border:none; }
        #reinspectTitle { color:#f8fafc; font-size:25px; font-weight:700; }
        #reinspectDescription { color:#c2ccd8; font-size:13px; font-weight:500; }
        #reinspectSectionTitle { color:#f8fafc; font-size:16px; font-weight:700; }
        #reinspectCloseButton { color:#e2e8f0; background:transparent; border:none; font-size:27px; font-weight:300; }
        #reinspectCloseButton:hover { color:#ffffff; background-color:#1e293b; border-radius:6px; }
        #reinspectUploadBox { background-color:#102231; border:1px solid #64748b; border-radius:9px; }
        #reinspectMutedText { color:#b6c2d0; font-size:13px; }
        #reinspectFileButton { color:#fff; background-color:#2f64b3; border:none; border-radius:8px; font-size:13px; font-weight:700; }
        #reinspectFileButton:hover { background-color:#3974c7; }
        #reinspectUploadedFile { color:#4ade80; font-size:13px; font-weight:600; }
        #reinspectFileSize { color:#a8b4c3; font-size:12px; }
        #reinspectRuleBox { background-color:#132534; border:1px solid #405368; border-radius:8px; }
        #reinspectRuleValue { color:#fff; font-size:13px; font-weight:700; }
        #reinspectRuleNote { color:#73b2ff; font-size:11px; font-weight:500; }
        #reinspectSummaryLabel { color:#a8b4c3; font-size:12px; font-weight:600; }
        #reinspectSummaryValue { color:#fff; font-size:18px; font-weight:700; }
        #reinspectCancelButton { color:#f8fafc; background-color:#243748; border:none; border-radius:8px; font-size:13px; font-weight:600; }
        #reinspectCancelButton:hover { background-color:#30485d; }
        #reinspectStartButton { color:#fff; background-color:#642fc2; border:none; border-radius:8px; font-size:13px; font-weight:700; }
        #reinspectStartButton:hover { background-color:#7540d4; }
        #reinspectUploadScroll QScrollBar:vertical { background:transparent; width:8px; margin:0; }
        #reinspectUploadScroll QScrollBar::handle:vertical { background:#475569; min-height:28px; border-radius:4px; }
        #reinspectUploadScroll QScrollBar::add-line:vertical, #reinspectUploadScroll QScrollBar::sub-line:vertical { height:0; }
        """

    def _light_style(self):
        return """
        #reinspectPanel { background-color:#ffffff; border:1px solid #94a3b8; border-radius:14px; }
        #reinspectHeader, #reinspectContent, #reinspectUploadContainer, #reinspectUploadScroll { background:transparent; border:none; }
        #reinspectTitle { color:#0f172a; font-size:25px; font-weight:700; }
        #reinspectDescription { color:#475569; font-size:13px; font-weight:500; }
        #reinspectSectionTitle { color:#0f172a; font-size:16px; font-weight:700; }
        #reinspectCloseButton { color:#475569; background:transparent; border:none; font-size:27px; font-weight:300; }
        #reinspectCloseButton:hover { color:#0f172a; background-color:#e2e8f0; border-radius:6px; }
        #reinspectUploadBox { background-color:#f8fafc; border:1px solid #94a3b8; border-radius:9px; }
        #reinspectMutedText { color:#475569; font-size:13px; }
        #reinspectFileButton { color:#fff; background-color:#2563eb; border:none; border-radius:8px; font-size:13px; font-weight:700; }
        #reinspectFileButton:hover { background-color:#1d4ed8; }
        #reinspectUploadedFile { color:#15803d; font-size:13px; font-weight:600; }
        #reinspectFileSize { color:#64748b; font-size:12px; }
        #reinspectRuleBox { background-color:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; }
        #reinspectRuleValue { color:#0f172a; font-size:13px; font-weight:700; }
        #reinspectRuleNote { color:#2563eb; font-size:11px; font-weight:500; }
        #reinspectSummaryLabel { color:#64748b; font-size:12px; font-weight:600; }
        #reinspectSummaryValue { color:#0f172a; font-size:18px; font-weight:700; }
        #reinspectCancelButton { color:#334155; background-color:#e2e8f0; border:none; border-radius:8px; font-size:13px; font-weight:600; }
        #reinspectCancelButton:hover { background-color:#cbd5e1; }
        #reinspectStartButton { color:#fff; background-color:#6d28d9; border:none; border-radius:8px; font-size:13px; font-weight:700; }
        #reinspectStartButton:hover { background-color:#5b21b6; }
        #reinspectUploadScroll QScrollBar:vertical { background:transparent; width:8px; margin:0; }
        #reinspectUploadScroll QScrollBar::handle:vertical { background:#cbd5e1; min-height:28px; border-radius:4px; }
        #reinspectUploadScroll QScrollBar::add-line:vertical, #reinspectUploadScroll QScrollBar::sub-line:vertical { height:0; }
        """

    def add_uploaded_file(self, file_name, file_size):
        row = QHBoxLayout()
        row.setSpacing(10)

        file_label = QLabel(f"✓ {file_name}")
        file_label.setObjectName("reinspectUploadedFile")
        file_label.setWordWrap(True)
        file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        size_label = QLabel(file_size)
        size_label.setObjectName("reinspectFileSize")
        size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        row.addWidget(file_label, 1)
        row.addWidget(size_label)
        self.upload_status_layout.insertLayout(
            max(0, self.upload_status_layout.count() - 1), row
        )

    def create_summary_item(self, title, value):
        layout = QVBoxLayout()
        layout.setSpacing(7)

        title_label = QLabel(title)
        title_label.setObjectName("reinspectSummaryLabel")

        value_label = QLabel(value)
        value_label.setObjectName("reinspectSummaryValue")
        value_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return layout

    def _refresh_uploaded_files(self):
        while self.upload_status_layout.count() > 1:
            item = self.upload_status_layout.takeAt(0)
            child_layout = item.layout()
            widget = item.widget()
            if child_layout is not None:
                while child_layout.count():
                    child = child_layout.takeAt(0)
                    if child.widget() is not None:
                        child.widget().deleteLater()
            elif widget is not None:
                widget.deleteLater()

        for file_path in self.selected_files:
            path = Path(file_path)
            size = path.stat().st_size if path.is_file() else 0
            if size < 1024:
                size_text = f"{size} B"
            elif size < 1024 * 1024:
                size_text = f"{size / 1024:.1f} KB"
            else:
                size_text = f"{size / (1024 * 1024):.1f} MB"
            self.add_uploaded_file(path.name, size_text)

        if hasattr(self, "file_summary_value"):
            value_label = self.file_summary_value.itemAt(1).widget()
            if value_label is not None:
                value_label.setText(f"{len(self.selected_files)}개")

        if hasattr(self, "time_summary_value"):
            value_label = self.time_summary_value.itemAt(1).widget()
            if value_label is not None:
                if not self.selected_files:
                    value_label.setText("-")
                else:
                    total_bytes = sum(
                        Path(file_path).stat().st_size
                        for file_path in self.selected_files
                        if Path(file_path).is_file()
                    )
                    rule_count = self.rule_count or 0
                    estimated_seconds = max(
                        1,
                        round(1.0 + len(self.selected_files) * 0.35 + rule_count * 0.04 + total_bytes / (1024 * 1024) * 0.15),
                    )
                    value_label.setText(f"약 {estimated_seconds}초")

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "수정 산출물 선택",
            "",
            "지원 파일 (*.xlsx *.xls *.docx *.doc *.pdf *.hwp *.hwpx);;모든 파일 (*.*)",
        )
        if not files:
            return
        existing = set(self.selected_files)
        for file_path in files:
            if file_path not in existing:
                self.selected_files.append(file_path)
                existing.add(file_path)
        self._refresh_uploaded_files()
