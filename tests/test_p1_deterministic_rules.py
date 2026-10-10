from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.p1_document_engine import P1DocumentRuleEngine
from rules.definitions.document_p1_rules import get_p1_deterministic_rules


def _xlsx_document(name, rows, sheet="Sheet1"):
    blocks = tuple(
        DocumentBlock(
            block_type="sheet_row",
            text=" | ".join(value for value in row if value),
            sheet=sheet,
            location=f"{sheet} / 행 {index}",
            metadata={"cell_values": tuple(row)},
        )
        for index, row in enumerate(rows, start=1)
    )
    return ParsedDocument(
        file_path=Path(name),
        file_type="xlsx",
        blocks=blocks,
    )


def _engine():
    return P1DocumentRuleEngine(list(get_p1_deterministic_rules()))


def test_aud_014_passes_complete_test_plan():
    document = _xlsx_document(
        "통합시험계획.xlsx",
        [
            ("시험항목", "시험방법", "예상결과"),
            ("로그인", "정상 계정으로 로그인", "메인 화면 표시"),
        ],
    )

    issues = _engine().inspect_document(document)

    assert all(issue.rule_code != "AUD-014" for issue in issues)


def test_aud_014_detects_missing_required_value():
    document = _xlsx_document(
        "통합시험계획.xlsx",
        [
            ("시험항목", "시험방법", "예상결과"),
            ("로그인", "정상 계정으로 로그인", ""),
        ],
    )

    issues = [
        issue for issue in _engine().inspect_document(document)
        if issue.rule_code == "AUD-014"
    ]

    assert len(issues) == 1
    assert "예상결과" in issues[0].evidence


def test_aud_014_detects_missing_required_header():
    document = _xlsx_document(
        "단위시험계획.xlsx",
        [
            ("시험항목", "시험방법"),
            ("조회", "조회 버튼 클릭"),
        ],
    )

    issues = [
        issue for issue in _engine().inspect_document(document)
        if issue.rule_code == "AUD-014"
    ]

    assert len(issues) == 1
    assert "필수 헤더 누락" in issues[0].evidence
    assert "예상결과" in issues[0].evidence


def test_aud_014_ignores_empty_template_row():
    document = _xlsx_document(
        "시험시나리오.xlsx",
        [
            ("시험항목", "시험방법", "예상결과"),
            ("", "", ""),
        ],
    )

    issues = _engine().inspect_document(document)

    assert all(issue.rule_code != "AUD-014" for issue in issues)


def test_aud_016_detects_open_defect():
    document = _xlsx_document(
        "시험결함목록.xlsx",
        [
            ("결함ID", "내용", "상태", "조치결과"),
            ("DEF-001", "로그인 오류", "진행중", "수정 중"),
        ],
    )

    issues = [
        issue for issue in _engine().inspect_document(document)
        if issue.rule_code == "AUD-016"
    ]

    assert len(issues) == 1
    assert "미종결 시험결함" in issues[0].evidence


def test_aud_016_detects_completed_without_action_result():
    document = _xlsx_document(
        "시험결함목록.xlsx",
        [
            ("결함ID", "내용", "상태", "조치결과"),
            ("DEF-002", "조회 오류", "완료", ""),
        ],
    )

    issues = [
        issue for issue in _engine().inspect_document(document)
        if issue.rule_code == "AUD-016"
    ]

    assert len(issues) == 1
    assert "조치결과 공란" in issues[0].evidence


def test_aud_016_ignores_cancelled_or_not_applicable_defect():
    document = _xlsx_document(
        "시험결함목록.xlsx",
        [
            ("결함ID", "내용", "상태", "조치결과"),
            ("DEF-003", "중복 오류", "취소", "중복 등록"),
            ("DEF-004", "비대상", "해당없음", ""),
        ],
    )

    issues = _engine().inspect_document(document)

    assert all(issue.rule_code != "AUD-016" for issue in issues)


def test_fp_008_passes_when_explicit_complexity_exists():
    document = _xlsx_document(
        "FP산정표.xlsx",
        [
            ("기능유형", "복잡도", "RET/FTR", "DET", "기능점수"),
            ("EI", "LOW", "", "", "3"),
        ],
    )

    issues = _engine().inspect_document(document)

    assert all(issue.rule_code != "FP-008" for issue in issues)


def test_fp_008_detects_missing_detail_basis():
    document = _xlsx_document(
        "FP산정표.xlsx",
        [
            ("기능유형", "복잡도", "RET/FTR", "DET", "기능점수"),
            ("EI", "", "", "10", "4"),
        ],
    )

    issues = [
        issue for issue in _engine().inspect_document(document)
        if issue.rule_code == "FP-008"
    ]

    assert len(issues) == 1
    assert "RET/FTR" in issues[0].evidence


def test_fp_008_passes_when_ret_ftr_and_det_exist():
    document = _xlsx_document(
        "FP산정표.xlsx",
        [
            ("기능유형", "복잡도", "RET/FTR", "DET", "기능점수"),
            ("EO", "", "2", "10", "5"),
        ],
    )

    issues = _engine().inspect_document(document)

    assert all(issue.rule_code != "FP-008" for issue in issues)
