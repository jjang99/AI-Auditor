from dataclasses import dataclass
from enum import Enum


class AssessmentLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class IssueSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass(frozen=True)
class IssueAssessment:
    impact: AssessmentLevel
    impact_reason: str
    likelihood: AssessmentLevel
    likelihood_reason: str
    severity: IssueSeverity
    severity_reason: str


_SEVERITY_MATRIX = {
    (AssessmentLevel.HIGH, AssessmentLevel.LOW): IssueSeverity.MEDIUM,
    (AssessmentLevel.HIGH, AssessmentLevel.MEDIUM): IssueSeverity.HIGH,
    (AssessmentLevel.HIGH, AssessmentLevel.HIGH): IssueSeverity.CRITICAL,
    (AssessmentLevel.MEDIUM, AssessmentLevel.LOW): IssueSeverity.LOW,
    (AssessmentLevel.MEDIUM, AssessmentLevel.MEDIUM): IssueSeverity.MEDIUM,
    (AssessmentLevel.MEDIUM, AssessmentLevel.HIGH): IssueSeverity.HIGH,
    (AssessmentLevel.LOW, AssessmentLevel.LOW): IssueSeverity.LOW,
    (AssessmentLevel.LOW, AssessmentLevel.MEDIUM): IssueSeverity.LOW,
    (AssessmentLevel.LOW, AssessmentLevel.HIGH): IssueSeverity.MEDIUM,
}


def calculate_severity(
    impact: AssessmentLevel,
    likelihood: AssessmentLevel,
) -> IssueSeverity:
    """Return the deterministic severity defined by the approved matrix."""
    return _SEVERITY_MATRIX[(impact, likelihood)]
