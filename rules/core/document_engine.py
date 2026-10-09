import re

from app.parsers.models import ParsedDocument
from rules.core.deliverable_baseline import (
    DeliverableRequirement,
    deliverable_matches_file,
    derive_required_deliverables,
)
from rules.core.fp_calculator import find_fp_mismatches
from rules.core.models import (
    DocumentRule,
    DocumentRuleIssue,
    RuleExecutionType,
)


def _is_requirement_document(document: ParsedDocument) -> bool:
    """REQ 계열의 문서 자체에만 요구사항 ID Rule을 적용한다."""
    name = document.file_path.stem.lower()
    return any(
        marker in name
        for marker in ("요구사항", "requirement", "requirements", "srs")
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

        # 외부에서 명시적으로 전달한 목록은 기존 호환용/테스트용으로 유지한다.
        # 실제 제품 경로에서는 업로드된 산출물목록/테일러링 대비표에서 자동 도출한다.
        self.required_deliverables = required_deliverables or []

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[DocumentRuleIssue, ...]:
        issues: list[DocumentRuleIssue] = []

        for rule in self.rules:
            if rule.code == "REQ-001":
                if _is_requirement_document(document):
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

    def _aud_001_baseline(
        self,
        documents: list[ParsedDocument],
    ) -> tuple[DeliverableRequirement, ...]:
        """AUD-001의 필수 산출물 기준을 결정한다.

        우선순위:
        1. 테스트/외부 호출에서 명시한 required_deliverables
        2. 실제 업로드된 산출물목록/테일러링 대비표

        기준문서를 찾지 못하면 임의 표준목록을 만들지 않는다.
        """
        if self.required_deliverables:
            return tuple(
                DeliverableRequirement(
                    name=deliverable,
                    source_file="explicit_required_deliverables",
                    source_kind="explicit",
                )
                for deliverable in self.required_deliverables
            )

        return derive_required_deliverables(documents)

    def _inspect_aud_001(
        self,
        documents: list[ParsedDocument],
        rule: DocumentRule,
    ) -> tuple[DocumentRuleIssue, ...]:
        """AUD-001 필수 산출물 누락 점검."""
        issues: list[DocumentRuleIssue] = []
        baseline = self._aud_001_baseline(documents)

        # 산출물목록/테일러링 대비표가 없고 외부 기준도 없으면
        # 임의의 표준 산출물을 가정하지 않아 오탐을 방지한다.
        if not baseline:
            return ()

        uploaded_paths = [document.file_path for document in documents]

        for requirement in baseline:
            if any(
                deliverable_matches_file(requirement.name, uploaded_path)
                for uploaded_path in uploaded_paths
            ):
                continue

            source_name = (
                requirement.source_file
                if requirement.source_kind != "explicit"
                else "명시적 필수 산출물 기준"
            )
            evidence = f"필수 산출물 누락: {requirement.name}"
            if requirement.source_kind != "explicit":
                evidence += f" (기준: {source_name})"

            issues.append(
                DocumentRuleIssue(
                    rule_code=rule.code,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    file_path=requirement.source_file,
                    block_type="document_set",
                    evidence=evidence,
                    description=rule.description,
                    location=requirement.location or requirement.name,
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

        # 일반 REQ-001 형식과 실제 사업 산출물의 SFR-043-ID-02,
        # UI-SFR-043-ID-01-001 같은 요구사항 계층형 ID를 함께 인정한다.
        requirement_id_pattern = re.compile(
            r"\b(?:REQ-\d+|(?:UI-)?[A-Z]{2,}-\d+-ID-\d+(?:-\d+)*)\b",
            re.IGNORECASE,
        )

        requirement_keywords = (
            "해야 한다",
            "하여야 한다",
            "제공한다",
            "지원한다",
            "처리한다",
            "조회한다",
            "수정한다",
            "가능해야 한다",
            "할 수 있어야 한다",
        )

        # 단순 참조/목차/ID 단독 반복은 중복 요구사항 정의가 아니다.
        # 동일 ID가 서로 다른 실질 요구사항 문장에 붙은 경우만 중복으로 본다.
        requirement_definition_texts: dict[str, set[str]] = {}

        for block in document.blocks:
            text = block.text.strip()

            if not text:
                continue

            matches = [
                match.upper()
                for match in requirement_id_pattern.findall(text)
            ]

            has_requirement_keyword = any(
                keyword in text
                for keyword in requirement_keywords
            )

            has_requirement_id = bool(matches)

            if has_requirement_keyword and has_requirement_id:
                normalized_text = " ".join(text.split()).lower()
                for requirement_id in matches:
                    requirement_definition_texts.setdefault(
                        requirement_id,
                        set(),
                    ).add(normalized_text)

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

        duplicate_ids = sorted(
            requirement_id
            for requirement_id, definition_texts in requirement_definition_texts.items()
            if len(definition_texts) > 1
        )

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
        """FP-009 FP 산정값 재계산 검증.

        실제 XLS/XLSX FP 산정표에서는 기능유형 + 복잡도 또는 RET/FTR·DET +
        기능개수 + 보고 FP를 이용해 재계산한다. 기존 한 줄 덧셈 산식 검증은
        호환용으로 유지한다.
        """
        issues: list[DocumentRuleIssue] = []

        # 1) 실제 FP 표 구조 기반 재계산
        for mismatch in find_fp_mismatches(document):
            issues.append(
                DocumentRuleIssue(
                    rule_code=rule.code,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    file_path=str(document.file_path),
                    block_type="sheet_row",
                    evidence=(
                        "FP 산정값 불일치: "
                        f"{mismatch.function_type}/{mismatch.complexity}, "
                        f"기능개수 {mismatch.count:g}, "
                        f"보고값 {mismatch.reported_fp:g} FP, "
                        f"재계산 결과 {mismatch.calculated_fp:g} FP "
                        f"(근거: {mismatch.basis})"
                    ),
                    description=rule.description,
                    location=mismatch.location,
                    sheet=mismatch.sheet,
                )
            )

        # 2) 기존 텍스트 한 줄 산식 검증도 유지
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
