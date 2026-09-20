import re

from app.parsers.models import ParsedDocument
from rules.core.models import (
    DocumentRule,
    DocumentRuleIssue,
    RuleExecutionType,
)


class DocumentRuleEngine:
    """ParsedDocument를 대상으로 deterministic 문서 Rule 검사를 수행한다."""

    def __init__(
        self,
        rules: list[DocumentRule],
        required_deliverables: list[str] | None = None,
    ):
        self.rules = [
            rule
            for rule in rules
            if rule.enabled
            and rule.execution_type == RuleExecutionType.RULE
        ]

        self.required_deliverables = required_deliverables or []

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[DocumentRuleIssue, ...]:
        issues: list[DocumentRuleIssue] = []

        for rule in self.rules:
            if rule.code == "REQ-001":
                issues.extend(
                    self._inspect_req_001(document, rule)
                )

            elif rule.code == "FP-009":
                issues.extend(
                    self._inspect_fp_009(document, rule)
                )

        return tuple(issues)

    def inspect_documents(
        self,
        documents: list[ParsedDocument],
    ) -> tuple[DocumentRuleIssue, ...]:
        issues: list[DocumentRuleIssue] = []

        for rule in self.rules:
            if rule.code == "AUD-001":
                issues.extend(
                    self._inspect_aud_001(documents, rule)
                )

        for document in documents:
            issues.extend(
                self.inspect_document(document)
            )

        return tuple(issues)

    def _inspect_aud_001(
        self,
        documents: list[ParsedDocument],
        rule: DocumentRule,
    ) -> tuple[DocumentRuleIssue, ...]:
        """AUD-001 필수 산출물 누락 점검."""
        issues: list[DocumentRuleIssue] = []

        uploaded_names = [
            document.file_path.stem.lower()
            for document in documents
        ]

        missing_deliverables = [
            deliverable
            for deliverable in self.required_deliverables
            if not any(
                deliverable.lower() in uploaded_name
                for uploaded_name in uploaded_names
            )
        ]

        for deliverable in missing_deliverables:
            issues.append(
                DocumentRuleIssue(
                    rule_code=rule.code,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    file_path="",
                    block_type="document_set",
                    evidence=f"필수 산출물 누락: {deliverable}",
                    description=rule.description,
                    location=deliverable,
                )
            )

        return tuple(issues)

    def _inspect_req_001(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> tuple[DocumentRuleIssue, ...]:
        """REQ-001 요구사항 ID 누락·중복 점검."""
        issues: list[DocumentRuleIssue] = []

        requirement_id_pattern = re.compile(
            r"\bREQ-\d+\b",
            re.IGNORECASE,
        )

        requirement_keywords = (
            "해야 한다",
            "하여야 한다",
            "제공한다",
            "지원한다",
            "처리한다",
            "가능해야 한다",
            "할 수 있어야 한다",
        )

        requirement_ids: list[str] = []

        for block in document.blocks:
            text = block.text.strip()

            if not text:
                continue

            matches = requirement_id_pattern.findall(text)

            requirement_ids.extend(
                match.upper()
                for match in matches
            )

            has_requirement_keyword = any(
                keyword in text
                for keyword in requirement_keywords
            )

            has_requirement_id = bool(
                requirement_id_pattern.search(text)
            )

            if has_requirement_keyword and not has_requirement_id:
                issues.append(
                    DocumentRuleIssue(
                        rule_code=rule.code,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        file_path=str(document.file_path),
                        block_type=block.block_type,
                        evidence=f"요구사항 ID 누락 후보: {text[:200]}",
                        description=rule.description,
                        location=block.location,
                        page=block.page,
                        sheet=block.sheet,
                        slide=block.slide,
                    )
                )

        duplicate_ids = sorted({
            requirement_id
            for requirement_id in requirement_ids
            if requirement_ids.count(requirement_id) > 1
        })

        for duplicate_id in duplicate_ids:
            issues.append(
                DocumentRuleIssue(
                    rule_code=rule.code,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    file_path=str(document.file_path),
                    block_type="document",
                    evidence=f"중복 요구사항 ID: {duplicate_id}",
                    description=rule.description,
                    location=duplicate_id,
                )
            )

        return tuple(issues)

    def _inspect_fp_009(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> tuple[DocumentRuleIssue, ...]:
        """FP-009 FP 산정값 재계산 검증."""
        issues: list[DocumentRuleIssue] = []

        fp_expression_pattern = re.compile(
            r"(?:총\s*)?FP\s*[:=]?\s*"
            r"((?:\d+(?:\.\d+)?\s*\+\s*)+\d+(?:\.\d+)?)"
            r"\s*=\s*(\d+(?:\.\d+)?)",
            re.IGNORECASE,
        )

        for block in document.blocks:
            text = block.text.strip()

            if not text:
                continue

            for match in fp_expression_pattern.finditer(text):
                expression = match.group(1)
                reported_value = float(match.group(2))

                values = [
                    float(value.strip())
                    for value in expression.split("+")
                ]

                calculated_value = sum(values)

                if abs(calculated_value - reported_value) < 0.000001:
                    continue

                issues.append(
                    DocumentRuleIssue(
                        rule_code=rule.code,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        file_path=str(document.file_path),
                        block_type=block.block_type,
                        evidence=(
                            f"FP 산정값 불일치: "
                            f"{expression} = {reported_value:g}, "
                            f"재계산 결과 = {calculated_value:g}"
                        ),
                        description=rule.description,
                        location=block.location,
                        page=block.page,
                        sheet=block.sheet,
                        slide=block.slide,
                    )
                )

        return tuple(issues)
