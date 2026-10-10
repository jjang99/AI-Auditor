"""P1-B REQ-007 / REQ-012 / REQ-017 Hybrid 확장 Engine.

기존 DocumentHybridEngine을 그대로 유지하면서 P1-B의 구조적 후보 추출만 추가한다.
Registry 활성화 전 targeted test로 동작을 검증한다.
"""

import re

from app.parsers.models import ParsedDocument
from rules.core.hybrid_engine import DocumentHybridEngine, HybridInspectionContext
from rules.core.models import DocumentRule
from rules.core.p1_requirement_checks import (
    build_req007_evidence,
    build_req017_evidence,
)


class P1RequirementHybridEngine(DocumentHybridEngine):
    """기존 Hybrid Engine에 P1-B 요구사항 사전분석을 추가한다."""

    def build_context(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
    ) -> HybridInspectionContext:
        if rule.code == "REQ-007":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_req007_evidence(document),
            )

        if rule.code == "REQ-012":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=self._build_req012_trace_evidence(document),
            )

        if rule.code == "REQ-017":
            return HybridInspectionContext(
                document=document,
                rule=rule,
                evidence=build_req017_evidence(document),
            )

        return super().build_context(document, rule)

    @staticmethod
    def _compact(value: str) -> str:
        return re.sub(r"[\s_./\\-]+", "", str(value).strip().lower())

    @classmethod
    def _build_req012_trace_evidence(
        cls,
        document: ParsedDocument,
    ) -> tuple[str, ...]:
        """추적표에 시험열이 명시된 경우 공란 시험참조 후보를 추출한다.

        이 단계에서는 '시험열 자체가 존재하는 추적표'만 다룬다.
        단순 요구사항 문서에 시험정보가 없다는 이유만으로 누락 후보를 만들지 않는다.
        """
        requirement_id_re = re.compile(
            r"^(?:REQ-\d+|(?:UI-)?[A-Z]{2,}-\d+-ID-\d+(?:-\d+)*|[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*)$",
            re.IGNORECASE,
        )
        req_headers = {"요구사항id", "요구사항번호", "요구id"}
        test_headers = {
            "시험id", "테스트id", "통합테스트", "시험항목", "테스트항목", "시험참조",
        }
        excluded = {"na", "n/a", "해당없음", "해당 없음", "비대상", "시험대상아님", "시험 대상 아님"}
        excluded_compact = {cls._compact(value) for value in excluded}

        headers_by_sheet: dict[str, tuple[int, int]] = {}
        evidence: list[str] = []

        for block in document.blocks:
            raw_cells = tuple(block.metadata.get("cell_values", ()))
            if not raw_cells:
                continue
            cells = tuple(str(value).strip() for value in raw_cells)
            normalized = [cls._compact(value) for value in cells]
            sheet = block.sheet or ""

            req_index = next((i for i, value in enumerate(normalized) if value in req_headers), None)
            test_index = next((i for i, value in enumerate(normalized) if value in test_headers), None)
            if req_index is not None and test_index is not None:
                headers_by_sheet[sheet] = (req_index, test_index)
                continue

            header = headers_by_sheet.get(sheet)
            if not header:
                continue
            req_index, test_index = header
            req_id = cells[req_index].strip() if req_index < len(cells) else ""
            if not requirement_id_re.fullmatch(req_id):
                continue

            test_ref = cells[test_index].strip() if test_index < len(cells) else ""
            compact_row = cls._compact(" ".join(cells))
            if any(marker in compact_row for marker in ("시험대상아님", "해당없음", "비대상")):
                continue
            if cls._compact(test_ref) in excluded_compact:
                continue
            if test_ref:
                continue

            evidence.append(
                f"{block.location or block.sheet or req_id}: {req_id} 시험항목 연결 누락 후보 | {block.text[:500]}"
            )

        return tuple(evidence)
