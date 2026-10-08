from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_engine import DocumentAIEngine
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
