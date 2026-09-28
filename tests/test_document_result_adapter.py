from pathlib import Path

from app.parsers.models import ParsedDocument
from rules.core.ai_provider import AIInspectionResult
from rules.core.document_result_adapter import (
    adapt_ai_result,
    adapt_document_issue,
)
from rules.core.models import (
    DocumentRule,
    DocumentRuleIssue,
    RuleExecutionType,
)


def test_adapt_document_issue_to_rule_issue():
    issue = DocumentRuleIssue(
        rule_code="REQ-001",
        rule_name="요구사항 ID 누락·중복 점검",
        category="요구사항 정합성",
        severity="High",
        file_path="sample.docx",
        block_type="paragraph",
        evidence="요구사항 ID 누락 후보",
        description="ID 미부여 및 중복 여부",
        location="문단 3",
        page=2,
    )

    adapted = adapt_document_issue(issue)

    assert adapted.rule_code == "REQ-001"
    assert adapted.rule_name == "요구사항 ID 누락·중복 점검"
    assert adapted.category == "요구사항 정합성"
    assert adapted.severity == "High"
    assert adapted.file_path == "sample.docx"
    assert adapted.line_number == 0
    assert "문단 3" in adapted.evidence
    assert "page 2" in adapted.evidence
    assert "요구사항 ID 누락 후보" in adapted.evidence


def test_adapt_ai_result_creates_issue_for_each_finding():
    document = ParsedDocument(
        file_path=Path("sample.docx"),
        file_type="docx",
        blocks=(),
    )

    rule = DocumentRule(
        code="REQ-002",
        name="요구사항 내용 중복 점검",
        category="요구사항 정합성",
        execution_type=RuleExecutionType.AI,
        severity="Medium",
        description="표현은 다르지만 의미가 같은 요구사항 후보",
    )

    result = AIInspectionResult(
        rule_code="REQ-002",
        findings=(
            "REQ-001과 REQ-005의 의미가 유사함",
            "REQ-003과 REQ-008의 의미가 유사함",
        ),
        execution_type="AI",
        provider_name="FakeProvider",
    )

    adapted = adapt_ai_result(
        result,
        document,
        rule,
    )

    assert len(adapted) == 2

    assert adapted[0].rule_code == "REQ-002"
    assert adapted[0].rule_name == "요구사항 내용 중복 점검"
    assert adapted[0].category == "요구사항 정합성"
    assert adapted[0].severity == "Medium"
    assert adapted[0].file_path == "sample.docx"
    assert adapted[0].line_number == 0
    assert adapted[0].evidence == "REQ-001과 REQ-005의 의미가 유사함"

    assert adapted[1].evidence == "REQ-003과 REQ-008의 의미가 유사함"


def test_adapt_ai_result_with_no_findings_creates_no_issue():
    document = ParsedDocument(
        file_path=Path("sample.docx"),
        file_type="docx",
        blocks=(),
    )

    rule = DocumentRule(
        code="AI-005",
        name="AI 출력 신뢰성·환각 대응 점검",
        category="AI 특화 검증",
        execution_type=RuleExecutionType.AI,
        severity="High",
        description="정확성·근거성 검증과 허위/환각 대응",
    )

    result = AIInspectionResult(
        rule_code="AI-005",
        findings=(),
    )

    adapted = adapt_ai_result(
        result,
        document,
        rule,
    )

    assert adapted == ()