from collections import Counter
import re
from datetime import datetime

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.database.repositories.inspection_repository import (
    get_inspection_history,
    get_issues_for_inspection,
    get_latest_inspection,
)
from app.database.repositories.project_repository import get_project_by_id


def _format_datetime(value):
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value).strftime("%Y.%m.%d %H:%M")
    except ValueError:
        return value.replace("T", " ")


def _display_grade(score):
    """Frozen UI grade standard shared by Projects and Project Detail."""
    if score is None:
        return "-"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "E"


def _grade_color(grade):
    return {
        "A": "#22c55e",
        "B": "#22c55e",
        "C": "#fbbf24",
        "D": "#f97316",
        "E": "#ef4444",
    }.get(grade, "#94a3b8")


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout(child_layout)


def _level_badge(value, role):
    label = QLabel(str(value or "-"))
    label.setObjectName(f"detailRiskBadge_{str(value or 'none').lower()}")
    label.setProperty("riskRole", role)
    label.setAlignment(Qt.AlignCenter)
    label.setFixedHeight(24)
    label.setMinimumWidth(56)
    return label


def _result_card(title, value, role, subtext=""):
    card = QFrame()
    card.setObjectName("detailRiskCard")
    box = QVBoxLayout(card)
    box.setContentsMargins(6, 7, 6, 7)
    box.setSpacing(5)
    heading = QLabel(title)
    heading.setObjectName("detailRiskCardTitle")
    heading.setAlignment(Qt.AlignCenter)
    badge = _level_badge(value, role)
    box.addWidget(heading)
    box.addWidget(badge)
    if subtext:
        sub = QLabel(subtext)
        sub.setObjectName("detailRiskSubtext")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        box.addWidget(sub)
    return card


def _section_title_with_help(title, callback):
    row = QHBoxLayout()
    row.setSpacing(5)
    label = QLabel(title)
    label.setObjectName("detailTextLabel")
    help_button = QPushButton("?")
    help_button.setObjectName("detailHelpButton")
    help_button.setFixedSize(16, 16)
    help_button.setCursor(Qt.PointingHandCursor)
    help_button.clicked.connect(callback)
    row.addWidget(label)
    row.addWidget(help_button)
    row.addStretch()
    return row


def _help_dialog_header(layout, icon, title, subtitle):
    head = QFrame()
    head.setObjectName("detailHelpHero")
    row = QHBoxLayout(head)
    row.setContentsMargins(12, 10, 12, 10)
    row.setSpacing(10)
    icon_label = QLabel(icon)
    icon_label.setObjectName("detailHelpHeroIcon")
    icon_label.setFixedSize(34, 34)
    icon_label.setAlignment(Qt.AlignCenter)
    text_box = QVBoxLayout()
    text_box.setSpacing(1)
    title_label = QLabel(title)
    title_label.setObjectName("detailHelpTitle")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("detailHelpSubtitle")
    subtitle_label.setWordWrap(True)
    text_box.addWidget(title_label)
    text_box.addWidget(subtitle_label)
    row.addWidget(icon_label)
    row.addLayout(text_box, 1)
    layout.addWidget(head)


def _help_section(layout, number, title, rows, audit=False):
    head = QHBoxLayout()
    head.setSpacing(7)
    number_label = QLabel(str(number))
    number_label.setObjectName("detailHelpSectionNumber")
    number_label.setFixedSize(22, 22)
    number_label.setAlignment(Qt.AlignCenter)
    title_label = QLabel(title)
    title_label.setObjectName("detailHelpSection")
    head.addWidget(number_label)
    head.addWidget(title_label)
    head.addStretch()
    layout.addLayout(head)

    group = QFrame()
    group.setObjectName("detailHelpGroup")
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(7, 7, 7, 7)
    group_layout.setSpacing(5)
    for value, desc in rows:
        item = QFrame()
        item.setObjectName("detailHelpItem")
        row = QHBoxLayout(item)
        row.setContentsMargins(9, 7, 9, 7)
        row.setSpacing(10)
        if audit:
            badge = QLabel(value)
            badge.setObjectName("detailAuditHelpBadge")
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(56, 24)
        else:
            badge = _level_badge(value, "help")
        text = QLabel(desc)
        text.setObjectName("detailHelpText")
        text.setWordWrap(True)
        row.addWidget(badge)
        row.addWidget(text, 1)
        group_layout.addWidget(item)
    layout.addWidget(group)


