import os

from PySide6.QtCore import Qt, QRectF, QSize, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.sidebar import Sidebar
from app.database.repositories.project_repository import get_all_projects


# =========================================================
# Score 원형 표시
# =========================================================
class CircularScore(QWidget):
    def __init__(self, score=None, parent=None):
        super().__init__(parent)
        self.score = score
        self.setFixedSize(72, 72)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(6, 6, 60, 60)

        background_pen = QPen(QColor("#334155"), 5)
        background_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(background_pen)
        painter.drawArc(rect, 0, 360 * 16)

        if self.score is not None:
            if self.score >= 80:
                score_color = QColor("#22c55e")
            elif self.score >= 70:
                score_color = QColor("#fbbf24")
            elif self.score >= 60:
                score_color = QColor("#f97316")
            else:
                score_color = QColor("#ef4444")

            score_pen = QPen(score_color, 5)
            score_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(score_pen)
            start_angle = 90 * 16
            span_angle = int(360 * 16 * (self.score / 100))
            painter.drawArc(rect, start_angle, span_angle)

        if self.score is not None:
            painter.setPen(QColor("#ffffff"))
            score_text = str(self.score)
        else:
            painter.setPen(QColor("#94a3b8"))
            score_text = "-"

        font = painter.font()
        font.setPointSize(15)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 14, 72, 28), Qt.AlignCenter, score_text)

        if self.score is not None:
            font.setPointSize(6)
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(QRectF(0, 40, 72, 16), Qt.AlignCenter, "/100")


