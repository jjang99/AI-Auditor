from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.core.inspection_engine import DocumentInspectionEngine
from rules.core.p1_fp_checks import build_fp002_evidence
from rules.core.p1_fp_hybrid_engine import P1FPHybridEngine
from rules.definitions.document_p1_fp_rules import get_p1_fp_rules


class RecordingProvider(BaseAIProvider):
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=("FP-002 테스트 지적",),
            raw_response="test",
        )


def _sheet_document(name, rows, sheet="FP산정"):
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


def test_engine_uses_p1_fp_hybrid_engine():
    engine = DocumentInspectionEngine(get_p1_fp_rules(), ai_provider=RecordingProvider())
    assert isinstance(engine.hybrid_engine, P1FPHybridEngine)


def test_fp002_normal_distinct_functions_pass():
    document = _sheet_document(
        "FP산정표.xlsx",
        [
            ("기능명", "FP유형", "설명"),
            ("사용자 조회", "EQ", "사용자 기본정보 조회"),
            ("사용자 등록", "EI", "사용자 신규정보 등록"),
        ],
    )

    assert build_fp002_evidence(document) == ()


def test_fp002_detects_clear_duplicate_candidate():
    document = _sheet_document(
        "FP산정표.xlsx",
        [
            ("기능명", "FP유형", "설명"),
            ("사용자 조회", "EQ", "사용자 기본정보 조회"),
            ("사용자 조회", "EQ", "사용자 기본정보 조회"),
        ],
    )

    evidence = build_fp002_evidence(document)

    assert len(evidence) == 1
    assert "사용자 조회" in evidence[0]
    assert "EQ" in evidence[0]


def test_fp002_same_name_but_distinct_details_is_not_candidate():
    document = _sheet_document(
        "FP산정표.xlsx",
        [
            ("기능명", "FP유형", "처리내용"),
            ("현황 조회", "EQ", "관리자용 전체 현황 조회"),
            ("현황 조회", "EQ", "일반사용자 본인 현황 조회"),
        ],
    )

    assert build_fp002_evidence(document) == ()


def test_fp002_ignores_summary_rows():
    document = _sheet_document(
        "FP산정표.xlsx",
        [
            ("기능명", "FP유형", "설명"),
            ("합계", "EQ", ""),
            ("합계", "EQ", ""),
        ],
    )

    assert build_fp002_evidence(document) == ()


def test_fp002_non_excel_document_is_ignored():
    document = ParsedDocument(
        file_path=Path("FP산정표.txt"),
        file_type="txt",
        blocks=(DocumentBlock(block_type="paragraph", text="사용자 조회 EQ"),),
    )

    assert build_fp002_evidence(document) == ()


def test_fp002_engine_calls_ai_only_when_duplicate_candidate_exists():
    duplicate_document = _sheet_document(
        "FP산정표.xlsx",
        [
            ("기능명", "FP유형", "설명"),
            ("사용자 조회", "EQ", "사용자 기본정보 조회"),
            ("사용자 조회", "EQ", "사용자 기본정보 조회"),
        ],
    )
    provider = RecordingProvider()
    engine = DocumentInspectionEngine(get_p1_fp_rules(), ai_provider=provider)

    results = engine.inspect_document(duplicate_document)

    assert len(provider.calls) == 1
    _document, rule, context = provider.calls[0]
    assert rule.code == "FP-002"
    assert context is not None and context.evidence
    assert len(results) == 1

    distinct_document = _sheet_document(
        "FP산정표2.xlsx",
        [
            ("기능명", "FP유형", "처리내용"),
            ("현황 조회", "EQ", "관리자용 전체 현황 조회"),
            ("현황 조회", "EQ", "일반사용자 본인 현황 조회"),
        ],
    )
    provider2 = RecordingProvider()
    engine2 = DocumentInspectionEngine(get_p1_fp_rules(), ai_provider=provider2)

    results2 = engine2.inspect_document(distinct_document)

    assert provider2.calls == []
    assert len(results2) == 1
    assert results2[0].findings == ()
