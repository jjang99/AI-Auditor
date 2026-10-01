from rules.core.issue_assessor import (
    BaseIssueAssessor,
    DeferredIssueAssessor,
    apply_issue_assessments,
)
from rules.core.models import RuleIssue
from rules.core.severity import (
    AssessmentLevel,
    IssueAssessment,
    IssueSeverity,
)


def _issue():
    return RuleIssue(
        rule_code="TEST-001",
        rule_name="판정 파이프라인",
        category="감리 사전점검",
        severity="Low",
        file_path="sample.docx",
        line_number=1,
        evidence="근거",
        description="설명",
    )


def test_deferred_assessor_preserves_existing_issue():
    issue = _issue()

    result = apply_issue_assessments(
        [issue],
        DeferredIssueAssessor(),
    )

    assert result == (issue,)
    assert result[0].assessment is None
    assert result[0].severity == "Low"


def test_assessor_result_uses_matrix_for_final_severity():
    class StubIssueAssessor(BaseIssueAssessor):
        def assess(self, issue):
            return IssueAssessment(
                impact=AssessmentLevel.HIGH,
                impact_reason="핵심 업무에 큰 영향",
                likelihood=AssessmentLevel.HIGH,
                likelihood_reason="반복 발생 가능",
                severity=IssueSeverity.LOW,
                severity_reason="판정기가 준 Severity는 Matrix가 재확정",
            )

    result = apply_issue_assessments(
        [_issue()],
        StubIssueAssessor(),
    )

    assessed = result[0]
    assert assessed.assessment is not None
    assert assessed.assessment.impact == AssessmentLevel.HIGH
    assert assessed.assessment.likelihood == AssessmentLevel.HIGH
    assert assessed.assessment.severity == IssueSeverity.CRITICAL
    assert assessed.severity == "Critical"
