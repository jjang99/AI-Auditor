"""P2-B 감리·요구사항 Rule용 보수적 사전분석.

원칙:
- 구조를 확인할 수 있는 행/ID/헤더만 사용한다.
- 교차문서 Rule은 실제 비교 가능한 문서가 둘 이상 있을 때만 후보를 만든다.
- 일부 문서 미업로드를 곧바로 오류로 확정하지 않는다.
"""

from __future__ import annotations

import re
from collections import defaultdict

from app.parsers.models import ParsedDocument


def _compact(value: object) -> str:
    return re.sub(r"[^가-힣a-z0-9]+", "", str(value).strip().lower())


def _cells(block) -> tuple[str, ...]:
    raw = tuple(block.metadata.get("cell_values", ()))
    return tuple(str(value).strip() for value in raw)


def _header_index(cells: tuple[str, ...], aliases: tuple[str, ...]) -> int | None:
    normalized = [_compact(value) for value in cells]
    wanted = {_compact(alias) for alias in aliases}
    for index, value in enumerate(normalized):
        if value in wanted:
            return index
    return None


def _cell(cells: tuple[str, ...], index: int | None) -> str:
    if index is None or index < 0 or index >= len(cells):
        return ""
    return cells[index].strip()


def _is_summary(cells: tuple[str, ...]) -> bool:
    text = _compact(" ".join(cells))
    return any(marker in text for marker in ("합계", "소계", "총계", "요약", "total", "subtotal"))


_ID_ALIASES = (
    "ID", "식별자", "요구사항ID", "요구사항번호", "인터페이스ID", "연계ID",
    "화면ID", "프로그램ID", "테이블ID", "기능ID",
)
_NAME_ALIASES = (
    "명칭", "이름", "요구사항명", "인터페이스명", "연계명", "기능명",
    "화면명", "프로그램명", "테이블명",
)


def build_aud005_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """AUD-005: 동일 ID가 여러 문서에서 다른 명칭으로 사용된 후보만 추린다."""
    occurrences: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for document in documents:
        headers: dict[str, tuple[int, int]] = {}
        for block in document.blocks:
            cells = _cells(block)
            if not cells:
                continue
            sheet = block.sheet or ""
            id_index = _header_index(cells, _ID_ALIASES)
            name_index = _header_index(cells, _NAME_ALIASES)
            if id_index is not None and name_index is not None:
                headers[sheet] = (id_index, name_index)
                continue

            indexes = headers.get(sheet)
            if not indexes or _is_summary(cells):
                continue
            identifier = _cell(cells, indexes[0])
            name = _cell(cells, indexes[1])
            if not identifier or not name:
                continue
            if len(_compact(identifier)) < 3:
                continue
            occurrences[_compact(identifier)].append((document.file_path.name, name))

    evidence: list[str] = []
    for identifier, items in occurrences.items():
        if len({file_name for file_name, _ in items}) < 2:
            continue
        distinct_names = {_compact(name) for _, name in items if name}
        if len(distinct_names) < 2:
            continue
        rendered = " / ".join(f"{file_name}: {name}" for file_name, name in items[:8])
        evidence.append(f"동일 ID 용어 불일치 후보 | ID={identifier} | {rendered}")
    return tuple(evidence)


_INTERFACE_ID_ALIASES = ("인터페이스ID", "연계ID", "IFID", "인터페이스번호", "연계번호")
_SENDER_ALIASES = ("송신시스템", "송신", "제공시스템", "출발시스템")
_RECEIVER_ALIASES = ("수신시스템", "수신", "사용시스템", "대상시스템")
_METHOD_ALIASES = ("연계방식", "인터페이스방식", "방식", "프로토콜")
_CYCLE_ALIASES = ("주기", "연계주기", "수행주기", "배치주기")
_DATA_ALIASES = ("데이터", "연계데이터", "전문", "메시지", "파일")


