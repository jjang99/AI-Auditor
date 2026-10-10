"""실제 실행 가능한 문서 Rule을 관리하는 중앙 Registry.

Full Catalog 105개와 실제 실행 가능한 Rule은 분리해서 관리한다.
새 Priority Rule은 상세 구현과 targeted regression을 통과한 뒤 이 Registry에
등록하고, 등록 후 전체 회귀검증으로 제품 통합 안정성을 다시 확인한다.

현재 기준:
- Full Catalog: 105개
- 기존 MVP 실행 Rule: 20개
- P1 활성 Rule: 7개
  (AUD-008, AUD-014, AUD-016, REQ-007, REQ-012, REQ-017, FP-008)
- 총 실제 실행 가능 Rule: 27개
- 나머지 P1 6개: 구현 전/진행 대상, 아직 비활성
"""

from collections.abc import Callable

from rules.core.models import DocumentRule
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.definitions.document_p1_aud008_rule import get_p1_aud008_rule
from rules.definitions.document_p1_rules import get_p1_deterministic_rules
from rules.definitions.document_p1_req_rules import get_p1_requirement_rules
from rules.definitions.document_rule_catalog import get_document_rule


P1_TARGET_CODES = (
    "AUD-008",
    "AUD-010",
    "AUD-014",
    "AUD-016",
    "AUD-018",
    "AUD-020",
    "AUD-022",
    "AUD-023",
    "REQ-007",
    "REQ-012",
    "REQ-017",
    "FP-002",
    "FP-008",
)


# 실제 Handler + targeted test를 통과한 Rule provider만 등록한다.
_IMPLEMENTED_RULE_PROVIDERS: tuple[
    Callable[[], tuple[DocumentRule, ...]], ...
] = (
    get_document_mvp_rules,
    get_p1_deterministic_rules,
    get_p1_aud008_rule,
    get_p1_requirement_rules,
)


def _validate_implemented_rules(
    rules: tuple[DocumentRule, ...],
) -> None:
    """Registry 오등록으로 인한 중복/카탈로그 불일치를 즉시 차단한다."""
    codes = [rule.code for rule in rules]
    if len(codes) != len(set(codes)):
        raise ValueError("실행 가능 문서 Rule Registry에 중복 Rule Code가 있습니다.")

    for rule in rules:
        catalog_rule = get_document_rule(rule.code)
        if catalog_rule is None:
            raise ValueError(
                f"실행 Rule이 Full Catalog에 없습니다: {rule.code}"
            )
        if catalog_rule.name != rule.name:
            raise ValueError(
                f"Rule 이름이 Full Catalog와 다릅니다: {rule.code}"
            )
        if catalog_rule.category != rule.category:
            raise ValueError(
                f"Rule 영역이 Full Catalog와 다릅니다: {rule.code}"
            )
        if catalog_rule.description != rule.description:
            raise ValueError(
                f"Rule 설명이 Full Catalog와 다릅니다: {rule.code}"
            )
        if catalog_rule.execution_type != rule.execution_type.value:
            raise ValueError(
                f"Rule 실행방식이 Full Catalog와 다릅니다: {rule.code}"
            )


def get_implemented_document_rules() -> tuple[DocumentRule, ...]:
    """현재 제품에서 실제 실행 가능한 문서 Rule만 반환한다."""
    rules = tuple(
        rule
        for provider in _IMPLEMENTED_RULE_PROVIDERS
        for rule in provider()
    )
    _validate_implemented_rules(rules)
    return rules


def get_implemented_document_rule_codes() -> tuple[str, ...]:
    return tuple(rule.code for rule in get_implemented_document_rules())


def is_document_rule_implemented(code: str) -> bool:
    return code in set(get_implemented_document_rule_codes())


def get_p1_target_codes() -> tuple[str, ...]:
    """감리자료 실무검증으로 확정한 P1 구현 대상 13개를 반환한다."""
    return P1_TARGET_CODES
