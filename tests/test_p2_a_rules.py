from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.p2_document_engine import P2DocumentRuleEngine
from rules.definitions.document_p2_a_rules import get_p2_a_rules


def _doc(name, rows, sheet="Sheet1", file_type="xlsx"):
    return ParsedDocument(
        file_path=Path(name),
        file_type=file_type,
        blocks=tuple(
            DocumentBlock(
                block_type="sheet_row",
                text=" | ".join(str(v) for v in row if v),
                sheet=sheet,
                location=f"{sheet} / 행 {i}",
                metadata={"cell_values": tuple(row)},
            )
            for i, row in enumerate(rows, start=1)
        ),
    )


def _engine(*codes):
    rules = [rule for rule in get_p2_a_rules() if rule.code in set(codes)]
    return P2DocumentRuleEngine(rules)


def test_p2_a_definition_has_exact_seven_rules():
    rules = get_p2_a_rules()
    assert len(rules) == 7
    assert {r.code for r in rules} == {
        "AUD-015", "AUD-019", "REQ-016", "REQ-020",
        "CHG-005", "FP-007", "AI-023",
    }


def test_aud015_completed_test_missing_result_is_detected():
    document = _doc(
        "통합시험결과.xlsx",
        [
            ("시험ID", "수행상태", "실제결과", "판정"),
            ("T-001", "완료", "", ""),
        ],
    )
    issues = _engine("AUD-015").inspect_document(document)
    assert len(issues) == 1
    assert issues[0].rule_code == "AUD-015"
    assert "실제결과" in issues[0].evidence


def test_aud015_scheduled_test_is_not_failed():
    document = _doc(
        "통합시험결과.xlsx",
        [
            ("시험ID", "수행상태", "실제결과", "판정"),
            ("T-001", "예정", "", ""),
        ],
    )
    assert _engine("AUD-015").inspect_document(document) == ()


def test_aud019_open_quality_finding_is_detected():
    document = _doc(
        "품질점검결과.xlsx",
        [
            ("지적번호", "지적사항", "조치상태"),
            ("Q-01", "요구사항 추적표 보완", "미조치"),
        ],
    )
    issues = _engine("AUD-019").inspect_document(document)
    assert len(issues) == 1
    assert issues[0].rule_code == "AUD-019"


def test_req016_important_requirement_without_test_is_detected():
    req = _doc(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "중요도", "시험대상"),
            ("SFR-100-ID-01", "중요", "Y"),
        ],
    )
    test = _doc(
        "통합시험시나리오.xlsx",
        [
            ("시험ID", "요구사항ID"),
            ("T-001", "SFR-999-ID-01"),
        ],
    )
    issues = _engine("REQ-016").inspect_documents([req, test])
    assert any(i.rule_code == "REQ-016" and "SFR-100-ID-01" in i.evidence for i in issues)


def test_req016_without_test_document_does_not_accuse():
    req = _doc(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "중요도"),
            ("SFR-100-ID-01", "중요"),
        ],
    )
    assert _engine("REQ-016").inspect_documents([req]) == ()


def test_req020_invalid_requirement_reference_is_detected():
    req = _doc(
        "요구사항정의서.xlsx",
        [
            ("요구사항ID", "내용"),
            ("SFR-100-ID-01", "사용자 조회 기능"),
        ],
    )
    design = _doc(
        "화면설계서.xlsx",
        [
            ("화면ID", "관련요구사항"),
            ("UI-001", "SFR-999-ID-01"),
        ],
    )
    issues = _engine("REQ-020").inspect_documents([req, design])
    assert any(i.rule_code == "REQ-020" and "SFR-999-ID-01" in i.evidence for i in issues)


def test_chg005_unapproved_applied_change_is_detected():
    document = _doc(
        "변경관리대장.xlsx",
        [
            ("변경ID", "승인상태", "반영상태"),
            ("CH-01", "미승인", "반영완료"),
        ],
    )
    issues = _engine("CHG-005").inspect_document(document)
    assert len(issues) == 1
    assert issues[0].rule_code == "CHG-005"


def test_fp007_explicit_blank_basis_is_detected():
    document = _doc(
        "FP산정표.xlsx",
        [
            ("산정방식", ""),
            ("적용기준", "IFPUG"),
        ],
    )
    issues = _engine("FP-007").inspect_document(document)
    assert len(issues) == 1
    assert issues[0].rule_code == "FP-007"


def test_ai023_blank_resource_limit_is_detected_only_for_ai_document():
    ai_doc = _doc(
        "AI서비스설계.xlsx",
        [
            ("timeout", ""),
            ("retry", "3"),
        ],
    )
    normal_doc = _doc(
        "일반설계.xlsx",
        [
            ("timeout", ""),
        ],
    )

    ai_issues = _engine("AI-023").inspect_document(ai_doc)
    normal_issues = _engine("AI-023").inspect_document(normal_doc)

    assert len(ai_issues) == 1
    assert ai_issues[0].rule_code == "AI-023"
    assert normal_issues == ()
