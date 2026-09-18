import re
from pathlib import Path

from rules.core.models import FileInspectionResult, InspectionSummary, Rule, RuleIssue


class InspectionCancelled(Exception):
    """Raised when a running inspection is cancelled by the user."""


class RuleEngine:
    """Deterministic local rule engine used before AI-assisted inspection."""

    def __init__(self, rules: list[Rule]):
        self.rules = [rule for rule in rules if rule.enabled]

    @staticmethod
    def _check_cancel(cancel_requested):
        if cancel_requested is not None and cancel_requested():
            raise InspectionCancelled("검사가 취소되었습니다.")

    def inspect_file(self, file_path: str | Path, cancel_requested=None) -> FileInspectionResult:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        issues: list[RuleIssue] = []
        executed_rule_count = 0

        for rule in self.rules:
            self._check_cancel(cancel_requested)
            if rule.file_extensions and path.suffix.lower() not in rule.file_extensions:
                continue

            executed_rule_count += 1
            expression = re.compile(rule.pattern, re.IGNORECASE)
            for line_number, line in enumerate(lines, start=1):
                self._check_cancel(cancel_requested)
                if not expression.search(line):
                    continue

                issues.append(
                    RuleIssue(
                        rule_code=rule.code,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        file_path=str(path),
                        line_number=line_number,
                        evidence=line.strip()[:500],
                        description=rule.description,
                        recommendation=rule.recommendation,
                    )
                )

        return FileInspectionResult(
            file_path=path,
            inspected_rule_count=executed_rule_count,
            issues=tuple(issues),
        )

    def inspect_files(self, file_paths: list[str | Path], cancel_requested=None) -> InspectionSummary:
        all_issues: list[RuleIssue] = []
        executed_rule_count = 0

        for file_path in file_paths:
            self._check_cancel(cancel_requested)
            result = self.inspect_file(file_path, cancel_requested=cancel_requested)
            executed_rule_count += result.inspected_rule_count
            all_issues.extend(result.issues)

        return InspectionSummary(
            file_count=len(file_paths),
            rule_count=len(self.rules),
            executed_rule_count=executed_rule_count,
            issues=tuple(all_issues),
        )
