from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.document_engine import DocumentRuleEngine
from rules.definitions.document_mvp_rules import get_document_mvp_rules


def test_req_001_ignores_structural_hwp_id_repetition():
    document = ParsedDocument(
        file_path=Path("요구사항기술서.hwp"),
        file_type="hwp",
        blocks=(
            DocumentBlock(block_type="paragraph", text="2.1. SFR-025-ID-01 2"),
            DocumentBlock(block_type="paragraph", text="SFR-025-ID-01"),
            DocumentBlock(block_type="paragraph", text="SFR-025-ID-01"),
            DocumentBlock(block_type="paragraph", text="SFR-025-ID-01"),
        ),
    )

    issues = DocumentRuleEngine(get_document_mvp_rules()).inspect_document(document)

    assert all(issue.evidence != "중복 요구사항 ID: SFR-025-ID-01" for issue in issues)


def test_req_001_detects_same_id_on_distinct_requirement_definitions():
    document = ParsedDocument(
        file_path=Path("요구사항기술서.hwp"),
        file_type="hwp",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="SFR-025-ID-01 대시보드 조회 기능을 제공한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="SFR-025-ID-01 기관별 이용현황 조회 기능을 제공한다.",
            ),
        ),
    )

    issues = DocumentRuleEngine(get_document_mvp_rules()).inspect_document(document)

    assert any(issue.evidence == "중복 요구사항 ID: SFR-025-ID-01" for issue in issues)
