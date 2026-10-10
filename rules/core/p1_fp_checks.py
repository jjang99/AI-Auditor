"""P1-E FP-002 구조형 FP 중복 후보 추출."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.parsers.models import ParsedDocument


@dataclass(frozen=True)
class FPDuplicateCandidate:
    sheet: str | None
    locations: tuple[str, ...]
    function_name: str
    function_type: str
    details: tuple[str, ...]
    evidence: str


_NAME_HEADERS = {
    "기능명", "단위프로세스명", "프로세스명", "업무기능명", "기능", "functionname", "function"
}
_TYPE_HEADERS = {"fp유형", "기능유형", "유형", "functiontype"}
_DETAIL_HEADERS = {
    "설명", "기능설명", "처리내용", "업무설명", "입력", "출력", "입출력", "처리조건", "비고", "근거"
}
_SUMMARY_MARKERS = {"합계", "소계", "총계", "계", "요약", "total", "subtotal"}


def _compact(value: str) -> str:
    return re.sub(r"[\s_./\\-]+", "", str(value).strip().lower())


def _cells(block) -> tuple[str, ...]:
    values = tuple(block.metadata.get("cell_values", ()))
    return tuple(str(value).strip() for value in values)


def _find_index(normalized: list[str], headers: set[str]) -> int | None:
    compact_headers = {_compact(item) for item in headers}
    return next((index for index, value in enumerate(normalized) if value in compact_headers), None)


def _normalize_function_name(value: str) -> str:
    text = re.sub(r"\([^)]*\)", "", str(value))
    text = re.sub(r"\[[^]]*\]", "", text)
    text = re.sub(r"[^0-9a-zA-Z가-힣]+", "", text.lower())
    return text


def _normalize_type(value: str) -> str:
    raw = str(value).strip().upper()
    aliases = {
        "내부논리파일": "ILF",
        "외부연계파일": "EIF",
        "외부인터페이스파일": "EIF",
        "외부입력": "EI",
        "외부출력": "EO",
        "외부조회": "EQ",
    }
    for code in ("ILF", "EIF", "EI", "EO", "EQ"):
        if re.search(rf"\b{code}\b", raw):
            return code
    compact = _compact(value)
    for alias, code in aliases.items():
        if alias in compact:
            return code
    return raw


def _detail_signature(values: tuple[str, ...]) -> str:
    return _compact(" ".join(value for value in values if value))


def _similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    return SequenceMatcher(None, left, right).ratio()


def _similar_function_name(left: str, right: str) -> bool:
    """FP 후보단계에서만 사용할 보수적 유사 기능명 판정."""
    if left == right:
        return True
    if min(len(left), len(right)) >= 4 and (left in right or right in left):
        return True
    return _similarity(left, right) >= 0.80


def _clearly_distinct_details(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    """상세근거가 모두 있고 내용 차이가 큰 경우에만 별도 기능으로 제외한다.

    단순 문구/표현 차이는 FP-002 후보로 남겨 AI가 실질 동일 기능인지 판단하도록 한다.
    """
    if not left or not right:
        return False
    left_signature = _detail_signature(left)
    right_signature = _detail_signature(right)
    if not left_signature or not right_signature:
        return False
    return _similarity(left_signature, right_signature) < 0.65


def build_fp002_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """구조형 FP 표에서 실질 중복 가능성이 높은 행 쌍만 후보화한다.

    보수적 기준:
    - XLS/XLSX만 대상으로 한다.
    - 기능명 + FP 유형 헤더가 확인된 표만 검사한다.
    - 합계/소계/요약행은 제외한다.
    - 동일하거나 충분히 유사한 기능명 + 같은 FP 유형인 행만 후보화한다.
    - 상세 설명/처리조건/입출력 정보가 모두 존재하고 서로 명확히 다른 경우만
      별도 기능으로 간주해 후보에서 제외한다.
    - 단순 표현 차이는 후보에서 제거하지 않고 AI 최종 판단에 맡긴다.
    """
    if document.file_type not in {"xlsx", "xls"}:
        return ()

    headers_by_sheet: dict[str, dict[str, object]] = {}
    rows_by_sheet_type: dict[
        tuple[str, str],
        list[tuple[str, str, tuple[str, ...], str]],
    ] = {}

    summary_markers = {_compact(item) for item in _SUMMARY_MARKERS}
    detail_headers = {_compact(item) for item in _DETAIL_HEADERS}

    for block in document.blocks:
        cells = _cells(block)
        if not cells:
            continue

        sheet = block.sheet or ""
        normalized = [_compact(value) for value in cells]
        name_index = _find_index(normalized, _NAME_HEADERS)
        type_index = _find_index(normalized, _TYPE_HEADERS)

        if name_index is not None and type_index is not None:
            detail_indexes = tuple(
                index
                for index, value in enumerate(normalized)
                if value in detail_headers
            )
            headers_by_sheet[sheet] = {
                "name": name_index,
                "type": type_index,
                "details": detail_indexes,
            }
            continue

        header = headers_by_sheet.get(sheet)
        if not header:
            continue

        name_idx = int(header["name"])
        type_idx = int(header["type"])
        if name_idx >= len(cells) or type_idx >= len(cells):
            continue

        function_name = cells[name_idx].strip()
        function_type = _normalize_type(cells[type_idx])
        normalized_name = _normalize_function_name(function_name)

        if not normalized_name or not function_type:
            continue
        if _compact(function_name) in summary_markers:
            continue

        detail_values = tuple(
            cells[index].strip()
            for index in tuple(header["details"])
            if index < len(cells) and cells[index].strip()
        )
        location = block.location or sheet or "위치 미상"
        rows_by_sheet_type.setdefault((sheet, function_type), []).append(
            (normalized_name, function_name, detail_values, location)
        )

    evidence: list[str] = []
    seen_pairs: set[tuple[str, str, str]] = set()

    for (sheet, function_type), rows in rows_by_sheet_type.items():
        for left_index in range(len(rows)):
            left_name_key, left_name, left_details, left_location = rows[left_index]
            for right_index in range(left_index + 1, len(rows)):
                right_name_key, right_name, right_details, right_location = rows[right_index]

                if not _similar_function_name(left_name_key, right_name_key):
                    continue
                if _clearly_distinct_details(left_details, right_details):
                    continue

                pair_key = tuple(sorted((left_location, right_location))) + (function_type,)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                left_detail_text = "; ".join(left_details) if left_details else "상세근거 없음"
                right_detail_text = "; ".join(right_details) if right_details else "상세근거 없음"
                display_name = (
                    left_name
                    if _normalize_function_name(left_name) == _normalize_function_name(right_name)
                    else f"{left_name} ↔ {right_name}"
                )

                evidence.append(
                    "FP 산정대상 중복 후보 | "
                    f"기능명={display_name} | 유형={function_type} | "
                    f"위치={left_location}, {right_location} | "
                    f"행별 상세={left_detail_text} || {right_detail_text}"
                )

    return tuple(evidence)
