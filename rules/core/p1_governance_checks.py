"""P1-D AUD-020/AUD-022/AUD-023 보수적 구조·교차문서 사전분석."""

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
            column_index = header[key]
            if column_index is None:
                # 송신/수신으로 인터페이스 표가 확인된 경우에만,
                # 핵심 정의열 자체가 없는 구조를 누락 후보로 본다.
                if key in {"method", "data"}:
                    missing.append(f"{label} 열 미정의")
                continue
            if not cell(column_index):
                missing.append(label)

        if missing:
            result.append(
                f"{block.location or sheet or '-'}: 인터페이스 핵심정보 누락 후보({', '.join(missing)}) | "
                f"송신={sender or '-'} | 수신={receiver or '-'}"
            )

    return tuple(result)


def _is_obligation_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(term in name for term in ("rfp", "계약", "과업", "제안요청", "사업수행", "요구사항"))


def _obligation_candidates(document: ParsedDocument):
    obligation_markers = (
        "하여야 한다", "해야 한다", "제출하여야", "제출해야",
        "납품", "수행하여야", "준수하여야",
    )
    not_due_markers = ("추후", "향후", "예정", "착수 후", "운영 전", "시기미도래")

    for block in document.blocks:
        text = (block.text or "").strip()
        if not text:
            continue
        lowered = text.lower()
        if not any(marker in lowered for marker in obligation_markers):
            continue
        if any(marker in lowered for marker in not_due_markers):
            continue
        yield block, text


def _keywords(text: str) -> tuple[str, ...]:
    stop = {
        "사업자는", "사업자", "하여야", "한다", "해야", "제출하여야", "제출해야",
        "수행하여야", "준수하여야", "관하여", "대한", "위한", "관련", "해당",
        "적용하여야", "적용해야", "적용", "준수", "기준", "지침", "표준",
    }
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", text.lower())
    result = []
    for token in tokens:
        normalized = token.strip()
        if len(normalized) < 3 or normalized in stop:
            continue
        if normalized not in result:
            result.append(normalized)
    return tuple(result[:12])


def _has_related_evidence(
    candidate_text: str,
    documents: list[ParsedDocument],
    evidence_markers: tuple[str, ...],
) -> bool:
    keywords = _keywords(candidate_text)
    if not keywords:
        return False

    for document in documents:
        for block in document.blocks:
            text = (block.text or "").strip().lower()
            if not text:
                continue
            if not any(marker in text for marker in evidence_markers):
                continue
            if any(keyword in text for keyword in keywords):
                return True
    return False


def build_aud022_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """단일 계약/RFP/과업 문서에서 명시적 의무 후보만 추출한다.

    실제 제품 실행은 build_aud022_cross_document_evidence()에서 업로드 문서 전체와
    교차검증한 뒤 후보를 만든다.
    """
    if not _is_obligation_document(document):
        return ()

    result = []
    for block, text in _obligation_candidates(document):
        result.append(
            f"{block.location or block.block_type}: 계약/과업 의무사항 반영·이행 근거 확인 필요 | {text[:300]}"
        )
    return tuple(result)


def build_aud022_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """계약/과업 의무와 다른 업로드 산출물의 이행근거를 교차검증한다."""
    source_documents = [document for document in documents if _is_obligation_document(document)]
    support_documents = [document for document in documents if not _is_obligation_document(document)]

    # 계약/과업 문서만 단독 업로드된 경우에는 증적 미업로드 가능성이 있으므로
    # 의무 미이행으로 후보화하지 않는다.
    if not source_documents or not support_documents:
        return ()

    evidence_markers = (
        "완료", "제출", "반영", "수행", "이행", "납품", "적용",
        "검토결과", "시험결과", "점검결과", "완료하였다", "완료함",
    )
    result = []
    for document in source_documents:
        for block, text in _obligation_candidates(document):
            if _has_related_evidence(text, support_documents, evidence_markers):
                continue
            result.append(
                f"{document.file_path.name} / {block.location or block.block_type}: "
                f"명시적 계약·과업 의무의 이행근거 교차확인 필요 | {text[:300]}"
            )
    return tuple(result)


def _standard_candidates(document: ParsedDocument):
    standard_markers = (
        "법령", "지침", "가이드", "표준", "기준", "웹접근성", "웹표준", "kisa", "전자정부"
    )
    application_markers = ("적용", "준수", "따른다", "대상", "준거")
    evidence_markers = ("점검", "검증", "진단", "확인", "적합", "통과", "준수결과", "검사결과")
    excluded = ("비적용", "해당없음", "n/a", "참고")

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
        yield block, text


def build_aud023_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """단일 문서에서 적용기준이 명시된 구조 후보만 추출한다.

    실제 제품 실행은 build_aud023_cross_document_evidence()에서 업로드 문서 전체의
    준수/검증근거와 교차검증한다.
    """
    return tuple(
        f"{block.location or block.block_type}: 적용 기준·지침의 준수근거 확인 필요 | {text[:300]}"
        for block, text in _standard_candidates(document)
    )


def build_aud023_cross_document_evidence(
    documents: list[ParsedDocument],
) -> tuple[str, ...]:
    """명시적으로 적용된 기준과 업로드 문서 전체의 준수·검증근거를 비교한다."""
    evidence_markers = (
        "점검", "검증", "진단", "확인", "적합", "통과", "준수결과", "검사결과", "조치완료"
    )
    result = []

    for document in documents:
        for block, text in _standard_candidates(document):
            if _has_related_evidence(text, documents, evidence_markers):
                continue
            result.append(
                f"{document.file_path.name} / {block.location or block.block_type}: "
                f"적용 기준·지침의 준수·검증근거 교차확인 필요 | {text[:300]}"
            )

    return tuple(result)
