from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.p1_audit_checks import build_aud010_evidence, build_aud018_evidence


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


def test_aud010_complete_wbs_passes():
    document = _sheet_document(
        "WBS.xlsx",
        [
            ("작업명", "시작일", "종료일", "담당자"),
            ("요구사항 분석", "2026-10-01", "2026-10-03", "홍길동"),
        ],
    )
    assert build_aud010_evidence(document) == ()


def test_aud010_detects_missing_owner():
    document = _sheet_document(
        "WBS.xlsx",
        [
            ("작업명", "시작일", "종료일", "담당자"),
            ("설계 검토", "2026-10-01", "2026-10-03", ""),
        ],
    )
    evidence = build_aud010_evidence(document)
    assert len(evidence) == 1
    assert "담당자" in evidence[0]


def test_aud010_detects_reversed_dates():
    document = _sheet_document(
        "WBS.xlsx",
        [
            ("작업명", "시작일", "종료일", "담당자"),
            ("통합시험", "2026-10-10", "2026-10-05", "홍길동"),
        ],
    )
    evidence = build_aud010_evidence(document)
    assert any("일정 역전" in item for item in evidence)


def test_aud010_ignores_milestone_row():
    document = _sheet_document(
        "WBS.xlsx",
        [
            ("작업명", "시작일", "종료일", "담당자"),
            ("마일스톤-중간보고", "", "", ""),
        ],
    )
    assert build_aud010_evidence(document) == ()


def test_aud018_matching_quality_activity_passes():
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("요구사항 검토", "2026-10-01", "완료"),
        ],
    )
    result = _sheet_document(
        "품질활동결과.xlsx",
        [
            ("활동명", "결과"),
            ("요구사항 검토", "완료"),
        ],
    )
    assert build_aud018_evidence([plan, result]) == ()


def test_aud018_detects_missing_execution_evidence():
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("설계 품질점검", "2026-10-01", "완료"),
        ],
    )
    result = _sheet_document(
        "품질활동결과.xlsx",
        [
            ("활동명", "결과"),
            ("요구사항 검토", "완료"),
        ],
    )
    evidence = build_aud018_evidence([plan, result])
    assert len(evidence) == 1
    assert "설계 품질점검" in evidence[0]


def test_aud018_ignores_not_due_activity():
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("운영전환 점검", "2026-12-01", "시기미도래"),
        ],
    )
    result = _sheet_document(
        "품질활동결과.xlsx",
        [("활동명", "결과"), ("요구사항 검토", "완료")],
    )
    assert build_aud018_evidence([plan, result]) == ()


def test_aud018_does_not_accuse_without_evidence_document():
    plan = _sheet_document(
        "품질보증계획서.xlsx",
        [
            ("활동명", "예정일", "상태"),
            ("설계 품질점검", "2026-10-01", "완료"),
        ],
    )
    assert build_aud018_evidence([plan]) == ()
