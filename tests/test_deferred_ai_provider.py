from pathlib import Path

from app.parsers.models import ParsedDocument
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.providers.deferred_ai_provider import DeferredAIProvider


def test_deferred_ai_provider_returns_no_fake_findings():
    document = ParsedDocument(
        file_path=Path("sample.docx"),
        file_type="docx",
        blocks=(),
    )

    rule = next(
        rule
        for rule in get_document_mvp_rules()
        if rule.code == "AI-005"
    )

    provider = DeferredAIProvider()

    result = provider.inspect(
        document,
        rule,
    )

    assert result.rule_code == "AI-005"
    assert result.findings == ()
    assert result.raw_response == ""