from abc import ABC, abstractmethod
from dataclasses import replace

from rules.core.models import RuleIssue
from rules.core.severity import IssueAssessment, calculate_severity


class BaseIssueAssessor(ABC):
    """Issue의 Impact/Likelihood를 평가하는 교체 가능한 인터페이스."""

    @abstractmethod
    def assess(self, issue: RuleIssue) -> IssueAssessment | None:
        raise NotImplementedError


class DeferredIssueAssessor(BaseIssueAssessor):
    """실제 AI 판정 연결 전까지 기존 Issue를 변경하지 않는 기본 구현."""

    def assess(self, issue: RuleIssue) -> IssueAssessment | None:
        return None


def apply_issue_assessments(
    issues: tuple[RuleIssue, ...] | list[RuleIssue],
    assessor: BaseIssueAssessor,
) -> tuple[RuleIssue, ...]:
    """Issue에 판정 결과를 붙이고 Matrix로 최종 Severity를 확정한다."""

    assessed_issues = []

    for issue in issues:
        assessment = assessor.assess(issue)

        if assessment is None:
            assessed_issues.append(issue)
            continue

        calculated_severity = calculate_severity(
            assessment.impact,
            assessment.likelihood,
        )

        normalized_assessment = replace(
            assessment,
            severity=calculated_severity,
        )

        assessed_issues.append(
            replace(
                issue,
                severity=calculated_severity.value,
                assessment=normalized_assessment,
            )
        )

    return tuple(assessed_issues)
