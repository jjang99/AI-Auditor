from rules.core.models import RuleIssue


def _issue(rule_code: str, rule_name: str, evidence: str) -> RuleIssue:
    return RuleIssue(
        rule_code=rule_code,
        rule_name=rule_name,
        category="변경영향도",
        severity="Low",
        file_path="sample.hwp",
        line_number=0,
        evidence=evidence,
        description="설명",
    )


def test_chg_001_title_uses_concrete_finding_text():
    issue = _issue(
        "CHG-001",
        "변경사항 식별 점검",
        "이용기관·보유기관 서비스 이용현황 대시보드 기능 구현으로 기능 범위 확장됨",
    )

    assert issue.title == (
        "CHG-001 이용기관·보유기관 서비스 이용현황 대시보드 기능 구현으로 기능 범위 확장됨"
    )


def test_non_chg_001_title_keeps_rule_name():
    issue = _issue(
        "CHG-006",
        "변경 영향대상 식별",
        "영향 후보",
    )

    assert issue.title == "CHG-006 변경 영향대상 식별"
