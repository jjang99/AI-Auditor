from app.parsers.models import ParsedDocument
from rules.core.ai_engine import DocumentAIEngine
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.core.models import DocumentRule, DocumentRuleIssue
from rules.core.p1_document_engine import P1DocumentRuleEngine
from rules.core.p1_requirement_hybrid_engine import P1RequirementHybridEngine


class DocumentInspectionEngine:
    """Rule, AI, Hybrid 방식의 문서 검사를 통합 실행한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        ai_provider: BaseAIProvider,
        required_deliverables: list[str] | None = None,
    ):
        # P1DocumentRuleEngine은 기존 DocumentRuleEngine을 상속하므로
        # MVP Rule 동작은 유지하면서 검증 완료된 P1 결정형 Handler만 추가한다.
        self.rule_engine = P1DocumentRuleEngine(
            list(rules),
            required_deliverables=required_deliverables,
        )

        self.ai_engine = DocumentAIEngine(
            rules,
            ai_provider,
        )

        # P1RequirementHybridEngine은 기존 DocumentHybridEngine을 상속하므로
        # 기존 Hybrid Rule 동작을 유지하면서 P1-B 사전분석만 확장한다.
        self.hybrid_engine = P1RequirementHybridEngine(
            rules,
            ai_provider,
        )

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[DocumentRuleIssue | AIInspectionResult, ...]:
        results: list[DocumentRuleIssue | AIInspectionResult] = []

        results.extend(
            self.rule_engine.inspect_document(document)
        )

        results.extend(
            self.ai_engine.inspect_document(document)
        )

        results.extend(
            self.hybrid_engine.inspect_document(document)
        )

        return tuple(results)
