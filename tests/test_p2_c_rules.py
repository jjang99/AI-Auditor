from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionResult
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
from rules.core.p2_c_ai_engine import P2CAIEngine
from rules.core.p2_c_checks import (
    build_chg008_cross_document_evidence,
    build_chg010_cross_document_evidence,
    build_fp006_evidence,
    build_fp011_cross_document_evidence,
)
from rules.core.p2_c_hybrid_engine import P2CHybridEngine
from rules.definitions.document_p2_c_rules import get_p2_c_rules


class RecordingProvider:
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=(f"{rule.code} 테스트 지적",),
            raw_response="test",
        )


def _doc(name, rows, sheet="Sheet1", file_type="xlsx"):
    return ParsedDocument(
        file_path=Path(name),
        file_type=file_type,
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


def _rule(code):
    return next(rule for rule in get_p2_c_rules() if rule.code == code)


def test_p2_c_definition_has_exact_four_rules():
    rules = get_p2_c_rules()
    assert len(rules) == 4
    assert {rule.code for rule in rules} == {
        "CHG-008", "CHG-010", "FP-006", "FP-011"
    }


def test_p2_c_ai_strategies_are_explicit():
    assert get_ai_processing_strategy("CHG-008") == AIProcessingStrategy.EVIDENCE
    assert get_ai_processing_strategy("CHG-010") == AIProcessingStrategy.EVIDENCE
    assert get_ai_processing_strategy("FP-006") == AIProcessingStrategy.EVIDENCE
    assert get_ai_processing_strategy("FP-011") == AIProcessingStrategy.EVIDENCE


def test_chg008_requires_change_and_design_documents():
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

    assert build_chg008_cross_document_evidence([change]) == ()
    evidence = build_chg008_cross_document_evidence([change, design])
    assert len(evidence) == 1
    assert "CH-01" in evidence[0]
    assert "화면설계서.xlsx" in evidence[0]


def test_chg010_requires_explicit_data_impact():
    change = _doc(
        "변경관리대장.xlsx",
        [
            ("변경ID", "변경내용", "영향대상", "상태"),
            ("CH-01", "사용자 조회조건 변경", "화면설계", "승인"),
            ("CH-02", "사용자 테이블 컬럼 추가", "데이터설계", "승인"),
        ],
    )
    data = _doc(
        "테이블정의서.xlsx",
        [("테이블", "컬럼"), ("TB_USER", "USER_ID")],
    )

    evidence = build_chg010_cross_document_evidence([change, data])
    assert len(evidence) == 1
    assert "CH-02" in evidence[0]
    assert "CH-01" not in evidence[0]


def test_fp011_requires_functional_change_and_fp_document():
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

    assert build_fp011_cross_document_evidence([change]) == ()
    evidence = build_fp011_cross_document_evidence([change, fp])
    assert len(evidence) == 1
    assert "CH-10" in evidence[0]
    assert "기능점수산정표.xlsx" in evidence[0]


def test_fp006_structured_split_candidate_is_built():
    fp = _doc(
        "기능점수산정표.xlsx",
        [
            ("기능명", "FP유형", "기능설명"),
            ("사용자 등록", "EI", "사용자 정보를 처리한다"),
            ("사용자 조회", "EI", "사용자 정보를 처리한다"),
        ],
    )
    evidence = build_fp006_evidence(fp)
    assert any("과도분할 후보" in item for item in evidence)


def test_fp006_exact_duplicate_is_left_to_fp002():
    fp = _doc(
        "기능점수산정표.xlsx",
        [
            ("기능명", "FP유형", "기능설명"),
            ("사용자 조회", "EQ", "사용자 조회"),
            ("사용자 조회", "EQ", "사용자 조회"),
        ],
    )
    assert build_fp006_evidence(fp) == ()


def test_p2_c_hybrid_engine_calls_ai_only_on_cross_document_anchor():
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
    rule = _rule("CHG-008")
    engine = P2CHybridEngine([rule], provider)
    engine.prepare_documents([change, design])

    first = engine.inspect_document(change)
    second = engine.inspect_document(design)

    assert len(provider.calls) == 1
    assert first[0].findings
    assert second[0].findings == ()


def test_p2_c_ai_engine_uses_structured_fp006_evidence():
    fp = _doc(
        "기능점수산정표.xlsx",
        [
            ("기능명", "FP유형", "기능설명"),
            ("사용자 등록", "EI", "사용자 정보를 처리한다"),
            ("사용자 조회", "EI", "사용자 정보를 처리한다"),
        ],
    )
    provider = RecordingProvider()
    engine = P2CAIEngine([_rule("FP-006")], provider)

    results = engine.inspect_document(fp)

    assert len(provider.calls) == 1
    assert provider.calls[0][2] is not None
    assert provider.calls[0][2].evidence
    assert results[0].rule_code == "FP-006"
