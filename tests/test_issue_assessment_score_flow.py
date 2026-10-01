from app.database.repositories.inspection_repository import calculate_score_grade
from rules.core.issue_assessor import BaseIssueAssessor, apply_issue_assessments
from rules.core.models import InspectionSummary, RuleIssue
from rules.core.severity import (
    AssessmentLevel,
    IssueAssessment,
    IssueSeverity,
)


class HighHighAssessor(BaseIssueAssessor):
    def assess(self, issue):
        return IssueAssessment(
            impact=AssessmentLevel.HIGH,
            impact_reason="핵심 업무 영향",
            likelihood=AssessmentLevel.HIGH,
            likelihood_reason="반복 발생 가능",
            severity=IssueSeverity.LOW,
            severity_reason="Matrix가 최종 Severity를 결정",
        )


def test_calculated_severity_is_used_by_score_flow():
    original = RuleIssue(
        rule_code="TEST-004",
        rule_name="점수 연계 테스트",
        category="감리 사전점검",
        severity="Low",
        file_path="sample.docx",
        line_number=1,
        evidence="근거",
        description="설명",
    )

    assessed_issue = apply_issue_assessments(
        [original],
        HighHighAssessor(),
    )[0]

    summary = InspectionSummary(
        file_count=1,
        rule_count=1,
        executed_rule_count=1,
        issues=(assessed_issue,),
    )

    score, grade = calculate_score_grade(summary)

    assert assessed_issue.severity == "Critical"
    assert score == 80
    assert grade == "B"
