"""P2-A 구조형/결정형 Rule 검사 유틸리티.

오탐 방지 원칙:
- 구조를 확정할 수 있는 표/행만 검사한다.
- 합계/구분/예시행은 가능한 범위에서 제외한다.
- 교차문서 Rule은 필요한 기준문서가 함께 업로드된 경우에만 판정한다.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.parsers.models import ParsedDocument
from rules.core.p1_rule_checks import (
    P1StructuredFinding,
    _cell,
    _compact,
    _find_index,
    _is_summary_row,
    _structured_cells,
)


_DONE = {"완료", "수행완료", "실행완료", "종료", "종결", "pass", "passed", "fail", "failed"}
_NOT_DUE = {"예정", "미수행", "미실시", "대기", "계획", "notrun", "scheduled", "pending"}
_OPEN = {"미조치", "미처리", "진행중", "조치중", "처리중", "open", "inprogress", "pending"}
_CLOSED_EXCLUDED = {"완료", "조치완료", "처리완료", "종결", "해결", "취소", "중복", "해당없음", "na", "n/a"}


def _finding(block, evidence: str) -> P1StructuredFinding:
    return P1StructuredFinding(
        evidence=evidence,
        block_type=block.block_type,
        location=block.location,
        page=block.page,
        sheet=block.sheet,
        slide=block.slide,
    )


def find_test_execution_result_gaps(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """AUD-015: 수행완료 시험행의 실제결과/판정 누락을 찾는다."""
    item_headers = {"시험항목", "테스트항목", "시험id", "테스트id", "케이스id", "시험명", "테스트명"}
    status_headers = {"수행상태", "시험상태", "실행상태", "상태", "수행여부"}
    result_headers = {"실제결과", "수행결과", "시험결과", "테스트결과", "결과"}
    judge_headers = {"판정", "성공여부", "합격여부", "passfail", "정상여부"}

    headers_by_sheet: dict[str, dict[str, int]] = {}
    findings: list[P1StructuredFinding] = []

    for block in document.blocks:
        cells = _structured_cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        norm = [_compact(v) for v in cells]
        item = _find_index(norm, item_headers)
        status = _find_index(norm, status_headers)
        result = _find_index(norm, result_headers)
        judge = _find_index(norm, judge_headers)
        if item is not None and status is not None and (result is not None or judge is not None):
            h = {"item": item, "status": status}
            if result is not None:
                h["result"] = result
            if judge is not None:
                h["judge"] = judge
            headers_by_sheet[sheet] = h
            continue

        h = headers_by_sheet.get(sheet)
        if not h or _is_summary_row(cells):
            continue
        item_value = _cell(cells, h.get("item"))
        if not item_value:
            continue
        status_raw = _cell(cells, h.get("status"))
        status_value = _compact(status_raw)
        if not status_value or status_value in _NOT_DUE:
            continue
        if status_value not in _DONE:
            continue

        missing = []
        if "result" in h and not _cell(cells, h.get("result")):
            missing.append("실제결과")
        if "judge" in h and not _cell(cells, h.get("judge")):
            missing.append("판정")
        if missing:
            findings.append(_finding(block, f"시험 수행결과 누락: {item_value} / 상태={status_raw} / 누락={', '.join(missing)}"))

    return tuple(findings)


def find_open_quality_findings(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """AUD-019: 품질점검/검토 지적사항의 미조치 상태를 찾는다."""
    id_headers = {"지적id", "지적번호", "점검id", "검토id", "번호"}
    content_headers = {"지적사항", "지적내용", "점검내용", "검토의견", "의견", "내용"}
    status_headers = {"상태", "조치상태", "처리상태", "완료여부"}

    headers_by_sheet: dict[str, dict[str, int]] = {}
    findings: list[P1StructuredFinding] = []

    for block in document.blocks:
        cells = _structured_cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        norm = [_compact(v) for v in cells]
        identifier = _find_index(norm, id_headers)
        content = _find_index(norm, content_headers)
        status = _find_index(norm, status_headers)
        if status is not None and (identifier is not None or content is not None):
            h = {"status": status}
            if identifier is not None:
                h["identifier"] = identifier
            if content is not None:
                h["content"] = content
            headers_by_sheet[sheet] = h
            continue

        h = headers_by_sheet.get(sheet)
        if not h or _is_summary_row(cells):
            continue
        label = _cell(cells, h.get("identifier")) or _cell(cells, h.get("content"))[:80]
        if not label:
            continue
        status_raw = _cell(cells, h.get("status"))
        status_value = _compact(status_raw)
        if not status_value or status_value in _CLOSED_EXCLUDED:
            continue
        if status_value in _OPEN:
            findings.append(_finding(block, f"미조치 품질지적사항: {label} / 상태={status_raw}"))

    return tuple(findings)


def _is_requirement_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(term in name for term in ("요구사항", "requirement", "requirements", "srs"))


def _is_test_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(term in name for term in ("시험", "테스트", "test", "시나리오", "결과"))


_REQ_ID_RE = re.compile(r"\b(?:REQ-\d+|(?:UI-)?[A-Z]{2,}-\d+-ID-\d+(?:-\d+)*)\b", re.IGNORECASE)
_IMPORTANT = {"중요", "필수", "high", "must", "critical", "핵심", "상"}
_NON_TEST = {"해당없음", "비대상", "시험제외", "테스트제외", "na", "n/a"}


def _collect_requirement_ids(documents: list[ParsedDocument]) -> set[str]:
    ids: set[str] = set()
    for document in documents:
        if not _is_requirement_document(document):
            continue
        for block in document.blocks:
            for value in _REQ_ID_RE.findall(block.text or ""):
                ids.add(value.upper())
    return ids


def find_important_requirement_test_gaps(documents: list[ParsedDocument]) -> tuple[P1StructuredFinding, ...]:
    """REQ-016: 중요 요구사항 중 시험근거가 없는 항목을 찾는다."""
    requirement_docs = [d for d in documents if _is_requirement_document(d)]
    test_docs = [d for d in documents if _is_test_document(d)]
    if not requirement_docs or not test_docs:
        return ()

    test_ids: set[str] = set()
    for document in test_docs:
        for block in document.blocks:
            for value in _REQ_ID_RE.findall(block.text or ""):
                test_ids.add(value.upper())

    findings: list[P1StructuredFinding] = []
    priority_headers = {"중요도", "우선순위", "priority", "등급"}
    id_headers = {"요구사항id", "요구id", "requirementid", "id"}
    test_target_headers = {"시험대상", "테스트대상", "검증대상", "시험여부"}

    for document in requirement_docs:
        headers_by_sheet: dict[str, dict[str, int]] = {}
        for block in document.blocks:
            cells = _structured_cells(block)
            if not cells:
                continue
            sheet = block.sheet or ""
            norm = [_compact(v) for v in cells]
            id_idx = _find_index(norm, id_headers)
            priority_idx = _find_index(norm, priority_headers)
            target_idx = _find_index(norm, test_target_headers)
            if id_idx is not None and priority_idx is not None:
                h = {"id": id_idx, "priority": priority_idx}
                if target_idx is not None:
                    h["target"] = target_idx
                headers_by_sheet[sheet] = h
                continue
            h = headers_by_sheet.get(sheet)
            if not h or _is_summary_row(cells):
                continue
            req_id = _cell(cells, h.get("id")).upper()
            if not _REQ_ID_RE.fullmatch(req_id):
                continue
            priority = _compact(_cell(cells, h.get("priority")))
            if priority not in _IMPORTANT:
                continue
            if "target" in h and _compact(_cell(cells, h.get("target"))) in _NON_TEST:
                continue
            if req_id not in test_ids:
                findings.append(_finding(block, f"중요 요구사항 시험범위 누락: {req_id}"))

    return tuple(findings)


def find_invalid_requirement_references(documents: list[ParsedDocument]) -> tuple[P1StructuredFinding, ...]:
    """REQ-020: 존재하지 않는 요구사항 ID 참조를 찾는다."""
    baseline = _collect_requirement_ids(documents)
    if not baseline:
        return ()

    findings: list[P1StructuredFinding] = []
    seen: set[tuple[str, str | None, str]] = set()
    for document in documents:
        if _is_requirement_document(document):
            continue
        for block in document.blocks:
            text = block.text or ""
            if not text.strip():
                continue
            for value in _REQ_ID_RE.findall(text):
                req_id = value.upper()
                if req_id in baseline:
                    continue
                key = (str(document.file_path), block.location, req_id)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(_finding(block, f"존재하지 않는 요구사항 참조: {req_id}"))
    return tuple(findings)


def find_unapproved_applied_changes(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """CHG-005: 미승인/대기 변경이 이미 반영완료된 구조적 불일치를 찾는다."""
    id_headers = {"변경id", "변경번호", "요청id", "요청번호", "번호"}
    approval_headers = {"승인상태", "승인여부", "결재상태", "승인"}
    apply_headers = {"반영상태", "적용상태", "처리상태", "반영여부", "적용여부"}
    unapproved = {"미승인", "승인대기", "대기", "검토중", "pending", "미결재", "반려"}
    applied = {"반영완료", "적용완료", "완료", "반영", "적용", "처리완료", "done", "applied"}

    headers_by_sheet: dict[str, dict[str, int]] = {}
    findings: list[P1StructuredFinding] = []
    for block in document.blocks:
        cells = _structured_cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        norm = [_compact(v) for v in cells]
        identifier = _find_index(norm, id_headers)
        approval = _find_index(norm, approval_headers)
        apply = _find_index(norm, apply_headers)
        if identifier is not None and approval is not None and apply is not None:
            headers_by_sheet[sheet] = {"id": identifier, "approval": approval, "apply": apply}
            continue
        h = headers_by_sheet.get(sheet)
        if not h or _is_summary_row(cells):
            continue
        change_id = _cell(cells, h.get("id"))
        if not change_id:
            continue
        approval_raw = _cell(cells, h.get("approval"))
        apply_raw = _cell(cells, h.get("apply"))
        if _compact(approval_raw) in unapproved and _compact(apply_raw) in applied:
            findings.append(_finding(block, f"미승인 변경 반영 후보: {change_id} / 승인={approval_raw} / 반영={apply_raw}"))
    return tuple(findings)


def find_fp_method_basis_gaps(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """FP-007: 명시된 산정방식/적용기준 필드가 공란인 경우를 찾는다."""
    if document.file_type not in {"xlsx", "xls"}:
        return ()
    label_aliases = {"산정방식", "fp산정방식", "적용방식", "적용기준", "산정기준", "fp기준"}
    findings: list[P1StructuredFinding] = []
    for block in document.blocks:
        cells = _structured_cells(block)
        if len(cells) < 2:
            continue
        label = _compact(cells[0])
        if label not in label_aliases:
            continue
        value = next((cell.strip() for cell in cells[1:] if cell.strip()), "")
        if not value:
            findings.append(_finding(block, f"FP 산정방식/적용기준 공란: {cells[0]}"))
    return tuple(findings)


def _looks_like_ai_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    if any(term in name for term in ("ai", "인공지능", "llm", "rag", "생성형")):
        return True
    joined = " ".join((block.text or "")[:300] for block in document.blocks[:20]).lower()
    return any(term in joined for term in ("인공지능", "생성형 ai", "llm", "rag", "prompt", "모델"))


def find_ai_resource_limit_gaps(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """AI-023: AI 자원통제 구조에서 명시적 제한값 공란을 찾는다."""
    if not _looks_like_ai_document(document):
        return ()
    labels = {
        "timeout", "타임아웃", "재시도", "retry", "최대토큰", "maxtokens", "토큰제한",
        "호출제한", "요청제한", "동시호출", "rate limit", "ratelimit", "입력크기", "출력크기",
    }
    findings: list[P1StructuredFinding] = []
    for block in document.blocks:
        cells = _structured_cells(block)
        if len(cells) < 2:
            continue
        label = _compact(cells[0])
        if not any(_compact(term) == label for term in labels):
            continue
        value = next((cell.strip() for cell in cells[1:] if cell.strip()), "")
        if not value:
            findings.append(_finding(block, f"AI 자원사용 제한값 공란: {cells[0]}"))
    return tuple(findings)