def _show_risk_help(parent):
    dialog = QDialog(parent)
    dialog.setObjectName("detailHelpDialog")
    dialog.setWindowTitle("위험도 기준")
    dialog.setModal(True)
    dialog.setFixedWidth(500)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(16, 14, 16, 16)
    layout.setSpacing(10)

    _help_dialog_header(
        layout, "?", "위험도 기준",
        "Impact와 Likelihood를 각각 판정한 뒤 Matrix로 최종 Severity를 결정합니다.",
    )
    _help_section(layout, 1, "Impact (영향도)", (
        ("High", "핵심 기능·업무·보안 또는 중요 검증에 중대한 영향"),
        ("Medium", "품질·관리·검증에 영향이 있으나 범위가 제한적"),
        ("Low", "국소적 문서·표현 수준의 제한적 영향"),
    ))
    _help_section(layout, 2, "Likelihood (발생가능성)", (
        ("High", "영향 현실화 가능성이 높거나 이미 징후가 확인됨"),
        ("Medium", "후속 영향 가능성이 있으나 근거가 부분적"),
        ("Low", "현재 징후가 없고 추가 조건이 필요함"),
    ))

    head = QHBoxLayout()
    head.setSpacing(7)
    num = QLabel("3"); num.setObjectName("detailHelpSectionNumber"); num.setFixedSize(22,22); num.setAlignment(Qt.AlignCenter)
    title = QLabel("Severity (위험도)"); title.setObjectName("detailHelpSection")
    head.addWidget(num); head.addWidget(title); head.addStretch(); layout.addLayout(head)
    matrix_card = QFrame(); matrix_card.setObjectName("detailHelpMatrixCard")
    matrix_layout = QVBoxLayout(matrix_card); matrix_layout.setContentsMargins(10,9,10,10); matrix_layout.setSpacing(7)
    note = QLabel("Impact × Likelihood Matrix"); note.setObjectName("detailHelpMatrixNote"); matrix_layout.addWidget(note)
    grid = QGridLayout(); grid.setSpacing(4)
    matrix = [
        ("Impact × Likelihood", "Low", "Medium", "High"),
        ("High", "Medium", "High", "Critical"),
        ("Medium", "Low", "Medium", "High"),
        ("Low", "Low", "Low", "Medium"),
    ]
    for r, values in enumerate(matrix):
        for col, value in enumerate(values):
            cell = QLabel(value)
            cell.setObjectName("detailMatrixHeader" if r == 0 or col == 0 else f"detailMatrix_{value.lower()}")
            cell.setAlignment(Qt.AlignCenter)
            cell.setMinimumHeight(30)
            grid.addWidget(cell, r, col)
    matrix_layout.addLayout(grid)
    layout.addWidget(matrix_card)
    dialog.exec()


def _show_audit_help(parent):
    dialog = QDialog(parent)
    dialog.setObjectName("detailHelpDialog")
    dialog.setWindowTitle("감리 개선판정 기준")
    dialog.setModal(True)
    dialog.setFixedWidth(500)
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(16, 14, 16, 16)
    layout.setSpacing(10)

    _help_dialog_header(
        layout, "✓", "감리 개선판정 기준",
        "Severity와 별개로 감리 대응 관점에서 개선 유형·시점·중요 여부를 판단합니다.",
    )
    _help_section(layout, 1, "개선권고유형", (
        ("필수", "감리 지적 가능성이 높아 반드시 개선 필요"),
        ("협의", "감리 검토 후 개선 여부 협의 필요"),
        ("권고", "품질 향상을 위해 개선 권고"),
    ), audit=True)
    _help_section(layout, 2, "개선시점", (
        ("단기", "사업 기간 내 조치 권장"),
        ("장기", "유지보수 등 후속 단계에서 조치"),
    ), audit=True)
    _help_section(layout, 3, "중요 여부", (
        ("O", "사업·업무에 중요한 영향이 있는 경우"),
        ("-", "상대적으로 영향이 낮은 경우"),
    ), audit=True)
    dialog.exec()


