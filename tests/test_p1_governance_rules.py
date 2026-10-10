from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.inspection_engine import DocumentInspectionEngine
from rules.core.p1_governance_checks import (
    build_aud020_evidence,
    build_aud022_evidence,
    build_aud023_evidence,
)
from rules.core.p1_governance_hybrid_engine import P1GovernanceHybridEngine
from rules.definitions.document_p1_governance_rules import get_p1_governance_rules


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


def _text_document(name, lines):
    return ParsedDocument(
        file_path=Path(name),
        file_type="txt",
        blocks=tuple(
            DocumentBlock(block_type="paragraph", text=line, location=f"문단 {index}")
            for index, line in enumerate(lines, start=1)
        ),
    )


def test_engine_uses_p1_governance_hybrid_engine():
    engine = DocumentInspectionEngine(get_p1_governance_rules(), ai_provider=None)
    assert isinstance(engine.hybrid_engine, P1GovernanceHybridEngine)


def test_aud020_complete_interface_definition_passes():
    document = _sheet_document(
        "인터페이스정의서.xlsx",
        [
            ("인터페이스ID", "송신시스템", "수신시스템", "연계방식", "데이터", "주기"),
            ("IF-001", "포털", "외부시스템", "REST", "신청정보", "실시간"),
        ],
    )
    assert build_aud020_evidence(document) == ()


def test_aud020_detects_missing_required_interface_info():
    document = _sheet_document(
        "인터페이스정의서.xlsx",
        [
            ("인터페이스ID", "송신시스템", "수신시스템", "연계방식", "데이터"),
            ("IF-001", "포털", "외부시스템", "", "신청정보"),
        ],
    )
    evidence = build_aud020_evidence(document)
    assert len(evidence) == 1
    assert "연계방식" in evidence[0]


def test_aud020_ignores_plain_external_agency_mention():
    document = _text_document("회의록.txt", ["국토부와 향후 협의 예정이다."])
    assert build_aud020_evidence(document) == ()


def test_aud022_detects_explicit_contract_obligation_candidate():
    document = _text_document(
        "과업내용서.txt",
        ["사업자는 통합시험 결과보고서를 제출하여야 한다."],
    )
    evidence = build_aud022_evidence(document)
    assert len(evidence) == 1
    assert "제출하여야" in evidence[0]


def test_aud022_ignores_not_due_obligation():
    document = _text_document(
        "과업내용서.txt",
        ["사업자는 운영 전 최종 교육을 수행하여야 한다."],
    )
    assert build_aud022_evidence(document) == ()


def test_aud022_ignores_general_background_text():
    document = _text_document(
        "과업내용서.txt",
        ["본 사업은 업무 효율성을 향상하기 위한 사업이다."],
    )
    assert build_aud022_evidence(document) == ()


def test_aud023_detects_applied_standard_without_compliance_evidence():
    document = _text_document(
        "설계서.txt",
        ["웹접근성 표준을 적용하여야 한다."],
    )
    evidence = build_aud023_evidence(document)
    assert len(evidence) == 1
    assert "웹접근성" in evidence[0]


def test_aud023_passes_when_compliance_evidence_is_present():
    document = _text_document(
        "설계서.txt",
        ["웹접근성 표준을 적용하고 점검 결과 적합 판정을 확인하였다."],
    )
    assert build_aud023_evidence(document) == ()


def test_aud023_ignores_non_applicable_standard():
    document = _text_document(
        "설계서.txt",
        ["본 기준은 비적용 대상으로 분류한다."],
    )
    assert build_aud023_evidence(document) == ()
