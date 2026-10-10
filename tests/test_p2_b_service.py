from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.inspection_service import InspectionService
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_p2_b_rules import get_p2_b_rules


class RecordingProvider(BaseAIProvider):
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=(f"{rule.code} 테스트 지적",),
            raw_response="test",
        )


def _doc(name, rows, sheet="Sheet1"):
    return ParsedDocument(
        file_path=Path(name),
        file_type="xlsx",
        blocks=tuple(
            DocumentBlock(
                block_type="sheet_row",
                text=" | ".join(str(v) for v in row if v),
                sheet=sheet,
                location=f"{sheet} / 행 {index}",
                metadata={"cell_values": tuple(row)},
            )
            for index, row in enumerate(rows, start=1)
        ),
    )


def _rules(*codes):
    wanted = set(codes)
    return tuple(rule for rule in get_p2_b_rules() if rule.code in wanted)


def _run(service, monkeypatch, documents):
    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: documents)
    return service.run(["dummy.xlsx"])


def test_aud005_service_runs_once_as_cross_document_ai(monkeypatch):
    left = _doc(
        "요구사항정의서.xlsx",
        [("요구사항ID", "요구사항명"), ("SFR-001", "사용자 조회")],
    )
    right = _doc(
        "화면설계서.xlsx",
        [("요구사항ID", "요구사항명"), ("SFR-001", "회원 조회")],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AUD-005"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [left, right])

    assert len(provider.calls) == 1
    document, rule, context = provider.calls[0]
    assert rule.code == "AUD-005"
    assert document.file_type == "terminology_comparison"
    assert context is not None and context.evidence
    assert any(issue.rule_code == "AUD-005" for issue in summary.issues)


def test_aud005_service_skips_ai_without_cross_document_candidate(monkeypatch):
    left = _doc(
        "요구사항정의서.xlsx",
        [("요구사항ID", "요구사항명"), ("SFR-001", "사용자 조회")],
    )
    right = _doc(
        "화면설계서.xlsx",
        [("요구사항ID", "요구사항명"), ("SFR-001", "사용자 조회")],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AUD-005"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [left, right])

    assert provider.calls == []
    assert all(issue.rule_code != "AUD-005" for issue in summary.issues)


def test_req028_runs_after_confirmed_requirement_issue(monkeypatch):
    document = _doc(
        "요구사항정의서.xlsx",
        [("요구사항ID", "상태", "승인상태"), ("SFR-001", "완료", "미승인")],
    )

    provider = RecordingProvider()
    service = InspectionService(
        rules=_rules("REQ-021", "REQ-028"),
        ai_provider=provider,
    )

    _inspection_id, summary = _run(service, monkeypatch, [document])

    assert [call[1].code for call in provider.calls] == ["REQ-021", "REQ-028"]
    synthesis_document, synthesis_rule, synthesis_context = provider.calls[1]
    assert synthesis_rule.code == "REQ-028"
    assert synthesis_document.file_type == "inspection_findings"
    assert synthesis_context is not None and synthesis_context.evidence
    assert "REQ-021" in synthesis_context.evidence[0]
    assert any(issue.rule_code == "REQ-028" for issue in summary.issues)


def test_req028_does_not_run_without_source_requirement_issue(monkeypatch):
    document = _doc(
        "요구사항정의서.xlsx",
        [("요구사항ID", "상태", "승인상태"), ("SFR-001", "완료", "승인")],
    )

    provider = RecordingProvider()
    service = InspectionService(
        rules=_rules("REQ-021", "REQ-028"),
        ai_provider=provider,
    )

    _inspection_id, summary = _run(service, monkeypatch, [document])

    assert provider.calls == []
    assert all(issue.rule_code != "REQ-028" for issue in summary.issues)
