from pathlib import Path

from rules.core.engine import RuleEngine
from rules.definitions.default_rules import get_default_rules


def test_rule_engine_detects_basic_issues(tmp_path: Path):
    source = tmp_path / "sample.py"
    source.write_text(
        'password = "secret123"\n'
        '# TODO remove temporary code\n'
        'print("debug")\n',
        encoding="utf-8",
    )

    engine = RuleEngine(get_default_rules())
    result = engine.inspect_files([source])
    codes = {issue.rule_code for issue in result.issues}

    assert result.file_count == 1
    assert "SEC-001" in codes
    assert "QUAL-001" in codes
    assert "QUAL-002" in codes
