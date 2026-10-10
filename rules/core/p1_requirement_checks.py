"""P1-B REQ-007 / REQ-012 / REQ-017용 보수적 사전분석.

목표:
- 구조적으로 확인 가능한 후보만 AI에 전달한다.
- REQ-003/REQ-018과 역할을 분리한다.
- N/A, 해당없음, 별도 시트 참조 등 명시적 예외는 누락으로 보지 않는다.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from app.parsers.models import ParsedDocument


_REQUIREMENT_ID_RE = re.compile(
    r"\b(?:REQ-\d+|(?:UI-)?[A-Z]{2,}-\d+-ID-\d+(?:-\d+)*|[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*)\b",
    re.IGNORECASE,
)

_EXCLUDED_VALUES = {"na", "n/a", "해당없음", "해당 없음", "비대상", "시험대상아님", "시험 대상 아님"}


@dataclass(frozen=True)
class RequirementRecord:
    requirement_id: str
    text: str
    file_path: str
    location: str | None = None
    verification_method: str | None = None
    test_reference: str | None = None


def _compact(value: str) -> str:
    return re.sub(r"[\s_./\\-]+", "", str(value).strip().lower())


def _cell_values(block) -> tuple[str, ...]:
    values = tuple(block.metadata.get("cell_values", ()))
    return tuple(str(value).strip() for value in values)


def _is_requirement_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    if any(marker in name for marker in ("요구사항", "requirement", "requirements", "srs", "추적표")):
        return True
    return any(_REQUIREMENT_ID_RE.search(block.text or "") for block in document.blocks[:30])


def _is_test_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(marker in name for marker in ("시험", "테스트", "test", "시나리오", "검증"))


def _is_excluded(value: str) -> bool:
    compact = _compact(value)
    return compact in {_compact(item) for item in _EXCLUDED_VALUES}


def extract_requirement_records(document: ParsedDocument) -> tuple[RequirementRecord, ...]:
    """요구사항 ID/내용과 구조형 검증·시험 참조정보를 보수적으로 추출한다."""
    if not _is_requirement_document(document):
        return ()

    records: list[RequirementRecord] = []
    headers_by_sheet: dict[str, dict[str, int]] = {}

    req_id_headers = {"요구사항id", "요구사항번호", "요구id", "requirementid", "id"}
    req_text_headers = {"요구사항명", "요구사항내용", "요구내용", "내용", "requirement"}
    verification_headers = {
        "검증방법", "확인방법", "시험방법", "검증방안", "검증절차", "수용기준", "판정기준",
    }
    test_ref_headers = {
        "시험id", "테스트id", "통합테스트", "시험항목", "테스트항목", "시험참조",
    }

    for block in document.blocks:
        cells = _cell_values(block)
        sheet = block.sheet or ""

        if cells:
            normalized = [_compact(value) for value in cells]
            req_id_index = next((i for i, v in enumerate(normalized) if v in req_id_headers), None)
            req_text_index = next((i for i, v in enumerate(normalized) if v in req_text_headers), None)
            verification_index = next((i for i, v in enumerate(normalized) if v in verification_headers), None)
            test_ref_index = next((i for i, v in enumerate(normalized) if v in test_ref_headers), None)

            if req_id_index is not None and (req_text_index is not None or verification_index is not None or test_ref_index is not None):
                indexes = {"id": req_id_index}
                if req_text_index is not None:
                    indexes["text"] = req_text_index
                if verification_index is not None:
                    indexes["verification"] = verification_index
                if test_ref_index is not None:
                    indexes["test_ref"] = test_ref_index
                headers_by_sheet[sheet] = indexes
                continue

            indexes = headers_by_sheet.get(sheet)
            if indexes:
                def cell(index_name: str) -> str:
                    index = indexes.get(index_name)
                    return cells[index].strip() if index is not None and index < len(cells) else ""

                req_id = cell("id")
                if not _REQUIREMENT_ID_RE.fullmatch(req_id):
                    continue
                text = cell("text") or block.text.strip()
                verification = cell("verification")
                test_ref = cell("test_ref")
                records.append(
                    RequirementRecord(
                        requirement_id=req_id.upper(),
                        text=text,
                        file_path=str(document.file_path),
                        location=block.location or block.sheet,
                        verification_method=verification or None,
                        test_reference=test_ref or None,
                    )
                )
                continue

        text = (block.text or "").strip()
        if not text:
            continue
        match = _REQUIREMENT_ID_RE.search(text)
        if not match:
            continue
        records.append(
            RequirementRecord(
                requirement_id=match.group(0).upper(),
                text=text,
                file_path=str(document.file_path),
                location=block.location,
            )
        )

    unique: list[RequirementRecord] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        key = (record.requirement_id, record.text.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return tuple(unique)


def build_req007_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """REQ-007: 검증방법 공란/미정 등 구조적으로 확인 가능한 후보만 반환한다."""
    records = extract_requirement_records(document)
    if not records:
        return ()

    evidence: list[str] = []
    unresolved_markers = ("미정", "추후", "협의", "tbd", "정의예정", "예정")

    for record in records:
        # 검증방법 열이 구조적으로 존재했던 행만 '공란'을 의미 있게 본다.
        method = (record.verification_method or "").strip()
        if record.verification_method is None:
            continue
        if not method:
            evidence.append(
                f"{record.location or record.requirement_id}: {record.requirement_id} 검증방법 공란 | {record.text[:500]}"
            )
            continue
        if any(marker in method.lower() for marker in unresolved_markers):
            evidence.append(
                f"{record.location or record.requirement_id}: {record.requirement_id} 검증방법 미확정({method}) | {record.text[:500]}"
            )

    return tuple(evidence)


def _extract_test_requirement_refs(document: ParsedDocument) -> set[str]:
    refs: set[str] = set()
    if not _is_test_document(document):
        return refs
    for block in document.blocks:
        text = block.text or ""
        refs.update(match.upper() for match in _REQUIREMENT_ID_RE.findall(text))
    return refs


def build_req012_evidence(documents: list[ParsedDocument]) -> tuple[str, ...]:
    """REQ-012: 요구사항 ID와 업로드된 시험문서의 명시적 연결을 비교한다.

    시험문서가 하나도 없으면 업로드 불완전 가능성이 크므로 Issue 후보를 만들지 않는다.
    구조상 비시험대상/N/A가 명시된 요구사항도 제외한다.
    """
    requirement_records = tuple(
        record
        for document in documents
        for record in extract_requirement_records(document)
    )
    test_documents = [document for document in documents if _is_test_document(document)]
    if not requirement_records or not test_documents:
        return ()

    test_refs: set[str] = set()
    for document in test_documents:
        test_refs.update(_extract_test_requirement_refs(document))

    evidence: list[str] = []
    for record in requirement_records:
        if record.test_reference and _is_excluded(record.test_reference):
            continue
        if record.requirement_id in test_refs:
            continue
        if record.test_reference and not _is_excluded(record.test_reference):
            # 추적표에 시험참조가 있는데 실제 시험문서에서 ID 연결을 못 찾은 경우.
            evidence.append(
                f"{record.requirement_id}: 명시 시험참조 '{record.test_reference}'의 실제 시험근거 확인 필요 | {record.text[:500]}"
            )
        else:
            evidence.append(
                f"{record.requirement_id}: 업로드된 시험문서에서 요구사항 ID 연결을 찾지 못함 | {record.text[:500]}"
            )
    return tuple(evidence)


def build_req017_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """REQ-017: 추적표에서 명시된 필수 후속 링크의 공란 후보를 추출한다.

    REQ-018처럼 모든 기능 추적열을 강제하지 않고, 현재 표에 실제 존재하는
    후속 산출물 열 가운데 최소 2개 이상이 정의된 추적표만 대상으로 한다.
    """
    if not _is_requirement_document(document):
        return ()

    link_aliases = {
        "설계": ("설계id", "설계", "화면id", "프로그램id", "테이블id"),
        "시험": ("시험id", "테스트id", "통합테스트", "시험", "테스트"),
        "구현": ("소스id", "구현id", "모듈id", "프로그램id"),
    }

    evidence: list[str] = []
    headers_by_sheet: dict[str, tuple[int, dict[str, int]]] = {}

    for block in document.blocks:
        cells = _cell_values(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        normalized = [_compact(value) for value in cells]

        req_index = next(
            (i for i, value in enumerate(normalized) if value in {"요구사항id", "요구사항번호", "요구id"}),
            None,
        )
        if req_index is not None:
            links: dict[str, int] = {}
            for label, aliases in link_aliases.items():
                exact = {_compact(alias) for alias in aliases}
                index = next((i for i, value in enumerate(normalized) if value in exact), None)
                if index is not None:
                    links[label] = index
            if len(links) >= 2:
                headers_by_sheet[sheet] = (req_index, links)
            continue

        header = headers_by_sheet.get(sheet)
        if not header:
            continue
        req_index, links = header
        req_id = cells[req_index].strip() if req_index < len(cells) else ""
        if not _REQUIREMENT_ID_RE.fullmatch(req_id):
            continue

        compact_row = _compact(" ".join(cells))
        if any(marker in compact_row for marker in ("해당없음", "비대상", "별도시트참조", "시트참고")):
            continue

        missing: list[str] = []
        for label, index in links.items():
            value = cells[index].strip() if index < len(cells) else ""
            if _is_excluded(value):
                continue
            compact_value = _compact(value)
            if "시트" in compact_value and ("참고" in compact_value or "참조" in compact_value):
                continue
            if not value:
                missing.append(label)

        if missing:
            evidence.append(
                f"{block.location or block.sheet or req_id}: {req_id} 필수 추적링크 누락 후보({', '.join(missing)}) | {block.text[:500]}"
            )

    return tuple(evidence)
