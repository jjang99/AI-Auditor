from rules.core.issue_assessor import BaseIssueAssessor, apply_issue_assessments
from rules.core.models import RuleIssue
from rules.core.severity import (
    AssessmentLevel,
    AuditImprovementJudgment,
    AuditImprovementTiming,
    AuditImportantFlag,
    AuditRecommendationType,
    IssueAssessment,
    IssueSeverity,
)


class _FixedAssessor(BaseIssueAssessor):
    def assess(self, issue):
        return IssueAssessment(
            impact=AssessmentLevel.LOW,
            impact_reason="테스트",
            likelihood=AssessmentLevel.LOW,
            likelihood_reason="테스트",
            severity=IssueSeverity.LOW,
            severity_reason="테스트",
        )

    def judge_audit_many(self, issues):
        judgment = AuditImprovementJudgment(
            recommendation_type=AuditRecommendationType.REQUIRED,
            improvement_timing=AuditImprovementTiming.SHORT_TERM,
            important=AuditImportantFlag.YES,
        )
        return tuple(judgment for _ in issues)


def _issue(rule_code, rule_name):
    return RuleIssue(
        rule_code=rule_code,
        rule_name=rule_name,
        category="변경영향도",
        severity="Low",
        file_path="requirements_v1.1.hwp",
        line_number=None,
        evidence="테스트 근거",
        description="테스트 설명",
    )


def test_change_fact_does_not_receive_audit_improvement_judgment():
    issues = (
        _issue("CHG-001", "변경사항 식별 점검"),
        _issue("CHG-006", "변경 영향대상 식별"),
    )

    result = apply_issue_assessments(
        issues,
        _FixedAssessor(),
        include_audit_judgment=True,
    )

    assert result[0].audit_judgment is None
    assert result[1].audit_judgment is not None
    assert result[1].audit_judgment.recommendation_type == AuditRecommendationType.REQUIRED
