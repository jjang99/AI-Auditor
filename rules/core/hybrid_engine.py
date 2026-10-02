import re
from dataclasses import dataclass, replace

from app.parsers.models import ParsedDocument
from rules.core.ai_provider import (
    AIInspectionContext,
    AIInspectionResult,
    BaseAIProvider,
)
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
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

        strategy = get_ai_processing_strategy(rule.code)

        if rule.code == "REQ-003":
            evidence = self._build_req_003_evidence(document)
        elif rule.code == "REQ-018":
            evidence = self._build_req_018_evidence(document)
        elif strategy in (
            AIProcessingStrategy.CANDIDATE,
            AIProcessingStrategy.EVIDENCE,
        ):
            evidence = self._build_relevant_evidence(document, rule)

        return HybridInspectionContext(
            document=document,
            rule=rule,
            evidence=evidence,
        )

    @staticmethod
    def _build_relevant_evidence(
        document: ParsedDocument,
        rule: DocumentRule,
        max_items: int = 12,
        max_chars: int = 4500,
    ) -> tuple[str, ...]:
        """후보/근거확인형 Rule에 관련성이 높은 블록만 전달한다."""

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
        """REQ-018: 추적표 헤더를 기준으로 누락 의심행만 AI 후보로 선별한다."""

        evidence: list[str] = []
        trace_columns: dict[str, int] | None = None

        required_groups = {
            "유스케이스": ("유스케이스id", "유스케이스"),
            "화면": ("화면id", "화면"),
            "프로그램": ("프로그램id", "프로그램"),
            "테이블": ("테이블id", "테이블"),
            "통합테스트": ("통합테스트", "시험", "테스트"),
        }

        for block in document.blocks:
            if block.block_type != "sheet_row":
                continue

            text = block.text.strip()
            if not text:
                continue

            # 비기능 요구사항은 화면/프로그램/테이블 등이 본질적으로
            # 적용되지 않을 수 있으므로 기능 추적열의 구조적 누락으로 확정하지 않는다.
            sheet_name = (block.sheet or "").replace(" ", "").lower()
            if "비기능" in sheet_name:
                continue

            columns = [value.strip() for value in text.split("|")]
            normalized = [value.lower().replace(" ", "") for value in columns]

            if (
                any("요구사항id" in value for value in normalized)
                and any("통합테스트" in value for value in normalized)
            ):
                trace_columns = {}
                for label, aliases in required_groups.items():
                    for index, value in enumerate(normalized):
                        if any(alias in value for alias in aliases):
                            trace_columns[label] = index
                            break
                continue

            if not trace_columns:
                continue

            first_column = columns[0] if columns else ""
            if not re.match(
                r"^[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*$",
                first_column,
                re.IGNORECASE,
            ):
                continue

            missing = []
            for label, index in trace_columns.items():
                value = columns[index].strip() if index < len(columns) else ""
                # N/A는 명시적인 비적용 값이므로 누락으로 보지 않는다.
                if not value:
                    missing.append(label)

            if not missing:
                continue

            location = block.location or block.sheet or "위치 미상"
            evidence.append(
                f"{location}: 추적정보 누락 후보({', '.join(missing)}) | {text[:600]}"
            )

        return tuple(evidence)

    def _build_req_018_findings(
        self,
        context: HybridInspectionContext,
    ) -> AIInspectionResult:
        """REQ-018의 구조적으로 확정된 누락은 Rule 결과로 직접 생성한다."""

        findings = tuple(
            (
                "요구사항 추적정보 누락이 확인되었습니다. "
                + evidence.replace("추적정보 누락 후보", "추적정보 누락")
            )
            for evidence in context.evidence
        )

        return AIInspectionResult(
            rule_code=context.rule.code,
            findings=findings,
            raw_response="",
            provider_name="RulePreanalysis",
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

            if rule.code == "REQ-018":
                if context.evidence:
                    result = self._build_req_018_findings(context)
                else:
                    result = AIInspectionResult(
                        rule_code=rule.code,
                        findings=(),
                        raw_response="",
                        provider_name=self.provider.__class__.__name__,
                    )
            else:
                strategy = get_ai_processing_strategy(rule.code)
                if strategy in (
                    AIProcessingStrategy.CANDIDATE,
                    AIProcessingStrategy.EVIDENCE,
                ) and not context.evidence:
                    result = AIInspectionResult(
                        rule_code=rule.code,
                        findings=(),
                        raw_response="",
                        provider_name=self.provider.__class__.__name__,
                    )
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