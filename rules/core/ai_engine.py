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
        # AUD-024는 개별 검사결과를 종합하는 후처리 Rule이므로
        # 원문 문서 대상의 일반 AI 검사 루프에서는 실행하지 않는다.
        self.document_rules = [
            rule for rule in self.rules
            if rule.code != "AUD-024"
        ]

        self.provider = provider

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results: list[AIInspectionResult] = []

        for rule in self.document_rules:
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
    