from app.parsers.models import ParsedDocument
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.core.models import DocumentRule, DocumentRuleIssue
from rules.core.p2_c_ai_engine import P2CAIEngine
from rules.core.p2_c_hybrid_engine import P2CHybridEngine
from rules.core.p2_document_engine import P2DocumentRuleEngine


class DocumentInspectionEngine:
    """Rule, AI, Hybrid 방식의 문서 검사를 통합 실행한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        ai_provider: BaseAIProvider,
        required_deliverables: list[str] | None = None,
    ):
        # P2DocumentRuleEngine은
        # P1DocumentRuleEngine → 기존 DocumentRuleEngine을 상속하므로
        # MVP + P1 결정형 동작을 유지하면서 P2-A Handler만 추가한다.
        self.rule_engine = P2DocumentRuleEngine(
            list(rules),
            required_deliverables=required_deliverables,
        )

        # P2CAIEngine은 기존 DocumentAIEngine을 유지하면서
        # FP-006에만 구조형 FP 후보 사전분석을 추가한다.
        self.ai_engine = P2CAIEngine(
            rules,
            ai_provider,
        )

        # P2CHybridEngine은
        # P2BHybridEngine → P1FPHybridEngine → P1GovernanceHybridEngine →
        # P1AuditHybridEngine → P1RequirementHybridEngine → DocumentHybridEngine을
        # 상속하므로 기존 MVP/P1/P2-B Hybrid 동작을 유지하면서 P2-C만 추가한다.
        self.hybrid_engine = P2CHybridEngine(
            rules,
            ai_provider,
        )

    def prepare_documents(self, documents: list[ParsedDocument]) -> None:
        """업로드 문서 전체를 교차문서 Hybrid Rule에 전달한다."""
        self.hybrid_engine.prepare_documents(documents)

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
