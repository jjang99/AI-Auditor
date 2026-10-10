"""AUD-008 계획 대비 산출물 작성상태 점검.

AUD-001과 역할을 분리한다.
- AUD-001: 실제 제출 파일의 존재/누락
- AUD-008: 계획표상 현재 대상 산출물의 작성·제출 상태 관리

오탐 방지:
- 미적용/제외/해당없음/시기미도래는 검사 제외
- 기준 문서가 없으면 임의 상태를 추정하지 않음
- 상태가 완료인데 파일이 없는 경우는 AUD-001 영역이므로 AUD-008에서 중복 지적하지 않음
"""

from dataclasses import dataclass

from app.parsers.models import ParsedDocument
from rules.core.deliverable_baseline import (
    _cell,
    _header_indexes,
    _is_not_applicable,
    _is_not_due,
    _is_positive_application,
    _source_kind,
)


@dataclass(frozen=True)
class DeliverableStatusFinding:
    evidence: str
    file_path: str
    block_type: str
    location: str | None = None
    page: int | None = None
    sheet: str | None = None
    slide: int | None = None


_INCOMPLETE_STATUS_MARKERS = (
    "미작성",
    "작성중",
    "작성 중",
    "미제출",
    "제출전",
    "제출 전",
    "미완료",
    "진행중",
    "진행 중",
    "보완중",
    "보완 중",
)


def _is_explicitly_incomplete(status: str) -> bool:
    normalized = str(status).strip().lower()
    return any(marker in normalized for marker in _INCOMPLETE_STATUS_MARKERS)


def find_deliverable_status_gaps(
    documents: list[ParsedDocument],
) -> tuple[DeliverableStatusFinding, ...]:
    """업로드된 산출물목록/테일러링 표에서 현재 대상의 상태 미작성·미완료를 찾는다."""
    findings: list[DeliverableStatusFinding] = []

    for document in documents:
        source_kind = _source_kind(document)
        if source_kind not in {"deliverable_list", "tailoring"}:
            continue

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
            status_index = indexes.get("status")
            status = _cell(cells, status_index)
            row_text = " ".join(value for value in cells if value)

            # 미적용·제외·해당없음은 현재 점검대상에서 제외한다.
            if application and _is_not_applicable(application):
                continue
            if any(marker in row_text.replace(" ", "") for marker in ("미적용", "적용제외")):
                continue

            # 시기미도래·점검제외·해당없음은 현재 미완료로 보지 않는다.
            if status and _is_not_due(status):
                continue
            compact_row = row_text.replace(" ", "")
            if any(marker in compact_row for marker in ("시기미도래", "점검제외", "해당없음")):
                continue

            # 테일러링 단독 기준은 명시적으로 적용 대상인 행만 사용한다.
            if source_kind == "tailoring":
                if application:
                    if not _is_positive_application(application):
                        continue
                elif status:
                    if not _is_positive_application(status) and not _is_explicitly_incomplete(status):
                        continue
                else:
                    continue

            # 상태 열 자체가 없는 기준표는 작성상태를 추정하지 않는다.
            if status_index is None:
                continue

            if not status:
                evidence = f"계획 대비 산출물 작성상태 미작성: {deliverable} / 상태 공란"
            elif _is_explicitly_incomplete(status):
                evidence = (
                    f"계획 대비 산출물 작성상태 미완료: {deliverable} / 상태={status}"
                )
            else:
                continue

            findings.append(
                DeliverableStatusFinding(
                    evidence=evidence,
                    file_path=str(document.file_path),
                    block_type=block.block_type,
                    location=block.location or block.sheet,
                    page=block.page,
                    sheet=block.sheet,
                    slide=block.slide,
                )
            )

    return tuple(findings)
