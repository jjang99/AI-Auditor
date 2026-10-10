from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.inspection_service import InspectionService
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_p1_governance_rules import get_p1_governance_rules


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


def _text_document(name, lines):
    return ParsedDocument(
        file_path=Path(name),
        file_type="txt",
        blocks=tuple(
            DocumentBlock(
                block_type="paragraph",
                text=line,
                location=f"문단 {index}",
            )
            for index, line in enumerate(lines, start=1)
        ),
    )


def _rules(*codes):
    wanted = set(codes)
    return tuple(rule for rule in get_p1_governance_rules() if rule.code in wanted)


def _run(service, monkeypatch, documents):
    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.txt")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: documents)
    return service.run(["dummy.txt"])


def test_aud022_service_calls_ai_once_for_missing_cross_document_evidence(monkeypatch):
    contract = _text_document(
        "과업내용서.txt",
        ["사업자는 통합시험 결과보고서를 제출하여야 한다."],
    )
    unrelated = _text_document("회의록.txt", ["요구사항 회의 수행 완료"])

    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AUD-022"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [contract, unrelated])

    assert len(provider.calls) == 1
    document, rule, context = provider.calls[0]
    assert rule.code == "AUD-022"
    assert document.file_type == "governance_comparison"
    assert context is not None and context.evidence
    assert "통합시험 결과보고서" in context.evidence[0]
    assert any(issue.rule_code == "AUD-022" for issue in summary.issues)


def test_aud022_service_skips_ai_when_related_evidence_exists(monkeypatch):
    contract = _text_document(
        "과업내용서.txt",
        ["사업자는 통합시험 결과보고서를 제출하여야 한다."],
    )
    evidence = _text_document(
        "통합시험결과보고서.txt",
        ["통합시험 결과보고서 제출 완료 및 검토를 수행하였다."],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AUD-022"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [contract, evidence])

    assert provider.calls == []
    assert all(issue.rule_code != "AUD-022" for issue in summary.issues)


def test_aud023_service_calls_ai_once_for_missing_cross_document_evidence(monkeypatch):
    design = _text_document("설계서.txt", ["웹접근성 표준을 적용하여야 한다."])
    unrelated = _text_document("회의록.txt", ["인터페이스 검토를 완료하였다."])

    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AUD-023"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [design, unrelated])

    assert len(provider.calls) == 1
    document, rule, context = provider.calls[0]
    assert rule.code == "AUD-023"
    assert document.file_type == "governance_comparison"
    assert context is not None and context.evidence
    assert "웹접근성" in context.evidence[0]
    assert any(issue.rule_code == "AUD-023" for issue in summary.issues)


def test_aud023_service_skips_ai_when_compliance_evidence_exists(monkeypatch):
    design = _text_document("설계서.txt", ["웹접근성 표준을 적용하여야 한다."])
    evidence = _text_document(
        "웹접근성점검결과.txt",
        ["웹접근성 점검 결과 적합 판정을 확인하였다."],
    )

    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AUD-023"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [design, evidence])

    assert provider.calls == []
    assert all(issue.rule_code != "AUD-023" for issue in summary.issues)
