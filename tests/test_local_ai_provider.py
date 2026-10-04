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
    response_format = captured["payload"]["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    assert response_format["json_schema"]["schema"]["required"] == ["findings"]
    prompt = captured["payload"]["messages"][0]["content"]
    assert "사전근거" in prompt
    assert "REQ-101 사용자는 로그인할 수 있다." not in prompt
    assert "[선별 문서근거]" in prompt
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


def test_local_provider_limits_large_document_prompt_to_relevant_evidence():
    rule = _rule()
    blocks = tuple(
        DocumentBlock(
            block_type="paragraph",
            text=(
                f"일반 설명 {index} " + ("X" * 500)
                if index < 30
                else "REQ-101과 REQ-205는 동일한 로그인 요구사항으로 보인다."
            ),
        )
        for index in range(31)
    )
    document = ParsedDocument(
        file_path=Path("large.docx"),
        file_type="docx",
        blocks=blocks,
    )
    provider = LlamaCppAIProvider()

    prompt = provider._build_prompt(document, rule, None)

    assert "REQ-101과 REQ-205" in prompt
    assert len(prompt) < 9000
    assert "[관련 문서근거]" in prompt


def test_chg012_prompt_marks_direct_test_coverage():
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "CHG-012")
    document = ParsedDocument(
        file_path=Path("change-test"),
        file_type="change_test_comparison",
        blocks=(
            DocumentBlock(
                block_type="confirmed_change",
                text="서비스별 이용현황(송수신현황) 모니터링 기능이 추가됨",
            ),
            DocumentBlock(
                block_type="test_document",
                text=(
                    "[시험 산출물] 통합테스트.xlsx\n"
                    "ITS-ID-003 | 서비스별 이용현황(송수신현황) 모니터링 | "
                    "검색조건을 입력하여 조회 | 조건에 맞는 현황목록이 조회된다."
                ),
            ),
        ),
    )
    provider = LlamaCppAIProvider()
    captured = {}

    def fake_complete(prompt, response_format=None):
        captured["prompt"] = prompt
        return '{"findings":[]}'

    with patch.object(provider, "_complete", side_effect=fake_complete):
        result = provider.inspect(document, rule)

    assert result.findings == ()
    assert "[직접 반영 근거]" in captured["prompt"]
    assert "시험문구 직접 확인" in captured["prompt"]
    assert "서비스별 이용현황 송수신현황 모니터링" in captured["prompt"]
    assert "그 근거와 모순되게" in captured["prompt"]


def test_chg012_does_not_mark_partial_requirement_id_coverage():
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "CHG-012")
    document = ParsedDocument(
        file_path=Path("change-test"),
        file_type="change_test_comparison",
        blocks=(
            DocumentBlock(
                block_type="confirmed_change",
                text="SFR-043-ID-02 및 SFR-044-ID-01 요구사항이 분리 및 취합됨",
            ),
            DocumentBlock(
                block_type="test_document",
                text="SFR-044-ID-01 | 사용자 관리 | 이용/보유기관 담당자 등록신청",
            ),
        ),
    )
    provider = LlamaCppAIProvider()
    captured = {}

    def fake_complete(prompt, response_format=None):
        captured["prompt"] = prompt
        return '{"findings":[]}'

    with patch.object(provider, "_complete", side_effect=fake_complete):
        provider.inspect(document, rule)

    direct_section = captured["prompt"].split("[직접 반영 근거]\n", 1)[1].split(
        "\n\n[관련 시험행]", 1
    )[0]
    assert "요구사항 ID 직접 확인" not in direct_section
