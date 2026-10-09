from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_engine import DocumentAIEngine
from rules.core.document_engine import DocumentRuleEngine
from rules.core.hybrid_engine import DocumentHybridEngine
from rules.core.requirement_design_alignment import (
    build_requirement_design_batches,
    build_requirement_design_cases,
)
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


def test_req009_builds_cross_document_case_from_requirement_and_design_files():
    requirement = ParsedDocument(
        file_path=Path("PRJ-REQ-01-요구사항기술서_v1.0.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text=(
                    "SFR-101 사용자는 신청 상세화면에서 첨부파일을 조회하고 "
                    "다운로드할 수 있어야 한다."
                ),
                location="문단 12",
            ),
        ),
    )
    screen_design = ParsedDocument(
        file_path=Path("PRJ-UI-01-화면설계서_v1.0.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text=(
                    "SFR-101 | 신청 상세화면 | 첨부파일 목록 조회 버튼과 "
                    "다운로드 기능을 제공한다."
                ),
                location="화면 UI-031",
            ),
        ),
    )

    cases = build_requirement_design_cases([requirement, screen_design])

    assert len(cases) == 1
    assert cases[0].requirement_id == "SFR-101"
    assert cases[0].requirement_source == requirement.file_path.name
    assert len(cases[0].design_evidence) == 1
    assert "화면설계서" in cases[0].design_evidence[0]
    assert "SFR-101" in cases[0].design_evidence[0]


def test_req009_prefers_direct_requirement_id_over_loose_keyword_match():
    requirement = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="SFR-202 사용자는 회원 탈퇴 신청을 취소할 수 있어야 한다.",
            ),
        ),
    )
    direct_design = ParsedDocument(
        file_path=Path("화면설계서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="SFR-202 | 회원 탈퇴 신청 취소 버튼 및 확인 팝업을 정의한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="회원 신청 화면에서 사용자 정보 조회 및 취소 안내를 제공한다.",
            ),
        ),
    )

    cases = build_requirement_design_cases([requirement, direct_design])

    assert len(cases) == 1
    assert cases[0].design_evidence
    assert "SFR-202" in cases[0].design_evidence[0]


def test_req009_does_not_invent_missing_design_issue_without_linkable_evidence():
    requirement = ParsedDocument(
        file_path=Path("요구사항기술서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="SFR-303 모바일 인증 실패 시 별도 복구절차를 제공한다.",
            ),
        ),
    )
    unrelated_design = ParsedDocument(
        file_path=Path("인터페이스설계서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="IF-001 기관코드 조회 인터페이스의 요청/응답 항목을 정의한다.",
            ),
        ),
    )

    cases = build_requirement_design_cases([requirement, unrelated_design])
    batches = build_requirement_design_batches([requirement, unrelated_design])

    assert cases == ()
    assert batches == ()


def test_req009_batches_preserve_requirement_and_design_source_names():
    requirement = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-404 | 대시보드 통계 조회 | 조건별 통계 조회 기능 제공",
                sheet="기능요구사항",
                location="기능요구사항 / 행 8",
            ),
        ),
    )
    program_design = ParsedDocument(
        file_path=Path("프로그램설계서.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-404 | PRG-0404 | 대시보드 조건별 통계 조회 처리",
                sheet="프로그램",
                location="프로그램 / 행 14",
            ),
        ),
    )

    batches = build_requirement_design_batches([requirement, program_design])

    assert len(batches) == 1
    assert batches[0].case_count == 1
    combined = "\n".join(batches[0].evidence)
    assert "요구사항추적표.xlsx" in combined
    assert "프로그램설계서.xlsx" in combined
    assert "SFR-404" in combined
