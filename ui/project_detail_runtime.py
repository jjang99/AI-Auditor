from collections import Counter
import re
from datetime import datetime

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton, QScrollArea, QVBoxLayout, QWidget

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


def _format_detail_text(value):
    """Improve long issue evidence readability without changing its meaning."""
    text = str(value or "-").strip()
    text = re.sub(r"\s*\|\s*", "\n", text)
    text = re.sub(r"(?<!\n)(근거:|위반사항:|위험:|권고:)", r"\n\1", text)
    text = re.sub(r"(?<=[.!?])\s+(?=[가-힣A-Za-z0-9'\"])", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
            row = self.create_issue_row(
                issue["severity"], issue["rule_code"], issue["title"], issue["status"]
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

        self.add_detail_section(layout, "제목", issue["title"] or "-")
        self.add_detail_section(layout, "설명", _format_detail_text(issue["description"]))
        self.add_detail_section(layout, "근거", _format_detail_text(issue["evidence"]))
        self.add_detail_section(layout, "영향", issue["impact"] or "분석 예정")

        ai_title = QLabel("AI 권고")
        ai_title.setObjectName("detailTextLabel")
        layout.addWidget(ai_title)
        ai_box = QFrame()
        ai_box.setObjectName("detailAIBox")
        ai_layout = QHBoxLayout(ai_box)
        ai_layout.setContentsMargins(10, 9, 10, 9)
        ai_text = QLabel(issue["ai_recommendation"] or "AI 권고는 후속 AI 분석 단계에서 제공됩니다.")
        ai_text.setObjectName("detailAIText")
        ai_text.setWordWrap(True)
        ai_layout.addWidget(ai_text)
        layout.addWidget(ai_box)

        category = QLabel(f"카테고리    {issue['category'] or '-'}")
        category.setObjectName("detailTagText")
        rule = QLabel(f"발견 기준    {issue['rule_code']}")
        rule.setObjectName("detailTagText")
        layout.addWidget(category)
        layout.addWidget(rule)
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
