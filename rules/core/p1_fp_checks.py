"""P1-E FP-002 구조형 FP 중복 후보 추출."""

from __future__ import annotations

import re
from dataclasses import dataclass

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


def build_fp002_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """구조형 FP 표에서 실질 중복 가능성이 높은 행 묶음만 후보화한다.

    보수적 기준:
    - XLS/XLSX만 대상으로 한다.
    - 기능명 + FP 유형 헤더가 확인된 표만 검사한다.
    - 합계/소계/요약행은 제외한다.
    - 같은 정규화 기능명 + 같은 FP 유형이 2건 이상일 때만 후보화한다.
    - 상세 설명/처리조건/입출력 정보가 모두 존재하고 서로 명확히 다르면
      별도 기능일 가능성이 높으므로 후보에서 제외한다.
    """
    if document.file_type not in {"xlsx", "xls"}:
        return ()

    headers_by_sheet: dict[str, dict[str, object]] = {}
    grouped: dict[tuple[str, str, str], list[tuple[str, tuple[str, ...], str]]] = {}

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
                if value in {_compact(header) for header in _DETAIL_HEADERS}
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
        if _compact(function_name) in {_compact(item) for item in _SUMMARY_MARKERS}:
            continue

        detail_values = tuple(
            cells[index].strip()
            for index in tuple(header["details"])
            if index < len(cells) and cells[index].strip()
        )
        location = block.location or sheet or "위치 미상"
        grouped.setdefault((sheet, normalized_name, function_type), []).append(
            (location, detail_values, function_name)
        )

    evidence: list[str] = []
    for (_sheet, _name_key, function_type), rows in grouped.items():
        if len(rows) < 2:
            continue

        signatures = [
            _detail_signature(details)
            for _location, details, _original_name in rows
            if details
        ]

        # 모든 중복행에 충분한 상세정보가 있고 그 상세가 서로 모두 다르면
        # 이름이 같아도 별도 사용자 기능일 가능성이 높아 후보에서 제외한다.
        if len(signatures) == len(rows) and len(set(signatures)) == len(rows):
            continue

        locations = tuple(location for location, _details, _name in rows)
        display_name = rows[0][2]
        detail_text = tuple(
            "; ".join(details) if details else "상세근거 없음"
            for _location, details, _name in rows
        )
        evidence.append(
            "FP 산정대상 중복 후보 | "
            f"기능명={display_name} | 유형={function_type} | "
            f"위치={', '.join(locations)} | "
            f"행별 상세={' || '.join(detail_text)}"
        )

    return tuple(evidence)
