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
        """REQ-018: 추적표에서 추적정보 누락 의심행만 AI 후보로 선별한다."""

        evidence: list[str] = []
        trace_header_seen = False

        for block in document.blocks:
            if block.block_type != "sheet_row":
                continue

            text = block.text.strip()
            if not text:
                continue

            columns = [value.strip() for value in text.split("|")]
            normalized = [value.lower() for value in columns]

            if (
                "요구사항id" in normalized
                and any("통합테스트" in value for value in normalized)
            ):
                trace_header_seen = True
                continue

            if not trace_header_seen:
                continue

            # 실제 추적 데이터 행은 요구사항 식별자로 시작한다.
            first_column = columns[0] if columns else ""
            if not re.match(
                r"^[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*$",
                first_column,
                re.IGNORECASE,
            ):
                continue

            # 현재 추적표 구조에서 핵심 양방향 연결정보:
            # 요구사항 → 유스케이스 → 화면 → 프로그램 → 테이블 → 통합테스트.
            # 인터페이스는 N/A가 정상일 수 있어 필수 누락 판정에서 제외한다.
            expected_indexes = {
                2: "유스케이스",
                4: "화면",
                7: "프로그램",
                9: "테이블",
                10: "통합테스트",
            }
            missing = [
                label
                for index, label in expected_indexes.items()
                if index >= len(columns)
                or not columns[index]
                or columns[index].upper() == "N/A"
            ]

            if not missing:
                continue

            location = block.location or block.sheet or "위치 미상"
            evidence.append(
                f"{location}: 추적정보 누락 후보({', '.join(missing)}) | {text[:600]}"
            )

        return tuple(evidence)

    def _inspect_req_018_in_batches(
        self,
        context: HybridInspectionContext,
        batch_size: int = 10,
    ) -> AIInspectionResult:
        """REQ-018 근거 전체를 작은 묶음으로 검사하고 결과를 통합한다."""

        findings: list[str] = []
        raw_responses: list[str] = []

        for start in range(0, len(context.evidence), batch_size):
            batch = context.evidence[start:start + batch_size]
            result = self.provider.inspect(
                context.document,
                context.rule,
                AIInspectionContext(evidence=batch),
            )
            findings.extend(result.findings)
            if result.raw_response:
                raw_responses.append(result.raw_response)

        # 동일 지적이 여러 배치에서 나온 경우 최초 1건만 유지한다.
        unique_findings = tuple(dict.fromkeys(findings))

        return AIInspectionResult(
            rule_code=context.rule.code,
            findings=unique_findings,
            raw_response="\n".join(raw_responses),
            provider_name=self.provider.__class__.__name__,
        )

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

            if rule.code == "REQ-018" and context.evidence:
                result = self._inspect_req_018_in_batches(context)
            else:
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