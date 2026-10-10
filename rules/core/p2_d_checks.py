"""P2-D AI/RAG 품질·보안·운영 사전분석 유틸리티.

오탐 방지 원칙:
- AI/LLM/RAG 맥락이 확인된 문서에만 적용한다.
- 특정 목표값·정책·보안수준을 임의 생성하지 않는다.
- 구조적 근거가 없으면 AI 호출 후보를 만들지 않는다.
"""

from __future__ import annotations

from app.parsers.models import ParsedDocument


_AI_CONTEXT_TERMS = (
    "인공지능",
    "생성형 ai",
    "generative ai",
    "llm",
    "rag",
    "prompt",
    "프롬프트",
    "ai 모델",
    "llm 모델",
    "machine learning",
    "머신러닝",
    "embedding",
    "임베딩",
)


def looks_like_ai_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    if any(term in name for term in ("ai", "인공지능", "llm", "rag", "생성형", "머신러닝")):
        return True

    joined = " ".join((block.text or "")[:500] for block in document.blocks[:30]).lower()
    return any(term in joined for term in _AI_CONTEXT_TERMS)


def _collect_evidence(
    document: ParsedDocument,
    *,
    trigger_terms: tuple[str, ...],
    context_terms: tuple[str, ...] = (),
    max_items: int = 12,
) -> tuple[str, ...]:
    if not looks_like_ai_document(document):
        return ()

    lowered_triggers = tuple(term.lower() for term in trigger_terms)
    lowered_context = tuple(term.lower() for term in context_terms)

    matched_any_trigger = False
    evidence: list[str] = []
    seen: set[str] = set()

    for block in document.blocks:
        text = (block.text or "").strip()
        if not text:
            continue
        lowered = text.lower()
        trigger_hit = any(term in lowered for term in lowered_triggers)
        context_hit = any(term in lowered for term in lowered_context)
        if not trigger_hit and not context_hit:
            continue
        if trigger_hit:
            matched_any_trigger = True

        location = block.location or block.sheet or (
            f"page {block.page}" if block.page is not None else None
        ) or (
            f"slide {block.slide}" if block.slide is not None else None
        ) or "위치 미상"
        item = f"{location}: {text[:900]}"
        if item in seen:
            continue
        seen.add(item)
        evidence.append(item)
        if len(evidence) >= max_items:
            break

    if not matched_any_trigger:
        return ()
    return tuple(evidence)


def build_ai003_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """AI-003: 성능/품질 목표 또는 평가기준 관련 근거를 수집한다."""
    return _collect_evidence(
        document,
        trigger_terms=(
            "정확도", "precision", "recall", "f1", "응답시간", "latency",
            "품질목표", "성능목표", "목표값", "허용수준", "평가기준",
        ),
        context_terms=("품질", "성능", "평가", "sla", "목표"),
    )


def build_ai008_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """AI-008: 민감정보 처리대상과 통제근거 관련 후보를 수집한다."""
    return _collect_evidence(
        document,
        trigger_terms=(
            "개인정보", "민감정보", "기밀", "비밀", "주민번호", "전화번호",
            "이메일", "계정정보", "보안정보",
        ),
        context_terms=(
            "마스킹", "비식별", "차단", "필터링", "필터", "권한", "접근통제",
            "입력통제", "출력통제", "노출방지",
        ),
    )


def build_ai013_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """AI-013: 학습/참조데이터 관리 근거 후보를 수집한다."""
    return _collect_evidence(
        document,
        trigger_terms=(
            "학습데이터", "학습 데이터", "참조데이터", "참조 데이터", "데이터셋",
            "dataset", "fine-tuning", "파인튜닝", "튜닝데이터",
        ),
        context_terms=(
            "출처", "품질", "적합성", "정제", "전처리", "검증", "라벨",
            "버전", "갱신", "수집",
        ),
    )


def build_ai015_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """AI-015: RAG/검색증강이 명시된 문서에서 검색·답변근거 후보를 수집한다."""
    return _collect_evidence(
        document,
        trigger_terms=(
            "rag", "검색증강", "검색 증강", "retrieval augmented", "벡터검색",
            "vector search", "vector db", "vectordb", "임베딩", "embedding",
            "retriever",
        ),
        context_terms=(
            "검색근거", "검색 결과", "검색결과", "답변근거", "출처", "citation",
            "chunk", "청크", "top-k", "유사도",
        ),
    )


def build_ai017_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """AI-017: AI 평가/테스트 체계 관련 근거 후보를 수집한다."""
    return _collect_evidence(
        document,
        trigger_terms=(
            "평가데이터", "평가 데이터", "테스트데이터", "테스트 데이터", "시험데이터",
            "평가셋", "test set", "validation set", "벤치마크", "테스트케이스",
        ),
        context_terms=(
            "정상입력", "예외입력", "위험입력", "공격입력", "평가방법", "평가기준",
            "합격기준", "회귀시험", "회귀 테스트", "성능평가",
        ),
    )


def build_ai021_evidence(document: ParsedDocument) -> tuple[str, ...]:
    """AI-021: AI 추적성과 운영 모니터링 근거 후보를 수집한다."""
    return _collect_evidence(
        document,
        trigger_terms=(
            "ai 로그", "llm 로그", "모델로그", "모델 로그", "추적성", "traceability",
            "모델버전", "모델 버전", "프롬프트버전", "프롬프트 버전",
            "토큰사용량", "token usage", "inference log",
        ),
        context_terms=(
            "모니터링", "이상탐지", "품질모니터링", "운영품질", "입력기록", "출력기록",
            "결과기록", "감사로그", "audit log", "대시보드", "알림",
        ),
    )
