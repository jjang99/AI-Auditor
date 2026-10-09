import re
from dataclasses import dataclass

from app.parsers.models import ParsedDocument


_REQUIREMENT_ID_RE = re.compile(
    r"\b[A-Z]{2,5}-?\d+(?:-[A-Z0-9]+)*\b",
    re.IGNORECASE,
)

_REQUIREMENT_FILE_MARKERS = (
    "요구사항정의",
    "요구사항기술",
    "요구사항추적",
    "requirement",
    "requirements",
    "srs",
)

_DESIGN_FILE_MARKERS = (
    "설계",
    "화면",
    "인터페이스",
    "테이블",
    "데이터",
    "프로그램",
    "아키텍처",
    "유스케이스",
    "클래스",
    "시퀀스",
    "erd",
    "모형",
    "업무규칙",
)

_STOP_TERMS = {
    "요구사항",
    "요구",
    "시스템",
    "기능",
    "서비스",
    "관련",
    "대한",
    "위한",
    "제공",
    "처리",
    "화면",
    "설계",
    "정의",
    "사용자",
    "관리",
    "정보",
}


@dataclass(frozen=True)
class RequirementDesignCase:
    requirement_id: str
    requirement_source: str
    requirement_location: str | None
    requirement_text: str
    design_evidence: tuple[str, ...]


@dataclass(frozen=True)
class RequirementDesignBatch:
    evidence: tuple[str, ...]
    case_count: int
    source_file: str


def _normalized_name(document: ParsedDocument) -> str:
    return document.file_path.stem.replace(" ", "").lower()


def _is_requirement_source(document: ParsedDocument) -> bool:
    name = _normalized_name(document)
    return any(marker in name for marker in _REQUIREMENT_FILE_MARKERS)


def _is_design_source(document: ParsedDocument) -> bool:
    if _is_requirement_source(document):
        return False
    name = _normalized_name(document)
    return any(marker in name for marker in _DESIGN_FILE_MARKERS)


def _requirement_terms(text: str) -> tuple[str, ...]:
    terms: list[str] = []
    for token in re.findall(r"[가-힣A-Za-z0-9_]+", text):
        normalized = token.lower().strip("_")
        if (
            len(normalized) < 2
            or normalized in _STOP_TERMS
            or _REQUIREMENT_ID_RE.fullmatch(normalized)
        ):
            continue
        if normalized not in terms:
            terms.append(normalized)
    return tuple(terms[:14])


def _extract_requirement_cases(
    documents: list[ParsedDocument],
) -> list[tuple[str, ParsedDocument, object, str]]:
    cases: list[tuple[str, ParsedDocument, object, str]] = []
    seen: set[tuple[str, str]] = set()

    for document in documents:
        if not _is_requirement_source(document):
            continue

        for block in document.blocks:
            text = block.text.strip() if block.text else ""
            if not text:
                continue
            ids = tuple(dict.fromkeys(
                item.upper() for item in _REQUIREMENT_ID_RE.findall(text)
            ))
            if not ids:
                continue

            bounded_text = " ".join(text.split())[:1400]
            for requirement_id in ids:
                key = (requirement_id, bounded_text)
                if key in seen:
                    continue
                seen.add(key)
                cases.append((requirement_id, document, block, bounded_text))

    return cases


def _rank_design_blocks(
    requirement_id: str,
    requirement_text: str,
    design_documents: list[ParsedDocument],
) -> tuple[str, ...]:
    terms = _requirement_terms(requirement_text)
    ranked: list[tuple[int, int, str]] = []
    sequence = 0

    for document in design_documents:
        for block in document.blocks:
            text = block.text.strip() if block.text else ""
            if not text:
                continue

            text_lower = text.lower()
            direct_id = requirement_id.lower() in text_lower
            term_matches = sum(1 for term in terms if term in text_lower)

            # 실제 요구사항 ID가 직접 연결된 설계근거를 최우선으로 사용한다.
            # ID가 없을 때는 요구내용의 핵심어가 3개 이상 겹치는 경우만 보수적으로 후보화한다.
            if not direct_id and term_matches < 3:
                continue

            score = (100 if direct_id else 0) + term_matches
            location = block.location or block.sheet or (
                f"page {block.page}" if block.page is not None else block.block_type
            )
            evidence = (
                f"[설계근거] {document.file_path.name} | {location} | "
                f"{' '.join(text.split())[:1100]}"
            )
            ranked.append((-score, sequence, evidence))
            sequence += 1

    ranked.sort()
    return tuple(item[2] for item in ranked[:4])


def build_requirement_design_cases(
    documents: list[ParsedDocument],
) -> tuple[RequirementDesignCase, ...]:
    """REQ-009용 요구사항↔설계 교차검증 사례를 만든다.

    설계근거가 하나도 연결되지 않는 경우는 REQ-009에서 즉시 '미반영'으로 단정하지 않는다.
    그런 경우는 추적성 계열 Rule과 함께 판단해야 하므로 여기서는 제외한다.
    """

    design_documents = [
        document for document in documents
        if _is_design_source(document)
    ]
    if not design_documents:
        return ()

    cases: list[RequirementDesignCase] = []
    for requirement_id, document, block, text in _extract_requirement_cases(documents):
        design_evidence = _rank_design_blocks(
            requirement_id,
            text,
            design_documents,
        )
        if not design_evidence:
            continue

        cases.append(
            RequirementDesignCase(
                requirement_id=requirement_id,
                requirement_source=document.file_path.name,
                requirement_location=block.location or block.sheet,
                requirement_text=text,
                design_evidence=design_evidence,
            )
        )

    return tuple(cases)


def build_requirement_design_batches(
    documents: list[ParsedDocument],
    max_cases: int = 4,
    max_chars: int = 7600,
) -> tuple[RequirementDesignBatch, ...]:
    """저사양 Local AI에서도 처리 가능한 크기로 REQ-009 근거를 묶는다."""

    cases = build_requirement_design_cases(documents)
    if not cases:
        return ()

    batches: list[RequirementDesignBatch] = []
    current: list[str] = []
    current_case_count = 0
    current_chars = 0
    current_source_file = ""

    for case in cases:
        header = (
            f"[요구사항] {case.requirement_id} | {case.requirement_source} | "
            f"{case.requirement_location or '위치 미상'} | {case.requirement_text}"
        )
        parts = [header, *case.design_evidence]
        case_text = "\n".join(parts)

        if current and (
            current_case_count >= max_cases
            or current_chars + len(case_text) > max_chars
        ):
            batches.append(
                RequirementDesignBatch(
                    evidence=tuple(current),
                    case_count=current_case_count,
                    source_file=current_source_file,
                )
            )
            current = []
            current_case_count = 0
            current_chars = 0
            current_source_file = ""

        # 한 사례가 매우 길더라도 요구사항+설계근거 연결구조는 유지하되 상한만 둔다.
        if len(case_text) > max_chars:
            case_text = case_text[:max_chars]

        if not current_source_file:
            current_source_file = case.requirement_source
        current.append(case_text)
        current_case_count += 1
        current_chars += len(case_text) + 1

    if current:
        batches.append(
            RequirementDesignBatch(
                evidence=tuple(current),
                case_count=current_case_count,
                source_file=current_source_file,
            )
        )

    return tuple(batches)
