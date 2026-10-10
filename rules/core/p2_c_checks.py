"""P2-C 변경영향·FP 사전분석.

보수적 원칙:
- 교차문서 검사는 명시적인 변경관리 표와 대응 산출물이 함께 있을 때만 후보를 만든다.
- 문서 한쪽만 업로드됐다는 이유로 미반영을 단정하지 않는다.
- FP-006은 구조형 FP 행에서 분할/통합 의심 후보만 좁히고 최종 의미판단은 AI에 맡긴다.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from app.parsers.models import ParsedDocument


def _compact(value: str) -> str:
    return re.sub(r"[\s_./\\-]+", "", str(value).strip().lower())


def _cells(block) -> tuple[str, ...]:
    values = tuple(block.metadata.get("cell_values", ()))
    return tuple(str(value).strip() for value in values)


def _find_index(normalized: list[str], aliases: set[str]) -> int | None:
    compact_aliases = {_compact(value) for value in aliases}
    return next(
        (index for index, value in enumerate(normalized) if value in compact_aliases),
        None,
    )


def _cell(cells: tuple[str, ...], index: int | None) -> str:
    if index is None or index < 0 or index >= len(cells):
        return ""
    return cells[index].strip()


_CHANGE_ID_HEADERS = {
    "변경ID", "변경번호", "요청ID", "요청번호", "변경요청ID", "changeid", "changeno"
}
_CHANGE_CONTENT_HEADERS = {
    "변경내용", "변경사항", "변경요청내용", "요청내용", "변경대상", "변경내역", "내용"
}
_CHANGE_STATUS_HEADERS = {
    "상태", "승인상태", "처리상태", "반영상태", "진행상태"
}
_CHANGE_IMPACT_HEADERS = {
    "영향대상", "영향범위", "관련산출물", "대상산출물", "영향산출물", "반영대상"
}
_EXCLUDED_CHANGE_STATUSES = {
    "취소", "반려", "거절", "해당없음", "제외", "중복", "cancelled", "rejected", "na", "n/a"
}


def _extract_change_records(documents: list[ParsedDocument]) -> tuple[str, ...]:
    """변경관리 구조가 명확한 표에서 현재 유효한 변경행만 추출한다."""
    records: list[str] = []

    for document in documents:
        headers_by_sheet: dict[str, dict[str, int | None]] = {}
        name = document.file_path.stem.lower()
        likely_change_document = any(
            term in name for term in ("변경", "change", "형상", "요청")
        )

        for block in document.blocks:
            cells = _cells(block)
            if not cells:
                continue
            sheet = block.sheet or ""
            normalized = [_compact(value) for value in cells]

            identifier = _find_index(normalized, _CHANGE_ID_HEADERS)
            content = _find_index(normalized, _CHANGE_CONTENT_HEADERS)
            status = _find_index(normalized, _CHANGE_STATUS_HEADERS)
            impact = _find_index(normalized, _CHANGE_IMPACT_HEADERS)

            if content is not None and (
                identifier is not None or status is not None or impact is not None
            ):
                headers_by_sheet[sheet] = {
                    "id": identifier,
                    "content": content,
                    "status": status,
                    "impact": impact,
                }
                continue

            header = headers_by_sheet.get(sheet)
            if not header:
                continue

            change_content = _cell(cells, header.get("content"))
            if not change_content:
                continue

            change_id = _cell(cells, header.get("id"))
            status_raw = _cell(cells, header.get("status"))
            impact_raw = _cell(cells, header.get("impact"))
            if _compact(status_raw) in {_compact(value) for value in _EXCLUDED_CHANGE_STATUSES}:
                continue

            # 일반 표를 변경관리 표로 오인하지 않도록 파일명 또는 변경ID/영향열 근거가 필요하다.
            if not likely_change_document and not change_id and not impact_raw:
                continue

            location = block.location or sheet or "위치 미상"
            records.append(
                "변경근거 | "
                f"파일={document.file_path.name} | 위치={location} | "
                f"ID={change_id or '-'} | 내용={change_content} | "
                f"영향={impact_raw or '-'} | 상태={status_raw or '-'}"
            )

    return tuple(dict.fromkeys(records))


def _is_data_design_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(
        term in name
        for term in (
            "데이터", "테이블", "컬럼", "엔터티", "엔티티", "erd", "db설계", "database",
            "논리모델", "물리모델", "데이터모델"
        )
    )


def _is_fp_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower().replace(" ", "")
    return any(term in name for term in ("fp", "기능점수", "functionpoint"))


def _is_general_design_document(document: ParsedDocument) -> bool:
    if _is_data_design_document(document) or _is_fp_document(document):
        return False
    name = document.file_path.stem.lower()
    return any(
        term in name
        for term in (
            "설계", "화면", "인터페이스", "연계", "프로그램", "컴포넌트", "architecture", "아키텍처"
        )
    )


def _document_snippets(
    documents: tuple[ParsedDocument, ...],
    *,
    max_items: int = 12,
    max_chars: int = 5000,
) -> tuple[str, ...]:
    snippets: list[str] = []
    used = 0

    for document in documents:
        for block in document.blocks:
            text = (block.text or "").strip()
            if not text:
                continue
            remaining = max_chars - used
            if remaining <= 0 or len(snippets) >= max_items:
                return tuple(snippets)
            snippet = text[: min(600, remaining)]
            snippets.append(
                f"{document.file_path.name} | {block.location or block.block_type} | {snippet}"
            )
            used += len(snippet) + 1

    return tuple(snippets)


def _cross_document_evidence(
    change_records: tuple[str, ...],
    target_documents: tuple[ParsedDocument, ...],
    label: str,
) -> tuple[str, ...]:
    if not change_records or not target_documents:
        return ()

    snippets = _document_snippets(target_documents)
    if not snippets:
        return ()

    target_text = " || ".join(snippets)
    return tuple(
        f"{label} | {record} | 대응산출물={target_text}"
        for record in change_records[:8]
    )


def build_chg008_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """CHG-008: 명시적 변경과 일반 설계 산출물을 함께 AI에 전달한다."""
    changes = _extract_change_records(documents)
    design_documents = tuple(
        document for document in documents if _is_general_design_document(document)
    )
    return _cross_document_evidence(changes, design_documents, "설계 변경반영 확인 후보")


def build_chg010_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """CHG-010: 데이터 영향이 명시된 변경만 데이터설계와 교차검증한다."""
    data_terms = (
        "데이터", "테이블", "컬럼", "칼럼", "엔터티", "엔티티", "db", "스키마", "erd"
    )
    changes = tuple(
        record
        for record in _extract_change_records(documents)
        if any(term in record.lower() for term in data_terms)
    )
    data_documents = tuple(
        document for document in documents if _is_data_design_document(document)
    )
    return _cross_document_evidence(changes, data_documents, "데이터설계 변경반영 확인 후보")


def build_fp011_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """FP-011: 기능/요구 변경과 FP 산정자료가 함께 있을 때만 후보를 만든다."""
    functional_terms = (
        "요구", "기능", "화면", "서비스", "프로그램", "업무", "추가", "삭제", "변경"
    )
    changes = tuple(
        record
        for record in _extract_change_records(documents)
        if any(term in record.lower() for term in functional_terms)
    )
    fp_documents = tuple(document for document in documents if _is_fp_document(document))
    return _cross_document_evidence(changes, fp_documents, "FP 변경반영 확인 후보")


# FP-006 구조형 사전분석
_FP_NAME_HEADERS = {
    "기능명", "단위프로세스명", "프로세스명", "업무기능명", "기능", "functionname", "function"
}
_FP_TYPE_HEADERS = {"fp유형", "기능유형", "유형", "functiontype"}
_FP_DETAIL_HEADERS = {
    "설명", "기능설명", "처리내용", "업무설명", "입력", "출력", "입출력", "처리조건", "비고", "근거"
}
_SUMMARY_MARKERS = {"합계", "소계", "총계", "계", "요약", "total", "subtotal"}
_ACTION_TERMS = (
    "등록", "수정", "삭제", "조회", "검색", "승인", "반려", "신청", "발급", "전송", "수신", "처리"
)


def _normalize_function_name(value: str) -> str:
    text = re.sub(r"\([^)]*\)|\[[^]]*\]", "", str(value).lower())
    return re.sub(r"[^0-9a-z가-힣]+", "", text)


def _base_function_name(value: str) -> str:
    normalized = _normalize_function_name(value)
    changed = True
    while changed and normalized:
        changed = False
        for term in _ACTION_TERMS:
            if normalized.endswith(term) and len(normalized) > len(term) + 1:
                normalized = normalized[: -len(term)]
                changed = True
                break
    return normalized


def _similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def build_fp006_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """FP-006: 과도한 분할/부적절 통합 가능성이 있는 구조형 FP 행만 후보화한다."""
    if document.file_type not in {"xlsx", "xls"}:
        return ()

    headers_by_sheet: dict[str, dict[str, object]] = {}
    rows_by_sheet: dict[str, list[tuple[str, str, str, tuple[str, ...], str]]] = {}
    detail_headers = {_compact(value) for value in _FP_DETAIL_HEADERS}
    summary_markers = {_compact(value) for value in _SUMMARY_MARKERS}

    for block in document.blocks:
        cells = _cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        normalized = [_compact(value) for value in cells]
        name_index = _find_index(normalized, _FP_NAME_HEADERS)
        type_index = _find_index(normalized, _FP_TYPE_HEADERS)

        if name_index is not None and type_index is not None:
            detail_indexes = tuple(
                index for index, value in enumerate(normalized) if value in detail_headers
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
        name = _cell(cells, int(header["name"]))
        fp_type = _cell(cells, int(header["type"]))
        if not name or not fp_type or _compact(name) in summary_markers:
            continue

        details = tuple(
            _cell(cells, index)
            for index in tuple(header["details"])
            if _cell(cells, index)
        )
        location = block.location or sheet or "위치 미상"
        rows_by_sheet.setdefault(sheet, []).append(
            (_normalize_function_name(name), _base_function_name(name), fp_type, details, location)
        )

        joined = " ".join((name, *details))
        actions = tuple(term for term in _ACTION_TERMS if term in joined)
        if len(set(actions)) >= 2 and any(connector in joined for connector in (" 및 ", "·", ",", "와 ", "과 ")):
            rows_by_sheet.setdefault(f"{sheet}::__integrated__", []).append(
                (_normalize_function_name(name), _base_function_name(name), fp_type, details, location)
            )

    evidence: list[str] = []

    # 한 행에 독립 행위가 복수로 묶인 경우: 통합 과다 후보
    for key, rows in rows_by_sheet.items():
        if not key.endswith("::__integrated__"):
            continue
        for _name_key, _base, fp_type, details, location in rows:
            evidence.append(
                "FP 기능 통합 후보 | "
                f"위치={location} | 유형={fp_type} | 상세={' ; '.join(details) or '상세근거 없음'}"
            )

    # 같은 핵심기능이 여러 행으로 나뉘고 상세근거가 상당히 유사한 경우: 과도 분할 후보
    for sheet, rows in rows_by_sheet.items():
        if sheet.endswith("::__integrated__"):
            continue
        for left_index in range(len(rows)):
            left_name, left_base, left_type, left_details, left_location = rows[left_index]
            for right_index in range(left_index + 1, len(rows)):
                right_name, right_base, right_type, right_details, right_location = rows[right_index]
                if not left_base or left_base != right_base:
                    continue
                if left_name == right_name:
                    # 완전 동일 기능명은 FP-002 중복산정의 책임영역이다.
                    continue
                left_detail = _compact(" ".join(left_details))
                right_detail = _compact(" ".join(right_details))
                if not left_detail or not right_detail:
                    continue
                if _similarity(left_detail, right_detail) < 0.55:
                    continue

                evidence.append(
                    "FP 기능 과도분할 후보 | "
                    f"위치={left_location}, {right_location} | "
                    f"핵심기능={left_base} | 유형={left_type}/{right_type} | "
                    f"상세={'; '.join(left_details)} || {'; '.join(right_details)}"
                )

    return tuple(dict.fromkeys(evidence))
