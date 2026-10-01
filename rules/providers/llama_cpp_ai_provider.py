import json
from dataclasses import dataclass
from urllib import request

from rules.core.ai_provider import AIInspectionContext, AIInspectionResult, BaseAIProvider


@dataclass(frozen=True)
class LocalAIConfig:
    base_url: str = "http://127.0.0.1:8080"
    model: str = "Qwen3-4B"
    timeout_seconds: int = 120


class LlamaCppAIProvider(BaseAIProvider):
    """llama.cpp의 OpenAI 호환 로컬 서버를 사용하는 문서검사 Provider."""

    def __init__(self, config: LocalAIConfig | None = None):
        self.config = config or LocalAIConfig()

    def inspect(self, document, rule, context: AIInspectionContext | None = None):
        prompt = self._build_prompt(document, rule, context)
        raw_response = self._chat(prompt)
        findings = self._parse_findings(raw_response)
        return AIInspectionResult(
            rule_code=rule.code,
            findings=findings,
            raw_response=raw_response,
            execution_type=getattr(rule, "execution_type", ""),
            provider_name="llama.cpp",
        )

    def _chat(self, prompt: str) -> str:
        payload = json.dumps({
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "당신은 정보시스템 산출물 품질검사 도우미입니다. "
                        "제공된 검사기준과 문서 내용만 근거로 판단하고, "
                        "문제가 없으면 findings를 빈 배열로 반환하세요. "
                        "반드시 JSON 객체 {\"findings\":[\"...\"]} 형식으로만 답하세요."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }, ensure_ascii=False).encode("utf-8")

        req = request.Request(
            f"{self.config.base_url.rstrip('/')}/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]

    @staticmethod
    def _parse_findings(raw_response: str) -> tuple[str, ...]:
        text = raw_response.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]).strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()
        data = json.loads(text)
        findings = data.get("findings", [])
        if not isinstance(findings, list):
            raise ValueError("AI 응답의 findings는 배열이어야 합니다.")
        return tuple(str(item).strip() for item in findings if str(item).strip())

    @staticmethod
    def _build_prompt(document, rule, context) -> str:
        blocks = getattr(document, "blocks", ())
        content = "\n".join(
            str(getattr(block, "text", block))
            for block in blocks
        )
        evidence = "\n".join(context.evidence) if context else ""
        return (
            f"[검사기준]\n코드: {rule.code}\n제목: {rule.title}\n"
            f"설명: {rule.description}\n\n"
            f"[Rule 사전분석 근거]\n{evidence or '없음'}\n\n"
            f"[문서 내용]\n{content}"
        )