# =========================================================
# 세로 구분선
# =========================================================
class VerticalSeparator(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("projectSeparator")
        self.setFixedWidth(1)
        self.setFixedHeight(74)


# =========================================================
# Projects Page
# =========================================================
class ProjectsPage(QWidget):
    project_selected = Signal(dict)

    def __init__(self):
        super().__init__()
        self.project_cards = []

        base_path = os.path.dirname(os.path.dirname(__file__))
        self.icon_path = os.path.join(base_path, "assets", "icons")

        page_layout = QHBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Sidebar는 Project Detail과 공통 사용하므로 현재 비율 유지
        self.sidebar = Sidebar("Projects")
        page_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("projectsContent")

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 22, 20, 20)
        main_layout.setSpacing(0)
        page_layout.addWidget(content, 1)

        # =================================================
        # 1. Header
        # =================================================
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_area = QVBoxLayout()
        title_area.setSpacing(5)

        title = QLabel("Projects")
        title.setObjectName("pageTitle")

        description = QLabel(
            "등록된 프로젝트와 최근 AI 검사 결과를 확인하고 관리할 수 있습니다."
        )
        description.setObjectName("pageDescription")

        title_area.addWidget(title)
        title_area.addWidget(description)

        new_project_button = QPushButton("＋  New Project")
        new_project_button.setObjectName("newProjectButton")
        new_project_button.setCursor(Qt.PointingHandCursor)
        new_project_button.setFixedSize(122, 40)

        header_layout.addLayout(title_area)
        header_layout.addStretch()
        header_layout.addWidget(new_project_button, 0, Qt.AlignTop)
        main_layout.addLayout(header_layout)

        # =================================================
        # 2. Search
        # =================================================
        main_layout.addSpacing(17)

        search_row = QHBoxLayout()
        search_row.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("projectSearchInput")
        self.search_input.setPlaceholderText("⌕   Search Projects...")
        self.search_input.setFixedSize(400, 38)
        self.search_input.textChanged.connect(self.filter_projects)

        search_row.addWidget(self.search_input)
        search_row.addStretch()
        main_layout.addLayout(search_row)
        main_layout.addSpacing(14)

        # =================================================
        # 3. 프로젝트 데이터 - DB 기준 유지
        # =================================================
        db_projects = get_all_projects()
        sample_projects = []

        for project in db_projects:
            sample_projects.append(
                {
                    "id": project["id"],
                    "name": project["name"],
                    "department": project["department"] or "-",
                    "date": "",
                    "score": None,
                    "grade": "-",
                    "issues": 0,
                    "resolved": 0,
                    "status": "검사 전",
                }
            )

        # =================================================
        # 4. 프로젝트 카드
        # =================================================
        self.projects_layout = QVBoxLayout()
        self.projects_layout.setSpacing(8)

        for project in sample_projects:
            card = self.create_project_card(project)
            self.projects_layout.addWidget(card)
            self.project_cards.append(
                (card, project["name"].lower(), project["department"].lower())
            )

        main_layout.addLayout(self.projects_layout)
        main_layout.addStretch(1)

        # =================================================
        # 5. Bottom
        # =================================================
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 8, 0, 0)

        total_label = QLabel(f"총 {len(sample_projects)}개 프로젝트")
        total_label.setObjectName("projectTotal")

        previous_button = QPushButton("‹")
        previous_button.setObjectName("paginationButton")
        page_button = QPushButton("1")
        page_button.setObjectName("paginationCurrentButton")
        next_button = QPushButton("›")
        next_button.setObjectName("paginationButton")

        for button in (previous_button, page_button, next_button):
            button.setFixedSize(34, 32)

        bottom_layout.addWidget(total_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(previous_button)
        bottom_layout.addWidget(page_button)
        bottom_layout.addWidget(next_button)
        main_layout.addLayout(bottom_layout)

    # =====================================================
    # 프로젝트 카드
    # =====================================================
    def create_project_card(self, project):
        card = QFrame()
        card.setObjectName("projectCard")
        card.setCursor(Qt.PointingHandCursor)

        # 페이지당 5개 표시 조건을 위해 높이는 유지
        card.setFixedHeight(128)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 11, 10, 11)
        card_layout.setSpacing(10)

        # =================================================
        # 1열 : 프로젝트 정보
        # =================================================
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)

        folder_icon = QLabel()
        project_icon = QIcon(os.path.join(self.icon_path, "project.svg"))
        folder_icon.setPixmap(project_icon.pixmap(QSize(38, 38)))
        folder_icon.setFixedSize(44, 44)
        folder_icon.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setContentsMargins(0, 1, 0, 1)

        project_name = QLabel(project["name"])
        project_name.setObjectName("projectName")

        department = QLabel(project["department"])
        department.setObjectName("projectDepartment")
        department.setMaximumWidth(105)

        inspection_date = QLabel(project["date"])
        inspection_date.setObjectName("projectMeta")

        status = QLabel()
        if project["status"] == "검사 실패":
            status.setText("●  검사 실패")
            status.setObjectName("projectFailedStatus")
        elif project["status"] == "검사 전":
            status.setText("●  검사 전")
            status.setObjectName("projectPendingStatus")
        else:
            status.setText("●  AI 검사 완료")
            status.setObjectName("projectStatus")

        text_layout.addWidget(project_name)
        text_layout.addWidget(department, 0, Qt.AlignLeft)
        text_layout.addWidget(inspection_date)
        text_layout.addWidget(status)

        info_layout.addWidget(folder_icon, 0, Qt.AlignVCenter)
        info_layout.addLayout(text_layout, 1)
        card_layout.addWidget(info_widget, 5)

        card_layout.addWidget(VerticalSeparator(), 0, Qt.AlignVCenter)

        # =================================================
        # 2열 : Score
        # =================================================
        score_widget = QWidget()
        score_layout = QVBoxLayout(score_widget)
        score_layout.setContentsMargins(2, 0, 2, 0)
        score_layout.setAlignment(Qt.AlignCenter)
        score_area = CircularScore(project["score"])
        score_layout.addWidget(score_area, 0, Qt.AlignCenter)
        card_layout.addWidget(score_widget, 0)

        # =================================================
        # 3열 : Grade
        # =================================================
        grade_widget = QWidget()
        grade_widget.setFixedWidth(56)
        grade_layout = QVBoxLayout(grade_widget)
        grade_layout.setContentsMargins(0, 0, 0, 0)
        grade_layout.setSpacing(2)
        grade_layout.setAlignment(Qt.AlignCenter)

        grade = QLabel(project["grade"])
        grade_object_map = {
            "A": "projectGradeA",
            "B": "projectGradeB",
            "C": "projectGradeC",
            "D": "projectGradeD",
            "E": "projectGradeE",
            "-": "projectGradeNone",
        }
        grade.setObjectName(grade_object_map.get(project["grade"], "projectGradeNone"))
        grade.setAlignment(Qt.AlignCenter)

        grade_text_map = {
            "A": "우수",
            "B": "양호",
            "C": "보통",
            "D": "미흡",
            "E": "불량",
            "-": "-",
        }
        grade_text = QLabel(grade_text_map.get(project["grade"], "-"))
        grade_text.setObjectName("projectGradeText")
        grade_text.setAlignment(Qt.AlignCenter)

        grade_layout.addWidget(grade)
        grade_layout.addWidget(grade_text)
        card_layout.addWidget(grade_widget)

        card_layout.addWidget(VerticalSeparator(), 0, Qt.AlignVCenter)

        # =================================================
        # 4열 : Issues / Resolved
        # =================================================
        result_widget = QWidget()
        result_widget.setMinimumWidth(145)
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(5, 3, 0, 3)
        result_layout.setSpacing(6)

        issues_row = QHBoxLayout()
        issues_row.setSpacing(4)

        if project["status"] in ("검사 실패", "검사 전"):
            issues_value = QLabel("-")
            issues_value.setObjectName("projectIssueNone")
            issues_suffix = QLabel("")
        else:
            issues_value = QLabel(str(project["issues"]))
            if project["issues"] <= 6:
                issues_value.setObjectName("projectIssueGood")
            else:
                issues_value.setObjectName("projectIssueWarning")
            issues_suffix = QLabel("개 이슈")
            issues_suffix.setObjectName("projectResultTitle")

        issues_row.addWidget(issues_value)
        issues_row.addWidget(issues_suffix)
        issues_row.addStretch()
        result_layout.addLayout(issues_row)

        if project["status"] in ("검사 실패", "검사 전") or not project["issues"]:
            resolved_text = "- / -"
            progress_value = 0
            percent_text = "-"
        else:
            resolved_text = f'{project["resolved"]} / {project["issues"]} 조치'
            progress_value = round(project["resolved"] / project["issues"] * 100)
            percent_text = f"{progress_value}%"

        resolved = QLabel(resolved_text)
        resolved.setObjectName("projectResolvedText")
        result_layout.addWidget(resolved)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(6)
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(progress_value)
        progress.setTextVisible(False)
        progress.setFixedHeight(6)

        if project["status"] == "검사 실패":
            progress.setObjectName("projectProgressFailed")
        elif progress_value >= 75:
            progress.setObjectName("projectProgressGood")
        else:
            progress.setObjectName("projectProgressWarning")

        percent_label = QLabel(percent_text)
        percent_label.setObjectName("projectProgressPercent")
        percent_label.setFixedWidth(28)
        percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        progress_row.addWidget(progress, 1)
        progress_row.addWidget(percent_label)
        result_layout.addLayout(progress_row)
        card_layout.addWidget(result_widget, 3)

        more_label = QLabel("⋮")
        more_label.setObjectName("projectMore")
        more_label.setFixedWidth(12)
        more_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        card_layout.addWidget(more_label)

        card.mousePressEvent = lambda event, p=project: self.project_selected.emit(p)
        return card

    # =====================================================
    # 검색
    # =====================================================
    def filter_projects(self, text):
        keyword = text.strip().lower()

        for card, name, department in self.project_cards:
            visible = keyword in name or keyword in department
            card.setVisible(visible)