def _detail_section_card(title, body, icon):
    card = QFrame()
    card.setObjectName("detailSectionCard")
    row = QHBoxLayout(card)
    row.setContentsMargins(9, 8, 9, 8)
    row.setSpacing(8)
    icon_label = QLabel(icon)
    icon_label.setObjectName("detailSectionIcon")
    icon_label.setFixedSize(18, 18)
    icon_label.setAlignment(Qt.AlignCenter)
    text_box = QVBoxLayout()
    text_box.setSpacing(3)
    title_label = QLabel(title)
    title_label.setObjectName("detailSectionTitle")
    body_label = QLabel(str(body or "-"))
    body_label.setObjectName("detailTextBody")
    body_label.setWordWrap(True)
    body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    text_box.addWidget(title_label)
    text_box.addWidget(body_label)
    row.addWidget(icon_label, 0, Qt.AlignTop)
    row.addLayout(text_box, 1)
    return card


def _numbered_section_title(number, title, icon, help_callback=None):
    """Approved detail header: icon + title only. number kept for call compatibility."""
    row = QHBoxLayout()
    row.setSpacing(7)
    icon_label = QLabel(icon)
    icon_label.setObjectName("detailSectionHeaderIcon")
    icon_label.setFixedSize(18, 18)
    icon_label.setAlignment(Qt.AlignCenter)
    label = QLabel(title)
    label.setObjectName("detailSectionHeaderTitle")
    row.addWidget(icon_label)
    row.addWidget(label)
    if help_callback is not None:
        help_button = QPushButton("?")
        help_button.setObjectName("detailHelpButton")
        help_button.setFixedSize(16, 16)
        help_button.setCursor(Qt.PointingHandCursor)
        help_button.clicked.connect(help_callback)
        row.addWidget(help_button)
    row.addStretch()
    return row


def _reason_item(title, body, icon):
    item = QFrame()
    item.setObjectName("detailReasonItem")
    box = QVBoxLayout(item)
    box.setContentsMargins(9, 7, 9, 8)
    box.setSpacing(4)

    header = QHBoxLayout()
    header.setSpacing(6)
    icon_label = QLabel(icon)
    icon_label.setObjectName("detailReasonIcon")
    icon_label.setFixedSize(16, 16)
    icon_label.setAlignment(Qt.AlignCenter)
    title_label = QLabel(title)
    title_label.setObjectName("detailReasonTitle")
    header.addWidget(icon_label)
    header.addWidget(title_label)
    header.addStretch()

    body_label = QLabel(str(body or "-"))
    body_label.setObjectName("detailReasonBody")
    body_label.setWordWrap(True)
    body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    box.addLayout(header)
    box.addWidget(body_label)
    return item


def _format_detail_text(value):
    """Format stored evidence into short, readable audit paragraphs."""
    text = str(value or "-").strip()
    text = re.sub(r":0(?=\s*(?:\||$))", "", text)
    text = re.sub(r"\s*\|\s*", "\n", text)

    # Put semantic labels on their own line and visually separate sections.
    text = re.sub(
        r"(?i)\s*(체크포인트\s+[A-Z]+-\d+\s+위반)\s*:\s*",
        r"\1:\n",
        text,
    )
    text = re.sub(
        r"(?<!^)(?<!\n)(위반사항|위반 내용|근거|판단|사유|권고)\s*:\s*",
        r"\n\n\1:\n",
        text,
    )
    text = re.sub(r"(?<=[.!?])\s+(?=[가-힣A-Za-z0-9'\"])", "\n\n", text)

    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        if "\\" in line and len(line) > 34:
            line = line.replace("\\", "\\\u200b")
        lines.append(line)

    return "\n".join(lines).strip()


def _summarize_evidence(value):
    """Keep the finding understandable at a glance without changing DB evidence."""
    text = _format_detail_text(value)
    if text == "-":
        return text

    kept = []
    char_count = 0
    for block in re.split(r"\n\s*\n|\n", text):
        block = block.strip(" \t•-")
        if not block or "\\" in block:
            continue
        if block in kept:
            continue
        # Keep semantic headings and the most useful first evidence statements.
        if char_count + len(block) > 420 and kept:
            break
        kept.append(block)
        char_count += len(block)
        if len(kept) >= 6:
            break

    return "\n\n".join(kept) if kept else "-"


