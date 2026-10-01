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
    ) -> tuple[str, ...]:
        """요구사항 비교형 Rule의 전체 요구사항 행을 추출한다.

        비교 대상 자체를 임의 개수로 자르지 않는다. AI 호출량은 후속
        후보 선별 단계에서 제어한다.
        """
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
            evidence.append(normalized[:1200])

        return tuple(evidence)

    @staticmethod
    def _requirement_semantic_text(text: str) -> str:
        """추적표 행에서 비교 의미가 큰 요구사항 ID/명칭 영역만 사용한다."""
        parts = [part.strip() for part in text.split("|")]
        if not parts:
            return text

        # 실제 추적표는 대체로
        # 상위요구사항ID | 상세요구사항ID | 요구사항명 | UC... 형태다.
        # ID 자체는 유사도 점수에서 제외하고 요구사항명/내용만 비교한다.
        if len(parts) >= 3 and parts[1]:
            return parts[2] or parts[1]
        if len(parts) >= 2:
            return parts[1]
        return parts[0]

    @classmethod
    def _build_comparison_pairs(
        cls,
        evidence: tuple[str, ...],
        *,
        rule_code: str = "REQ-002",
        max_pairs: int = 6,
    ) -> tuple[tuple[str, str], ...]:
        """Rule 목적별 Python 사전선별로 AI 비교 후보쌍만 만든다."""
        import re
        from difflib import SequenceMatcher

        def tokens(text: str) -> set[str]:
            semantic = cls._requirement_semantic_text(text)
            return {
                token.lower()
                for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", semantic)
            }

        ranked = []
        for left_index in range(len(evidence)):
            left = evidence[left_index]
            left_semantic = cls._requirement_semantic_text(left).lower()
            left_tokens = tokens(left)

            for right_index in range(left_index + 1, len(evidence)):
                right = evidence[right_index]
                right_semantic = cls._requirement_semantic_text(right).lower()
                right_tokens = tokens(right)

                union = left_tokens | right_tokens
                jaccard = (
                    len(left_tokens & right_tokens) / len(union)
                    if union else 0.0
                )
                sequence = SequenceMatcher(None, left_semantic, right_semantic).ratio()

                if rule_code == "REQ-002":
                    # 중복은 명칭/내용 자체의 강한 유사성이 있어야 AI 후보로 보낸다.
                    similarity = max(jaccard, sequence)
                    if similarity < 0.45:
                        continue
                    score = similarity
                elif rule_code == "REQ-004":
                    # 상충은 같은 기능/대상을 다루는 요구사항끼리만 AI가 판단한다.
                    # 단순히 같은 추적 UI/프로그램을 쓴다는 이유로 후보가 되지 않는다.
                    shared = left_tokens & right_tokens
                    if not shared:
                        continue
                    similarity = max(jaccard, sequence)
                    if similarity < 0.30:
                        continue
                    score = similarity
                else:
                    continue

                ranked.append((-score, left_index, right_index, left, right))

        ranked.sort()
        return tuple(
            (left, right)
            for _score, _left_index, _right_index, left, right
            in ranked[:max_pairs]
        )

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
                    findings = []
                    raw_responses = []
                    for pair in self._build_comparison_pairs(evidence, rule_code=rule.code):
                        pair_result = self.provider.inspect(
                            document,
                            rule,
                            AIInspectionContext(evidence=pair),
                        )
                        findings.extend(pair_result.findings)
                        if pair_result.raw_response:
                            raw_responses.append(pair_result.raw_response)

                    result = AIInspectionResult(
                        rule_code=rule.code,
                        findings=tuple(dict.fromkeys(findings)),
                        raw_response="\n".join(raw_responses),
                        provider_name=self.provider.__class__.__name__,
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
    