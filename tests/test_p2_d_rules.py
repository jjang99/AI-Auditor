from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionResult
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
from rules.core.p2_d_ai_engine import P2DAIEngine
from rules.core.p2_d_checks import (
    build_ai003_evidence,
    build_ai008_evidence,
    build_ai013_evidence,
    build_ai015_evidence,
    build_ai017_evidence,
    build_ai021_evidence,
    looks_like_ai_document,
)
from rules.core.p2_d_hybrid_engine import P2DHybridEngine
from rules.definitions.document_p2_d_rules import get_p2_d_rules


class RecordingProvider:
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=(f"{rule.code} 테스트 지적",),
            raw_response="test",
        )


def _doc(name, *texts, file_type="txt"):
    return ParsedDocument(
        file_path=Path(name),
        file_type=file_type,
        blocks=tuple(
            DocumentBlock(
                block_type="paragraph",
                text=text,
                location=f"문단 {index}",
            )
            for index, text in enumerate(texts, start=1)
        ),
    )


def _rule(code):
    return next(rule for rule in get_p2_d_rules() if rule.code == code)


def test_p2_d_definition_has_exact_six_rules():
    rules = get_p2_d_rules()
    assert len(rules) == 6
    assert {rule.code for rule in rules} == {
        "AI-003", "AI-008", "AI-013", "AI-015", "AI-017", "AI-021"
    }


def test_p2_d_ai_strategies_are_explicit_evidence():
    for code in ("AI-003", "AI-008", "AI-013", "AI-015", "AI-017", "AI-021"):
        assert get_ai_processing_strategy(code) == AIProcessingStrategy.EVIDENCE


def test_generic_data_model_document_is_not_ai_document():
    document = _doc(
        "데이터모델설계서.txt",
        "논리 데이터 모델과 물리 데이터 모델을 정의한다.",
        "테이블 관계와 정규화 원칙을 설명한다.",
    )
    assert not looks_like_ai_document(document)
    assert build_ai003_evidence(document) == ()
    assert build_ai021_evidence(document) == ()


def test_ai003_collects_performance_goal_evidence_only_in_ai_context():
    document = _doc(
        "AI_품질설계서.txt",
        "생성형 AI 서비스의 품질 목표를 정의한다.",
        "정확도와 응답시간을 평가기준으로 사용하며 목표값은 별도 표에서 관리한다.",
    )
    evidence = build_ai003_evidence(document)
    assert evidence
    assert any("정확도" in item for item in evidence)


def test_ai008_requires_sensitive_information_trigger():
    document = _doc(
        "AI_보안설계서.txt",
        "LLM 서비스는 사용자 입력을 처리한다.",
        "권한과 필터링 정책을 적용한다.",
    )
    assert build_ai008_evidence(document) == ()

    sensitive = _doc(
        "AI_보안설계서.txt",
        "LLM 서비스에서 개인정보가 입력될 수 있다.",
        "개인정보 마스킹 및 출력 필터링 정책을 적용한다.",
    )
    assert build_ai008_evidence(sensitive)


def test_ai013_collects_training_reference_data_evidence():
    document = _doc(
        "AI_데이터관리서.txt",
        "머신러닝 학습데이터의 출처와 품질을 관리한다.",
        "데이터셋 정제와 검증 절차를 기록한다.",
    )
    assert build_ai013_evidence(document)


def test_ai015_requires_explicit_rag_context():
    plain_ai = _doc(
        "AI_서비스설계서.txt",
        "LLM이 사용자의 질문에 답변한다.",
        "답변의 출처를 표시한다.",
    )
    assert build_ai015_evidence(plain_ai) == ()

    rag = _doc(
        "RAG_서비스설계서.txt",
        "RAG 구조에서 벡터검색으로 관련 문서를 조회한다.",
        "검색 결과와 답변 근거를 함께 관리한다.",
    )
    assert build_ai015_evidence(rag)


def test_ai017_collects_evaluation_test_evidence():
    document = _doc(
        "AI_평가계획서.txt",
        "LLM 평가데이터와 테스트케이스를 구성한다.",
        "정상입력과 예외입력, 위험입력을 포함하고 평가기준을 정의한다.",
    )
    assert build_ai017_evidence(document)


def test_ai021_does_not_trigger_on_generic_application_log_only():
    document = _doc(
        "AI_운영설계서.txt",
        "LLM 서비스를 운영한다.",
        "일반 애플리케이션 로그를 파일로 저장한다.",
    )
    assert build_ai021_evidence(document) == ()

    tracked = _doc(
        "AI_운영설계서.txt",
        "LLM 서비스의 AI 로그와 모델 버전을 기록한다.",
        "운영 품질 모니터링과 이상탐지 알림을 수행한다.",
    )
    assert build_ai021_evidence(tracked)


def test_p2_d_hybrid_engine_skips_provider_without_evidence():
    document = _doc(
        "AI_서비스설계서.txt",
        "LLM 서비스의 기본 구성만 정의한다.",
    )
    provider = RecordingProvider()
    engine = P2DHybridEngine([_rule("AI-008")], provider)

    results = engine.inspect_document(document)

    assert provider.calls == []
    assert results[0].findings == ()


def test_p2_d_hybrid_engine_calls_provider_with_evidence():
    document = _doc(
        "AI_서비스설계서.txt",
        "LLM 서비스에서 개인정보가 입력될 수 있다.",
        "개인정보 마스킹과 출력 필터링을 적용한다.",
    )
    provider = RecordingProvider()
    engine = P2DHybridEngine([_rule("AI-008")], provider)

    results = engine.inspect_document(document)

    assert len(provider.calls) == 1
    assert provider.calls[0][2] is not None
    assert provider.calls[0][2].evidence
    assert results[0].rule_code == "AI-008"


def test_p2_d_ai_engine_calls_ai015_only_for_rag_evidence():
    provider = RecordingProvider()
    engine = P2DAIEngine([_rule("AI-015")], provider)

    plain = _doc("AI_서비스설계서.txt", "LLM이 질문에 답변한다.")
    plain_result = engine.inspect_document(plain)
    assert provider.calls == []
    assert plain_result[0].findings == ()

    rag = _doc(
        "RAG_서비스설계서.txt",
        "RAG 기반 벡터검색으로 문서를 조회한다.",
        "검색근거와 답변근거를 함께 제공한다.",
    )
    rag_result = engine.inspect_document(rag)
    assert len(provider.calls) == 1
    assert provider.calls[0][2] is not None and provider.calls[0][2].evidence
    assert rag_result[0].rule_code == "AI-015"
