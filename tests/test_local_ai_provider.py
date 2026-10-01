import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionContext
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.providers.local_ai_provider import (
    LlamaCppAIProvider,
    LocalAIProviderError,
    LocalAISettings,
)


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload, ensure_ascii=False).encode("utf-8")


def _document():
    return ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(DocumentBlock(block_type="paragraph", text="REQ-101 사용자는 로그인할 수 있다."),),
    )


def _rule():
    return next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-002")


def test_local_provider_calls_llama_server_and_parses_findings():
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _Response({
            "choices": [{"message": {"content": '{"findings":["REQ-101의 검증기준이 확인되지 않는다."]}'}}]
        })

    provider = LlamaCppAIProvider(LocalAISettings(base_url="http://127.0.0.1:18080"))

    with patch("rules.providers.local_ai_provider.request.urlopen", fake_urlopen):
        result = provider.inspect(
            _document(),
            _rule(),
            AIInspectionContext(evidence=("사전근거",)),
        )

    assert captured["url"] == "http://127.0.0.1:18080/v1/chat/completions"
    assert captured["payload"]["temperature"] == 0.7
    assert captured["payload"]["top_p"] == 0.8
    assert captured["payload"]["top_k"] == 20
    assert captured["payload"]["min_p"] == 0.0
    assert captured["payload"]["seed"] == 42
    assert "사전근거" in captured["payload"]["messages"][0]["content"]
    assert result.findings == ("REQ-101의 검증기준이 확인되지 않는다.",)
    assert result.provider_name == "LlamaCppAIProvider"


def test_local_provider_accepts_empty_findings():
    provider = LlamaCppAIProvider()
    with patch.object(provider, "_complete", return_value='{"findings":[]}'):
        result = provider.inspect(_document(), _rule())
    assert result.findings == ()


@pytest.mark.parametrize(
    "raw",
    [
        "not-json",
        '{"unexpected":[]}',
        '{"findings":"문자열"}',
        '{"findings":[""]}',
    ],
)
def test_local_provider_rejects_invalid_model_output(raw):
    provider = LlamaCppAIProvider()
    with patch.object(provider, "_complete", return_value=raw):
        with pytest.raises(LocalAIProviderError):
            provider.inspect(_document(), _rule())
