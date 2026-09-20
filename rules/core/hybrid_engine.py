from dataclasses import dataclass, replace

from app.parsers.models import ParsedDocument
from rules.core.ai_provider import (
    AIInspectionContext,
    AIInspectionResult,
    BaseAIProvider,
)
from rules.core.models import DocumentRule, RuleExecutionType


@dataclass(frozen=True)
class HybridInspectionContext:
    """Hybrid 검사에서 AI 판단 전에 준비되는 사전분석 정보."""

    document: ParsedDocument
    rule: DocumentRule
    evidence: tuple[str, ...] = ()


class DocumentHybridEngine:
    """Rule 기반 사전분석과 AI 판단을 결합하는 Hybrid 검사 Engine."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        provider: BaseAIProvider,
    ):
        self.rules = [
            rule
            for rule in rules
            if rule.enabled
            and rule.execution_type == RuleExecutionType.HYBRID
        ]

        self.provider = provider

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        """AI 판단 전에 사용할 공통 Hybrid 검사 Context를 만든다."""

        evidence: tuple[str, ...] = ()

        if rule.code == "REQ-003":
            evidence = self._build_req_003_evidence(document)

        return HybridInspectionContext(
            document=document,
            rule=rule,
            evidence=evidence,
        )

    def _build_req_003_evidence(
        self,
        document: ParsedDocument,
    ) -> tuple[str, ...]:
        """REQ-003: 판단기준이 불명확할 수 있는 표현 후보를 찾는다."""

        ambiguous_terms = (
            "적절히",
            "필요시",
            "필요 시",
        )

        evidence: list[str] = []

        for block in document.blocks:
            text = block.text.strip()

            if not text:
                continue

            matched_terms = [
                term
                for term in ambiguous_terms
                if term in text
            ]

            if matched_terms:
                evidence.append(
                    f"모호 표현 후보({', '.join(matched_terms)}): {text}"
                )

        return tuple(evidence)

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results: list[AIInspectionResult] = []

        for rule in self.rules:
            context = self.build_context(
                document,
                rule,
            )

            result = self.provider.inspect(
                context.document,
                context.rule,
                AIInspectionContext(
                    evidence=context.evidence,
                ),
            )

            result = replace(
                result,
                execution_type=rule.execution_type.value,
                provider_name=self.provider.__class__.__name__,
            )

            results.append(result)

        return tuple(results)