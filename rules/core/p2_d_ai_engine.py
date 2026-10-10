"""P2-D AI-015 RAG 근거형 AI 확장 Engine."""

from dataclasses import replace

from app.parsers.models import ParsedDocument
from rules.core.ai_provider import AIInspectionContext, AIInspectionResult, BaseAIProvider
from rules.core.models import DocumentRule, RuleExecutionType
from rules.core.p2_c_ai_engine import P2CAIEngine
from rules.core.p2_d_checks import build_ai015_evidence


class P2DAIEngine(P2CAIEngine):
    """기존 AI 동작을 유지하면서 AI-015에 RAG 전용 사전분석을 적용한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        provider: BaseAIProvider,
    ):
        self.ai015_rule = next(
            (
                rule
                for rule in rules
                if rule.enabled
                and rule.code == "AI-015"
                and rule.execution_type == RuleExecutionType.AI
            ),
            None,
        )
        super().__init__(
            tuple(rule for rule in rules if rule.code != "AI-015"),
            provider,
        )

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results = list(super().inspect_document(document))

        rule = self.ai015_rule
        if rule is None:
            return tuple(results)

        evidence = build_ai015_evidence(document)
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
