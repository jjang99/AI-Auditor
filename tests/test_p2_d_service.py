from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.inspection_service import InspectionService
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_p2_d_rules import get_p2_d_rules


class RecordingProvider(BaseAIProvider):
    def __init__(self):
        self.calls = []

    def inspect(self, document, rule, context=None):
        self.calls.append((document, rule, context))
        return AIInspectionResult(
            rule_code=rule.code,
            findings=(f"{rule.code} 테스트 지적",),
            raw_response="test",
        )


def _doc(name, *texts):
    return ParsedDocument(
        file_path=Path(name),
        file_type="txt",
        blocks=tuple(
            DocumentBlock(
                block_type="paragraph",
                text=text,
                location=f"문단 {index}",
            )
            for index, text in enumerate(texts, start=1)
        ),
    )


def _rules(*codes):
    wanted = set(codes)
    return tuple(rule for rule in get_p2_d_rules() if rule.code in wanted)


def _run(service, monkeypatch, documents):
    monkeypatch.setattr(service, "validate_files", lambda paths: ([Path("dummy.txt")], []))
    monkeypatch.setattr(service, "parse_documents", lambda paths: documents)
    return service.run(["dummy.txt"])


def test_ai003_service_calls_provider_with_ai_quality_evidence(monkeypatch):
    document = _doc(
        "AI_품질설계서.txt",
        "생성형 AI 서비스의 품질 목표를 정의한다.",
        "정확도와 응답시간을 평가기준으로 사용하고 목표값을 관리한다.",
    )
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AI-003"), ai_provider=provider)

    _inspection_id, summary = _run(service, monkeypatch, [document])

    assert len(provider.calls) == 1
    assert provider.calls[0][1].code == "AI-003"
    assert provider.calls[0][2] is not None and provider.calls[0][2].evidence
    assert any(issue.rule_code == "AI-003" for issue in summary.issues)


def test_p2_d_service_skips_general_non_ai_document(monkeypatch):
    document = _doc(
        "데이터모델설계서.txt",
        "논리 데이터 모델과 물리 데이터 모델을 정의한다.",
        "테이블 관계와 정규화 원칙을 설명한다.",
    )
    provider = RecordingProvider()
    service = InspectionService(
        rules=_rules("AI-003", "AI-008", "AI-013", "AI-015", "AI-017", "AI-021"),
        ai_provider=provider,
    )

    _inspection_id, summary = _run(service, monkeypatch, [document])

    assert provider.calls == []
    assert all(not issue.rule_code.startswith("AI-") for issue in summary.issues)


def test_ai015_service_skips_non_rag_ai_and_calls_for_rag(monkeypatch):
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AI-015"), ai_provider=provider)

    plain = _doc(
        "AI_서비스설계서.txt",
        "LLM이 사용자의 질문에 답변한다.",
        "답변 결과를 화면에 표시한다.",
    )
    _inspection_id, plain_summary = _run(service, monkeypatch, [plain])
    assert provider.calls == []
    assert all(issue.rule_code != "AI-015" for issue in plain_summary.issues)

    rag = _doc(
        "RAG_서비스설계서.txt",
        "RAG 구조에서 벡터검색으로 관련 문서를 조회한다.",
        "검색근거와 답변근거를 함께 관리한다.",
    )
    _inspection_id, rag_summary = _run(service, monkeypatch, [rag])
    assert len(provider.calls) == 1
    assert provider.calls[0][1].code == "AI-015"
    assert any(issue.rule_code == "AI-015" for issue in rag_summary.issues)


def test_ai021_service_skips_generic_app_log_but_uses_ai_trace_log(monkeypatch):
    provider = RecordingProvider()
    service = InspectionService(rules=_rules("AI-021"), ai_provider=provider)

    generic = _doc(
        "AI_운영설계서.txt",
        "LLM 서비스를 운영한다.",
        "일반 애플리케이션 로그를 파일에 저장한다.",
    )
    _inspection_id, generic_summary = _run(service, monkeypatch, [generic])
    assert provider.calls == []
    assert all(issue.rule_code != "AI-021" for issue in generic_summary.issues)

    traced = _doc(
        "AI_운영설계서.txt",
        "LLM 서비스의 AI 로그와 모델 버전을 기록한다.",
        "운영 품질 모니터링과 이상탐지 알림을 수행한다.",
    )
    _inspection_id, traced_summary = _run(service, monkeypatch, [traced])
    assert len(provider.calls) == 1
    assert provider.calls[0][1].code == "AI-021"
    assert any(issue.rule_code == "AI-021" for issue in traced_summary.issues)
