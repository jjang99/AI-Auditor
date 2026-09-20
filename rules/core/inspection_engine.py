from app.parsers.models import ParsedDocument
from rules.core.ai_engine import DocumentAIEngine
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.core.document_engine import DocumentRuleEngine
from rules.core.hybrid_engine import DocumentHybridEngine
from rules.core.models import DocumentRule, DocumentRuleIssue


class DocumentInspectionEngine:
    """Rule, AI, Hybrid 방식의 문서 검사를 통합 실행한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        ai_provider: BaseAIProvider,
        required_deliverables: list[str] | None = None,
    ):
        self.rule_engine = DocumentRuleEngine(
            rules,
            required_deliverables=required_deliverables,
        )

        self.ai_engine = DocumentAIEngine(
            rules,
            ai_provider,
        )

        self.hybrid_engine = DocumentHybridEngine(
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