"""P1 결정형 Rule에서 재사용하는 보수적 구조검사.

원칙:
- 빈 셀 위치가 보존되는 XLS/XLSX `cell_values`를 우선 사용한다.
- 구조를 확정할 수 없는 문서는 임의 추정하지 않는다.
- 합계/요약/템플릿 행을 실제 업무행으로 단정하지 않는다.
"""

from dataclasses import dataclass

from app.parsers.models import ParsedDocument
from rules.core.fp_calculator import (
    _cell as _fp_cell,
    _complexity as _fp_complexity,
    _function_type as _fp_function_type,
    _header_indexes as _fp_header_indexes,
    _number as _fp_number,
)


@dataclass(frozen=True)
class P1StructuredFinding:
    evidence: str
    block_type: str
    location: str | None = None
    page: int | None = None
    sheet: str | None = None
    slide: int | None = None


def _compact(value: str) -> str:
    return "".join(str(value).strip().lower().split()).replace("_", "")


def _structured_cells(block) -> tuple[str, ...]:
    raw = tuple(block.metadata.get("cell_values", ()))
    if not raw:
        return ()
    return tuple(str(value).strip() for value in raw)


def _cell(cells: tuple[str, ...], index: int | None) -> str:
    if index is None or index < 0 or index >= len(cells):
        return ""
    return cells[index].strip()


def _find_index(normalized: list[str], aliases: set[str]) -> int | None:
    return next(
        (index for index, value in enumerate(normalized) if value in aliases),
        None,
    )


def _is_summary_row(cells: tuple[str, ...]) -> bool:
    joined = _compact(" ".join(cells))
    return any(marker in joined for marker in ("합계", "소계", "총계", "subtotal", "total"))


_TEST_ITEM_HEADERS = {
    "시험항목", "테스트항목", "시험id", "테스트id", "시나리오id",
    "케이스id", "시험케이스", "테스트케이스", "시험명", "테스트명",
}
_TEST_METHOD_HEADERS = {
    "시험방법", "테스트방법", "수행방법", "검증방법", "시험절차", "테스트절차",
    "수행절차", "시험조건", "테스트조건", "조건", "입력", "입력값",
}
_EXPECTED_HEADERS = {
    "예상결과", "기대결과", "예상값", "기대값", "expectedresult", "expected",
}


def _test_plan_header(cells: tuple[str, ...]) -> dict[str, int] | None:
    normalized = [_compact(value) for value in cells]
    item = _find_index(normalized, _TEST_ITEM_HEADERS)
    method = _find_index(normalized, _TEST_METHOD_HEADERS)
    expected = _find_index(normalized, _EXPECTED_HEADERS)

    # 시험표라고 확정할 수 있을 때만 검사한다.
    present = sum(index is not None for index in (item, method, expected))
    if item is None or present < 2:
        return None

    result = {"item": item}
    if method is not None:
        result["method"] = method
    if expected is not None:
        result["expected"] = expected
    return result


