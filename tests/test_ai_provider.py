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

    # REQ-018은 사전분석 후보가 없으면 Provider를 호출하지 않는다.
    assert len(provider.received_contexts) == 10

    for context in provider.received_contexts:
        assert context is not None
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

def test_req_018_prefilters_only_missing_traceability_candidates():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 유스케이스명 | 화면ID | 화면명 | 인터페이스ID | 프로그램ID | 프로그램명 | 테이블ID | 통합테스트 시나리오ID",
                sheet="SFR_기능",
                location="SFR_기능 / 행 3",
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-001 | SFR-001-AD-01 | 로그인 | UC-01 | 로그인 | UI-01 | 로그인화면 | N/A | PRG-01 | 로그인처리 | TB_USER | ITS-01",
                sheet="SFR_기능",
                location="SFR_기능 / 행 4",
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-002 | SFR-002-AD-01 | 조회 |  | 조회 | UI-02 | 조회화면 | N/A | PRG-02 | 조회처리 | TB_DATA | ",
                sheet="SFR_기능",
                location="SFR_기능 / 행 5",
            ),
        ),
    )

    provider = FakeAIProvider()
    req_018_rule = next(
        rule for rule in get_document_mvp_rules()
        if rule.code == "REQ-018"
    )
    engine = DocumentHybridEngine((req_018_rule,), provider)

    context = engine.build_context(document, req_018_rule)

    assert len(context.evidence) == 1
    assert "SFR_기능 / 행 5" in context.evidence[0]
    assert "유스케이스" in context.evidence[0]
    assert "통합테스트" in context.evidence[0]
    assert "SFR_기능 / 행 4" not in context.evidence[0]




def test_req_018_skips_provider_when_no_missing_candidates():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 유스케이스명 | 화면ID | 화면명 | 인터페이스ID | 프로그램ID | 프로그램명 | 테이블ID | 통합테스트 시나리오ID",
                sheet="SFR_기능",
                location="SFR_기능 / 행 3",
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-001 | SFR-001-AD-01 | 로그인 | UC-01 | 로그인 | UI-01 | 로그인화면 | N/A | PRG-01 | 로그인처리 | TB_USER | ITS-01",
                sheet="SFR_기능",
                location="SFR_기능 / 행 4",
            ),
        ),
    )
    provider = FakeAIProvider()
    req_018_rule = next(
        rule for rule in get_document_mvp_rules()
        if rule.code == "REQ-018"
    )
    engine = DocumentHybridEngine((req_018_rule,), provider)

    results = engine.inspect_document(document)

    assert len(results) == 1
    assert results[0].rule_code == "REQ-018"
    assert results[0].findings == ()
    assert results[0].execution_type == "Hybrid"
    assert provider.received_contexts == []


def test_req_018_confirmed_missing_trace_becomes_finding_without_ai():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 유스케이스명 | 화면ID | 화면명 | 인터페이스ID | 프로그램ID | 프로그램명 | 테이블ID | 통합테스트 시나리오ID",
                sheet="SFR_기능",
                location="SFR_기능 / 행 3",
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-999 | SFR-999-AD-01 | 로그인 기능 | UC-999 | 로그인 | UI-999 | 로그인화면 | N/A | PRG-999 | 로그인처리 | TB_USER | ",
                sheet="SFR_기능",
                location="SFR_기능 / 행 4",
            ),
        ),
    )
    provider = FakeAIProvider()
    req_018_rule = next(
        rule for rule in get_document_mvp_rules()
        if rule.code == "REQ-018"
    )
    engine = DocumentHybridEngine((req_018_rule,), provider)

    result = engine.inspect_document(document)[0]

    assert len(result.findings) == 1
    assert "통합테스트" in result.findings[0]
    assert "SFR-999" in result.findings[0]
    assert result.raw_response == ""
    assert provider.received_contexts == []


def test_ai_engine_defers_aud_024_from_raw_document_loop():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(DocumentBlock(block_type="paragraph", text="테스트 문서"),),
    )
    provider = FakeAIProvider()
    engine = DocumentAIEngine(get_document_mvp_rules(), provider)

    engine.inspect_document(document)

    assert all(
        result.rule_code != "AUD-024"
        for result in engine.inspect_document(document)
    )


def test_comparison_ai_rules_receive_requirement_rows_only():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(block_type="sheet_row", text="문서 제목 | 요구사항추적표"),
            DocumentBlock(block_type="sheet_row", text="SFR-001 | 로그인 기능 | 사용자는 로그인할 수 있다."),
            DocumentBlock(block_type="sheet_row", text="SFR-002 | 인증 기능 | 사용자는 계정으로 로그인할 수 있다."),
            DocumentBlock(block_type="sheet_row", text="일반 설명 | 비교 대상 아님"),
        ),
    )
    provider = FakeAIProvider()
    rules = tuple(
        rule for rule in get_document_mvp_rules()
        if rule.code in {"REQ-002", "REQ-004"}
    )
    engine = DocumentAIEngine(rules, provider)

    results = engine.inspect_document(document)

    assert {result.rule_code for result in results} == {"REQ-002", "REQ-004"}
    assert len(provider.received_contexts) == 2
    for context in provider.received_contexts:
        assert context is not None
        assert len(context.evidence) == 2
        assert all(item.startswith("SFR-") for item in context.evidence)
        assert all("일반 설명" not in item for item in context.evidence)


def test_comparison_ai_rule_skips_provider_when_fewer_than_two_requirements():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(block_type="sheet_row", text="SFR-001 | 로그인 기능"),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-002")
    engine = DocumentAIEngine((rule,), provider)

    result = engine.inspect_document(document)[0]

    assert result.findings == ()
    assert provider.received_contexts == []


def test_hybrid_evidence_strategy_skips_provider_without_relevant_evidence():
    document = ParsedDocument(
        file_path=Path("일반문서.docx"),
        file_type="docx",
        blocks=(DocumentBlock(block_type="paragraph", text="일반 프로젝트 설명입니다."),),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "AI-009")
    engine = DocumentHybridEngine((rule,), provider)

    result = engine.inspect_document(document)[0]

    assert result.findings == ()
    assert provider.received_contexts == []


def test_hybrid_evidence_strategy_passes_only_relevant_blocks():
    document = ParsedDocument(
        file_path=Path("AI설계서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(block_type="paragraph", text="일반 프로젝트 설명입니다."),
            DocumentBlock(block_type="paragraph", text="Prompt Injection 공격에 대비한 입력 필터링과 권한제한을 적용한다."),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "AI-009")
    engine = DocumentHybridEngine((rule,), provider)

    engine.inspect_document(document)

    assert len(provider.received_contexts) == 1
    evidence = provider.received_contexts[0].evidence
    assert len(evidence) == 1
    assert "Prompt Injection" in evidence[0]
    assert all("일반 프로젝트 설명" not in item for item in evidence)
