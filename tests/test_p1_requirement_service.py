from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.inspection_service import InspectionService
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_p1_req_rules import get_p1_requirement_rules


class RecordingProvider(BaseAIProvider):
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=("REQ-012 테스트 지적",),
            raw_response="test",
        )


def _sheet_document(name, rows, sheet="Sheet1"):
    blocks = tuple(
        DocumentBlock(
            block_type="sheet_row",
            text=" | ".join(value for value in row if value),
            sheet=sheet,
            location=f"{sheet} / 행 {index}",
            metadata={"cell_values": tuple(row)},
        )
        for index, row in enumerate(rows, start=1)
    )
    return ParsedDocument(
        file_path=Path(name),
        file_type="xlsx",
        blocks=blocks,
    )


def _req012_rule():
    return tuple(rule for rule in get_p1_requirement_rules() if rule.code == "REQ-012")


def test_req012_service_calls_ai_once_for_cross_document_missing_test_link(monkeypatch):
    requirement = _sheet_document(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "요구사항내용", "시험ID"),
            ("REQ-101", "로그인 기능을 제공한다", ""),
        ],
    )
    test_document = _sheet_document(
        "통합시험.xlsx",
        [
            ("시험ID", "시험항목", "요구사항ID"),
            ("T-001", "조회 시험", "REQ-999"),
        ],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_req012_rule(), ai_provider=provider)

    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: [requirement, test_document])

    _inspection_id, summary = service.run(["dummy.xlsx"])

    assert len(provider.calls) == 1
    document, rule, context = provider.calls[0]
    assert rule.code == "REQ-012"
    assert document.file_type == "requirement_test_comparison"
    assert context is not None
    assert context.evidence
    assert "REQ-101" in context.evidence[0]
    assert any(issue.rule_code == "REQ-012" for issue in summary.issues)


def test_req012_service_does_not_call_ai_without_test_documents(monkeypatch):
    requirement = _sheet_document(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "요구사항내용", "시험ID"),
            ("REQ-101", "로그인 기능을 제공한다", ""),
        ],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_req012_rule(), ai_provider=provider)

    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: [requirement])

    _inspection_id, summary = service.run(["dummy.xlsx"])

    assert provider.calls == []
    assert all(issue.rule_code != "REQ-012" for issue in summary.issues)


def test_req012_service_does_not_call_ai_when_test_document_has_requirement_link(monkeypatch):
    requirement = _sheet_document(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "요구사항내용", "시험ID"),
            ("REQ-101", "로그인 기능을 제공한다", "T-001"),
        ],
    )
    test_document = _sheet_document(
        "통합시험.xlsx",
        [
            ("시험ID", "시험항목", "요구사항ID"),
            ("T-001", "로그인 시험", "REQ-101"),
        ],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_req012_rule(), ai_provider=provider)

    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: [requirement, test_document])

    _inspection_id, summary = service.run(["dummy.xlsx"])

    assert provider.calls == []
    assert all(issue.rule_code != "REQ-012" for issue in summary.issues)
