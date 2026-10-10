from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
from rules.core.p2_b_checks import (
    build_aud005_cross_document_evidence,
    build_aud021_cross_document_evidence,
    build_req021_evidence,
    build_req027_evidence,
)
from rules.core.p2_b_hybrid_engine import P2BHybridEngine
from rules.definitions.document_p2_b_rules import get_p2_b_rules


class NoopProvider:
    def inspect(self, document, rule, context=None):
        raise AssertionError("이 테스트에서는 AI 호출이 필요하지 않습니다.")


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


def _rule(code):
    return next(rule for rule in get_p2_b_rules() if rule.code == code)


def test_p2_b_definition_has_exact_six_rules():
    rules = get_p2_b_rules()
    assert len(rules) == 6
    assert {rule.code for rule in rules} == {
        "AUD-005", "AUD-021", "REQ-006", "REQ-021", "REQ-027", "REQ-028"
    }


def test_p2_b_ai_strategies_are_explicit():
    assert get_ai_processing_strategy("AUD-005") == AIProcessingStrategy.SYNTHESIS
    assert get_ai_processing_strategy("AUD-021") == AIProcessingStrategy.EVIDENCE
    assert get_ai_processing_strategy("REQ-006") == AIProcessingStrategy.EVIDENCE
    assert get_ai_processing_strategy("REQ-021") == AIProcessingStrategy.CANDIDATE
    assert get_ai_processing_strategy("REQ-027") == AIProcessingStrategy.CANDIDATE
    assert get_ai_processing_strategy("REQ-028") == AIProcessingStrategy.SYNTHESIS


def test_aud005_cross_document_same_id_different_name_is_candidate():
    left = _doc("요구사항정의서.xlsx", [("요구사항ID", "요구사항명"), ("SFR-001", "사용자 조회")])
    right = _doc("화면설계서.xlsx", [("요구사항ID", "요구사항명"), ("SFR-001", "회원 조회")])

    evidence = build_aud005_cross_document_evidence([left, right])

    assert len(evidence) == 1
    assert "사용자 조회" in evidence[0]
    assert "회원 조회" in evidence[0]


def test_aud005_single_document_does_not_accuse():
    document = _doc("요구사항정의서.xlsx", [("요구사항ID", "요구사항명"), ("SFR-001", "사용자 조회")])
    assert build_aud005_cross_document_evidence([document]) == ()


def test_aud021_cross_document_interface_mismatch_is_candidate():
    left = _doc(
        "인터페이스설계서.xlsx",
        [("인터페이스ID", "송신시스템", "수신시스템", "연계방식"), ("IF-001", "A", "B", "REST")],
    )
    right = _doc(
        "연계정의서.xlsx",
        [("인터페이스ID", "송신시스템", "수신시스템", "연계방식"), ("IF-001", "A", "B", "SOAP")],
    )

    evidence = build_aud021_cross_document_evidence([left, right])

    assert len(evidence) == 1
    assert "방식" in evidence[0]
    assert "REST" in evidence[0]
    assert "SOAP" in evidence[0]


def test_req021_completed_but_unapproved_is_candidate():
    document = _doc(
        "요구사항정의서.xlsx",
        [("요구사항ID", "상태", "승인상태"), ("SFR-001", "완료", "미승인")],
    )
    evidence = build_req021_evidence(document)
    assert len(evidence) == 1
    assert "SFR-001" in evidence[0]


def test_req027_explicit_source_column_blank_is_candidate():
    document = _doc(
        "요구사항정의서.xlsx",
        [("요구사항ID", "출처"), ("SFR-001", ""), ("SFR-002", "해당없음")],
    )
    evidence = build_req027_evidence(document)
    assert len(evidence) == 1
    assert "SFR-001" in evidence[0]
    assert "SFR-002" not in evidence[0]


def test_p2_b_hybrid_engine_uses_cross_document_aud021_context():
    rules = [_rule("AUD-021")]
    engine = P2BHybridEngine(rules, NoopProvider())
    left = _doc(
        "인터페이스설계서.xlsx",
        [("인터페이스ID", "송신시스템", "수신시스템", "연계방식"), ("IF-001", "A", "B", "REST")],
    )
    right = _doc(
        "연계정의서.xlsx",
        [("인터페이스ID", "송신시스템", "수신시스템", "연계방식"), ("IF-001", "A", "B", "SOAP")],
    )
    engine.prepare_documents([left, right])

    context = engine.build_context(left, rules[0])
    second = engine.build_context(right, rules[0])

    assert context.evidence
    assert second.evidence == ()
