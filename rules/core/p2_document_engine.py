"""P2-A 결정형 Rule용 DocumentRuleEngine 확장."""

from app.parsers.models import ParsedDocument
from rules.core.models import DocumentRule, DocumentRuleIssue
from rules.core.p1_document_engine import P1DocumentRuleEngine
from rules.core.p2_a_checks import (
    find_ai_resource_limit_gaps,
    find_fp_method_basis_gaps,
    find_important_requirement_test_gaps,
    find_invalid_requirement_references,
    find_open_quality_findings,
    find_test_execution_result_gaps,
    find_unapproved_applied_changes,
)


class P2DocumentRuleEngine(P1DocumentRuleEngine):
    """기존 MVP + P1 결정형 Rule을 유지하면서 P2-A만 추가한다."""

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[DocumentRuleIssue, ...]:
        issues = list(super().inspect_document(document))

        for rule in self.rules:
            if rule.code == "AUD-015":
                findings = find_test_execution_result_gaps(document)
            elif rule.code == "AUD-019":
                findings = find_open_quality_findings(document)
            elif rule.code == "CHG-005":
                findings = find_unapproved_applied_changes(document)
            elif rule.code == "FP-007":
                findings = find_fp_method_basis_gaps(document)
            elif rule.code == "AI-023":
                findings = find_ai_resource_limit_gaps(document)
            else:
                continue

            issues.extend(self._adapt_findings(document, rule, findings))

        return tuple(issues)

    def inspect_documents(
        self,
        documents: list[ParsedDocument],
    ) -> tuple[DocumentRuleIssue, ...]:
        issues = list(super().inspect_documents(documents))

        rule_by_code = {rule.code: rule for rule in self.rules}

        req016 = rule_by_code.get("REQ-016")
        if req016 is not None:
            issues.extend(
                self._adapt_set_findings(
                    req016,
                    find_important_requirement_test_gaps(documents),
                )
            )

        req020 = rule_by_code.get("REQ-020")
        if req020 is not None:
            issues.extend(
                self._adapt_set_findings(
                    req020,
                    find_invalid_requirement_references(documents),
                )
            )

        return tuple(issues)

    @staticmethod
    def _adapt_set_findings(rule: DocumentRule, findings):
        return tuple(
            DocumentRuleIssue(
                rule_code=rule.code,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                file_path=finding.location or "document_set",
                block_type=finding.block_type,
                evidence=finding.evidence,
                description=rule.description,
                location=finding.location,
                page=finding.page,
                sheet=finding.sheet,
                slide=finding.slide,
            )
            for finding in findings
        )
