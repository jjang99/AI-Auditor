from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rules.core.severity import AuditImprovementJudgment, IssueAssessment

class RuleExecutionType(str, Enum):
    RULE = "Rule"
    AI = "AI"
    HYBRID = "Hybrid"


@dataclass(frozen=True)
class DocumentRule:
    code: str
    name: str
    category: str
    execution_type: RuleExecutionType
    severity: str
    description: str
    check_points: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True

@dataclass(frozen=True)
class DocumentRuleIssue:
    rule_code: str
    rule_name: str
    category: str
    severity: str
    file_path: str
    block_type: str
    evidence: str
    description: str
    location: str | None = None
    page: int | None = None
    sheet: str | None = None
    slide: int | None = None

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
    assessment: IssueAssessment | None = None
    audit_judgment: AuditImprovementJudgment | None = None

    @property
    def title(self) -> str:
        if self.rule_code == "CHG-001":
            finding = " ".join(str(self.evidence or "").split()).strip()
            if finding:
                return f"{self.rule_code} {finding}"
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
