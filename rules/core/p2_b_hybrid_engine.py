"""P2-B AUD-021/REQ-021/REQ-027 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_fp_hybrid_engine import P1FPHybridEngine
from rules.core.p2_b_checks import (
    build_aud021_cross_document_evidence,
    build_req021_evidence,
    build_req027_evidence,
)


class P2BHybridEngine(P1FPHybridEngine):
    """기존 MVP/P1 Hybrid 동작을 유지하면서 P2-B 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "AUD-021":
            if not self._is_cross_document_anchor(document):
                return HybridInspectionContext(document=document, rule=rule, evidence=())
            return self._cross_document_context(
                rule,
                build_aud021_cross_document_evidence(list(self._document_set)),
            )

        if rule.code == "REQ-021":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_req021_evidence(document),
            )

        if rule.code == "REQ-027":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_req027_evidence(document),
            )

        return super().build_context(document, rule)
