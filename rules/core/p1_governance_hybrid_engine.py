"""P1-D AUD-020/AUD-022/AUD-023 Hybrid 확장 Engine."""

from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_audit_hybrid_engine import P1AuditHybridEngine
from rules.core.p1_governance_checks import (
    build_aud020_evidence,
    build_aud022_cross_document_evidence,
    build_aud023_cross_document_evidence,
)


class P1GovernanceHybridEngine(P1AuditHybridEngine):
    """P1-A/B/C 동작을 유지하면서 P1-D 사전분석을 추가한다."""

    def __init__(self, rules, provider):
        super().__init__(rules, provider)
        self._document_set: tuple[ParsedDocument, ...] = ()

    def prepare_documents(self, documents: list[ParsedDocument]) -> None:
        """검사 시작 시 업로드 문서 전체를 교차문서 Rule에 제공한다."""
        self._document_set = tuple(documents)

    def _is_cross_document_anchor(self, document: ParsedDocument) -> bool:
        return bool(self._document_set) and document is self._document_set[0]

    @staticmethod
    def _cross_document_context(
        rule: DocumentRule,
        evidence: tuple[str, ...],
    ) -> HybridInspectionContext:
        synthetic_document = ParsedDocument(
            file_path=Path(f"{rule.code}-cross-document.txt"),
            file_type="governance_comparison",
            blocks=tuple(
                DocumentBlock(
                    block_type="governance_case",
                    text=item,
                )
                for item in evidence
            ),
            metadata={
                "source": "cross_document_governance_evidence",
                "case_count": len(evidence),
            },
        )
        return HybridInspectionContext(
            document=synthetic_document,
            rule=rule,
            evidence=evidence,
        )

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "AUD-020":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_aud020_evidence(document),
            )

        if rule.code == "AUD-022":
            if not self._is_cross_document_anchor(document):
                return HybridInspectionContext(document=document, rule=rule, evidence=())
            return self._cross_document_context(
                rule,
                build_aud022_cross_document_evidence(list(self._document_set)),
            )

        if rule.code == "AUD-023":
            if not self._is_cross_document_anchor(document):
                return HybridInspectionContext(document=document, rule=rule, evidence=())
            return self._cross_document_context(
                rule,
                build_aud023_cross_document_evidence(list(self._document_set)),
            )

        return super().build_context(document, rule)
