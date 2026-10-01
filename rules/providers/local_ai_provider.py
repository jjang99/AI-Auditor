import json
from dataclasses import dataclass
from urllib import error, request

from rules.core.ai_provider import AIInspectionContext, AIInspectionResult, BaseAIProvider


class LocalAIProviderError(RuntimeError):
    """Local llama.cpp server 호출 또는 응답 검증 실패."""


@dataclass(frozen=True)
class LocalAISettings:
    base_url: str = "http://127.0.0.1:8080"
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    min_p: float = 0.0
    seed: int = 42
    max_tokens: int = 512
    timeout_seconds: float = 120.0


class LlamaCppAIProvider(BaseAIProvider):
    """llama.cpp의 로컬 OpenAI-compatible endpoint를 사용하는 문서검사 Provider."""

    def __init__(self, settings: LocalAISettings | None = None):
        self.settings = settings or LocalAISettings()

    def inspect(self, document, rule, context: AIInspectionContext | None = None):
        prompt = self._build_prompt(document, rule, context)
        raw_response = self._complete(prompt)
        findings = self._parse_findings(raw_response)

        return AIInspectionResult(
            rule_code=rule.code,
            findings=findings,
            raw_response=raw_response,
            provider_name=self.__class__.__name__,
        )

    def _build_prompt(self, document, rule, context):
        document_text = "\n".join(
            block.text.strip()
            for block in document.blocks
            if block.text and block.text.strip()
        )
        evidence = ()
        if context is not None:
            evidence = tuple(item for item in context.evidence if item)

        evidence_text = "\n".join(f"- {item}" for item in evidence) or "- 없음"

        # Hybrid 사전근거가 있으면 선별된 근거를 AI의 주 판단대상으로 사용한다.
        # 대용량 문서 전체를 함께 전달하면 저사양 로컬 환경에서 불필요한 지연과
        # timeout이 발생할 수 있으므로 중복 전달하지 않는다.
        inspection_text = evidence_text if evidence else document_text
        inspection_label = "선별 문서근거" if evidence else "문서"

        return (
            "당신은 정보시스템 프로젝트 품질점검 보조 AI입니다.\n"
            "제공된 문서와 검사기준만 근거로 판단하세요. 입력에 없는 사실은 만들지 마세요.\n"
            "각 체크포인트는 실제 판정기준입니다. 문서 근거와 각 체크포인트를 직접 대조하세요.\n"
            "체크포인트 위반이 문서에서 확인될 때만 findings에 구체적인 지적사항을 작성하세요.\n"
            "각 지적사항에는 위반 내용과 이를 뒷받침하는 문서 근거를 한국어로 작성하세요.\n"
            "문서에 근거가 부족하거나 위반이 확인되지 않으면 findings를 빈 배열로 반환하세요.\n"
            "예시 문구를 그대로 복사하지 마세요. findings의 모든 내용은 반드시 실제 문서에 근거해야 합니다.\n"
            "반드시 한국어로 작성하고, JSON 객체 하나만 출력하며 설명이나 마크다운을 덧붙이지 마세요.\n\n"
            f"[검사코드] {rule.code}\n"
            f"[검사명] {rule.name}\n"
            f"[검사설명] {rule.description}\n"
            f"[체크포인트] {'; '.join(rule.check_points)}\n"
            f"[Rule/Hybrid 사전근거]\n{evidence_text}\n\n"
            f"[{inspection_label}]\n{inspection_text}\n\n"
            '{"findings":["구체적인 위반 내용과 문서 근거를 작성"]}'
        )

    def _complete(self, prompt: str) -> str:
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.settings.temperature,
            "top_p": self.settings.top_p,
            "top_k": self.settings.top_k,
            "min_p": self.settings.min_p,
            "seed": self.settings.seed,
            "max_tokens": self.settings.max_tokens,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            f"{self.settings.base_url.rstrip('/')}/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.settings.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LocalAIProviderError(f"로컬 AI 호출에 실패했습니다: {exc}") from exc

        try:
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LocalAIProviderError("로컬 AI 응답 형식이 올바르지 않습니다.") from exc

        if not isinstance(content, str) or not content.strip():
            raise LocalAIProviderError("로컬 AI가 빈 응답을 반환했습니다.")

        return content.strip()

    @staticmethod
    def _parse_findings(raw_response: str) -> tuple[str, ...]:
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise LocalAIProviderError("로컬 AI 응답이 유효한 JSON이 아닙니다.") from exc

        if not isinstance(payload, dict) or set(payload) != {"findings"}:
            raise LocalAIProviderError("로컬 AI 응답의 findings 구조가 올바르지 않습니다.")

        findings = payload["findings"]
        if not isinstance(findings, list):
            raise LocalAIProviderError("findings는 배열이어야 합니다.")

        normalized = []
        for finding in findings:
            if not isinstance(finding, str) or not finding.strip():
                raise LocalAIProviderError("findings에는 비어 있지 않은 문자열만 허용됩니다.")
            normalized.append(finding.strip())

        return tuple(normalized)
