from dataclasses import replace
from app.parsers.models import ParsedDocument
from rules.core.ai_provider import AIInspectionContext, AIInspectionResult, BaseAIProvider
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
from rules.core.models import DocumentRule, RuleExecutionType


class DocumentAIEngine:
    """ParsedDocument를 대상으로 AI 방식 문서 검사를 수행한다."""

    def __init__(
        self,
        rules: list[DocumentRule] | tuple[DocumentRule, ...],
        provider: BaseAIProvider,
    ):
        self.rules = [
            rule
            for rule in rules
            if rule.enabled
            and rule.execution_type == RuleExecutionType.AI
        ]
        # AUD-024는 개별 검사결과를 종합하는 후처리 Rule이므로
        # 원문 문서 대상의 일반 AI 검사 루프에서는 실행하지 않는다.
        self.document_rules = [
            rule for rule in self.rules
            if rule.code != "AUD-024"
        ]

        self.provider = provider

    @staticmethod
    def _build_requirement_comparison_evidence(
        document: ParsedDocument,
    ) -> tuple[str, ...]:
        """요구사항 비교형 Rule의 전체 요구사항 행을 구조적으로 추출한다.

        XLSX는 Parser가 보존한 원래 셀 위치와 헤더를 사용한다.
        그 외 문서는 기존 텍스트 기반 식별을 사용한다.
        """
        import re

        requirement_id = re.compile(
            r"^[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*$",
            re.IGNORECASE,
        )
        evidence = []
        seen = set()

        if document.file_type == "xlsx":
            headers_by_sheet: dict[str, tuple[str, ...]] = {}

            for block in document.blocks:
                cells = tuple(block.metadata.get("cell_values", ()))
                if not cells:
                    continue

                sheet = block.sheet or ""
                normalized_headers = tuple(
                    re.sub(r"\s+", "", str(value)).lower()
                    for value in cells
                )

                id_indexes = [
                    index
                    for index, value in enumerate(normalized_headers)
                    if "요구사항" in value and ("id" in value or "아이디" in value)
                ]
                name_indexes = [
                    index
                    for index, value in enumerate(normalized_headers)
                    if "요구사항" in value
                    and any(term in value for term in ("명", "내용", "설명"))
                ]

                if id_indexes and name_indexes:
                    headers_by_sheet[sheet] = tuple(str(value) for value in cells)
                    continue

                headers = headers_by_sheet.get(sheet)
                if not headers:
                    continue

                id_index = next(
                    (
                        index for index, value in enumerate(headers)
                        if "요구사항" in re.sub(r"\s+", "", value).lower()
                        and (
                            "id" in re.sub(r"\s+", "", value).lower()
                            or "아이디" in re.sub(r"\s+", "", value).lower()
                        )
                    ),
                    None,
                )
                semantic_indexes = [
                    index
                    for index, value in enumerate(headers)
                    if "요구사항" in re.sub(r"\s+", "", value).lower()
                    and any(
                        term in re.sub(r"\s+", "", value).lower()
                        for term in ("명", "내용", "설명")
                    )
                ]

                detail_indexes = [
                    index
                    for index, value in enumerate(headers)
                    if re.sub(r"\s+", "", value).lower()
                    in ("상세내용", "세부내용", "요구내용")
                ]
                semantic_indexes.extend(
                    index
                    for index in detail_indexes
                    if index not in semantic_indexes
                )

                if id_index is None or id_index >= len(cells):
                    continue

                req_id = cells[id_index].strip()
                if not requirement_id.match(req_id):
                    continue

                semantic_values = [
                    cells[index].strip()
                    for index in semantic_indexes
                    if index < len(cells) and cells[index].strip()
                ]
                if not semantic_values:
                    continue

                normalized = " | ".join((req_id, *semantic_values))
                if normalized in seen:
                    continue
                seen.add(normalized)
                evidence.append(normalized)

            return tuple(evidence)

        for block in document.blocks:
            text = block.text.strip() if block.text else ""
            if not text:
                continue

            first = text.split("|", 1)[0].strip()
            if not requirement_id.match(first):
                continue

            normalized = " ".join(text.split())
            if normalized in seen:
                continue
            seen.add(normalized)
            evidence.append(normalized[:1200])

        return tuple(evidence)

    @staticmethod
    def _requirement_semantic_text(text: str) -> str:
        """추적표 행에서 비교에 사용할 요구사항 의미 텍스트를 반환한다."""
        parts = [part.strip() for part in text.split("|")]
        if not parts:
            return text

        # 첫 필드는 요구사항 ID이며, 이후 필드는 Parser가 헤더 기준으로
        # 추출한 요구사항명/내용/설명이다. ID는 비교 점수에서 제외한다.
        return " ".join(part for part in parts[1:] if part)

    @classmethod
    def _build_comparison_pairs(
        cls,
        evidence: tuple[str, ...],
        *,
        rule_code: str = "REQ-002",
    ) -> tuple[tuple[str, str], ...]:
        """확정적으로 선별 가능한 비교 후보만 만든다.

        임의 임계값/상위 N개 제한으로 검사 범위를 잘라내지 않는다.
        REQ-002는 정규화 후 의미 텍스트가 동일한 경우만 확정 후보로 만든다.
        REQ-004는 현재 평탄화된 XLSX 행만으로 상충 후보를 안전하게 사전선별할
        근거가 없으므로 추정 후보를 만들지 않는다.
        """
        import re

        def normalized(text: str) -> str:
            semantic = cls._requirement_semantic_text(text).lower()
            return re.sub(r"[^가-힣a-z0-9]+", "", semantic)

        if rule_code == "REQ-002":
            groups: dict[str, list[str]] = {}
            for item in evidence:
                key = normalized(item)
                if key:
                    groups.setdefault(key, []).append(item)

            pairs = []
            for items in groups.values():
                if len(items) < 2:
                    continue
                for left_index in range(len(items)):
                    for right_index in range(left_index + 1, len(items)):
                        pairs.append((items[left_index], items[right_index]))
            return tuple(pairs)

        if rule_code == "REQ-004":
            # 상충은 요구사항명이 같은 경우에만 비교한다.
            # 동일 명칭 아래 세부 요구내용/조건이 서로 다르면 AI가 양립 가능 여부를 판단한다.
            # 이름 자체가 다른 기능까지 상충 후보로 확장하지 않는다.
            groups: dict[str, list[str]] = {}
            for item in evidence:
                semantic_parts = [
                    part.strip()
                    for part in cls._requirement_semantic_text(item).split("|")
                    if part.strip()
                ]
                if not semantic_parts:
                    continue
                name_key = re.sub(
                    r"[^가-힣a-z0-9]+",
                    "",
                    semantic_parts[0].lower(),
                )
                if name_key:
                    groups.setdefault(name_key, []).append(item)

            pairs = []
            for items in groups.values():
                if len(items) < 2:
                    continue
                for left_index in range(len(items)):
                    for right_index in range(left_index + 1, len(items)):
                        if normalized(items[left_index]) == normalized(items[right_index]):
                            continue
                        pairs.append((items[left_index], items[right_index]))
            return tuple(pairs)

        return ()

    @staticmethod
    def _build_relevant_evidence(
        document: ParsedDocument,
        rule: DocumentRule,
        max_items: int = 12,
        max_chars: int = 4500,
    ) -> tuple[str, ...]:
        """AI 근거확인형 Rule에 관련성이 높은 블록만 전달한다."""
        import re

        terms = []
        for value in (rule.name, rule.description, *rule.check_points):
            for term in re.split(r"[\\s·/,()]+", str(value)):
                normalized = term.strip("[]{}.,:;'\"")
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

        ranked.sort()
        selected = []
        used = 0
        for _score, _index, text in ranked:
            remaining = max_chars - used
            if remaining <= 0 or len(selected) >= max_items:
                break
            snippet = text[: min(800, remaining)]
            selected.append(snippet)
            used += len(snippet) + 1

        return tuple(selected)

    def inspect_document(
        self,
        document: ParsedDocument,
    ) -> tuple[AIInspectionResult, ...]:
        results: list[AIInspectionResult] = []

        for rule in self.document_rules:
            strategy = get_ai_processing_strategy(rule.code)

            if strategy == AIProcessingStrategy.COMPARISON:
                evidence = self._build_requirement_comparison_evidence(document)
                if len(evidence) < 2:
                    result = AIInspectionResult(
                        rule_code=rule.code,
                        findings=(),
                        raw_response="",
                        provider_name=self.provider.__class__.__name__,
                    )
                else:
                    pairs = self._build_comparison_pairs(
                        evidence,
                        rule_code=rule.code,
                    )
                    if not pairs:
                        result = AIInspectionResult(
                            rule_code=rule.code,
                            findings=(),
                            raw_response="",
                            provider_name=self.provider.__class__.__name__,
                        )
                    else:
                        findings = []
                        raw_responses = []
                        for pair in pairs:
                            pair_result = self.provider.inspect(
                                document,
                                rule,
                                AIInspectionContext(evidence=pair),
                            )
                            findings.extend(pair_result.findings)
                            if pair_result.raw_response:
                                raw_responses.append(pair_result.raw_response)

                        result = AIInspectionResult(
                            rule_code=rule.code,
                            findings=tuple(dict.fromkeys(findings)),
                            raw_response="\n".join(raw_responses),
                            provider_name=self.provider.__class__.__name__,
                        )
            elif strategy == AIProcessingStrategy.SYNTHESIS:
                # 종합형 Rule은 앞선 검사결과를 입력으로 사용하는 후처리 단계에서 실행한다.
                result = AIInspectionResult(
                    rule_code=rule.code,
                    findings=(),
                    raw_response="",
                    provider_name=self.provider.__class__.__name__,
                )
            elif strategy == AIProcessingStrategy.EVIDENCE:
                evidence = self._build_relevant_evidence(document, rule)
                if not evidence:
                    result = AIInspectionResult(
                        rule_code=rule.code,
                        findings=(),
                        raw_response="",
                        provider_name=self.provider.__class__.__name__,
                    )
                else:
                    result = self.provider.inspect(
                        document,
                        rule,
                        AIInspectionContext(evidence=evidence),
                    )
            else:
                result = self.provider.inspect(
                    document,
                    rule,
                )

            result = replace(
                result,
                execution_type=rule.execution_type.value,
                provider_name=self.provider.__class__.__name__,
            )

            results.append(result)

        return tuple(results)
    