from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.core.models import DocumentRuleIssue

class FakeAIProvider(BaseAIProvider):
    """자동테스트용 가짜 AI Provider."""

    def __init__(self):
        self.received_contexts = []

    def inspect(
        self,
        document: ParsedDocument,
        rule,
        context=None,
    ) -> AIInspectionResult:
        self.received_contexts.append(context)

        return AIInspectionResult(
            rule_code=rule.code,
            findings=(
                f"{document.file_path.name}에서 테스트 지적사항 발견",
            ),
            raw_response="fake-ai-response",
        )


def test_ai_provider_can_inspect_document():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="사용자 인증 기능을 제공한다.",
            ),
        ),
    )

    rule = next(
        rule
        for rule in get_document_mvp_rules()
        if rule.code == "AUD-024"
    )

    provider = FakeAIProvider()

    result = provider.inspect(document, rule)

    assert result.rule_code == "AUD-024"
    assert len(result.findings) == 1
    assert "요구사항정의서.docx" in result.findings[0]
    assert result.raw_response == "fake-ai-response"

    assert result.execution_type == ""
    assert result.provider_name == ""

from rules.core.ai_engine import DocumentAIEngine


def test_ai_engine_executes_only_ai_rules():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="테스트 문서 내용",
            ),
        ),
    )

    provider = FakeAIProvider()

    engine = DocumentAIEngine(
        get_document_mvp_rules(),
        provider,
    )

    results = engine.inspect_document(document)

    executed_rule_codes = {
        result.rule_code
        for result in results
    }

    assert executed_rule_codes == {
        "AUD-024",
        "REQ-002",
        "REQ-004",
        "CHG-006",
        "CHG-018",
        "AI-005",
    }

    assert all(
        result.execution_type == "AI"
        for result in results
    )

    assert all(
        result.provider_name == "FakeAIProvider"
        for result in results
    )

from rules.core.hybrid_engine import DocumentHybridEngine


def test_hybrid_engine_selects_only_hybrid_rules():
    provider = FakeAIProvider()

    engine = DocumentHybridEngine(
        get_document_mvp_rules(),
        provider,
    )

    selected_rule_codes = {
        rule.code
        for rule in engine.rules
    }

    assert selected_rule_codes == {
        "AUD-002",
        "AUD-007",
        "REQ-003",
        "REQ-009",
        "REQ-018",
        "CHG-001",
        "CHG-012",
        "FP-005",
        "AI-009",
        "AI-019",
        "AI-022",
    }

def test_hybrid_engine_executes_hybrid_rules_through_provider():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="Hybrid 검사 테스트 문서",
            ),
        ),
    )

    provider = FakeAIProvider()

    engine = DocumentHybridEngine(
        get_document_mvp_rules(),
        provider,
    )

    results = engine.inspect_document(document)

    executed_rule_codes = {
        result.rule_code
        for result in results
    }

    assert len(results) == 11

    assert executed_rule_codes == {
        "AUD-002",
        "AUD-007",
        "REQ-003",
        "REQ-009",
        "REQ-018",
        "CHG-001",
        "CHG-012",
        "FP-005",
        "AI-009",
        "AI-019",
        "AI-022",
    }

    assert all(
        result.execution_type == "Hybrid"
        for result in results
    )

    assert all(
        result.provider_name == "FakeAIProvider"
        for result in results
    )

def test_hybrid_engine_passes_context_to_provider():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="Hybrid Context 전달 테스트",
            ),
        ),
    )

    provider = FakeAIProvider()

    engine = DocumentHybridEngine(
        get_document_mvp_rules(),
        provider,
    )

    engine.inspect_document(document)

    assert len(provider.received_contexts) == 11

    for rule, context in zip(engine.rules, provider.received_contexts):
        assert context is not None
        if rule.code == "REQ-018":
            assert context.evidence == ()
        else:
            assert context.evidence == ()

def test_req_003_builds_ambiguity_evidence_and_passes_it_to_provider():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="REQ-101 시스템은 필요시 관리자에게 알림을 제공한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-102 시스템은 사용자 정보를 적절히 표시한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-103 시스템은 로그인 이력을 1년간 보관한다.",
            ),
        ),
    )

    provider = FakeAIProvider()

    req_003_rule = next(
        rule
        for rule in get_document_mvp_rules()
        if rule.code == "REQ-003"
    )

    engine = DocumentHybridEngine(
        (req_003_rule,),
        provider,
    )

    results = engine.inspect_document(document)

    assert len(results) == 1
    assert len(provider.received_contexts) == 1

    context = provider.received_contexts[0]

    assert context is not None
    assert len(context.evidence) == 2

    assert any(
        "필요시" in evidence
        and "REQ-101" in evidence
        for evidence in context.evidence
    )

    assert any(
        "적절히" in evidence
        and "REQ-102" in evidence
        for evidence in context.evidence
    )

    assert all(
        "REQ-103" not in evidence
        for evidence in context.evidence
    )

    assert results[0].execution_type == "Hybrid"
    assert results[0].provider_name == "FakeAIProvider"

from rules.core.inspection_engine import DocumentInspectionEngine


def test_document_inspection_engine_combines_rule_ai_and_hybrid_results():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(
                block_type="paragraph",
                text="REQ-101 시스템은 필요시 관리자에게 알림을 제공한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-101 시스템은 관리자 정보를 조회한다.",
            ),
            DocumentBlock(
                block_type="paragraph",
                text="REQ-102 시스템은 사용자 정보를 적절히 표시한다.",
            ),
        ),
    )

    provider = FakeAIProvider()

    engine = DocumentInspectionEngine(
        get_document_mvp_rules(),
        provider,
    )

    results = engine.inspect_document(document)

    rule_results = [
        result
        for result in results
        if isinstance(result, DocumentRuleIssue)
    ]

    ai_results = [
        result
        for result in results
        if isinstance(result, AIInspectionResult)
    ]

    assert any(
        result.rule_code == "REQ-001"
        for result in rule_results
    )

    assert any(
        result.rule_code == "REQ-002"
        for result in ai_results
    )

    assert any(
        result.rule_code == "REQ-003"
        for result in ai_results
    )

    assert any(
        result.rule_code == "AI-022"
        for result in ai_results
    )

def test_req_018_builds_traceability_evidence_and_limits_context():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항ID | 유스케이스 | 화면 | 프로그램 | 통합테스트",
                sheet="SFR_기능",
                location="SFR_기능 / 행 1",
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="REQ-101 | UC-01 | SCR-01 | PRG-01 | TEST-01",
                sheet="SFR_기능",
                location="SFR_기능 / 행 2",
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="개정이력 | 1.2 | 종료단계 감리결과 반영",
                sheet="개정이력",
                location="개정이력 / 행 3",
            ),
        ),
    )

    provider = FakeAIProvider()
    req_018_rule = next(
        rule for rule in get_document_mvp_rules()
        if rule.code == "REQ-018"
    )
    engine = DocumentHybridEngine((req_018_rule,), provider)

    engine.inspect_document(document)

    context = provider.received_contexts[0]
    assert context is not None
    assert len(context.evidence) == 2
    assert any("요구사항ID" in item for item in context.evidence)
    assert any("REQ-101" in item for item in context.evidence)
    assert all("개정이력" not in item for item in context.evidence)