def find_test_plan_gaps(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """AUD-014: 시험계획 표의 필수 헤더/값 누락을 찾는다."""
    findings: list[P1StructuredFinding] = []
    headers_by_sheet: dict[str, dict[str, int]] = {}

    for block in document.blocks:
        cells = _structured_cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""

        header = _test_plan_header(cells)
        if header is not None:
            headers_by_sheet[sheet] = header
            missing_headers = []
            if "method" not in header:
                missing_headers.append("시험방법/조건")
            if "expected" not in header:
                missing_headers.append("예상결과")
            if missing_headers:
                findings.append(
                    P1StructuredFinding(
                        evidence=(
                            "시험계획 필수 헤더 누락: "
                            + ", ".join(missing_headers)
                        ),
                        block_type=block.block_type,
                        location=block.location,
                        page=block.page,
                        sheet=block.sheet,
                        slide=block.slide,
                    )
                )
            continue

        indexes = headers_by_sheet.get(sheet)
        if not indexes or _is_summary_row(cells):
            continue

        item = _cell(cells, indexes.get("item"))
        # 실제 시험항목을 식별할 값이 없으면 빈 템플릿/구분행으로 보고 제외한다.
        if not item:
            continue

        missing = []
        if "method" in indexes and not _cell(cells, indexes.get("method")):
            missing.append("시험방법/조건")
        if "expected" in indexes and not _cell(cells, indexes.get("expected")):
            missing.append("예상결과")
        if not missing:
            continue

        findings.append(
            P1StructuredFinding(
                evidence=(
                    f"시험항목 '{item}' 필수정보 누락: "
                    + ", ".join(missing)
                ),
                block_type=block.block_type,
                location=block.location,
                page=block.page,
                sheet=block.sheet,
                slide=block.slide,
            )
        )

    return tuple(findings)


_DEFECT_ID_HEADERS = {
    "결함id", "오류id", "이슈id", "결함번호", "오류번호", "이슈번호", "번호",
}
_DEFECT_CONTENT_HEADERS = {
    "결함내용", "오류내용", "이슈내용", "현상", "내용", "제목",
}
_DEFECT_STATUS_HEADERS = {
    "상태", "조치상태", "처리상태", "완료여부", "종결여부",
}
_DEFECT_ACTION_HEADERS = {
    "조치결과", "처리결과", "조치내용", "처리내용", "해결내용",
}
_OPEN_STATUSES = {
    "미조치", "미처리", "진행중", "처리중", "조치중", "재검증필요",
    "재시험필요", "재검증", "재시험", "open", "inprogress", "pending",
}
_CLOSED_STATUSES = {
    "완료", "조치완료", "처리완료", "종결", "해결", "closed", "resolved",
}
_EXCLUDED_CLOSED_STATUSES = {
    "취소", "해당없음", "중복", "제외", "cancelled", "duplicate", "na", "n/a",
}


def _defect_header(cells: tuple[str, ...]) -> dict[str, int] | None:
    normalized = [_compact(value) for value in cells]
    identifier = _find_index(normalized, _DEFECT_ID_HEADERS)
    content = _find_index(normalized, _DEFECT_CONTENT_HEADERS)
    status = _find_index(normalized, _DEFECT_STATUS_HEADERS)
    action = _find_index(normalized, _DEFECT_ACTION_HEADERS)

    if status is None or (identifier is None and content is None):
        return None

    result = {"status": status}
    if identifier is not None:
        result["identifier"] = identifier
    if content is not None:
        result["content"] = content
    if action is not None:
        result["action"] = action
    return result


def find_open_test_defects(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """AUD-016: 결함표에서 미조치/미종결 또는 완료-조치결과 불일치를 찾는다."""
    findings: list[P1StructuredFinding] = []
    headers_by_sheet: dict[str, dict[str, int]] = {}

    for block in document.blocks:
        cells = _structured_cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""

        header = _defect_header(cells)
        if header is not None:
            headers_by_sheet[sheet] = header
            continue

        indexes = headers_by_sheet.get(sheet)
        if not indexes or _is_summary_row(cells):
            continue

        identifier = _cell(cells, indexes.get("identifier"))
        content = _cell(cells, indexes.get("content"))
        if not identifier and not content:
            continue

        status_raw = _cell(cells, indexes.get("status"))
        status = _compact(status_raw)
        if not status:
            continue

        label = identifier or content[:60]
        if status in _EXCLUDED_CLOSED_STATUSES:
            continue

        if status in _OPEN_STATUSES:
            findings.append(
                P1StructuredFinding(
                    evidence=f"미종결 시험결함: {label} / 상태={status_raw}",
                    block_type=block.block_type,
                    location=block.location,
                    page=block.page,
                    sheet=block.sheet,
                    slide=block.slide,
                )
            )
            continue

        if status in _CLOSED_STATUSES and "action" in indexes:
            action = _cell(cells, indexes.get("action"))
            if not action:
                findings.append(
                    P1StructuredFinding(
                        evidence=(
                            f"시험결함 완료상태-조치결과 불일치: {label} / "
                            f"상태={status_raw}, 조치결과 공란"
                        ),
                        block_type=block.block_type,
                        location=block.location,
                        page=block.page,
                        sheet=block.sheet,
                        slide=block.slide,
                    )
                )

    return tuple(findings)


def find_fp_detail_gaps(document: ParsedDocument) -> tuple[P1StructuredFinding, ...]:
    """FP-008: 기능유형/FP가 있는 실제 산정행의 상세 근거 부족을 찾는다."""
    if document.file_type not in {"xlsx", "xls"}:
        return ()

    findings: list[P1StructuredFinding] = []
    headers_by_sheet: dict[str, dict[str, int]] = {}

    for block in document.blocks:
        cells = _structured_cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""

        header = _fp_header_indexes(cells)
        if header is not None:
            headers_by_sheet[sheet] = header
            continue

        indexes = headers_by_sheet.get(sheet)
        if not indexes or _is_summary_row(cells):
            continue

        function_type = _fp_function_type(_fp_cell(cells, indexes.get("type")))
        reported_fp = _fp_number(_fp_cell(cells, indexes.get("fp")))
        if function_type is None or reported_fp is None:
            continue

        # 복잡도가 명시되어 있으면 상세 산정근거가 존재하는 것으로 인정한다.
        complexity = _fp_complexity(_fp_cell(cells, indexes.get("complexity")))
        if complexity is not None:
            continue

        ret_ftr = _fp_number(_fp_cell(cells, indexes.get("ret_ftr")))
        det = _fp_number(_fp_cell(cells, indexes.get("det")))
        missing = []
        if ret_ftr is None:
            missing.append("RET/FTR")
        if det is None:
            missing.append("DET")
        if not missing:
            continue

        findings.append(
            P1StructuredFinding(
                evidence=(
                    f"FP 상세 산정근거 누락: {function_type}, 보고값 {reported_fp:g} FP, "
                    f"복잡도 미기재 및 {', '.join(missing)} 누락"
                ),
                block_type=block.block_type,
                location=block.location,
                page=block.page,
                sheet=block.sheet,
                slide=block.slide,
            )
        )

    return tuple(findings)
