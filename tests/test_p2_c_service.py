from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.inspection_service import InspectionService
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_p2_c_rules import get_p2_c_rules


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
                text=" | ".join(str(value) for value in row if value),
                sheet=sheet,
                location=f"{sheet} / 행 {index}",
                metadata={"cell_values": tuple(row)},
            )
            for index, row in enumerate(rows, start=1)
        ),
    )


def _rules(*codes):
    wanted = set(codes)
    return tuple(rule for rule in get_p2_c_rules() if rule.code in wanted)


def _run(service, monkeypatch, documents):
    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.xlsx")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: documents)
    return service.run(["dummy.xlsx"])


def test_chg008_service_calls_ai_once_with_change_and_design(monkeypatch):
    change = _doc(
        "변경관리대장.xlsx",
        [
            ("변경ID", "변경내용", "영향대상", "상태"),
            ("CH-01", "사용자 조회조건 변경", "화면설계", "승인"),
        ],
    )
    design = _doc(
        "화면설계서.xlsx",
        [("화면ID", "설명"), ("UI-001", "사용자 조회 화면")],
    )
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("CHG-008"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [change, design])

    assert len(provider.calls) == 1
    assert provider.calls[0][1].code == "CHG-008"
    assert provider.calls[0][2] is not None and provider.calls[0][2].evidence
    assert any(issue.rule_code == "CHG-008" for issue in summary.issues)


def test_chg010_service_skips_ai_without_data_design_document(monkeypatch):
    change = _doc(
        "변경관리대장.xlsx",
        [
            ("변경ID", "변경내용", "영향대상", "상태"),
            ("CH-02", "사용자 테이블 컬럼 추가", "데이터설계", "승인"),
        ],
    )
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("CHG-010"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [change])

    assert provider.calls == []
    assert all(issue.rule_code != "CHG-010" for issue in summary.issues)


def test_fp011_service_calls_ai_only_when_change_and_fp_are_together(monkeypatch):
    change = _doc(
        "변경관리대장.xlsx",
        [
            ("변경ID", "변경내용", "영향대상", "상태"),
            ("CH-10", "신규 조회 기능 추가", "기능/FP", "승인"),
        ],
    )
    fp = _doc(
        "기능점수산정표.xlsx",
        [("기능명", "FP유형"), ("사용자 조회", "EQ")],
    )
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("FP-011"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [change, fp])

    assert len(provider.calls) == 1
    assert provider.calls[0][1].code == "FP-011"
    assert any(issue.rule_code == "FP-011" for issue in summary.issues)


def test_fp006_service_uses_structured_candidate(monkeypatch):
    fp = _doc(
        "기능점수산정표.xlsx",
        [
            ("기능명", "FP유형", "기능설명"),
            ("사용자 등록", "EI", "사용자 정보를 처리한다"),
            ("사용자 조회", "EI", "사용자 정보를 처리한다"),
        ],
    )
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("FP-006"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [fp])

    assert len(provider.calls) == 1
    assert provider.calls[0][1].code == "FP-006"
    assert provider.calls[0][2] is not None and provider.calls[0][2].evidence
    assert any(issue.rule_code == "FP-006" for issue in summary.issues)
