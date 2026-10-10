from enum import Enum


class AIProcessingStrategy(str, Enum):
    RULE_FIRST = "Rule-first"
    CANDIDATE = "Candidate"
    COMPARISON = "Comparison"
    EVIDENCE = "Evidence"
    SYNTHESIS = "Synthesis"


AI_RULE_STRATEGIES = {
    "AUD-002": AIProcessingStrategy.CANDIDATE,
    "AUD-007": AIProcessingStrategy.CANDIDATE,
    "AUD-010": AIProcessingStrategy.CANDIDATE,
    "AUD-018": AIProcessingStrategy.EVIDENCE,
    "AUD-020": AIProcessingStrategy.CANDIDATE,
    "AUD-022": AIProcessingStrategy.EVIDENCE,
    "AUD-023": AIProcessingStrategy.EVIDENCE,
    "AUD-024": AIProcessingStrategy.SYNTHESIS,
    "REQ-002": AIProcessingStrategy.COMPARISON,
    "REQ-003": AIProcessingStrategy.CANDIDATE,
    "REQ-004": AIProcessingStrategy.COMPARISON,
    "REQ-007": AIProcessingStrategy.CANDIDATE,
    "REQ-009": AIProcessingStrategy.EVIDENCE,
    "REQ-012": AIProcessingStrategy.EVIDENCE,
    "REQ-017": AIProcessingStrategy.CANDIDATE,
    "REQ-018": AIProcessingStrategy.RULE_FIRST,
    "CHG-001": AIProcessingStrategy.EVIDENCE,
    "CHG-006": AIProcessingStrategy.SYNTHESIS,
    "CHG-012": AIProcessingStrategy.EVIDENCE,
    "CHG-018": AIProcessingStrategy.SYNTHESIS,
    "FP-005": AIProcessingStrategy.EVIDENCE,
    "AI-005": AIProcessingStrategy.EVIDENCE,
    "AI-009": AIProcessingStrategy.EVIDENCE,
    "AI-019": AIProcessingStrategy.EVIDENCE,
    "AI-022": AIProcessingStrategy.EVIDENCE,
}


def get_ai_processing_strategy(rule_code: str) -> AIProcessingStrategy:
    return AI_RULE_STRATEGIES[rule_code]
