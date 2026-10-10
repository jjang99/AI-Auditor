"""P1-D AUD-020/AUD-022/AUD-023 Hybrid 확장 Engine."""

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_audit_hybrid_engine import P1AuditHybridEngine
from rules.core.p1_governance_checks import build_aud020_evidence


class P1GovernanceHybridEngine(P1AuditHybridEngine):
    """P1-A/B/C 동작을 유지하면서 P1-D 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "AUD-020":
            evidence = build_aud020_evidence(document)
        elif rule.code in {"AUD-022", "AUD-023"}:
            # 계약/과업 이행과 기준/지침 준수는 업로드 문서 전체를 함께 봐야 하므로
            # 개별 문서 Hybrid에서는 evidence를 만들지 않고 InspectionService에서
            # 교차문서 후처리로 실행한다.
            evidence = ()
        else:
            return super().build_context(document, rule)

        return HybridInspectionContext(
            document=document,
            rule=rule,
            evidence=evidence,
        )
