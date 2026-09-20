from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.document_engine import DocumentRuleEngine
from rules.definitions.document_mvp_rules import get_document_mvp_rules


def test_aud_001_detects_missing_deliverable():
    documents = [
        ParsedDocument(
            file_path=Path("01_요구사항정의서_v1.0.docx"),
            file_type="docx",
            blocks=(
                DocumentBlock(
                    block_type="paragraph",
                    text="테스트",
                ),
            ),
        ),
        ParsedDocument(
            file_path=Path("02_화면설계서.xlsx"),
            file_type="xlsx",
            blocks=(
                DocumentBlock(
                    block_type="cell",
                    text="테스트",
                ),
            ),
        ),
    ]

    engine = DocumentRuleEngine(
        get_document_mvp_rules(),
        required_deliverables=[
            "요구사항정의서",
            "화면설계서",
            "테이블정의서",
        ],
    )

    issues = engine.inspect_documents(documents)

    assert len(issues) == 1
    assert issues[0].rule_code == "AUD-001"
    assert issues[0].evidence == "필수 산출물 누락: 테이블정의서"

def test_aud_001_passes_when_all_deliverables_exist():
    documents = [
        ParsedDocument(
            file_path=Path("01_요구사항정의서_v1.0.docx"),
            file_type="docx",
            blocks=(
                DocumentBlock(
                    block_type="paragraph",
                    text="테스트",
                ),
            ),
        ),
        ParsedDocument(
            file_path=Path("02_화면설계서.xlsx"),
            file_type="xlsx",
            blocks=(
                DocumentBlock(
                    block_type="cell",
                    text="테스트",
                ),
            ),
        ),
        ParsedDocument(
            file_path=Path("03_테이블정의서.hwp"),
            file_type="hwp",
            blocks=(
                DocumentBlock(
                    block_type="paragraph",
                    text="테스트",
                ),
            ),
        ),
    ]

    engine = DocumentRuleEngine(
        get_document_mvp_rules(),
        required_deliverables=[
            "요구사항정의서",
            "화면설계서",
            "테이블정의서",
        ],
    )

    issues = engine.inspect_documents(documents)

    assert len(issues) == 0    

def test_req_001_detects_duplicate_requirement_id():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="REQ-001 로그인 기능을 제공한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-002 사용자 정보를 조회한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-002 사용자 정보를 수정한다.",
            ),
        ),
    )

    engine = DocumentRuleEngine(
        get_document_mvp_rules()
    )

    issues = engine.inspect_document(document)

    assert len(issues) == 1
    assert issues[0].rule_code == "REQ-001"
    assert issues[0].evidence == "중복 요구사항 ID: REQ-002"


def test_req_001_detects_missing_requirement_id():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="REQ-001 로그인 기능을 제공한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="사용자 정보를 조회할 수 있어야 한다.",
            ),
        ),
    )

    engine = DocumentRuleEngine(
        get_document_mvp_rules()
    )

    issues = engine.inspect_document(document)

    assert len(issues) == 1
    assert issues[0].rule_code == "REQ-001"
    assert "요구사항 ID 누락 후보" in issues[0].evidence


def test_req_001_passes_valid_requirements():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="REQ-001 로그인 기능을 제공한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-002 사용자 정보를 조회할 수 있어야 한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-003 사용자 정보를 수정한다.",
            ),
        ),
    )

    engine = DocumentRuleEngine(
        get_document_mvp_rules()
    )

    issues = engine.inspect_document(document)

    assert len(issues) == 0

def test_fp_009_detects_incorrect_calculation():
    document = ParsedDocument(
        file_path=Path("FP산정서.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="cell",
                text="총 FP: 15 + 25 + 10 = 55",
                sheet="FP산정",
                location="F10",
            ),
        ),
    )

    engine = DocumentRuleEngine(
        get_document_mvp_rules()
    )

    issues = engine.inspect_document(document)

    assert len(issues) == 1
    assert issues[0].rule_code == "FP-009"
    assert "재계산 결과 = 50" in issues[0].evidence
    assert issues[0].sheet == "FP산정"
    assert issues[0].location == "F10"


def test_fp_009_passes_correct_calculation():
    document = ParsedDocument(
        file_path=Path("FP산정서.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="cell",
                text="총 FP: 15 + 25 + 10 = 50",
                sheet="FP산정",
                location="F10",
            ),
        ),
    )

    engine = DocumentRuleEngine(
        get_document_mvp_rules()
    )

    issues = engine.inspect_document(document)

    assert len(issues) == 0


def test_fp_009_ignores_unrelated_numbers():
    document = ParsedDocument(
        file_path=Path("일반문서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="사업기간은 10개월이며 참여인원은 20명이다.",
            ),
        ),
    )

    engine = DocumentRuleEngine(
        get_document_mvp_rules()
    )

    issues = engine.inspect_document(document)

    assert len(issues) == 0