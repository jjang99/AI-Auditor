from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.inspection_service import InspectionService
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_p1_audit_rules import get_p1_audit_rules


class RecordingProvider(BaseAIProvider):
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=("AUD-018 테스트 지적",),
            raw_response="test",
        )


def _sheet_document(name, rows, sheet="Sheet1"):
    return ParsedDocument(
        file_path=Path(name),
        file_type="xlsx",
        blocks=tuple(
            DocumentBlock(
                block_type="sheet_row",
                text=" | ".join(str(value) for value in row if value),
                sheet=sheet,
                location=f"{sheet} / 행 {index}",
                metadata={"cell_values": tuple(row)},
            )
            for index, row in enumerate(rows, start=1)
        ),
    )


def _aud018_rule():
    return tuple(rule for rule in get_p1_audit_rules() if rule.code == "AUD-018")


def test_aud018_service_calls_ai_for_missing_execution_evidence(monkeypatch):
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("설계 품질점검", "2026-10-01", "완료"),
        ],
    )
    result = _sheet_document(
        "품질활동결과.xlsx",
        [
            ("활동명", "결과"),
            ("요구사항 검토", "완료"),
        ],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_aud018_rule(), ai_provider=provider)

    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: [plan, result])

    _inspection_id, summary = service.run(["dummy.xlsx"])

    assert len(provider.calls) == 1
    document, rule, context = provider.calls[0]
    assert rule.code == "AUD-018"
    assert document.file_type == "quality_activity_comparison"
    assert context is not None
    assert context.evidence
    assert "설계 품질점검" in context.evidence[0]
    assert any(issue.rule_code == "AUD-018" for issue in summary.issues)


def test_aud018_service_does_not_call_ai_without_execution_document(monkeypatch):
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("설계 품질점검", "2026-10-01", "완료"),
        ],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_aud018_rule(), ai_provider=provider)

    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: [plan])

    _inspection_id, summary = service.run(["dummy.xlsx"])

    assert provider.calls == []
    assert all(issue.rule_code != "AUD-018" for issue in summary.issues)


def test_aud018_service_does_not_call_ai_when_activity_has_evidence(monkeypatch):
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("요구사항 검토", "2026-10-01", "완료"),
        ],
    )
    result = _sheet_document(
        "품질활동결과.xlsx",
        [
            ("활동명", "결과"),
            ("요구사항 검토", "완료"),
        ],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_aud018_rule(), ai_provider=provider)

    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: [plan, result])

    _inspection_id, summary = service.run(["dummy.xlsx"])

    assert provider.calls == []
    assert all(issue.rule_code != "AUD-018" for issue in summary.issues)
