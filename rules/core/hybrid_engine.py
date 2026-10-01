import re
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
        elif rule.code == "REQ-018":
            evidence = self._build_req_018_evidence(document)

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

    def _build_req_018_evidence(
        self,
        document: ParsedDocument,
    ) -> tuple[str, ...]:
        """REQ-018: 요구사항 추적성 판단에 필요한 표 행만 선별한다."""

        traceability_terms = (
            "요구사항id",
            "요구사항 id",
            "관련산출물",
            "구현내용",
            "유스케이스",
            "화면",
            "인터페이스",
            "프로그램",
            "테이블",
            "통합테스트",
            "시험",
            "테스트",
        )

        evidence: list[str] = []

        for block in document.blocks:
            text = block.text.strip()
            if not text:
                continue

            normalized = text.lower()
            has_traceability_term = any(
                term in normalized
                for term in traceability_terms
            )
            has_requirement_id = bool(
                re.search(
                    r"\b(?:REQ[-_]?\d+|[A-Z]{2,5}[-_]\d{2,})\b",
                    text,
                    re.IGNORECASE,
                )
            )

            if not (has_traceability_term or has_requirement_id):
                continue

            location = block.location or block.sheet or "위치 미상"
            evidence.append(f"{location}: {text[:600]}")

        # 저사양 로컬 AI에서 문서 전체를 전달하지 않도록 근거량을 제한한다.
        return tuple(evidence[:80])

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