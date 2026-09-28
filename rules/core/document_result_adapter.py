from rules.core.ai_provider import AIInspectionResult
from rules.core.models import DocumentRuleIssue, RuleIssue


def adapt_document_issue(issue: DocumentRuleIssue) -> RuleIssue:
    """DocumentRuleIssue를 기존 DB/UI 저장용 RuleIssue로 변환한다."""

    location_parts = []

    if issue.location:
        location_parts.append(str(issue.location))
    if issue.page is not None:
        location_parts.append(f"page {issue.page}")
    if issue.sheet:
        location_parts.append(f"sheet {issue.sheet}")
    if issue.slide is not None:
        location_parts.append(f"slide {issue.slide}")

    evidence = issue.evidence

    if location_parts:
        evidence = f"{' / '.join(location_parts)} | {evidence}"

    return RuleIssue(
        rule_code=issue.rule_code,
        rule_name=issue.rule_name,
        category=issue.category,
        severity=issue.severity,
        file_path=issue.file_path,
        line_number=0,
        evidence=evidence,
        description=issue.description,
        recommendation="",
    )


def adapt_ai_result(
    result: AIInspectionResult,
    document,
    rule,
) -> tuple[RuleIssue, ...]:
    """AI/Hybrid findings를 기존 DB/UI 저장용 RuleIssue로 변환한다."""

    issues = []

    for finding in result.findings:
        issues.append(
            RuleIssue(
                rule_code=rule.code,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                file_path=str(document.file_path),
                line_number=0,
                evidence=finding,
                description=rule.description,
                recommendation="",
            )
        )

    return tuple(issues)