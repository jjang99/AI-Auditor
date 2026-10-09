import re
from dataclasses import dataclass
from pathlib import Path

from app.parsers.models import ParsedDocument


@dataclass(frozen=True)
class DeliverableRequirement:
    """AUD-001에서 실제 제출대상으로 판단한 산출물 1건."""

    name: str
    source_file: str
    location: str | None = None
    source_kind: str = "deliverable_list"


_DELIVERABLE_HEADERS = {
    "산출물명",
    "산출물",
    "문서명",
    "표준산출물명",
    "테일러링산출물",
    "작성산출물명",
}
_APPLICATION_HEADERS = {
    "적용여부",
    "적용",
    "대상여부",
}
_STATUS_HEADERS = {
    "작성여부",
    "작성유무",
    "작성상태",
    "제출여부",
    "완료여부",
    "상태",
}

_NEGATIVE_APPLICATION = {
    "미적용",
    "제외",
    "해당없음",
    "해당사항없음",
    "na",
    "n/a",
    "-",
    "x",
    "×",
}
_NEGATIVE_DUE_STATUS = {
    "시기미도래",
    "미도래",
    "해당없음",
    "해당사항없음",
    "na",
    "n/a",
    "-",
    "제외",
    "점검제외",
}
_POSITIVE_APPLICATION = {
    "적용",
    "대상",
    "작성",
    "제출",
    "o",
    "y",
    "yes",
    "○",
    "◎",
    "●",
    "1",
}
_GENERIC_ALIASES = {
    "계획서",
    "결과서",
    "정의서",
    "설계서",
    "보고서",
    "목록",
    "대장",
    "문서",
    "산출물",
}


def _compact(value: str) -> str:
    return re.sub(r"[\s_()\[\]{}./\\-]+", "", str(value).strip().lower())


def _source_kind(document: ParsedDocument) -> str | None:
    name = _compact(document.file_path.stem)
    if "산출물목록" in name:
        return "deliverable_list"
    if "테일러링" in name or "tailoring" in name:
        return "tailoring"

    # 파일명이 단순한 경우에도 XLS/XLSX 표 헤더가 명확하면 기준문서로 인정한다.
    for block in document.blocks[:40]:
        cells = tuple(block.metadata.get("cell_values", ()))
        if not cells:
            continue
        normalized = {_compact(str(value)) for value in cells if str(value).strip()}
        if normalized & _DELIVERABLE_HEADERS:
            if normalized & (_APPLICATION_HEADERS | _STATUS_HEADERS):
                return "deliverable_list"
    return None


def _header_indexes(cells: tuple[str, ...]) -> dict[str, int] | None:
    normalized = [_compact(value) for value in cells]

    deliverable_index = next(
        (index for index, value in enumerate(normalized) if value in _DELIVERABLE_HEADERS),
        None,
    )
    if deliverable_index is None:
        return None

    indexes: dict[str, int] = {"deliverable": deliverable_index}
    application_index = next(
        (index for index, value in enumerate(normalized) if value in _APPLICATION_HEADERS),
        None,
    )
    status_index = next(
        (index for index, value in enumerate(normalized) if value in _STATUS_HEADERS),
        None,
    )
    if application_index is not None:
        indexes["application"] = application_index
    if status_index is not None:
        indexes["status"] = status_index
    return indexes


def _cell(cells: tuple[str, ...], index: int | None) -> str:
    if index is None or index >= len(cells):
        return ""
    return str(cells[index]).strip()


def _is_not_applicable(value: str) -> bool:
    compact = _compact(value)
    return compact in _NEGATIVE_APPLICATION or any(
        marker in compact for marker in ("미적용", "해당없음", "적용제외")
    )


def _is_not_due(value: str) -> bool:
    compact = _compact(value)
    return compact in _NEGATIVE_DUE_STATUS or any(
        marker in compact for marker in ("시기미도래", "미도래", "해당없음", "점검제외")
    )


def _is_positive_application(value: str) -> bool:
    return _compact(value) in _POSITIVE_APPLICATION


def _extract_structured_rows(
    document: ParsedDocument,
    source_kind: str,
) -> tuple[DeliverableRequirement, ...]:
    requirements: list[DeliverableRequirement] = []
    headers_by_sheet: dict[str, dict[str, int]] = {}

    for block in document.blocks:
        raw_cells = tuple(block.metadata.get("cell_values", ()))
        if not raw_cells:
            continue
        cells = tuple(str(value).strip() for value in raw_cells)
        sheet = block.sheet or ""

        header = _header_indexes(cells)
        if header is not None:
            headers_by_sheet[sheet] = header
            continue

        indexes = headers_by_sheet.get(sheet)
        if not indexes:
            continue

        deliverable = _cell(cells, indexes.get("deliverable"))
        if not deliverable:
            continue

        application = _cell(cells, indexes.get("application"))
        status = _cell(cells, indexes.get("status"))
        row_text = " ".join(value for value in cells if value)

        # 적용 제외는 작성상태와 무관하게 AUD-001 제출대상에서 제외한다.
        if application and _is_not_applicable(application):
            continue
        if any(marker in _compact(row_text) for marker in ("미적용", "적용제외")):
            continue

        # 아직 제출 시점이 아닌 산출물과 해당없음 항목은 현재 누락으로 보지 않는다.
        if status and _is_not_due(status):
            continue
        if any(marker in _compact(row_text) for marker in ("시기미도래", "점검제외")):
            continue

        if source_kind == "tailoring":
            # 테일러링 단독 사용 시에는 명시적으로 적용 대상임을 확인한 행만 사용한다.
            # X 표시는 테일러링에서는 미적용 의미일 수 있으므로 제출대상으로 추정하지 않는다.
            if application:
                if not _is_positive_application(application):
                    continue
            elif status:
                if not _is_positive_application(status):
                    continue
            else:
                continue

        requirements.append(
            DeliverableRequirement(
                name=deliverable,
                source_file=str(document.file_path),
                location=block.location or block.sheet,
                source_kind=source_kind,
            )
        )

    return tuple(requirements)


