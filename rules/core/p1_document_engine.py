"""P1 결정형 Rule용 DocumentRuleEngine 확장.

기존 MVP DocumentRuleEngine은 그대로 유지하고, P1 Rule만 이 확장 Engine에서
추가 처리한다. P1 Rule이 Registry에 등록되기 전까지 제품 실행에는 사용되지 않는다.
"""

from app.parsers.models import ParsedDocument
from rules.core.document_engine import DocumentRuleEngine
from rules.core.models import DocumentRule, DocumentRuleIssue
from rules.core.p1_deliverable_status import find_deliverable_status_gaps
from rules.core.p1_rule_checks import (
    find_fp_detail_gaps,
    find_open_test_defects,
    find_test_plan_gaps,
)


class P1DocumentRuleEngine(DocumentRuleEngine):
    """기존 MVP Rule 처리에 P1 결정형 Handler를 추가한다."""

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[DocumentRuleIssue, ...]:
        issues = list(super().inspect_document(document))

        for rule in self.rules:
            if rule.code == "AUD-014":
                issues.extend(self._adapt_findings(document, rule, find_test_plan_gaps(document)))
            elif rule.code == "AUD-016":
                issues.extend(self._adapt_findings(document, rule, find_open_test_defects(document)))
            elif rule.code == "FP-008":
                issues.extend(self._adapt_findings(document, rule, find_fp_detail_gaps(document)))

        return tuple(issues)

    def inspect_documents(
        self,
        documents: list[ParsedDocument],
    ) -> tuple[DocumentRuleIssue, ...]:
        # 부모 구현은 AUD-001 set-level 검사 후 self.inspect_document()를 호출하므로
        # 기존 MVP Rule과 P1 per-document Rule을 그대로 모두 유지한다.
        issues = list(super().inspect_documents(documents))

        for rule in self.rules:
            if rule.code != "AUD-008":
                continue

            for finding in find_deliverable_status_gaps(documents):
                issues.append(
                    DocumentRuleIssue(
                        rule_code=rule.code,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        file_path=finding.file_path,
                        block_type=finding.block_type,
                        evidence=finding.evidence,
                        description=rule.description,
                        location=finding.location,
                        page=finding.page,
                        sheet=finding.sheet,
                        slide=finding.slide,
                    )
                )

        return tuple(issues)

    @staticmethod
    def _adapt_findings(document, rule: DocumentRule, findings):
        return tuple(
            DocumentRuleIssue(
                rule_code=rule.code,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                file_path=str(document.file_path),
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
