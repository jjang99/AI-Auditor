from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    code: str
    name: str
    category: str
    severity: str
    description: str
    pattern: str
    file_extensions: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True
    recommendation: str = ""
    selection_index: int | None = None


@dataclass(frozen=True)
class RuleIssue:
    rule_code: str
    rule_name: str
    category: str
    severity: str
    file_path: str
    line_number: int
    evidence: str
    description: str
    recommendation: str = ""

    @property
    def title(self) -> str:
        return f"{self.rule_code} {self.rule_name}"


@dataclass(frozen=True)
class FileInspectionResult:
    file_path: Path
    inspected_rule_count: int
    issues: tuple[RuleIssue, ...]


@dataclass(frozen=True)
class InspectionSummary:
    file_count: int
    rule_count: int
    executed_rule_count: int
    issues: tuple[RuleIssue, ...]

    @property
    def total_issues(self) -> int:
        return len(self.issues)
