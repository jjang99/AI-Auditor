from dataclasses import replace
from app.parsers.models import ParsedDocument
from rules.core.ai_provider import AIInspectionContext, AIInspectionResult, BaseAIProvider
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
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

    @staticmethod
    def _build_requirement_comparison_evidence(
        document: ParsedDocument,
        max_items: int = 24,
    ) -> tuple[str, ...]:
        """요구사항 비교형 AI Rule에 전달할 요구사항 행만 추출한다."""
        import re

        evidence = []
        seen = set()

        for block in document.blocks:
            text = block.text.strip() if block.text else ""
            if not text:
                continue

            first = text.split("|", 1)[0].strip()
            if not re.match(r"^[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*$", first, re.IGNORECASE):
                continue

            normalized = " ".join(text.split())
            if normalized in seen:
                continue
            seen.add(normalized)
            evidence.append(normalized[:800])

            if len(evidence) >= max_items:
                break

        return tuple(evidence)

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results: list[AIInspectionResult] = []

        for rule in self.document_rules:
            strategy = get_ai_processing_strategy(rule.code)

            if strategy == AIProcessingStrategy.COMPARISON:
                evidence = self._build_requirement_comparison_evidence(document)
                if len(evidence) < 2:
                    result = AIInspectionResult(
                        rule_code=rule.code,
                        findings=(),
                        raw_response="",
                        provider_name=self.provider.__class__.__name__,
                    )
                else:
                    result = self.provider.inspect(
                        document,
                        rule,
                        AIInspectionContext(evidence=evidence),
                    )
            else:
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
    