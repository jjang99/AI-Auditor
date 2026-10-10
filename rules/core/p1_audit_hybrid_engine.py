"""P1-C AUD-010 / AUD-018 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_audit_checks import build_aud010_evidence
from rules.core.p1_requirement_hybrid_engine import P1RequirementHybridEngine


class P1AuditHybridEngine(P1RequirementHybridEngine):
    """P1-B Hybrid 동작을 유지하면서 P1-C 계획/품질 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "AUD-010":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_aud010_evidence(document),
            )

        if rule.code == "AUD-018":
            # AUD-018은 전체 업로드 문서의 품질계획↔수행근거를 비교해야 하므로
            # 개별 문서 실행에서는 evidence를 만들지 않고 Service 후처리에서 수행한다.
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=(),
            )

        return super().build_context(document, rule)
