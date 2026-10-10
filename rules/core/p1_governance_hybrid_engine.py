"""P1-D AUD-020/AUD-022/AUD-023 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_audit_hybrid_engine import P1AuditHybridEngine
from rules.core.p1_governance_checks import (
    build_aud020_evidence,
    build_aud022_evidence,
    build_aud023_evidence,
)


class P1GovernanceHybridEngine(P1AuditHybridEngine):
    """P1-A/B/C 동작을 유지하면서 P1-D 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "AUD-020":
            evidence = build_aud020_evidence(document)
        elif rule.code == "AUD-022":
            evidence = build_aud022_evidence(document)
        elif rule.code == "AUD-023":
            evidence = build_aud023_evidence(document)
        else:
            return super().build_context(document, rule)

        return HybridInspectionContext(
            document=document,
            rule=rule,
            evidence=evidence,
        )
