"""P1-E FP-002 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_fp_checks import build_fp002_evidence
from rules.core.p1_governance_hybrid_engine import P1GovernanceHybridEngine


class P1FPHybridEngine(P1GovernanceHybridEngine):
    """P1-A~D 동작을 유지하면서 FP-002 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "FP-002":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_fp002_evidence(document),
            )

        return super().build_context(document, rule)
