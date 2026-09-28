from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QProgressBar, QScrollArea, QVBoxLayout, QWidget,
)

from ui.sidebar import Sidebar
from ui.inspection_rules_dialog import InspectionRulesDialog
from ui.existing_project_dialog import ExistingProjectDialog

from app.database.repositories.project_repository import get_project_by_name
from app.database.repositories.inspection_repository import get_latest_inspection

class InspectionPage(QWidget):
    existing_project_selected = Signal(dict)
    inspection_result_requested = Signal()

    def __init__(self):
        self._rule_text_widgets = []
        super().__init__()
        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)
        self.sidebar = Sidebar("Inspection")
        page_layout.addWidget(self.sidebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("inspectionScroll")
        content = QWidget()
        content.setObjectName("inspectionContent")
        main = QVBoxLayout(content)
        main.setContentsMargins(18, 16, 18, 18)
        main.setSpacing(9)
        self.main_layout = main
        scroll.setWidget(content)
        page_layout.addWidget(scroll, 1)

        header = QHBoxLayout()
        title_area = QVBoxLayout()
        title_area.setSpacing(2)
        title = QLabel("Inspection")
        title.setObjectName("inspectionTitle")
        description = QLabel("검사할 프로젝트와 파일, 검사 기준을 선택하고 검사를 시작합니다.")
        description.setObjectName("inspectionDescription")
        title_area.addWidget(title)
        title_area.addWidget(description)
        help_button = QPushButton("ⓘ  도움말")
        help_button.setObjectName("inspectionHelpButton")
        help_button.setFixedSize(78, 30)
        header.addLayout(title_area)
        header.addStretch()
        header.addWidget(help_button)
        main.addLayout(header)

        project_card = self.create_card()
        project_layout = QVBoxLayout(project_card)
        project_layout.setContentsMargins(14, 11, 14, 11)
        project_layout.setSpacing(7)
        project_layout.addWidget(self.section_title("▣  1. 프로젝트 정보"))
        form_row = QHBoxLayout()
        form_row.setSpacing(16)
        left = QVBoxLayout(); left.setSpacing(3)
        project_label = QLabel("Project Name *"); project_label.setObjectName("inspectionFieldLabel")
        self.project_name = QLineEdit(); self.project_name.setObjectName("inspectionInput"); self.project_name.setFixedHeight(31)
        duplicate_row = QHBoxLayout()
        duplicate_row.setSpacing(4)

        self.duplicate_warning = QLabel(
            "프로젝트명을 입력하면 기존 프로젝트 여부를 확인합니다."
        )
        self.duplicate_warning.setObjectName("inspectionDuplicate")

        self.duplicate_button = QPushButton("기존 프로젝트 확인")
        self.duplicate_button.setObjectName("inspectionDuplicateButton")
        self.duplicate_button.setCursor(Qt.PointingHandCursor)
        self.duplicate_button.clicked.connect(self.open_existing_projects)
        self.duplicate_button.hide()

        duplicate_row.addWidget(self.duplicate_warning)
        duplicate_row.addWidget(self.duplicate_button)
        duplicate_row.addStretch()

        self.project_name.textChanged.connect(self.check_duplicate_project)

        self.project_name.textChanged.connect(self.check_duplicate_project)
        desc_label = QLabel("Description (선택)"); desc_label.setObjectName("inspectionFieldLabel")
        description_input = QLineEdit(); description_input.setObjectName("inspectionInput"); description_input.setFixedHeight(31)
        left.addWidget(project_label); left.addWidget(self.project_name); left.addLayout(duplicate_row); left.addWidget(desc_label); left.addWidget(description_input)
        right = QVBoxLayout(); right.setSpacing(4)
        dept_label = QLabel("부서명(기관명) (선택)"); dept_label.setObjectName("inspectionFieldLabel")
        department = QLineEdit(); department.setObjectName("inspectionInput"); department.setFixedHeight(31)
        type_label = QLabel("프로젝트 구분"); type_label.setObjectName("inspectionFieldLabel")
        project_type = QComboBox(); project_type.setObjectName("inspectionCombo"); project_type.addItems(["선택", "신규 구축", "고도화", "유지보수"]); project_type.setCurrentIndex(0); project_type.setFixedHeight(31)
        right.addWidget(dept_label); right.addWidget(department); right.addSpacing(8); right.addWidget(type_label); right.addWidget(project_type); right.addStretch()
        form_row.addLayout(left, 1); form_row.addLayout(right, 1); project_layout.addLayout(form_row); main.addWidget(project_card)

        files_card = self.create_card(); files_layout = QVBoxLayout(files_card); files_layout.setContentsMargins(14, 11, 14, 11); files_layout.setSpacing(7)
        files_layout.addWidget(self.section_title("▣  2. 검사 대상 파일"))
        upload_box = QFrame(); upload_box.setObjectName("inspectionUploadBox"); upload_box.setFixedHeight(52)
        upload_layout = QHBoxLayout(upload_box)
        upload_text = QLabel("♧   파일을 드래그 앤 드롭하거나"); upload_text.setObjectName("inspectionUploadText")
        choose_file = QPushButton("파일 선택"); choose_file.setObjectName("inspectionFileButton"); choose_file.setFixedSize(88, 32)
        upload_layout.addStretch(); upload_layout.addWidget(upload_text); upload_layout.addSpacing(18); upload_layout.addWidget(choose_file); upload_layout.addStretch(); files_layout.addWidget(upload_box)
        file_header = QHBoxLayout(); registered = QLabel("등록된 파일 18개 (12.3 MB)"); registered.setObjectName("inspectionFileCount")
        delete_all = QPushButton("♜  전체 삭제"); delete_all.setObjectName("inspectionSmallButton"); delete_all.setFixedSize(88, 28)
        file_header.addWidget(registered); file_header.addStretch(); file_header.addWidget(delete_all); files_layout.addLayout(file_header)
        file_table = QFrame(); file_table.setObjectName("inspectionFileTable"); table_layout = QVBoxLayout(file_table); table_layout.setContentsMargins(0,0,0,0); table_layout.setSpacing(0)
        files = [("UserController.java","src/main/java/com/auditor/controller/","8.5 KB"),("AuthService.java","src/main/java/com/auditor/service/","12.3 KB"),("SecurityUtils.java","src/main/java/com/auditor/util/","6.7 KB"),("application.yml","src/main/resources/","2.1 KB"),("README.md","/","1.2 KB")]
        for name, path, size in files:
            row = QFrame(); row.setObjectName("inspectionFileRow"); row.setFixedHeight(24); row_layout = QHBoxLayout(row); row_layout.setContentsMargins(10,2,10,2)
            name_label=QLabel(f"▣  {name}"); name_label.setObjectName("inspectionTableText"); name_label.setFixedWidth(190)
            path_label=QLabel(path); path_label.setObjectName("inspectionTableMuted")
            size_label=QLabel(size); size_label.setObjectName("inspectionTableText"); size_label.setFixedWidth(52)
            delete=QLabel("♜"); delete.setObjectName("inspectionTableText"); delete.setFixedWidth(18)
            row_layout.addWidget(name_label); row_layout.addWidget(path_label,1); row_layout.addWidget(size_label); row_layout.addWidget(delete); table_layout.addWidget(row)
        files_layout.addWidget(file_table)
        footer=QHBoxLayout(); more_files=QLabel("외 14개 파일"); more_files.setObjectName("inspectionTableMuted"); total_size=QLabel("총 12.3 MB"); total_size.setObjectName("inspectionTableMuted")
        footer.addWidget(more_files); footer.addStretch(); footer.addWidget(total_size); files_layout.addLayout(footer); main.addWidget(files_card)

        rules_card=self.create_card(); rules_layout=QVBoxLayout(rules_card); rules_layout.setContentsMargins(14,10,14,10); rules_layout.setSpacing(4); rule_header=QHBoxLayout()
        rule_title=self.section_title("▣  3. 검사 기준 선택"); note=QLabel("※ 변경 사항은 이번 검사에만 적용됩니다."); note.setObjectName("inspectionBlueNote")
        select_all=QPushButton("전체 선택"); select_all.setObjectName("inspectionSmallButton"); select_all.setFixedSize(75,28)
        clear_all=QPushButton("전체 해제"); clear_all.setObjectName("inspectionSmallButton"); clear_all.setFixedSize(75,28)
        rule_header.addWidget(rule_title); rule_header.addWidget(note); rule_header.addStretch(); rule_header.addWidget(select_all); rule_header.addWidget(clear_all); rules_layout.addLayout(rule_header)
        categories=[("✓","감리 사전점검","24개 규칙","사업 산출물의 완전성 및 적정성 점검"),("↔","요구사항 정합성","28개 규칙","요구사항과 관련 산출물 간 정합성 점검"),("△","변경영향도","18개 규칙","변경사항의 영향범위 및 반영 여부 점검"),("FP","FP 검증","12개 규칙","기능점수 산정의 누락·중복·적정성 점검"),("AI","AI 특화 검증","23개 규칙","AI 적용 시스템의 품질·보안·신뢰성 점검")]
        for index, category in enumerate(categories): rules_layout.addWidget(self.create_rule_row(*category, open_dialog=(index==0)))
        main.addWidget(rules_card)

        self.summary_card=self.create_card(); summary_layout=QVBoxLayout(self.summary_card); summary_layout.setContentsMargins(14,10,14,10); summary_layout.setSpacing(8); summary_layout.addWidget(self.section_title("4. 검사 준비 요약"))
        summary_row=QHBoxLayout(); summary_row.setSpacing(10)
        summary_row.addWidget(self.create_summary_box("▣","등록 파일","18개 파일","(12.3 MB)")); summary_row.addWidget(self.create_summary_box("☷","적용 규칙","97 / 102개","(5개 제외)")); summary_row.addWidget(self.create_summary_box("◷","예상 검사 시간","약 2분 20초","(시스템 사양 기준)"))
        self.start_button=QPushButton("▷  검사 시작"); self.start_button.setObjectName("inspectionStartButton"); self.start_button.setFixedWidth(155); self.start_button.clicked.connect(self.show_progress); summary_row.addWidget(self.start_button); summary_layout.addLayout(summary_row)
        info=QFrame(); info.setObjectName("inspectionInfoBox"); info_layout=QVBoxLayout(info); info_layout.setContentsMargins(10,7,10,7); info_layout.setSpacing(2)
        info_title=QLabel("ⓘ 안내"); info_title.setObjectName("inspectionInfoTitle")
        info_text=QLabel("• 검사 기준(규칙)의 추가, 수정, 활성/비활성 설정은 Administration > 검사 기준 관리에서 가능합니다.\n• 검사 파일은 텍스트 파일(.java, .py, .js, .yml, .xml 등)을 권장합니다."); info_text.setObjectName("inspectionInfoText")
        info_layout.addWidget(info_title); info_layout.addWidget(info_text); summary_layout.addWidget(info); main.addWidget(self.summary_card)

        self.progress_card=self.create_progress_card(); self.progress_card.hide(); main.addWidget(self.progress_card)
        self.complete_card=self.create_complete_card(); self.complete_card.hide(); main.addWidget(self.complete_card)
        self.demo_timer=QTimer(self); self.demo_timer.setSingleShot(True); self.demo_timer.timeout.connect(self.show_complete)
        main.addStretch(); self.setStyleSheet(self.inspection_style())

    def create_progress_card(self):
        card=self.create_card(); layout=QVBoxLayout(card); layout.setContentsMargins(14,12,14,12); layout.setSpacing(10); layout.addWidget(self.section_title("4. 검사 진행"))
        description=QLabel("AI Auditor가 등록된 산출물을 검사하고 있습니다."); description.setObjectName("inspectionProgressDescription"); layout.addWidget(description)
        progress_row=QHBoxLayout(); progress_row.setSpacing(14); percent=QLabel("42%"); percent.setObjectName("inspectionProgressPercent"); percent.setFixedWidth(70)
        bar=QProgressBar(); bar.setObjectName("inspectionProgressBar"); bar.setRange(0,100); bar.setValue(42); bar.setTextVisible(False); bar.setFixedHeight(18)
        cancel=QPushButton("검사 취소"); cancel.setObjectName("inspectionCancelButton"); cancel.setFixedSize(115,46); cancel.setCursor(Qt.PointingHandCursor); cancel.clicked.connect(self.cancel_progress)
        progress_row.addWidget(percent); progress_row.addWidget(bar,1); progress_row.addWidget(cancel); layout.addLayout(progress_row)
        status_row=QHBoxLayout(); status_row.setSpacing(10)
        status_row.addWidget(self.create_progress_info_box("완료 규칙","43 / 102개")); status_row.addWidget(self.create_progress_info_box("현재 검사 항목","SEC-011 입력값 검증"),2); status_row.addWidget(self.create_progress_info_box("예상 남은 시간","약 1분 15초")); status_row.addWidget(self.create_progress_info_box("처리 상태","검사 진행 중")); layout.addLayout(status_row); return card

    def create_progress_info_box(self,title,value):
        box=QFrame(); box.setObjectName("inspectionProgressInfoBox"); box.setFixedHeight(68); layout=QVBoxLayout(box); layout.setContentsMargins(10,8,10,8); layout.setSpacing(4)
        title_label=QLabel(title); title_label.setObjectName("inspectionProgressInfoTitle"); value_label=QLabel(value); value_label.setObjectName("inspectionProgressInfoValue"); layout.addWidget(title_label); layout.addWidget(value_label); layout.addStretch(); return box

    def create_complete_card(self):
        card=self.create_card(); layout=QVBoxLayout(card); layout.setContentsMargins(14,12,14,12); layout.setSpacing(10); layout.addWidget(self.section_title("4. 검사 완료"))
        message_row=QHBoxLayout(); message_row.setSpacing(12); check=QLabel("✓"); check.setObjectName("inspectionCompleteCheck"); check.setAlignment(Qt.AlignCenter); check.setFixedSize(32,32)
        message_area=QVBoxLayout(); message_area.setSpacing(2); message=QLabel("검사가 성공적으로 완료되었습니다."); message.setObjectName("inspectionCompleteMessage")
        description=QLabel("검사 결과를 확인하거나 Project Detail로 이동할 수 있습니다."); description.setObjectName("inspectionCompleteDescription"); description.setWordWrap(False)
        message_area.addWidget(message); message_area.addWidget(description); message_row.addWidget(check); message_row.addLayout(message_area); message_row.addStretch(); layout.addLayout(message_row)
        result_row=QHBoxLayout(); result_row.setSpacing(10)
        result_row.addWidget(self.create_complete_info_box("적용 규칙","100 / 100개")); result_row.addWidget(self.create_complete_info_box("발견 Issues","14개")); result_row.addWidget(self.create_complete_info_box("소요 시간","2분 18초")); result_row.addWidget(self.create_complete_info_box("검사 파일","18개"))
        result_button=QPushButton("검사 결과 보기 →"); result_button.setObjectName("inspectionResultButton"); result_button.setFixedSize(126,70); result_button.setCursor(Qt.PointingHandCursor); result_button.clicked.connect(self.inspection_result_requested.emit); result_row.addWidget(result_button); layout.addLayout(result_row)
        note=QLabel("※ 완료된 결과는 해당 Project의 Inspection History에 자동으로 저장됩니다."); note.setObjectName("inspectionCompleteNote"); layout.addWidget(note); return card

    def create_complete_info_box(self,title,value):
        box=QFrame(); box.setObjectName("inspectionCompleteInfoBox"); box.setFixedHeight(70); layout=QVBoxLayout(box); layout.setContentsMargins(12,9,12,9); layout.setSpacing(5)
        title_label=QLabel(title); title_label.setObjectName("inspectionCompleteInfoTitle"); value_label=QLabel(value); value_label.setObjectName("inspectionCompleteInfoValue"); layout.addWidget(title_label); layout.addWidget(value_label); layout.addStretch(); return box

    def show_progress(self):
        self.demo_timer.stop(); self.summary_card.hide(); self.complete_card.hide(); self.progress_card.show(); self.demo_timer.start(2500)
    def show_complete(self): self.progress_card.hide(); self.summary_card.hide(); self.complete_card.show()
    def cancel_progress(self): self.demo_timer.stop(); self.progress_card.hide(); self.complete_card.hide(); self.summary_card.show()
    def create_card(self): card=QFrame(); card.setObjectName("inspectionCard"); return card
    def section_title(self,text): label=QLabel(text); label.setObjectName("inspectionSectionTitle"); return label

    def create_rule_row(self,icon,name,count,description,open_dialog=False):
        row=QFrame(); row.setObjectName("inspectionRuleRow"); row.setFixedHeight(37); layout=QHBoxLayout(row); layout.setContentsMargins(10,3,8,3); layout.setSpacing(9)
        checked=QLabel("✓"); checked.setObjectName("inspectionCheck"); checked.setAlignment(Qt.AlignCenter); checked.setFixedSize(20,20)
        icon_label=QLabel(icon); icon_label.setObjectName("inspectionRuleIcon"); icon_label.setFixedWidth(28); name_label=QLabel(name); name_label.setObjectName("inspectionRuleName"); name_label.setFixedWidth(145); count_label=QLabel(count); count_label.setObjectName("inspectionRuleCount"); count_label.setFixedWidth(95); desc_label=QLabel(description); desc_label.setObjectName("inspectionRuleDescription")
        view=QPushButton("보기"); view.setObjectName("inspectionViewButton"); view.setFixedSize(58,27)
        self._rule_text_widgets.append((name_label, count_label, desc_label, view))
        if open_dialog: view.clicked.connect(self.open_security_rules)
        layout.addWidget(checked); layout.addWidget(icon_label); layout.addWidget(name_label); layout.addWidget(count_label); layout.addWidget(desc_label,1); layout.addWidget(view); return row

    def create_summary_box(self,icon,title,value,detail):
        box=QFrame(); box.setObjectName("inspectionSummaryBox"); box.setFixedHeight(72); layout=QHBoxLayout(box); layout.setContentsMargins(10,7,10,7)
        icon_label=QLabel(icon); icon_label.setObjectName("inspectionSummaryIcon"); icon_label.setFixedWidth(28); text=QVBoxLayout(); text.setSpacing(1)
        title_label=QLabel(title); title_label.setObjectName("inspectionSummaryTitle"); value_label=QLabel(value); value_label.setObjectName("inspectionSummaryValue"); detail_label=QLabel(detail); detail_label.setObjectName("inspectionSummaryDetail")
        text.addWidget(title_label); text.addWidget(value_label); text.addWidget(detail_label); layout.addWidget(icon_label); layout.addLayout(text,1); return box

    def open_security_rules(self): InspectionRulesDialog(self).exec()

    def check_duplicate_project(self):
        name = self.project_name.text().strip()

        if not name:
            self.duplicate_warning.setText(
                "프로젝트명을 입력하면 기존 프로젝트 여부를 확인합니다."
            )
            self.duplicate_button.hide()
            return

        existing_project = get_project_by_name(name)

        if existing_project:
            self.duplicate_warning.setText(
                "⚠ 동일한 이름의 프로젝트가 있습니다."
            )
            self.duplicate_button.show()
        else:
            self.duplicate_warning.setText(
                "✓ 사용 가능한 프로젝트명입니다."
            )
            self.duplicate_button.hide()

    def open_existing_projects(self):
        name = self.project_name.text().strip()
        project = get_project_by_name(name)

        if project is None:
            return

        latest_inspection = get_latest_inspection(project["id"])

        if latest_inspection:
            inspected_at = latest_inspection.get("inspected_at", "")
            date = inspected_at[:10].replace("-", ".") if inspected_at else "-"
        else:
            date = "-"

        modal_project = {
            "id": project["id"],
            "name": project["name"],
            "department": project.get("department") or "-",
            "type": project.get("project_type") or "-",
            "date": date,
        }

        dialog = ExistingProjectDialog(
            self,
            projects=[modal_project]
        )
        dialog.project_selected.connect(
            self.existing_project_selected.emit
        )
        dialog.exec()

    def apply_rule_text_theme(self, is_dark):
        """Set rule-row text directly so later/global QSS cannot wash it out."""
        if is_dark:
            styles = (
                "color:#f1f5f9; font-size:12px; font-weight:700;",
                "color:#cbd5e1; font-size:11px; font-weight:600;",
                "color:#cbd5e1; font-size:11px; font-weight:500;",
                "QPushButton#inspectionViewButton { color:#f1f5f9; background:#10161c; border:1px solid #475569; border-radius:6px; font-size:11px; font-weight:600; } QPushButton#inspectionViewButton:hover { background:#27465e; border-color:#6f91a9; }"
            )
        else:
            styles = (
                "color:#0f172a; font-size:12px; font-weight:700;",
                "color:#334155; font-size:11px; font-weight:600;",
                "color:#475569; font-size:11px; font-weight:500;",
                "QPushButton#inspectionViewButton { color:#0f172a; background:#ffffff; border:1px solid #94a3b8; border-radius:6px; font-size:11px; font-weight:600; } QPushButton#inspectionViewButton:hover { background:#e0eaf2; border-color:#7f9bad; }"
            )
        # Rule UI patches can replace/refresh row widgets after __init__, so the
        # cached list is not a reliable source of the currently visible controls.
        # Theme the live widgets in the page every time the mode changes.
        for name_label in self.findChildren(QLabel, "inspectionRuleName"):
            name_label.setStyleSheet(styles[0])
        for count_label in self.findChildren(QLabel, "inspectionRuleCount"):
            count_label.setStyleSheet(styles[1])
        for desc_label in self.findChildren(QLabel, "inspectionRuleDescription"):
            desc_label.setStyleSheet(styles[2])
        for view in self.findChildren(QPushButton, "inspectionViewButton"):
            view.setStyleSheet(styles[3])

    def inspection_style(self):
        return """
        #inspectionContent, #inspectionScroll { background:#09090b; border:none; }
        #inspectionTitle { color:#ffffff; font-size:25px; font-weight:700; }
        #inspectionDescription { color:#cbd5e1; font-size:11px; }
        #inspectionHelpButton, #inspectionSmallButton, #inspectionViewButton { color:#e2e8f0; background:#10161c; border:1px solid #334155; border-radius:6px; font-size:9px; }
        #inspectionCard { background:#10161c; border:1px solid #293747; border-radius:8px; }
        #inspectionSectionTitle { color:#f8fafc; font-size:13px; font-weight:700; }
        #inspectionFieldLabel { color:#cbd5e1; font-size:9px; }
        #inspectionInput { color:#e5e7eb; background:#0c141c; border:1px solid #334155; border-radius:5px; padding:0 10px; font-size:10px; }
        QComboBox#inspectionCombo { color:#e5e7eb; background:#0c141c; border:1px solid #557187; border-radius:7px; padding:0 10px; font-size:10px; font-weight:600; }
        QComboBox#inspectionCombo::drop-down { subcontrol-origin:padding; subcontrol-position:top right; width:30px; border-left:1px solid #405a6e; border-top-right-radius:7px; border-bottom-right-radius:7px; background:#132433; }
        QComboBox#inspectionCombo::down-arrow { width:9px; height:9px; }
        QComboBox#inspectionCombo::drop-down:hover { background:#23445b; }
        #inspectionDuplicate { color:#f59e0b; font-size:8px; }
        #inspectionDuplicateButton { color:#f59e0b; background:transparent; border:none; padding:0; font-size:8px; font-weight:600; text-decoration:underline; }
        #inspectionDuplicateButton:hover { color:#fbbf24; }
        #inspectionUploadBox { background:#0d1721; border:1px dashed #52667b; border-radius:6px; }
        #inspectionUploadText { color:#cbd5e1; font-size:10px; }
        #inspectionFileButton { color:white; background:#142e52; border:1px solid #3b82f6; border-radius:6px; font-size:10px; }
        #inspectionFileCount { color:#e5e7eb; font-size:10px; }
        #inspectionFileTable { background:#0d1721; border:1px solid #263747; border-radius:6px; }
        #inspectionFileRow { border-bottom:1px solid #223140; }
        #inspectionTableText { color:#e5e7eb; font-size:8px; }
        #inspectionTableMuted { color:#94a3b8; font-size:8px; }
        #inspectionBlueNote { color:#3b82f6; font-size:8px; }
        #inspectionRuleRow { background:#0d1721; border:1px solid #263747; border-radius:5px; }
        #inspectionCheck { color:white; background:#0866f5; border-radius:4px; font-size:12px; font-weight:700; }
        #inspectionRuleIcon { color:#60a5fa; font-size:13px; }
        #inspectionRuleName { color:#f1f5f9; font-size:10px; font-weight:600; }
        #inspectionRuleCount, #inspectionRuleDescription { color:#aebaca; font-size:9px; }
        #inspectionSummaryBox { background:#0d1721; border:1px solid #293747; border-radius:6px; }
        #inspectionSummaryIcon { color:#3b82f6; font-size:17px; }
        #inspectionSummaryTitle { color:#cbd5e1; font-size:9px; }
        #inspectionSummaryValue { color:#ffffff; font-size:14px; font-weight:600; }
        #inspectionSummaryDetail { color:#94a3b8; font-size:8px; }
        #inspectionStartButton { color:white; background:#0866f5; border:none; border-radius:6px; font-size:15px; font-weight:600; }
        #inspectionStartButton:hover { background:#1672ff; }
        #inspectionInfoBox { background:#0a121a; border:1px solid #263747; border-radius:6px; }
        #inspectionInfoTitle { color:#60a5fa; font-size:9px; }
        #inspectionInfoText { color:#94a3b8; font-size:8px; }
        #inspectionCompleteCheck { color:#d1fae5; background:#168653; border-radius:16px; font-size:20px; font-weight:700; }
        #inspectionCompleteMessage { color:#f8fafc; font-size:14px; font-weight:600; }
        #inspectionCompleteDescription { color:#94a3b8; font-size:9px; }
        #inspectionCompleteInfoBox { background:#0d1721; border:1px solid #293747; border-radius:6px; }
        #inspectionCompleteInfoTitle { color:#94a3b8; font-size:9px; }
        #inspectionCompleteInfoValue { color:#f8fafc; font-size:14px; font-weight:500; }
        #inspectionResultButton { color:#ffffff; background:#2f6fed; border:none; border-radius:7px; font-size:12px; font-weight:600; text-align:center; padding:0; }
        #inspectionResultButton:hover { background:#3b82f6; }
        #inspectionCompleteNote { color:#64748b; font-size:8px; }
        #inspectionProgressDescription { color:#94a3b8; font-size:10px; }
        #inspectionProgressPercent { color:#5b8cff; font-size:27px; font-weight:500; }
        QProgressBar#inspectionProgressBar { background:#263747; border:none; border-radius:9px; }
        QProgressBar#inspectionProgressBar::chunk { background:#3478f6; border-radius:9px; }
        #inspectionCancelButton { color:#ef6b6b; background:#10161c; border:1px solid #b94a4a; border-radius:7px; font-size:10px; }
        #inspectionCancelButton:hover { background:#211316; }
        #inspectionProgressInfoBox { background:#0d1721; border:1px solid #293747; border-radius:7px; }
        #inspectionProgressInfoTitle { color:#94a3b8; font-size:9px; }
        #inspectionProgressInfoValue { color:#f8fafc; font-size:11px; }
        """