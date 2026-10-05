from abc import ABC, abstractmethod
from dataclasses import replace

from rules.core.models import RuleIssue
from rules.core.severity import AuditImprovementJudgment, IssueAssessment, calculate_severity


_AUDIT_JUDGMENT_EXCLUDED_RULE_CODES = {
    # 변경사항 자체를 식별한 사실 결과다. 개선 필요성은 CHG-006/012/018 등
    # 후속 영향·미반영·위험 Rule에서 판단한다.
    "CHG-001",
}


def _normalize_audit_judgment(
    issue: RuleIssue,
    judgment: AuditImprovementJudgment | None,
) -> AuditImprovementJudgment | None:
    if issue.rule_code in _AUDIT_JUDGMENT_EXCLUDED_RULE_CODES:
        return None
    return judgment


class BaseIssueAssessor(ABC):
    """Issue의 Impact/Likelihood를 평가하는 교체 가능한 인터페이스."""

    @abstractmethod
    def assess(self, issue: RuleIssue) -> IssueAssessment | None:
        raise NotImplementedError

    def assess_many(
        self,
        issues: tuple[RuleIssue, ...],
    ) -> tuple[IssueAssessment | None, ...]:
        """기본 구현은 기존 호환성을 위해 개별 평가를 사용한다."""
        return tuple(self.assess(issue) for issue in issues)

    def judge_audit_many(
        self,
        issues: tuple[RuleIssue, ...],
    ) -> tuple[AuditImprovementJudgment | None, ...]:
        """감리 개선판정은 Severity와 독립적이며 필요한 Issue에만 적용한다."""
        return tuple(None for _ in issues)


class DeferredIssueAssessor(BaseIssueAssessor):
    """실제 AI 판정 연결 전까지 기존 Issue를 변경하지 않는 기본 구현."""

    def assess(self, issue: RuleIssue) -> IssueAssessment | None:
        return None


def apply_issue_assessments(
    issues: tuple[RuleIssue, ...] | list[RuleIssue],
    assessor: BaseIssueAssessor,
    *,
    include_audit_judgment: bool = False,
) -> tuple[RuleIssue, ...]:
    """Issue에 판정 결과를 붙이고 Matrix로 최종 Severity를 확정한다."""

    issue_tuple = tuple(issues)
    assessments = assessor.assess_many(issue_tuple)
    audit_judgments = (
        assessor.judge_audit_many(issue_tuple)
        if include_audit_judgment
        else tuple(issue.audit_judgment for issue in issue_tuple)
    )

    if len(assessments) != len(issue_tuple):
        raise ValueError("Issue 평가 결과 수가 입력 Issue 수와 일치하지 않습니다.")
    if len(audit_judgments) != len(issue_tuple):
        raise ValueError("감리 개선판정 결과 수가 입력 Issue 수와 일치하지 않습니다.")

    assessed_issues = []

    for issue, assessment, audit_judgment in zip(issue_tuple, assessments, audit_judgments):
        audit_judgment = _normalize_audit_judgment(issue, audit_judgment)

        if assessment is None:
            assessed_issues.append(replace(issue, audit_judgment=audit_judgment))
            continue

        calculated_severity = calculate_severity(
            assessment.impact,
            assessment.likelihood,
        )

        normalized_assessment = replace(
            assessment,
            severity=calculated_severity,
            severity_reason=(
                f"Impact {assessment.impact.value} × "
                f"Likelihood {assessment.likelihood.value} = "
                f"Severity {calculated_severity.value}"
            ),
        )

        assessed_issues.append(
            replace(
                issue,
                severity=calculated_severity.value,
                assessment=normalized_assessment,
                audit_judgment=audit_judgment,
            )
        )

    return tuple(assessed_issues)
