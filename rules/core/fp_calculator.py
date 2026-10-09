import re
from dataclasses import dataclass

from app.parsers.models import ParsedDocument


@dataclass(frozen=True)
class FPCalculationMismatch:
    sheet: str | None
    location: str | None
    function_type: str
    complexity: str
    count: float
    reported_fp: float
    calculated_fp: float
    basis: str


_WEIGHTS = {
    "ILF": {"LOW": 7.0, "AVERAGE": 10.0, "HIGH": 15.0},
    "EIF": {"LOW": 5.0, "AVERAGE": 7.0, "HIGH": 10.0},
    "EI": {"LOW": 3.0, "AVERAGE": 4.0, "HIGH": 6.0},
    "EO": {"LOW": 4.0, "AVERAGE": 5.0, "HIGH": 7.0},
    "EQ": {"LOW": 3.0, "AVERAGE": 4.0, "HIGH": 6.0},
}

_TYPE_ALIASES = {
    "내부논리파일": "ILF",
    "외부연계파일": "EIF",
    "외부인터페이스파일": "EIF",
    "외부입력": "EI",
    "외부출력": "EO",
    "외부조회": "EQ",
}

_COMPLEXITY_ALIASES = {
    "low": "LOW",
    "낮음": "LOW",
    "하": "LOW",
    "average": "AVERAGE",
    "avg": "AVERAGE",
    "보통": "AVERAGE",
    "중": "AVERAGE",
    "high": "HIGH",
    "높음": "HIGH",
    "상": "HIGH",
}

_TYPE_HEADERS = {"fp유형", "기능유형", "유형", "functiontype"}
_COMPLEXITY_HEADERS = {"복잡도", "complexity", "평균복잡도"}
_RET_FTR_HEADERS = {"ret/ftr", "retftr", "ret", "ftr", "⑤ret/ftr"}
_DET_HEADERS = {"det", "⑥det", "데이터요소유형", "데이터요소수"}
_COUNT_HEADERS = {"기능개수", "기능수", "개수", "건수", "count"}
_FP_HEADERS = {"기능점수", "fp", "fp점수", "산정fp", "기능점수(fp)"}


def _compact(value: str) -> str:
    return re.sub(r"\s+", "", str(value).strip().lower())


