"""P1-D AUD-020/AUD-022/AUD-023 보수적 구조 사전분석."""

from __future__ import annotations

import re
from app.parsers.models import ParsedDocument


def _compact(value: str) -> str:
    return re.sub(r"[\s_./\\-]+", "", str(value).strip().lower())


def _cells(block) -> tuple[str, ...]:
    values = tuple(block.metadata.get("cell_values", ()))
    return tuple(str(value).strip() for value in values)


def build_aud020_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """구조형 인터페이스 표에서 명확한 필수정보 누락 후보만 추출한다."""
    id_headers = {"인터페이스id", "연계id", "ifid", "interfaceid", "id"}
    sender_headers = {"송신시스템", "송신", "source", "출발시스템", "제공시스템"}
    receiver_headers = {"수신시스템", "수신", "target", "대상시스템", "사용시스템"}
    method_headers = {"연계방식", "방식", "protocol", "프로토콜", "인터페이스방식"}
    data_headers = {"데이터", "전송데이터", "항목", "메시지", "전문", "데이터항목"}
    cycle_headers = {"주기", "전송주기", "처리주기", "호출주기"}

    result: list[str] = []
    headers_by_sheet: dict[str, dict[str, int | None]] = {}

    for block in document.blocks:
        cells = _cells(block)
        if not cells:
            continue
        sheet = block.sheet or ""
        normalized = [_compact(value) for value in cells]

        def idx(headers):
            normalized_headers = {_compact(item) for item in headers}
            return next((i for i, value in enumerate(normalized) if value in normalized_headers), None)

        mapping = {
            "id": idx(id_headers),
            "sender": idx(sender_headers),
            "receiver": idx(receiver_headers),
            "method": idx(method_headers),
            "data": idx(data_headers),
            "cycle": idx(cycle_headers),
        }
        if mapping["sender"] is not None and mapping["receiver"] is not None:
            headers_by_sheet[sheet] = mapping
            continue

        header = headers_by_sheet.get(sheet)
        if not header:
            continue

        def cell(index: int | None) -> str:
            return cells[index].strip() if index is not None and index < len(cells) else ""

        sender = cell(header["sender"])
        receiver = cell(header["receiver"])
        if not sender and not receiver:
            continue

        missing = []
        for key, label in (
            ("sender", "송신시스템"),
            ("receiver", "수신시스템"),
            ("method", "연계방식"),
            ("data", "데이터"),
        ):
            if header[key] is not None and not cell(header[key]):
                missing.append(label)

        if missing:
            result.append(
                f"{block.location or sheet or '-'}: 인터페이스 핵심정보 누락 후보({', '.join(missing)}) | "
                f"송신={sender or '-'} | 수신={receiver or '-'}"
            )

    return tuple(result)


def _document_text(document: ParsedDocument) -> str:
    return "\n".join(
        block.text.strip()
        for block in document.blocks
        if block.text and block.text.strip()
    )


def build_aud022_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """계약/RFP/과업 문서의 명시적 의무표현 중 근거확인 필요 후보를 추출한다."""
    name = document.file_path.stem.lower()
    if not any(term in name for term in ("rfp", "계약", "과업", "제안요청", "사업수행", "요구사항")):
        return ()

    obligation_markers = ("하여야 한다", "해야 한다", "제출하여야", "제출해야", "납품", "수행하여야", "준수하여야")
    not_due_markers = ("추후", "향후", "예정", "착수 후", "운영 전", "시기미도래")
    evidence_markers = ("완료", "제출", "반영", "수행", "적용", "검토완료", "납품완료")

    result: list[str] = []
    for block in document.blocks:
        text = (block.text or "").strip()
        if not text:
            continue
        lowered = text.lower()
        if not any(marker in lowered for marker in obligation_markers):
            continue
        if any(marker in lowered for marker in not_due_markers):
            continue
        if any(marker in lowered for marker in evidence_markers) and any(token in lowered for token in ("완료", "제출완료", "반영완료", "수행완료")):
            continue
        result.append(
            f"{block.location or block.block_type}: 계약/과업 의무사항 반영·이행 근거 확인 필요 | {text[:300]}"
        )

    return tuple(result)


def build_aud023_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """적용기준이 명시됐으나 준수/검증근거가 함께 드러나지 않는 후보를 추출한다."""
    standard_markers = ("법령", "지침", "가이드", "표준", "기준", "웹접근성", "웹표준", "kisa", "전자정부")
    application_markers = ("적용", "준수", "따른다", "대상", "준거")
    evidence_markers = ("점검", "검증", "진단", "확인", "적합", "통과", "준수결과", "검사결과")
    excluded = ("비적용", "해당없음", "n/a", "참고")

    result: list[str] = []
    for block in document.blocks:
        text = (block.text or "").strip()
        if not text:
            continue
        lowered = text.lower()
        if any(marker in lowered for marker in excluded):
            continue
        if not any(marker in lowered for marker in standard_markers):
            continue
        if not any(marker in lowered for marker in application_markers):
            continue
        if any(marker in lowered for marker in evidence_markers):
            continue
        result.append(
            f"{block.location or block.block_type}: 적용 기준·지침의 준수근거 확인 필요 | {text[:300]}"
        )

    return tuple(result)