def _unique_requirements(
    requirements: list[DeliverableRequirement],
) -> tuple[DeliverableRequirement, ...]:
    unique: list[DeliverableRequirement] = []
    seen: set[str] = set()
    for item in requirements:
        key = _compact(item.name)
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return tuple(unique)


def _raw_aliases(value: str) -> tuple[str, ...]:
    value = str(value).strip()
    if not value:
        return ()

    # 경로/확장자/버전 표기를 제거하되 문서 식별코드는 그대로 둬서 오매칭을 줄인다.
    value = Path(value).name
    value = re.sub(r"\.(?:hwp|hwpx|doc|docx|xls|xlsx|pdf|ppt|pptx)$", "", value, flags=re.I)
    value = re.sub(r"(?i)[_\- ](?:v|ver)?\d+(?:\.\d+)*$", "", value)

    parts = [value]
    for match in re.findall(r"[\(\[]([^\)\]]+)[\)\]]", value):
        if match and "별첨" not in match:
            parts.append(match)
    without_parentheses = re.sub(r"[\(\[].*?[\)\]]", " ", value).strip()
    if without_parentheses:
        parts.append(without_parentheses)

    # 프로젝트 문서코드 뒤의 실질 산출물명도 별도 alias로 사용한다.
    code_stripped = re.sub(
        r"^(?:\d+[_\- ])?(?:[A-Z0-9]+[_\-]){2,8}(?:\[별첨\s*\d+\][_\-]?)?",
        "",
        value,
        flags=re.I,
    ).strip(" _-")
    if code_stripped and code_stripped != value:
        parts.append(code_stripped)

    aliases: list[str] = []
    for part in parts:
        alias = _compact(part)
        if len(alias) < 3 or alias in _GENERIC_ALIASES or alias in aliases:
            continue
        aliases.append(alias)
    return tuple(aliases)


def deliverable_matches_file(deliverable: str, uploaded_path: Path) -> bool:
    expected_aliases = _raw_aliases(deliverable)
    uploaded_aliases = _raw_aliases(uploaded_path.name)
    if not expected_aliases or not uploaded_aliases:
        return False

    for expected in expected_aliases:
        for uploaded in uploaded_aliases:
            if expected == uploaded:
                return True
            # 실질 산출물명이 프로젝트 문서코드/버전과 함께 붙는 일반적인 파일명을 허용한다.
            if len(expected) >= 5 and expected in uploaded:
                return True
            if len(uploaded) >= 5 and uploaded in expected:
                return True
    return False


def derive_required_deliverables(
    documents: list[ParsedDocument],
) -> tuple[DeliverableRequirement, ...]:
    """업로드된 산출물목록/테일러링 대비표에서 AUD-001 기준목록을 만든다.

    우선순위:
    1) 산출물목록: 실제 제출대상의 기준
    2) 테일러링 대비표: 산출물목록이 없을 때 명시적 적용행만 보수적으로 사용
       산출물목록이 함께 있으면 테일러링의 명시적 미적용 항목은 제외 근거로 사용
    """

    classified = [
        (document, _source_kind(document))
        for document in documents
    ]
    list_documents = [
        document for document, kind in classified
        if kind == "deliverable_list"
    ]
    tailoring_documents = [
        document for document, kind in classified
        if kind == "tailoring"
    ]

    if list_documents:
        requirements: list[DeliverableRequirement] = []
        for document in list_documents:
            requirements.extend(
                _extract_structured_rows(document, "deliverable_list")
            )

        # 산출물목록과 테일러링을 함께 올린 경우, 테일러링에서 명시적으로
        # 미적용인 항목은 제출대상에서 제외한다.
        excluded_names: list[str] = []
        for document in tailoring_documents:
            headers_by_sheet: dict[str, dict[str, int]] = {}
            for block in document.blocks:
                raw_cells = tuple(block.metadata.get("cell_values", ()))
                if not raw_cells:
                    continue
                cells = tuple(str(value).strip() for value in raw_cells)
                sheet = block.sheet or ""
                header = _header_indexes(cells)
                if header is not None:
                    headers_by_sheet[sheet] = header
                    continue
                indexes = headers_by_sheet.get(sheet)
                if not indexes:
                    continue
                name = _cell(cells, indexes.get("deliverable"))
                application = _cell(cells, indexes.get("application"))
                if name and application and _is_not_applicable(application):
                    excluded_names.append(name)

        if excluded_names:
            requirements = [
                item
                for item in requirements
                if not any(
                    set(_raw_aliases(item.name)) & set(_raw_aliases(excluded))
                    for excluded in excluded_names
                )
            ]
        return _unique_requirements(requirements)

    requirements = []
    for document in tailoring_documents:
        requirements.extend(_extract_structured_rows(document, "tailoring"))
    return _unique_requirements(requirements)
