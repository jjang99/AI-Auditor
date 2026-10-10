"""P2-C FP-006 구조형 AI 확장 Engine."""

from dataclasses import replace

from app.parsers.models import ParsedDocument
from rules.core.ai_engine import DocumentAIEngine
from rules.core.ai_provider import AIInspectionContext, AIInspectionResult, BaseAIProvider
from rules.core.models import DocumentRule, RuleExecutionType
from rules.core.p2_c_checks import build_fp006_evidence


class P2CAIEngine(DocumentAIEngine):
    """기존 AI Rule을 유지하면서 FP-006에 구조형 후보 사전분석을 적용한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        provider: BaseAIProvider,
    ):
        self.fp006_rule = next(
            (
                rule
                for rule in rules
                if rule.enabled
                and rule.code == "FP-006"
                and rule.execution_type == RuleExecutionType.AI
            ),
            None,
        )
        super().__init__(
            tuple(rule for rule in rules if rule.code != "FP-006"),
            provider,
        )

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results = list(super().inspect_document(document))

        rule = self.fp006_rule
        if rule is None:
            return tuple(results)

        evidence = build_fp006_evidence(document)
        if evidence:
            result = self.provider.inspect(
                document,
                rule,
                AIInspectionContext(evidence=evidence),
            )
        else:
            result = AIInspectionResult(
                rule_code=rule.code,
                findings=(),
                raw_response="",
                provider_name=self.provider.__class__.__name__,
            )

        results.append(
            replace(
                result,
                execution_type=rule.execution_type.value,
                provider_name=self.provider.__class__.__name__,
            )
        )
        return tuple(results)
