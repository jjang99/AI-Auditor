from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.document_engine import DocumentRuleEngine
from rules.definitions.document_mvp_rules import get_document_mvp_rules


def _rule(code):
    return next(rule for rule in get_document_mvp_rules() if rule.code == code)


def _row(*values, row=1):
    cell_values = tuple(str(value) for value in values)
    return DocumentBlock(
        block_type="sheet_row",
        text=" | ".join(value for value in cell_values if value),
        sheet="FP산정",
        location=f"FP산정 / 행 {row}",
        metadata={"cell_values": cell_values, "row_index": row},
    )


def test_fp009_detects_structured_row_mismatch_from_explicit_complexity():
    document = ParsedDocument(
        file_path=Path("FP산출내역서.xlsx"),
        file_type="xlsx",
        blocks=(
            _row("기능유형", "복잡도", "기능개수", "기능점수", row=1),
            _row("EI", "보통", "3", "15", row=2),
        ),
    )

    engine = DocumentRuleEngine((_rule("FP-009"),))
    issues = engine.inspect_document(document)

    assert len(issues) == 1
    assert issues[0].rule_code == "FP-009"
    assert "보고값 15 FP" in issues[0].evidence
    assert "재계산 결과 12 FP" in issues[0].evidence


def test_fp009_recalculates_complexity_from_ret_ftr_and_det():
    document = ParsedDocument(
        file_path=Path("FP산출내역서.xlsx"),
        file_type="xlsx",
        blocks=(
            _row("기능유형", "RET/FTR", "DET", "기능점수", row=1),
            _row("EO", "2", "20", "5", row=2),
        ),
    )

    engine = DocumentRuleEngine((_rule("FP-009"),))
    issues = engine.inspect_document(document)

    assert len(issues) == 1
    assert "EO/HIGH" in issues[0].evidence
    assert "재계산 결과 7 FP" in issues[0].evidence
    assert "RET/FTR=2, DET=20" in issues[0].evidence


def test_fp009_passes_correct_structured_row():
    document = ParsedDocument(
        file_path=Path("FP산출내역서.xlsx"),
        file_type="xlsx",
        blocks=(
            _row("기능유형", "RET/FTR", "DET", "기능개수", "기능점수", row=1),
            _row("ILF", "1", "18", "2", "14", row=2),
        ),
    )

    engine = DocumentRuleEngine((_rule("FP-009"),))
    issues = engine.inspect_document(document)

    assert issues == ()
