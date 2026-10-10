from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.core.inspection_engine import DocumentInspectionEngine
from rules.core.p1_requirement_hybrid_engine import P1RequirementHybridEngine
from rules.definitions.document_p1_req_rules import get_p1_requirement_rules


class RecordingProvider(BaseAIProvider):
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=(f"{rule.code} test finding",),
            raw_response="test",
        )


def _xlsx_document(name, rows, sheet="Sheet1"):
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


def _rule(code):
    return next(rule for rule in get_p1_requirement_rules() if rule.code == code)


def test_document_inspection_engine_uses_p1_requirement_hybrid_engine():
    provider = RecordingProvider()
    engine = DocumentInspectionEngine(get_p1_requirement_rules(), provider)

    assert isinstance(engine.hybrid_engine, P1RequirementHybridEngine)


def test_req007_detects_blank_verification_method():
    document = _xlsx_document(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "요구사항내용", "검증방법"),
            ("REQ-101", "사용자 로그인을 제공한다", ""),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-007"),), provider)

    result = engine.inspect_document(document)

    assert len(result) == 1
    assert len(provider.calls) == 1
    context = provider.calls[0][2]
    assert context is not None
    assert len(context.evidence) == 1
    assert "검증방법 공란" in context.evidence[0]
    assert "REQ-101" in context.evidence[0]


def test_req007_passes_defined_verification_method():
    document = _xlsx_document(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "요구사항내용", "검증방법"),
            ("REQ-101", "사용자 로그인을 제공한다", "통합시험으로 확인"),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-007"),), provider)

    result = engine.inspect_document(document)

    assert len(result) == 1
    assert result[0].findings == ()
    assert provider.calls == []


def test_req007_detects_unresolved_verification_method():
    document = _xlsx_document(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "요구사항내용", "검증방법"),
            ("REQ-101", "사용자 로그인을 제공한다", "추후 협의"),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-007"),), provider)

    engine.inspect_document(document)

    assert len(provider.calls) == 1
    assert "검증방법 미확정" in provider.calls[0][2].evidence[0]


def test_req012_detects_missing_test_reference_in_explicit_trace_table():
    document = _xlsx_document(
        "요구사항추적표.xlsx",
        [
            ("요구사항ID", "요구사항내용", "시험ID"),
            ("REQ-201", "로그인 기능", ""),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-012"),), provider)

    engine.inspect_document(document)

    assert len(provider.calls) == 1
    assert "시험항목 연결 누락 후보" in provider.calls[0][2].evidence[0]


def test_req012_ignores_non_test_target():
    document = _xlsx_document(
        "요구사항추적표.xlsx",
        [
            ("요구사항ID", "요구사항내용", "시험ID"),
            ("REQ-201", "운영 참고사항 시험대상아님", "N/A"),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-012"),), provider)

    result = engine.inspect_document(document)

    assert result[0].findings == ()
    assert provider.calls == []


def test_req017_detects_missing_required_trace_link():
    document = _xlsx_document(
        "요구사항추적표.xlsx",
        [
            ("요구사항ID", "설계ID", "시험ID"),
            ("REQ-301", "DES-001", ""),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-017"),), provider)

    engine.inspect_document(document)

    assert len(provider.calls) == 1
    evidence = provider.calls[0][2].evidence
    assert len(evidence) == 1
    assert "필수 추적링크 누락 후보" in evidence[0]
    assert "시험" in evidence[0]


def test_req017_ignores_na_and_separate_sheet_reference():
    document = _xlsx_document(
        "요구사항추적표.xlsx",
        [
            ("요구사항ID", "설계ID", "시험ID"),
            ("REQ-301", "N/A", "별도 시트 참고"),
        ],
    )
    provider = RecordingProvider()
    engine = P1RequirementHybridEngine((_rule("REQ-017"),), provider)

    result = engine.inspect_document(document)

    assert result[0].findings == ()
    assert provider.calls == []
