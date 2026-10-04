import re
import json
import time
from difflib import SequenceMatcher
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
        if rule.code == "CHG-001" and document.file_type == "version_comparison":
            return self._inspect_change_comparison(document, rule)
        if rule.code == "CHG-012" and document.file_type == "change_test_comparison":
            return self._inspect_change_test_comparison(document, rule)
        if rule.code == "CHG-018" and document.file_type == "inspection_findings":
            return self._inspect_change_risk_synthesis(document, rule)

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

    def _inspect_change_comparison(self, document, rule):
        """Compare versioned artifacts with deterministic paragraph diff + small AI batches."""
        previous_block = next(
            (block for block in document.blocks if block.block_type == "previous_document"),
            None,
        )
        current_block = next(
            (block for block in document.blocks if block.block_type == "current_document"),
            None,
        )
        if previous_block is None or current_block is None:
            return AIInspectionResult(
                rule_code=rule.code,
                findings=(),
                raw_response='{"findings":[]}',
                provider_name=self.__class__.__name__,
            )

        previous_lines = [
            line.strip() for line in previous_block.text.splitlines()[1:]
            if line.strip()
        ]
        current_lines = [
            line.strip() for line in current_block.text.splitlines()[1:]
            if line.strip()
        ]
        matcher = SequenceMatcher(a=previous_lines, b=current_lines, autojunk=False)
        candidates = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            before = " / ".join(previous_lines[i1:i2])
            after = " / ".join(current_lines[j1:j2])
            if not before and not after:
                continue
            candidates.append(
                f"변경형태={tag}; 이전={before or '[없음]'}; 현재={after or '[없음]'}"
            )

        if not candidates:
            return AIInspectionResult(
                rule_code=rule.code,
                findings=(),
                raw_response='{"findings":[]}',
                provider_name=self.__class__.__name__,
            )

        findings = []
        raw_responses = []
        # 한 번에 더 많은 diff 후보를 처리하되 입력 길이를 제한해 호출 수를 줄인다.
        batches = []
        current_batch = []
        current_chars = 0
        for candidate in candidates:
            candidate = candidate[:1200]
            if current_batch and (len(current_batch) >= 16 or current_chars + len(candidate) > 7000):
                batches.append(tuple(current_batch))
                current_batch = []
                current_chars = 0
            current_batch.append(candidate)
            current_chars += len(candidate)
        if current_batch:
            batches.append(tuple(current_batch))

        for batch in batches:
            candidate_text = "\n".join(
                f"{index + 1}. {item}" for index, item in enumerate(batch)
            )
            prompt = (
                "당신은 정보시스템 산출물 변경분석 보조 AI입니다. "
                "아래 변경 후보 중 의미 있는 변경만 판정하세요. "
                "서식·공백·단순 표현 차이는 제외하세요. "
                "각 finding은 120자 이내 한 문장으로 작성하고 최대 4건만 반환하세요. "
                "이전→현재의 핵심 차이만 쓰고 장문 원문을 복사하지 마세요. "
                "입력에 없는 변경을 만들지 마세요. 한국어 JSON 객체 하나만 출력하세요.\n\n"
                f"[이전 산출물] {document.metadata.get('previous_file', '')}\n"
                f"[현재 산출물] {document.metadata.get('current_file', '')}\n"
                f"[변경 후보]\n{candidate_text}\n\n"
                '{"findings":["의미 있는 실제 변경과 근거"]}'
            )
            raw = self._complete(prompt)
            raw_responses.append(raw)
            findings.extend(self._parse_findings(raw))

        # 배치 경계에서 같은 변경이 반복 보고되는 것을 최소화한다.
        unique_findings = []
        seen_findings = set()
        for finding in findings:
            normalized = " ".join(finding.split()).rstrip(".")
            if normalized in seen_findings:
                continue
            seen_findings.add(normalized)
            unique_findings.append(finding)

        return AIInspectionResult(
            rule_code=rule.code,
            findings=tuple(unique_findings),
            raw_response="\n".join(raw_responses),
            provider_name=self.__class__.__name__,
        )

    def _inspect_change_test_comparison(self, document, rule):
        """Inspect confirmed changes against a bounded set of relevant test rows."""
        change_texts = [
            block.text.strip()
            for block in document.blocks
            if block.block_type == "confirmed_change" and block.text and block.text.strip()
        ]
        test_blocks = [
            block
            for block in document.blocks
            if block.block_type == "test_document" and block.text and block.text.strip()
        ]
        if not change_texts or not test_blocks:
            return AIInspectionResult(
                rule_code=rule.code,
                findings=(),
                raw_response='{"findings":[]}',
                provider_name=self.__class__.__name__,
            )

        terms = []
        stop_terms = {"확인된", "변경", "현재", "문서", "기능", "내용", "요구사항", "산출물"}
        for text in change_texts:
            for term in re.findall(r"[가-힣A-Za-z0-9_-]{2,}", text):
                normalized = term.lower()
                if normalized not in stop_terms and normalized not in terms:
                    terms.append(normalized)

        ranked = []
        for index, block in enumerate(test_blocks):
            text = block.text.strip()
            score = sum(1 for term in terms if term in text.lower())
            if score:
                ranked.append((-score, index, text))
        ranked.sort()

        selected = []
        used = 0
        for _score, _index, text in ranked[:24]:
            snippet = text[:900]
            if used + len(snippet) > 7000:
                break
            selected.append(snippet)
            used += len(snippet) + 1

        if not selected:
            selected = [block.text.strip()[:900] for block in test_blocks[:8]]

        direct_coverage = []
        selected_text = "\n".join(selected).lower()
        for change in change_texts[:8]:
            requirement_ids = tuple(
                dict.fromkeys(
                    item.upper()
                    for item in re.findall(r"[A-Za-z]{2,}-\\d+(?:-[A-Za-z]+)?-\\d+", change)
                )
            )
            if requirement_ids and all(item.lower() in selected_text for item in requirement_ids):
                direct_coverage.append(
                    f"- 요구사항 ID 직접 확인: {', '.join(requirement_ids)}"
                )

            normalized_change = re.sub(r"[^가-힣A-Za-z0-9]+", " ", change).strip().lower()
            normalized_selected = re.sub(
                r"[^가-힣A-Za-z0-9]+", " ", selected_text
            ).strip().lower()
            phrases = [
                phrase.strip()
                for phrase in re.split(r"(?:으로|로|및|등|기능|구현|추가|확장|변경)", normalized_change)
                if len(phrase.strip()) >= 8
            ]
            for phrase in phrases:
                if phrase in normalized_selected:
                    direct_coverage.append(f"- 시험문구 직접 확인: {phrase}")
                    break

        direct_coverage = list(dict.fromkeys(direct_coverage))

        prompt = (
            "당신은 변경영향 시험반영 점검 AI입니다. "
            "확인된 변경사항과 관련 시험행만 비교하세요. "
            "변경된 요구·기능이 시험항목, 시험조건, 입력 또는 예상결과에 반영되지 않은 것이 "
            "근거로 확인될 때만 findings를 작성하세요. "
            "관련 시험행이 없다는 사실만으로 누락을 단정하지 마세요. "
            "아래 [직접 반영 근거]에 요구사항 ID나 핵심 시험문구가 확인되어 있으면, "
            "그 근거와 모순되게 해당 요구·기능이 시험에 없다고 판단하지 마세요. "
            "단, 일부 ID만 존재하거나 유사한 다른 기능만 존재하면 반영 완료로 간주하지 마세요. "
            "입력에 없는 사실을 만들지 말고 최대 4건, 각 140자 이내로 작성하세요. "
            "한국어 JSON 객체 하나만 출력하세요.\n\n"
            "[확인된 변경]\n" + "\n".join(change_texts[:8]) +
            "\n\n[직접 반영 근거]\n" + ("\n".join(direct_coverage) or "- 없음") +
            "\n\n[관련 시험행]\n" + "\n".join(selected) +
            '\n\n{"findings":["시험 변경 미반영 근거"]}'
        )
        try:
            raw = self._complete(prompt)
        except LocalAIProviderError as exc:
            raise LocalAIProviderError(
                f"{rule.code} ({rule.name}) 검사 중 오류: {exc}"
            ) from exc
        return AIInspectionResult(
            rule_code=rule.code,
            findings=self._parse_findings(raw),
            raw_response=raw,
            provider_name=self.__class__.__name__,
        )

    def _inspect_change_risk_synthesis(self, document, rule):
        """Synthesize only evidence-backed unresolved change-impact risks."""
        evidence = [
            block.text.strip()
            for block in document.blocks
            if block.text and block.text.strip()
        ]
        if not evidence:
            return AIInspectionResult(
                rule_code=rule.code,
                findings=(),
                raw_response='{"findings":[]}',
                provider_name=self.__class__.__name__,
            )

        prompt = (
            "당신은 변경영향도 종합 위험 점검 AI입니다. "
            "아래에는 이미 확인된 변경·영향·시험반영 결과만 제공됩니다. "
            "이 근거들 사이에서 실제 미반영, 불일치 또는 미해소 위험이 확인될 때만 findings를 작성하세요. "
            "정상, 위반 없음, 점검 수행됨, 문제 없음 같은 결론은 절대로 finding으로 작성하지 마세요. "
            "근거가 부족하거나 위험을 확정할 수 없으면 findings는 반드시 빈 배열이어야 합니다. "
            "입력에 없는 변경·영향·위험을 만들지 마세요. 최대 4건, 각 140자 이내의 한국어로 작성하세요. "
            "JSON 객체 하나만 출력하세요.\n\n"
            "[확인된 변경영향 근거]\n" + "\n".join(evidence[:16]) +
            '\n\n{"findings":["근거가 확인된 미반영 또는 불일치 위험"]}'
        )
        try:
            raw = self._complete(prompt)
        except LocalAIProviderError as exc:
            raise LocalAIProviderError(
                f"{rule.code} ({rule.name}) 검사 중 오류: {exc}"
            ) from exc
        findings = tuple(
            finding for finding in self._parse_findings(raw)
            if not any(
                phrase in finding
                for phrase in ("위반이 확인되지", "문제 없음", "이상 없음", "위반 없음", "점검이 수행")
            )
        )
        return AIInspectionResult(
            rule_code=rule.code,
            findings=findings,
            raw_response=raw,
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
