"""P2-D AI-003/008/013/017/021 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p2_c_hybrid_engine import P2CHybridEngine
from rules.core.p2_d_checks import (
    build_ai003_evidence,
    build_ai008_evidence,
    build_ai013_evidence,
    build_ai017_evidence,
    build_ai021_evidence,
)


class P2DHybridEngine(P2CHybridEngine):
    """기존 Hybrid 동작을 유지하면서 P2-D AI 특화 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "AI-003":
            evidence = build_ai003_evidence(document)
        elif rule.code == "AI-008":
            evidence = build_ai008_evidence(document)
        elif rule.code == "AI-013":
            evidence = build_ai013_evidence(document)
        elif rule.code == "AI-017":
            evidence = build_ai017_evidence(document)
        elif rule.code == "AI-021":
            evidence = build_ai021_evidence(document)
        else:
            return super().build_context(document, rule)

        return HybridInspectionContext(
            document=document,
            rule=rule,
            evidence=evidence,
        )
