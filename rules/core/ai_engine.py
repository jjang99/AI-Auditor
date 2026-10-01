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

    @staticmethod
    def _build_relevant_evidence(
        document: ParsedDocument,
        rule: DocumentRule,
        max_items: int = 12,
        max_chars: int = 4500,
    ) -> tuple[str, ...]:
        """AI 근거확인형 Rule에 관련성이 높은 블록만 전달한다."""
        import re

        terms = []
        for value in (rule.name, rule.description, *rule.check_points):
            for term in re.split(r"[\\s·/,()]+", str(value)):
                normalized = term.strip("[]{}.,:;'\"")
                if len(normalized) >= 2 and normalized not in terms:
                    terms.append(normalized)

        ranked = []
        for index, block in enumerate(document.blocks):
            text = block.text.strip() if block.text else ""
            if not text:
                continue
            score = sum(1 for term in terms if term.lower() in text.lower())
            if score:
                ranked.append((-score, index, text))

        ranked.sort()
        selected = []
        used = 0
        for _score, _index, text in ranked:
            remaining = max_chars - used
            if remaining <= 0 or len(selected) >= max_items:
                break
            snippet = text[: min(800, remaining)]
            selected.append(snippet)
            used += len(snippet) + 1

        return tuple(selected)

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
            elif strategy == AIProcessingStrategy.SYNTHESIS:
                # 종합형 Rule은 앞선 검사결과를 입력으로 사용하는 후처리 단계에서 실행한다.
                result = AIInspectionResult(
                    rule_code=rule.code,
                    findings=(),
                    raw_response="",
                    provider_name=self.provider.__class__.__name__,
                )
            elif strategy == AIProcessingStrategy.EVIDENCE:
                evidence = self._build_relevant_evidence(document, rule)
                if not evidence:
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
    