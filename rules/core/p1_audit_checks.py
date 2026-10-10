"""P1-C AUD-010 / AUD-018용 보수적 사전분석."""

from __future__ import annotations

from datetime import datetime
import re

from app.parsers.models import ParsedDocument


def _compact(value: str) -> str:
    return re.sub(r"[\s_./\\-]+", "", str(value).strip().lower())


def _cells(block) -> tuple[str, ...]:
    values = tuple(block.metadata.get("cell_values", ()))
    return tuple(str(value).strip() for value in values)


def _parse_date(value: str):
    text = str(value).strip()
    if not text:
        return None
    for fmt in (
        "%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d",
        "%y-%m-%d", "%y.%m.%d", "%y/%m/%d",
        "%Y%m%d",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def build_aud010_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """WBS 구조에서 명확한 누락/일정역전 후보만 추출한다."""
    work_headers = {"작업명", "업무명", "활동명", "task", "업무", "작업"}
    start_headers = {"시작일", "착수일", "start", "시작"}
    end_headers = {"종료일", "완료일", "end", "종료", "완료예정일"}
    owner_headers = {"담당자", "담당", "책임자", "owner", "담당부서"}

    headers_by_sheet: dict[str, tuple[int, int, int, int | None]] = {}
    evidence: list[str] = []

    for block in document.blocks:
        cells = _cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        normalized = [_compact(value) for value in cells]

        work_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in work_headers}), None)
        start_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in start_headers}), None)
        end_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in end_headers}), None)
        owner_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in owner_headers}), None)

        if work_idx is not None and start_idx is not None and end_idx is not None:
            headers_by_sheet[sheet] = (work_idx, start_idx, end_idx, owner_idx)
            continue

        header = headers_by_sheet.get(sheet)
        if not header:
            continue
        work_idx, start_idx, end_idx, owner_idx = header

        def cell(index: int | None) -> str:
            return cells[index].strip() if index is not None and index < len(cells) else ""

        work = cell(work_idx)
        if not work:
            continue
        compact_work = _compact(work)
        if compact_work in {"합계", "소계", "계", "구분"}:
            continue
        if any(marker in compact_work for marker in ("마일스톤", "milestone")):
            continue

        start = cell(start_idx)
        end = cell(end_idx)
        owner = cell(owner_idx)
        missing = []
        if not start:
            missing.append("시작일")
        if not end:
            missing.append("종료일")
        if owner_idx is not None and not owner:
            missing.append("담당자")

        if missing:
            evidence.append(
                f"{block.location or sheet or work}: WBS 핵심정보 누락 후보({', '.join(missing)}) | {work}"
            )

        start_date = _parse_date(start)
        end_date = _parse_date(end)
        if start_date is not None and end_date is not None and end_date < start_date:
            evidence.append(
                f"{block.location or sheet or work}: WBS 일정 역전 후보(시작 {start} > 종료 {end}) | {work}"
            )

    return tuple(evidence)


def _is_quality_plan(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(term in name for term in ("품질보증", "품질관리", "품질계획", "quality plan", "qa plan"))


def _is_quality_evidence(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(term in name for term in (
        "품질활동", "품질점검", "검토결과", "점검결과", "회의록", "검토회의", "qa result", "quality result"
    ))


def build_aud018_evidence(documents: list[ParsedDocument]) -> tuple[str, ...]:
    """품질활동 계획과 수행근거가 함께 업로드된 경우만 비교 후보를 만든다."""
    plans = [doc for doc in documents if _is_quality_plan(doc)]
    evidence_docs = [doc for doc in documents if _is_quality_evidence(doc)]
    if not plans or not evidence_docs:
        return ()

    actual_text = "\n".join(
        block.text.lower()
        for doc in evidence_docs
        for block in doc.blocks
        if block.text and block.text.strip()
    )

    activity_headers = {"활동명", "품질활동", "점검명", "검토명", "활동", "점검", "검토"}
    due_headers = {"예정일", "수행일", "계획일", "일정", "시점"}
    status_headers = {"상태", "수행상태", "진행상태"}
    excluded_status = ("시기미도래", "미도래", "향후", "예정", "해당없음", "n/a", "na")

    result: list[str] = []
    for doc in plans:
        headers_by_sheet: dict[str, tuple[int, int | None, int | None]] = {}
        for block in doc.blocks:
            cells = _cells(block)
            if not cells:
                continue
            sheet = block.sheet or ""
            normalized = [_compact(value) for value in cells]
            activity_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in activity_headers}), None)
            due_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in due_headers}), None)
            status_idx = next((i for i, v in enumerate(normalized) if v in {_compact(x) for x in status_headers}), None)
            if activity_idx is not None:
                headers_by_sheet[sheet] = (activity_idx, due_idx, status_idx)
                continue

            header = headers_by_sheet.get(sheet)
            if not header:
                continue
            activity_idx, due_idx, status_idx = header

            def cell(index: int | None) -> str:
                return cells[index].strip() if index is not None and index < len(cells) else ""

            activity = cell(activity_idx)
            if not activity:
                continue
            status = cell(status_idx).lower()
            if any(marker in status for marker in excluded_status):
                continue

            activity_key = _compact(activity)
            if len(activity_key) < 2:
                continue
            if activity_key in _compact(actual_text):
                continue

            due = cell(due_idx)
            result.append(
                f"{block.location or sheet or activity}: 계획된 품질활동 수행근거 확인 필요 | 활동={activity} | 시점={due or '-'}"
            )

    return tuple(result)
