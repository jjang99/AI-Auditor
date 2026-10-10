from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.p1_governance_checks import (
    build_aud020_evidence,
    build_aud022_cross_document_evidence,
    build_aud023_cross_document_evidence,
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


def test_aud020_detects_missing_core_columns():
    document = _sheet_document(
        "인터페이스정의서.xlsx",
        [
            ("인터페이스ID", "송신시스템", "수신시스템"),
            ("IF-001", "포털", "외부시스템"),
        ],
    )

    evidence = build_aud020_evidence(document)

    assert len(evidence) == 1
    assert "연계방식 열 미정의" in evidence[0]
    assert "데이터 열 미정의" in evidence[0]


def test_aud022_cross_document_passes_when_related_execution_evidence_exists():
    contract = _text_document(
        "과업내용서.txt",
        ["사업자는 통합시험 결과보고서를 제출하여야 한다."],
    )
    evidence_doc = _text_document(
        "통합시험결과보고서.txt",
        ["통합시험 결과보고서 제출 완료 및 검토를 수행하였다."],
    )

    assert build_aud022_cross_document_evidence([contract, evidence_doc]) == ()


def test_aud022_cross_document_detects_missing_related_evidence():
    contract = _text_document(
        "과업내용서.txt",
        ["사업자는 통합시험 결과보고서를 제출하여야 한다."],
    )
    unrelated = _text_document(
        "회의록.txt",
        ["요구사항 회의 수행 완료"],
    )

    evidence = build_aud022_cross_document_evidence([contract, unrelated])

    assert len(evidence) == 1
    assert "통합시험 결과보고서" in evidence[0]


def test_aud022_cross_document_does_not_accuse_when_only_contract_uploaded():
    contract = _text_document(
        "과업내용서.txt",
        ["사업자는 통합시험 결과보고서를 제출하여야 한다."],
    )

    assert build_aud022_cross_document_evidence([contract]) == ()


def test_aud023_cross_document_passes_when_compliance_evidence_exists():
    design = _text_document(
        "설계서.txt",
        ["웹접근성 표준을 적용하여야 한다."],
    )
    result = _text_document(
        "웹접근성점검결과.txt",
        ["웹접근성 점검 결과 적합 판정을 확인하였다."],
    )

    assert build_aud023_cross_document_evidence([design, result]) == ()


def test_aud023_cross_document_detects_missing_compliance_evidence():
    design = _text_document(
        "설계서.txt",
        ["웹접근성 표준을 적용하여야 한다."],
    )
    unrelated = _text_document(
        "회의록.txt",
        ["인터페이스 검토를 완료하였다."],
    )

    evidence = build_aud023_cross_document_evidence([design, unrelated])

    assert len(evidence) == 1
    assert "웹접근성" in evidence[0]


def test_aud023_cross_document_ignores_non_applicable_standard():
    design = _text_document(
        "설계서.txt",
        ["웹접근성 표준은 본 사업 비적용 대상이다."],
    )

    assert build_aud023_cross_document_evidence([design]) == ()
