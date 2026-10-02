import json
import time
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
    timeout_seconds: float = 300.0


class LlamaCppAIProvider(BaseAIProvider):
    """llama.cpp의 로컬 OpenAI-compatible endpoint를 사용하는 문서검사 Provider."""

    def __init__(self, settings: LocalAISettings | None = None):
        self.settings = settings or LocalAISettings()

    def build_requirement_conflict_groups(
        self,
        evidence: tuple[str, ...],
    ) -> tuple[tuple[str, ...], ...]:
        """요구사항을 작은 배치로 의미 구조화해 REQ-004 비교 단위를 만든다."""
        if len(evidence) < 2:
            return ()

        # 저사양 로컬 CPU에서 전체 요구사항을 한 번에 구조화하면 timeout이 발생한다.
        # 작은 배치에서 명시적 상충 후보만 선별하고, 최종 상충 여부는 inspect()가 재판정한다.
        batch_size = 12
        overlap = 1
        groups: list[tuple[str, ...]] = []
        seen: set[tuple[str, ...]] = set()
        self.last_requirement_conflict_diagnostics = {
            "evidence_count": len(evidence),
            "batch_count": 0,
            "raw_group_count": 0,
            "valid_group_count": 0,
            "batches": [],
        }

        start = 0
        while start < len(evidence):
            batch = evidence[start : start + batch_size]
            if len(batch) < 2:
                break

            numbered = "\n".join(
                f"{index}: {item}"
                for index, item in enumerate(batch)
            )
            prompt = (
                "당신은 요구사항 엔지니어링 분석기입니다. "
                "아래 요구사항을 대상(entity), 행위/속성(action/property), 조건(condition), "
                "효과/값(effect/value), 극성(polarity) 관점에서 분석하세요. "
                "이 단계는 단순 관련성 그룹화가 아니라 상충 가능성이 텍스트에 직접 드러나는 "
                "요구사항 쌍만 선별하는 단계입니다. "
                "동일 대상/속성에 대해 서로 동시에 만족할 수 없는 값·범위·조건·상태·극성이 "
                "확인되는 경우에만 한 쌍으로 반환하세요. "
                "같은 업무 주제이거나 같은 단어를 사용한다는 이유만으로 묶지 마세요. "
                "상충 근거가 명확하지 않은 요구사항은 제외하세요. "
                "각 그룹은 정확히 2개 index만 포함하세요. "
                "JSON 객체 하나만 출력하세요.\n\n"
                f"{numbered}"
            )
            schema = {
                "type": "json_schema",
                "json_schema": {
                    "name": "requirement_conflict_groups",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "groups": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "indexes": {
                                            "type": "array",
                                            "items": {"type": "integer"},
                                            "minItems": 2,
                                            "maxItems": 2,
                                            "uniqueItems": True,
                                        }
                                    },
                                    "required": ["indexes"],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": ["groups"],
                        "additionalProperties": False,
                    },
                },
            }
            self.last_requirement_conflict_diagnostics["batch_count"] += 1
            batch_started = time.perf_counter()
            raw = self._complete(prompt, response_format=schema)
            batch_seconds = round(time.perf_counter() - batch_started, 2)
            try:
                payload = json.loads(raw)
                raw_groups = payload["groups"]
                self.last_requirement_conflict_diagnostics["raw_group_count"] += len(raw_groups)
                self.last_requirement_conflict_diagnostics["batches"].append(
                    {
                        "start": start,
                        "items": len(batch),
                        "seconds": batch_seconds,
                        "raw_groups": len(raw_groups),
                    }
                )
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise LocalAIProviderError(
                    "REQ-004 의미 구조화 응답 형식이 올바르지 않습니다."
                ) from exc

            for group in raw_groups:
                indexes = group.get("indexes", [])
                valid_indexes = []
                for index in indexes:
                    if (
                        isinstance(index, int)
                        and 0 <= index < len(batch)
                        and index not in valid_indexes
                    ):
                        valid_indexes.append(index)
                if len(valid_indexes) < 2:
                    continue
                items = tuple(batch[index] for index in valid_indexes)
                key = tuple(sorted(items))
                if key in seen:
                    continue
                seen.add(key)
                groups.append(items)
                self.last_requirement_conflict_diagnostics["valid_group_count"] = len(groups)

            if start + batch_size >= len(evidence):
                break
            start += batch_size - overlap

        return tuple(groups)

    def inspect(self, document, rule, context: AIInspectionContext | None = None):
        prompt = self._build_prompt(document, rule, context)
        try:
            raw_response = self._complete(prompt)
        except LocalAIProviderError as exc:
            raise LocalAIProviderError(
                f"{rule.code} ({rule.name}) 검사 중 오류: {exc}"
            ) from exc
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
        inspection_text = evidence_text if evidence else self._select_relevant_document_text(
            document,
            rule,
        )
        inspection_label = "선별 문서근거" if evidence else "관련 문서근거"

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

    @staticmethod
    def _select_relevant_document_text(document, rule, max_chars: int = 6000) -> str:
        """대용량 문서에서 규칙과 관련성이 높은 블록만 AI 입력으로 선별한다."""
        terms = []
        for value in (rule.name, rule.description, *rule.check_points):
            for term in str(value).replace("/", " ").replace("·", " ").split():
                normalized = term.strip("[](){}.,:;'\"")
                if len(normalized) >= 2 and normalized not in terms:
                    terms.append(normalized)

        ranked = []
        for index, block in enumerate(document.blocks):
            text = block.text.strip() if block.text else ""
            if not text:
                continue
            score = sum(1 for term in terms if term.lower() in text.lower())
            if score:
                ranked.append((-score, index, text))

        # 관련 키워드가 전혀 잡히지 않는 문서는 앞부분을 제한적으로 사용한다.
        if not ranked:
            ranked = [(0, index, block.text.strip()) for index, block in enumerate(document.blocks)
                      if block.text and block.text.strip()]

        ranked.sort()
        selected = []
        used = 0
        for _score, _index, text in ranked:
            remaining = max_chars - used
            if remaining <= 0:
                break
            snippet = text[:remaining]
            selected.append(snippet)
            used += len(snippet) + 1

        return "\n".join(selected)

    def _complete(self, prompt: str, response_format: dict | None = None) -> str:
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.settings.temperature,
            "top_p": self.settings.top_p,
            "top_k": self.settings.top_k,
            "min_p": self.settings.min_p,
            "seed": self.settings.seed,
            "max_tokens": self.settings.max_tokens,
        }
        payload["response_format"] = response_format or {
            "type": "json_schema",
            "json_schema": {
                "name": "inspection_findings",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "findings": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["findings"],
                    "additionalProperties": False,
                },
            },
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
