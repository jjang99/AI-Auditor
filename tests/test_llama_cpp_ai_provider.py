import json
from unittest.mock import patch

from rules.providers.llama_cpp_ai_provider import LlamaCppAIProvider, LocalAIConfig


class FakeResponse:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def read(self):
        return json.dumps({
            "choices": [{"message": {"content": '{"findings":["요구사항 근거가 누락되었습니다."]}'}}]
        }, ensure_ascii=False).encode("utf-8")


def test_llama_cpp_provider_parses_openai_compatible_response():
    provider = LlamaCppAIProvider(LocalAIConfig(timeout_seconds=1))
    with patch("rules.providers.llama_cpp_ai_provider.request.urlopen", return_value=FakeResponse()):
        raw = provider._chat("테스트")
    assert provider._parse_findings(raw) == ("요구사항 근거가 누락되었습니다.",)


def test_llama_cpp_provider_accepts_empty_findings():
    provider = LlamaCppAIProvider()
    assert provider._parse_findings('{"findings":[]}') == ()
