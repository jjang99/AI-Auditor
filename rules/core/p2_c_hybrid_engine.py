"""P2-C CHG-008/CHG-010/FP-011 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p2_b_hybrid_engine import P2BHybridEngine
from rules.core.p2_c_checks import (
    build_chg008_cross_document_evidence,
    build_chg010_cross_document_evidence,
    build_fp011_cross_document_evidence,
)


class P2CHybridEngine(P2BHybridEngine):
    """기존 MVP/P1/P2-B Hybrid 동작을 유지하면서 P2-C를 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code in {"CHG-008", "CHG-010", "FP-011"}:
            if not self._is_cross_document_anchor(document):
                return HybridInspectionContext(document=document, rule=rule, evidence=())

            if rule.code == "CHG-008":
                evidence = build_chg008_cross_document_evidence(list(self._document_set))
            elif rule.code == "CHG-010":
                evidence = build_chg010_cross_document_evidence(list(self._document_set))
            else:
                evidence = build_fp011_cross_document_evidence(list(self._document_set))

            return self._cross_document_context(rule, evidence)

        return super().build_context(document, rule)