def build_aud021_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """AUD-021: 동일 인터페이스 ID의 핵심 정의가 문서 간 다를 때 후보화한다."""
    occurrences: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)

    for document in documents:
        headers: dict[str, dict[str, int]] = {}
        for block in document.blocks:
            cells = _cells(block)
            if not cells:
                continue
            sheet = block.sheet or ""
            identifier = _header_index(cells, _INTERFACE_ID_ALIASES)
            sender = _header_index(cells, _SENDER_ALIASES)
            receiver = _header_index(cells, _RECEIVER_ALIASES)
            method = _header_index(cells, _METHOD_ALIASES)
            cycle = _header_index(cells, _CYCLE_ALIASES)
            data = _header_index(cells, _DATA_ALIASES)
            if identifier is not None and sum(x is not None for x in (sender, receiver, method, cycle, data)) >= 2:
                headers[sheet] = {
                    key: index for key, index in {
                        "id": identifier, "송신": sender, "수신": receiver,
                        "방식": method, "주기": cycle, "데이터": data,
                    }.items() if index is not None
                }
                continue

            indexes = headers.get(sheet)
            if not indexes or _is_summary(cells):
                continue
            interface_id = _cell(cells, indexes.get("id"))
            if not interface_id:
                continue
            values = {
                key: _cell(cells, index)
                for key, index in indexes.items()
                if key != "id" and _cell(cells, index)
            }
            if values:
                occurrences[_compact(interface_id)].append((document.file_path.name, values))

    evidence: list[str] = []
    for interface_id, items in occurrences.items():
        if len({file_name for file_name, _ in items}) < 2:
            continue
        differing = []
        for field in ("송신", "수신", "방식", "주기", "데이터"):
            values = {_compact(data.get(field, "")) for _, data in items if data.get(field)}
            if len(values) >= 2:
                differing.append(field)
        if not differing:
            continue
        detail = " / ".join(
            f"{file_name}: " + ", ".join(f"{key}={value}" for key, value in values.items())
            for file_name, values in items[:6]
        )
        evidence.append(
            f"인터페이스 문서정보 불일치 후보 | ID={interface_id} | 불일치={','.join(differing)} | {detail}"
        )
    return tuple(evidence)


_REQ_ID_ALIASES = ("요구사항ID", "요구사항번호", "RequirementID", "REQID")
_REQ_STATUS_ALIASES = ("상태", "요구사항상태", "진행상태")
_REQ_APPROVAL_ALIASES = ("승인상태", "승인여부", "확정여부", "확정상태")
_REQ_SOURCE_ALIASES = ("출처", "근거", "상위요구", "상위요구사항", "RFP", "계약근거", "요구출처")


def build_req021_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """REQ-021: 상태와 승인/확정정보의 명확한 구조적 모순 후보."""
    evidence: list[str] = []
    headers: dict[str, dict[str, int]] = {}
    completed = {"완료", "확정", "closed", "done"}
    deleted = {"삭제", "폐기", "제외", "cancelled", "canceled"}
    unapproved = {"미승인", "승인대기", "미확정", "검토중", "대기", "pending"}
    approved = {"승인", "승인완료", "확정", "approved", "confirmed"}

    for block in document.blocks:
        cells = _cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        req_id = _header_index(cells, _REQ_ID_ALIASES)
        status = _header_index(cells, _REQ_STATUS_ALIASES)
        approval = _header_index(cells, _REQ_APPROVAL_ALIASES)
        if req_id is not None and status is not None and approval is not None:
            headers[sheet] = {"id": req_id, "status": status, "approval": approval}
            continue

        indexes = headers.get(sheet)
        if not indexes or _is_summary(cells):
            continue
        rid = _cell(cells, indexes["id"])
        status_raw = _cell(cells, indexes["status"])
        approval_raw = _cell(cells, indexes["approval"])
        if not rid or not status_raw or not approval_raw:
            continue
        status_norm = _compact(status_raw)
        approval_norm = _compact(approval_raw)
        contradiction = (
            status_norm in {_compact(v) for v in completed}
            and approval_norm in {_compact(v) for v in unapproved}
        ) or (
            status_norm in {_compact(v) for v in deleted}
            and approval_norm in {_compact(v) for v in approved}
        )
        if contradiction:
            evidence.append(
                f"요구사항 상태·승인정보 불일치 후보 | ID={rid} | 상태={status_raw} | 승인/확정={approval_raw}"
            )
    return tuple(evidence)


def build_req027_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """REQ-027: 출처/상위요구 필드가 있는 구조에서 근거가 비어 있는 요구사항 후보."""
    evidence: list[str] = []
    headers: dict[str, dict[str, int]] = {}
    excluded = {"해당없음", "비대상", "na", "n/a", "자체", "내부개선"}

    for block in document.blocks:
        cells = _cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        req_id = _header_index(cells, _REQ_ID_ALIASES)
        source = _header_index(cells, _REQ_SOURCE_ALIASES)
        if req_id is not None and source is not None:
            headers[sheet] = {"id": req_id, "source": source}
            continue

        indexes = headers.get(sheet)
        if not indexes or _is_summary(cells):
            continue
        rid = _cell(cells, indexes["id"])
        source_raw = _cell(cells, indexes["source"])
        if not rid:
            continue
        if _compact(source_raw) in {_compact(v) for v in excluded}:
            continue
        if not source_raw:
            evidence.append(f"요구사항 출처·상위요구 근거 누락 후보 | ID={rid}")
    return tuple(evidence)
