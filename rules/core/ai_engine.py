from dataclasses import replace
from app.parsers.models import ParsedDocument
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.core.models import DocumentRule, RuleExecutionType


class DocumentAIEngine:
    """ParsedDocument를 대상으로 AI 방식 문서 검사를 수행한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        provider: BaseAIProvider,
    ):
        self.rules = [
            rule
            for rule in rules
            if rule.enabled
            and rule.execution_type == RuleExecutionType.AI
        ]

        self.provider = provider

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results: list[AIInspectionResult] = []

        for rule in self.rules:
            result = self.provider.inspect(
                document,
                rule,
            )

            result = replace(
                result,
                execution_type=rule.execution_type.value,
                provider_name=self.provider.__class__.__name__,
            )

            results.append(result)

        return tuple(results)
    