def apply_project_detail_runtime(ProjectDetailPage):
    original_init = ProjectDetailPage.__init__

    def runtime_init(self):
        original_init(self)
        self.current_project_id = None
        self.current_inspection_id = None
        self._issue_row_data = {}
        self._current_issues = []
        self.issue_sort_key = "severity"

    def load_project(self, project_id, inspection_id=None):
        # Sorting is a view preference for the currently opened detail only.
        # Reset it whenever another Project Detail is opened.
        self.issue_sort_key = "severity"
        sort_combo = self.findChild(QComboBox, "detailSortCombo")
        if sort_combo is not None:
            sort_combo.blockSignals(True)
            sort_combo.setCurrentIndex(0)
            sort_combo.blockSignals(False)

        project = get_project_by_id(project_id)
        if project is None:
            return

        latest = get_latest_inspection(project_id)
        if inspection_id is not None:
            history = get_inspection_history(project_id, 100)
            latest = next((item for item in history if item["id"] == inspection_id), latest)
        if latest is None:
            return

        self.current_project_id = project_id
        self.current_inspection_id = latest["id"]
        issues = get_issues_for_inspection(latest["id"])
        history = get_inspection_history(project_id, 3)

        breadcrumb = self.findChild(QLabel, "detailBreadcrumb")
        if breadcrumb:
            breadcrumb.setText(f"Projects   ›   {project['name']}")

        project_name = self.findChild(QLabel, "detailProjectName")
        if project_name:
            project_name.setText(project["name"])

        # Final UI refinements rename the original detailDate label to
        # detailLastInspectionDate.  Support both names so the runtime binding
        # remains compatible with the frozen UI and older layouts.
        date_label = self.findChild(QLabel, "detailLastInspectionDate")
        if date_label is None:
            date_label = self.findChild(QLabel, "detailDate")
        if date_label:
            date_label.setText(f"▣   {_format_datetime(latest['inspected_at'])}")

        score_text = "-" if latest["score"] is None else str(latest["score"])
        grade_text = _display_grade(latest["score"])
        total_issues = len(issues)
        resolved = sum(1 for issue in issues if issue["status"] == "조치완료")
        resolved_percent = int(round((resolved / total_issues) * 100)) if total_issues else 0

        summary_score = self.findChild(QLabel, "detailSummaryScore")
        summary_grade = self.findChild(QLabel, "detailSummaryGrade")
        if summary_score:
            summary_score.setText(score_text)
        if summary_grade:
            summary_grade.setText(grade_text)
            summary_grade.setStyleSheet(
                f"color: {_grade_color(grade_text)}; font-size: 35px; font-weight: 700;"
            )

        stat_cards = self.findChildren(QFrame, "detailStatCard")
        if len(stat_cards) >= 4:
            values = [score_text, str(total_issues), grade_text]
            for card, value in zip(stat_cards[:3], values):
                label = card.findChild(QLabel, "detailStatValue")
                if label:
                    label.setText(value)
            resolved_value = stat_cards[3].findChild(QLabel, "detailResolvedValue")
            progress = stat_cards[3].findChild(QProgressBar, "detailProgress")
            percent = stat_cards[3].findChild(QLabel, "detailSmallText")
            if resolved_value:
                resolved_value.setText(f"{resolved} / {total_issues}")
            if progress:
                progress.setValue(resolved_percent)
            if percent:
                percent.setText(f"{resolved_percent}%")

        self._runtime_update_distribution(issues)
        self._runtime_update_history(history)
        self._runtime_update_issues(issues)
        self._runtime_update_issue_detail(issues[0] if issues else None)

    def _runtime_update_distribution(self, issues):
        card = next(iter(self.findChildren(QFrame, "detailBodyCard")), None)
        if card is None:
            return
        counts = Counter(issue["severity"] for issue in issues)
        level_keys = [("Critical", "critical"), ("High", "high"), ("Medium", "medium"), ("Low", "low")]
        max_count = max([counts.get(level, 0) for level, _ in level_keys] + [1])
        for level, key in level_keys:
            bars = card.findChildren(QProgressBar, f"detailDistribution_{key}")
            if bars:
                bars[0].setRange(0, max_count)
                bars[0].setValue(counts.get(level, 0))
        small_labels = card.findChildren(QLabel, "detailSmallText")
        numeric_labels = [label for label in small_labels if label.width() <= 20]
        for label, (level, _) in zip(numeric_labels, level_keys):
            label.setText(str(counts.get(level, 0)))

    def _runtime_update_history(self, history):
        cards = self.findChildren(QFrame, "detailBodyCard")
        if len(cards) < 2:
            return
        card = cards[1]
        layout = card.layout()
        if layout is None:
            return
        button = card.findChild(QPushButton, "detailHistoryButton")
        if button is not None:
            layout.removeWidget(button)
        while layout.count() > 1:
            item = layout.takeAt(1)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None and widget is not button:
                widget.deleteLater()
            elif child_layout is not None:
                _clear_layout(child_layout)
        for index, item in enumerate(history):
            row = QHBoxLayout()
            row.setSpacing(7)
            marker = QLabel("●")
            marker.setObjectName("detailHistoryActive" if index == 0 else "detailHistoryInactive")
            marker.setFixedWidth(12)
            text = QVBoxLayout()
            text.setSpacing(1)
            date_label = QLabel(_format_datetime(item["inspected_at"]))
            date_label.setObjectName("detailHistoryDate")
            type_label = QLabel(f"{item['inspection_type']} · {item['rule_count']} Rules")
            type_label.setObjectName("detailHistoryType")
            text.addWidget(date_label)
            text.addWidget(type_label)
            row.addWidget(marker, 0, Qt.AlignTop)
            row.addLayout(text, 1)
            layout.addLayout(row)
        layout.addStretch()
        if button is not None:
            layout.addWidget(button)

    def _runtime_update_issues(self, issues):
        self._current_issues = list(issues)
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sort_key = getattr(self, "issue_sort_key", "severity")
        if sort_key == "status":
            issues = sorted(issues, key=lambda issue: (issue.get("status") or "", severity_order.get(issue.get("severity"), 9), issue.get("rule_code") or ""))
        elif sort_key == "rule":
            issues = sorted(issues, key=lambda issue: (issue.get("rule_code") or "", severity_order.get(issue.get("severity"), 9)))
        else:
            issues = sorted(issues, key=lambda issue: (severity_order.get(issue.get("severity"), 9), issue.get("rule_code") or ""))

        cards = self.findChildren(QFrame, "detailBodyCard")
        if len(cards) < 3:
            return
        card = cards[2]
        title = card.findChild(QLabel, "detailBodyTitle")
        if title:
            title.setText(f"Issues ({len(issues)})")
        container = card.findChild(QWidget, "detailIssueContainer")
        if container is None or container.layout() is None:
            return
        layout = container.layout()
        _clear_layout(layout)
        if not issues:
            empty = QLabel("발견된 Issue가 없습니다.")
            empty.setObjectName("detailMuted")
            empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty)
            layout.addStretch()
            return
        for index, issue in enumerate(issues):
            display_title = str(issue["title"] or "").strip()
            rule_code = str(issue["rule_code"] or "").strip()
            if rule_code:
                display_title = re.sub(
                    rf"^(?:{re.escape(rule_code)}[\s:·\-]*)+",
                    "",
                    display_title,
                    flags=re.IGNORECASE,
                ).strip() or display_title
            row = self.create_issue_row(
                issue["severity"], issue["rule_code"], display_title, issue["status"]
            )
            # Runtime-created rows are added after the initial UI refinement pass,
            # so apply the same final sizing here as the frozen Project Detail UI.
            row.setFixedHeight(78)
            badge = next(
                (label for label in row.findChildren(QLabel)
                 if label.objectName().startswith("detailBadge_")),
                None,
            )
            if badge:
                badge.setFixedSize(54, 20)
                badge.setAlignment(Qt.AlignCenter)
            status = next(
                (label for label in row.findChildren(QLabel)
                 if label.objectName() in ("detailStatusResolved", "detailStatusOpen")),
                None,
            )
            if status:
                status.setFixedWidth(38)
            description = row.findChild(QLabel, "detailIssueDescription")
            if description:
                description.setWordWrap(True)
                description.setMinimumHeight(38)
                description.setMinimumWidth(0)
            row.setCursor(Qt.PointingHandCursor)
            row.setProperty("issueSelectable", True)
            self._issue_row_data[row] = issue
            row.installEventFilter(self)
            layout.addWidget(row)
        layout.addStretch()

    def event_filter(self, watched, event):
        if watched.property("issueSelectable") and event.type() == QEvent.MouseButtonRelease:
            issue = self._issue_row_data.get(watched)
            if issue is not None:
                self._runtime_update_issue_detail(issue)
                return True
        return False

    def _runtime_update_issue_detail(self, issue):
        cards = self.findChildren(QFrame, "detailBodyCard")
        if len(cards) < 4:
            return
        card = cards[3]

        # Project Detail refinements create one persistent scroll area below the
        # fixed "Issue Detail" title.  Keep that structure when runtime data is
        # refreshed; clearing the card layout here would delete the scroll area.
        scroll = card.findChild(QScrollArea, "detailContentScroll")
        content = scroll.widget() if scroll is not None else None
        layout = content.layout() if content is not None else None
        if layout is None:
            return

        _clear_layout(layout)

        if issue is None:
            empty = QLabel("선택할 Issue가 없습니다.\n이번 검사에서는 문제가 발견되지 않았습니다.")
            empty.setObjectName("detailTextBody")
            empty.setWordWrap(True)
            layout.addWidget(empty)
            layout.addStretch()
            return

        header = QHBoxLayout()
        badge = QLabel(issue["severity"])
        badge.setObjectName(f"detailBadge_{issue['severity'].lower()}")
        badge.setFixedWidth(54)
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignCenter)
        code = QLabel(issue["rule_code"])
        code.setObjectName("detailIssueDetailCode")
        status = QLabel(issue["status"])
        status.setObjectName("detailStatusResolved" if issue["status"] == "조치완료" else "detailStatusOpen")
        status.setFixedWidth(48)
        status.setMinimumHeight(24)
        status.setAlignment(Qt.AlignCenter)
        header.addWidget(badge)
        header.addWidget(code)
        header.addStretch()
        header.addWidget(status)
        layout.addLayout(header)

        # Preserve the frozen card layout while presenting the stored result
        # in the Issue Detail fields agreed for the severity/audit design.
        evidence_text = _format_detail_text(issue["evidence"])
        source_lines = [
            line.strip()
            for line in evidence_text.splitlines()
            if line.strip() and (
                "\\" in line
                or re.search(r"(?i)\.(?:hwp|hwpx|docx?|xlsx?|pdf|pptx?)$", line.strip())
                or line.startswith(("[시험 산출물]", "[이전 산출물]", "[현재 산출물]"))
            )
        ]
        finding_lines = [
            line.strip()
            for line in evidence_text.splitlines()
            if line.strip() and line.strip() not in source_lines
        ]

        source_text = "\n".join(source_lines) if source_lines else "-"
        finding_text = _summarize_evidence("\n".join(finding_lines) if finding_lines else evidence_text)

        description_text = _format_detail_text(issue["description"]) if issue["description"] else finding_text

        layout.addLayout(_numbered_section_title(1, "발견 내용", "▤"))
        meta = QFrame()
        meta.setObjectName("detailFindingMeta")
        meta_box = QVBoxLayout(meta)
        meta_box.setContentsMargins(10, 8, 10, 8)
        meta_box.setSpacing(5)
        meta_title = QLabel(f"◆  {issue['title'] or '-'}")
        meta_title.setObjectName("detailFindingMetaTitle")
        meta_file = QLabel(f"▣  {source_text}")
        meta_file.setObjectName("detailFindingMetaFile")
        meta_file.setWordWrap(True)
        meta_box.addWidget(meta_title)
        meta_box.addWidget(meta_file)
        layout.addWidget(meta)
        layout.addWidget(_detail_section_card("체크포인트", description_text, "▤"))

        layout.addLayout(_numbered_section_title(2, "위험도 판정", "◆", lambda: _show_risk_help(self)))
        impact_value = issue["impact"] or "-"
        likelihood_value = issue["likelihood"] or "-"
        severity_value = issue["severity"] or "-"
        severity_formula = f"{impact_value} × {likelihood_value}" if issue["impact"] and issue["likelihood"] else ""
        risk_stack = QVBoxLayout()
        risk_stack.setSpacing(5)
        risk_stack.addWidget(_result_card("Impact", impact_value, "impact"))
        risk_stack.addWidget(_result_card("Likelihood", likelihood_value, "likelihood"))
        risk_stack.addWidget(_result_card("Severity", severity_value, "severity", severity_formula))
        layout.addLayout(risk_stack)

        layout.addLayout(_numbered_section_title(3, "판정 근거", "▥"))
        evidence_summary = finding_text
        reason_box = QFrame()
        reason_box.setObjectName("detailReasonBox")
        reason_layout = QVBoxLayout(reason_box)
        reason_layout.setContentsMargins(7, 7, 7, 7)
        reason_layout.setSpacing(6)
        reason_items = []
        if evidence_summary and evidence_summary != description_text:
            reason_items.append(("검사 근거", evidence_summary, "▣"))
        if issue["impact_reason"]:
            reason_items.append(("Impact 근거", issue["impact_reason"], "↗"))
        if issue["likelihood_reason"]:
            reason_items.append(("Likelihood 근거", issue["likelihood_reason"], "◔"))
        if not reason_items and evidence_summary:
            reason_items.append(("검사 근거", evidence_summary, "▣"))
        for heading, body, icon in reason_items:
            reason_layout.addWidget(_reason_item(heading, body, icon))
        layout.addWidget(reason_box)

        layout.addLayout(_numbered_section_title(4, "감리 개선판정", "✓", lambda: _show_audit_help(self)))
        audit_stack = QVBoxLayout()
        audit_stack.setSpacing(5)
        audit_stack.addWidget(_result_card("개선권고유형", issue["audit_recommendation_type"] or "판정 없음", "audit"))
        audit_stack.addWidget(_result_card("개선시점", issue["audit_improvement_timing"] or "판정 없음", "audit"))
        audit_stack.addWidget(_result_card("중요 여부", issue["audit_important"] or "판정 없음", "audit"))
        layout.addLayout(audit_stack)

        layout.addLayout(_numbered_section_title(5, "기타 정보", "ⓘ"))
        other_grid = QHBoxLayout()
        other_grid.setSpacing(6)
        category_card = QFrame()
        category_card.setObjectName("detailOtherInfo")
        category_box = QVBoxLayout(category_card)
        category_box.setContentsMargins(9, 7, 9, 7)
        category_box.setSpacing(3)
        category_title = QLabel("카테고리")
        category_title.setObjectName("detailOtherLabel")
        category_value = QLabel(issue["category"] or "-")
        category_value.setObjectName("detailOtherText")
        category_value.setWordWrap(True)
        category_box.addWidget(category_title)
        category_box.addWidget(category_value)
        rule_card = QFrame()
        rule_card.setObjectName("detailOtherInfo")
        rule_box = QVBoxLayout(rule_card)
        rule_box.setContentsMargins(9, 7, 9, 7)
        rule_box.setSpacing(3)
        rule_title = QLabel("발견 기준")
        rule_title.setObjectName("detailOtherLabel")
        rule_value = QLabel(issue["rule_code"])
        rule_value.setObjectName("detailOtherText")
        rule_box.addWidget(rule_title)
        rule_box.addWidget(rule_value)
        other_grid.addWidget(category_card, 1)
        other_grid.addWidget(rule_card, 1)
        layout.addLayout(other_grid)

        layout.addStretch()

        # Wrapped labels recalculate their height after real DB text is set.
        # The minimum-size layout then makes QScrollArea expose the full content.
        content.adjustSize()

    ProjectDetailPage.__init__ = runtime_init
    original_event_filter = getattr(ProjectDetailPage, "eventFilter", None)

    def project_detail_event_filter(self, watched, event):
        if event_filter(self, watched, event):
            return True
        if original_event_filter is not None:
            return original_event_filter(self, watched, event)
        return False

    ProjectDetailPage.load_project = load_project
    ProjectDetailPage._runtime_update_distribution = _runtime_update_distribution
    ProjectDetailPage._runtime_update_history = _runtime_update_history
    ProjectDetailPage._runtime_update_issues = _runtime_update_issues
    ProjectDetailPage._runtime_update_issue_detail = _runtime_update_issue_detail
    ProjectDetailPage.eventFilter = project_detail_event_filter