def _number(value: str) -> float | None:
    text = str(value).strip().replace(",", "")
    if not text or text in {"-", "—", "–"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _function_type(value: str) -> str | None:
    raw = str(value).strip().upper()
    for code in _WEIGHTS:
        if re.search(rf"\b{code}\b", raw):
            return code
    compact = _compact(value)
    for alias, code in _TYPE_ALIASES.items():
        if alias in compact:
            return code
    return None


def _complexity(value: str) -> str | None:
    compact = _compact(value)
    if compact in _COMPLEXITY_ALIASES:
        return _COMPLEXITY_ALIASES[compact]
    upper = str(value).strip().upper()
    if upper in {"LOW", "AVERAGE", "HIGH"}:
        return upper
    return None


def _data_complexity(ret: float, det: float) -> str:
    if det <= 19:
        if ret <= 5:
            return "LOW"
        return "AVERAGE"
    if det <= 50:
        if ret <= 1:
            return "LOW"
        if ret <= 5:
            return "AVERAGE"
        return "HIGH"
    if ret <= 1:
        return "AVERAGE"
    return "HIGH"


def _transaction_complexity(function_type: str, ftr: float, det: float) -> str:
    if function_type == "EI":
        if det <= 4:
            if ftr <= 1:
                return "LOW"
            if ftr == 2:
                return "LOW"
            return "AVERAGE"
        if det <= 15:
            if ftr <= 1:
                return "LOW"
            if ftr == 2:
                return "AVERAGE"
            return "HIGH"
        if ftr <= 1:
            return "AVERAGE"
        return "HIGH"

    # EO / EQ
    upper_mid_ftr = 3 if function_type == "EO" else 2
    if det <= 5:
        if ftr <= upper_mid_ftr:
            return "LOW"
        return "AVERAGE"
    if det <= 19:
        if ftr <= 1:
            return "LOW"
        if ftr <= upper_mid_ftr:
            return "AVERAGE"
        return "HIGH"
    if ftr <= 1:
        return "AVERAGE"
    return "HIGH"


def complexity_from_counts(
    function_type: str,
    ret_ftr: float,
    det: float,
) -> str | None:
    if function_type in {"ILF", "EIF"}:
        return _data_complexity(ret_ftr, det)
    if function_type in {"EI", "EO", "EQ"}:
        return _transaction_complexity(function_type, ret_ftr, det)
    return None


def _header_indexes(cells: tuple[str, ...]) -> dict[str, int] | None:
    normalized = [_compact(value) for value in cells]

    def find(headers):
        return next((i for i, value in enumerate(normalized) if value in headers), None)

    type_index = find(_TYPE_HEADERS)
    fp_index = find(_FP_HEADERS)
    if type_index is None or fp_index is None:
        return None

    indexes = {"type": type_index, "fp": fp_index}
    complexity_index = find(_COMPLEXITY_HEADERS)
    ret_ftr_index = find(_RET_FTR_HEADERS)
    det_index = find(_DET_HEADERS)
    count_index = find(_COUNT_HEADERS)

    if complexity_index is not None:
        indexes["complexity"] = complexity_index
    if ret_ftr_index is not None:
        indexes["ret_ftr"] = ret_ftr_index
    if det_index is not None:
        indexes["det"] = det_index
    if count_index is not None:
        indexes["count"] = count_index
    return indexes


def _cell(cells: tuple[str, ...], index: int | None) -> str:
    if index is None or index >= len(cells):
        return ""
    return str(cells[index]).strip()


def find_fp_mismatches(document: ParsedDocument) -> tuple[FPCalculationMismatch, ...]:
    """XLS/XLSX Parser의 행 구조를 이용해 재계산 가능한 FP 행만 검증한다.

    보수적 원칙:
    - 기능유형과 보고 FP 값이 모두 있어야 한다.
    - 복잡도가 명시되어 있으면 해당 복잡도를 사용한다.
    - 복잡도가 없으면 RET/FTR + DET가 모두 있을 때만 표준 복잡도 행렬로 계산한다.
    - 건수 열이 없으면 행 단위 기능 1건으로 본다.
    - 계산 근거가 불충분한 행은 추정하지 않는다.
    """
    if document.file_type not in {"xlsx", "xls"}:
        return ()

    headers_by_sheet: dict[str, dict[str, int]] = {}
    mismatches: list[FPCalculationMismatch] = []

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

        function_type = _function_type(_cell(cells, indexes.get("type")))
        reported_fp = _number(_cell(cells, indexes.get("fp")))
        if function_type is None or reported_fp is None:
            continue

        count = _number(_cell(cells, indexes.get("count")))
        if count is None:
            count = 1.0
        if count <= 0:
            continue

        complexity = _complexity(_cell(cells, indexes.get("complexity")))
        basis = "명시 복잡도"

        if complexity is None:
            ret_ftr = _number(_cell(cells, indexes.get("ret_ftr")))
            det = _number(_cell(cells, indexes.get("det")))
            if ret_ftr is None or det is None or ret_ftr < 0 or det < 0:
                continue
            complexity = complexity_from_counts(function_type, ret_ftr, det)
            if complexity is None:
                continue
            basis = f"RET/FTR={ret_ftr:g}, DET={det:g}"

        calculated_fp = count * _WEIGHTS[function_type][complexity]
        if abs(calculated_fp - reported_fp) < 0.000001:
            continue

        mismatches.append(
            FPCalculationMismatch(
                sheet=block.sheet,
                location=block.location,
                function_type=function_type,
                complexity=complexity,
                count=count,
                reported_fp=reported_fp,
                calculated_fp=calculated_fp,
                basis=basis,
            )
        )

    return tuple(mismatches)
