"""AI Auditor 문서 검사체계 공통 기준정보.

제품 전체 검사체계(105개)와 해커톤 MVP 실행 대상(20개)의
영역별 기준을 Administration과 Inspection에서 공통으로 사용한다.

주의:
- 전체 Rule 수와 MVP 구현 수는 서로 다른 개념이다.
- 실제 MVP Rule 상세 정의는 document_mvp_rules.py에서 관리한다.
- 기존 소스코드 정적분석 Rule(default_rules.py)은 별도로 유지한다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentRuleCategory:
    code: str
    name: str
    total_count: int
    mvp_count: int


DOCUMENT_RULE_CATEGORIES = (
    DocumentRuleCategory("AUD", "감리 사전점검", 24, 4),
    DocumentRuleCategory("REQ", "요구사항 정합성", 28, 6),
    DocumentRuleCategory("CHG", "변경영향도", 18, 4),
    DocumentRuleCategory("FP", "FP 검증", 12, 2),
    DocumentRuleCategory("AI", "AI 특화 검증", 23, 4),
)


def get_document_rule_categories():
    """최종 5대 문서 검사영역 기준을 반환한다."""
    return DOCUMENT_RULE_CATEGORIES


def get_total_rule_count():
    """제품 전체 검사기준 수를 반환한다."""
    return sum(category.total_count for category in DOCUMENT_RULE_CATEGORIES)


def get_total_mvp_count():
    """현재 해커톤 MVP 대상 Rule 수를 반환한다."""
    return sum(category.mvp_count for category in DOCUMENT_RULE_CATEGORIES)