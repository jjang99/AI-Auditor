from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_engine import DocumentAIEngine
from rules.core.document_engine import DocumentRuleEngine
from rules.core.hybrid_engine import DocumentHybridEngine
from rules.definitions.document_mvp_rules import get_document_mvp_rules


def _rule(code):
    return next(rule for rule in get_document_mvp_rules() if rule.code == code)


def test_req002_candidates_include_same_requirement_name_with_different_details():
    evidence = (
        "SFR-001 | 사용자 로그인 기능 | 아이디와 비밀번호로 로그인한다",
        "SFR-002 | 사용자 로그인 | 간편인증으로 로그인한다",
        "SFR-003 | 관리자 통계 조회 | 통계 화면을 제공한다",
    )

    pairs = DocumentAIEngine._build_comparison_pairs(
        evidence,
        rule_code="REQ-002",
    )

    assert pairs == ((evidence[0], evidence[1]),)


def test_req002_candidates_do_not_pair_unrelated_requirement_names():
    evidence = (
        "SFR-001 | 사용자 로그인 | 로그인을 제공한다",
        "SFR-002 | 관리자 통계 조회 | 통계를 제공한다",
    )

    pairs = DocumentAIEngine._build_comparison_pairs(
        evidence,
        rule_code="REQ-002",
    )

    assert pairs == ()


def test_req003_detects_quantitative_target_without_value():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="PER-001 온라인 배치성 업무의 목표 응답시간을 정의하여야 한다.",
            ),
        ),
    )

    engine = DocumentHybridEngine((_rule("REQ-003"),), provider=None)
    context = engine.build_context(document, _rule("REQ-003"))

    assert len(context.evidence) == 1
    assert "정량기준 누락 가능성" in context.evidence[0]
    assert "응답시간" in context.evidence[0]


def test_req003_does_not_flag_quantitative_target_with_explicit_value():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="PER-001 온라인 업무의 목표 응답시간은 3초 이내로 한다.",
            ),
        ),
    )

    engine = DocumentHybridEngine((_rule("REQ-003"),), provider=None)
    context = engine.build_context(document, _rule("REQ-003"))

    assert context.evidence == ()


def test_req003_detects_unresolved_agreement_expression():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="TER-003 부하테스트 수행 횟수는 주관기관과 협의 후 확정한다.",
            ),
        ),
    )

    engine = DocumentHybridEngine((_rule("REQ-003"),), provider=None)
    context = engine.build_context(document, _rule("REQ-003"))

    assert len(context.evidence) == 1
    assert "협의 후 확정" in context.evidence[0]


def _xlsx_row(*values, row=1):
    cell_values = tuple(values)
    return DocumentBlock(
        block_type="sheet_row",
        text=" | ".join(value for value in cell_values if value),
        sheet="산출물목록",
        location=f"산출물목록 / 행 {row}",
        metadata={"cell_values": cell_values, "row_index": row},
    )


def test_aud001_uses_uploaded_deliverable_list_as_project_baseline():
    baseline = ParsedDocument(
        file_path=Path("PRJ-PP-01-[별첨1]산출물목록_v1.0.xlsx"),
        file_type="xlsx",
        blocks=(
            _xlsx_row("산출물명", "적용여부", "작성상태", row=1),
            _xlsx_row("요구사항정의서", "적용", "작성", row=2),
            _xlsx_row("인터페이스정의서", "적용", "작성", row=3),
            _xlsx_row("성능테스트결과서", "적용", "시기미도래", row=4),
            _xlsx_row("레거시전환계획서", "미적용", "", row=5),
        ),
    )
    uploaded = ParsedDocument(
        file_path=Path("PRJ-R0303-01-요구사항정의서_v1.2.docx"),
        file_type="docx",
        blocks=(DocumentBlock(block_type="paragraph", text="REQ-001 로그인 기능"),),
    )

    engine = DocumentRuleEngine((_rule("AUD-001"),))
    issues = engine.inspect_documents([baseline, uploaded])

    assert len(issues) == 1
    assert issues[0].rule_code == "AUD-001"
    assert "인터페이스정의서" in issues[0].evidence
    assert "성능테스트결과서" not in issues[0].evidence
    assert "레거시전환계획서" not in issues[0].evidence
    assert "산출물목록" in issues[0].evidence


def test_aud001_passes_when_all_due_deliverables_exist():
    baseline = ParsedDocument(
        file_path=Path("산출물목록.xlsx"),
        file_type="xlsx",
        blocks=(
            _xlsx_row("산출물명", "적용여부", row=1),
            _xlsx_row("요구사항정의서", "적용", row=2),
            _xlsx_row("인터페이스정의서", "적용", row=3),
        ),
    )
    documents = [
        baseline,
        ParsedDocument(
            file_path=Path("요구사항정의서_v1.0.docx"),
            file_type="docx",
            blocks=(DocumentBlock(block_type="paragraph", text="요구사항"),),
        ),
        ParsedDocument(
            file_path=Path("ABC-A0201-인터페이스정의서-v2.0.xlsx"),
            file_type="xlsx",
            blocks=(_xlsx_row("ID", "내용", row=1),),
        ),
    ]

    engine = DocumentRuleEngine((_rule("AUD-001"),))
    issues = engine.inspect_documents(documents)

    assert issues == ()


def test_aud001_without_baseline_does_not_invent_standard_deliverables():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(DocumentBlock(block_type="paragraph", text="REQ-001 로그인 기능"),),
    )

    engine = DocumentRuleEngine((_rule("AUD-001"),))
    issues = engine.inspect_documents([document])

    assert issues == ()
