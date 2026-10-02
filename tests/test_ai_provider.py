from pathlib import Path

from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.core.models import DocumentRuleIssue
from rules.providers.local_ai_provider import LlamaCppAIProvider

class FakeAIProvider(BaseAIProvider):
    """자동테스트용 가짜 AI Provider."""

    def __init__(self):
        self.received_contexts = []

    def build_requirement_conflict_groups(self, evidence):
        if len(evidence) < 2:
            return ()
        return (tuple(evidence[:2]),)

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

def test_hybrid_engine_skips_provider_without_strategy_evidence():
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

    results = engine.inspect_document(document)

    # 후보/근거확인형은 관련 근거가 없으면 AI를 호출하지 않고,
    # REQ-018도 구조적 누락 후보가 없으면 Rule-first에서 종료한다.
    assert len(results) == 11
    assert provider.received_contexts == []


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



def test_req_018_does_not_flag_nonfunctional_or_na_trace_values():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(block_type="sheet_row", text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 화면ID | 프로그램ID | 테이블ID | 통합테스트 시나리오ID", sheet="비기능", location="비기능 / 행 3"),
            DocumentBlock(block_type="sheet_row", text="SER-002 | SER-002-CT-01 | 보안 준수 | N/A |  |  |  | ", sheet="비기능", location="비기능 / 행 4"),
            DocumentBlock(block_type="sheet_row", text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 화면ID | 프로그램ID | 테이블ID | 통합테스트 시나리오ID", sheet="SFR_기능", location="SFR_기능 / 행 3"),
            DocumentBlock(block_type="sheet_row", text="SFR-001 | SFR-001-AD-01 | 로그인 | UC-01 | UI-01 | PRG-01 | TB_USER | N/A", sheet="SFR_기능", location="SFR_기능 / 행 4"),
        ),
    )
    provider = FakeAIProvider()
    req_018_rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-018")
    engine = DocumentHybridEngine((req_018_rule,), provider)

    result = engine.inspect_document(document)[0]

    assert result.findings == ()
    assert provider.received_contexts == []


def test_req_018_accepts_na_variants_and_sheet_references():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 화면ID | 프로그램ID | 테이블ID | 통합테스트 시나리오ID",
                sheet="기능",
                location="기능 / 행 3",
                metadata={"cell_values": ("요구사항", "요구사항ID", "요구사항명", "유스케이스ID", "화면ID", "프로그램ID", "테이블ID", "통합테스트 시나리오ID")},
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-050 | SFR-050-IC-01 | 정보유통 확대 | N/A | N/A | *SFR-050 시트 참고 | N./A | *SFR-050 시트 참고",
                sheet="기능",
                location="기능 / 행 4",
                metadata={"cell_values": ("SFR-050", "SFR-050-IC-01", "정보유통 확대", "N/A", "N/A", "*SFR-050 시트 참고", "N./A", "*SFR-050 시트 참고")},
            ),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-018")
    result = DocumentHybridEngine((rule,), provider).inspect_document(document)[0]

    assert result.findings == ()
    assert provider.received_contexts == []


def test_req_018_defers_parent_row_when_trace_is_delegated_to_detail_sheet():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 화면ID | 프로그램ID | 테이블ID | 통합테스트 시나리오ID | 비고",
                sheet="기능",
                location="기능 / 행 3",
                metadata={"cell_values": ("요구사항", "요구사항ID", "요구사항명", "유스케이스ID", "화면ID", "프로그램ID", "테이블ID", "통합테스트 시나리오ID", "비고")},
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-050 | SFR-050-IC-01 | 정보유통 확대 | N/A | *SFR-050 시트 참고",
                sheet="기능",
                location="기능 / 행 4",
                metadata={"cell_values": ("SFR-050", "SFR-050-IC-01", "정보유통 확대", "N/A", "", "", "", "", "*SFR-050 시트 참고")},
            ),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-018")

    result = DocumentHybridEngine((rule,), provider).inspect_document(document)[0]

    assert result.findings == ()
    assert provider.received_contexts == []


def test_req_018_prefers_id_column_over_name_column():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 | 요구사항ID | 요구사항명 | 유스케이스ID | 유스케이스명 | 화면ID | 화면명 | 프로그램명 | 프로그램ID | 테이블ID | 통합테스트",
                sheet="기능",
                location="기능 / 행 3",
                metadata={"cell_values": ("요구사항", "요구사항ID", "요구사항명", "유스케이스ID", "유스케이스명", "화면ID", "화면명", "프로그램명", "프로그램ID", "테이블ID", "통합테스트")},
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-007 | SFR-007-AD-04 | 정산 | UC-01 | 정산 | UI-01 | 정산화면 | N/A | N/A | TB-01 | ITS-01",
                sheet="기능",
                location="기능 / 행 4",
                metadata={"cell_values": ("SFR-007", "SFR-007-AD-04", "정산", "UC-01", "정산", "UI-01", "정산화면", "N/A", "N/A", "TB-01", "ITS-01")},
            ),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-018")

    result = DocumentHybridEngine((rule,), provider).inspect_document(document)[0]

    assert result.findings == ()


def test_req_018_accepts_na_in_paired_name_column():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="고유번호 | 요구사항ID | 화면ID | 화면명 | 프로그램ID | 프로그램명 | 테이블ID | 통합테스트ID",
                sheet="기능",
                location="기능 / 행 2",
                metadata={"cell_values": ("고유번호", "요구사항ID", "화면ID", "화면명", "프로그램ID", "프로그램명", "테이블ID", "통합테스트ID")},
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="SFR-007 | SFR-007-AD-04 | UI-0740 | 정산정보 | N/A | TB_FS200 | ITS-AS-0730",
                sheet="기능",
                location="기능 / 행 14",
                metadata={"cell_values": ("SFR-007", "SFR-007-AD-04", "UI-0740", "정산정보", "", "N/A", "TB_FS200", "ITS-AS-0730")},
            ),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-018")
    result = DocumentHybridEngine((rule,), provider).inspect_document(document)[0]
    assert result.findings == ()

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


def test_comparison_ai_rules_skip_when_xlsx_has_no_structured_columns():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(block_type="sheet_row", text="문서 제목 | 요구사항추적표"),
            DocumentBlock(block_type="sheet_row", text="SFR-001 | 로그인 기능 | 사용자는 로그인할 수 있다."),
            DocumentBlock(block_type="sheet_row", text="SFR-002 | 인증 기능 | 사용자는 계정으로 로그인할 수 있다."),
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
    assert provider.received_contexts == []


def test_xlsx_comparison_evidence_uses_requirement_columns_only():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항 ID | 요구사항명 | 화면 ID | 프로그램 ID",
                sheet="요구사항",
                metadata={
                    "cell_values": (
                        "요구사항 ID",
                        "요구사항명",
                        "화면 ID",
                        "프로그램 ID",
                    ),
                },
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="REQ-001 | 로그인 기능 | UI-001 | PRG-001",
                sheet="요구사항",
                metadata={
                    "cell_values": (
                        "REQ-001",
                        "로그인 기능",
                        "UI-001",
                        "PRG-001",
                    ),
                },
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="REQ-002 | 사용자 조회 | UI-002 | PRG-002",
                sheet="요구사항",
                metadata={
                    "cell_values": (
                        "REQ-002",
                        "사용자 조회",
                        "UI-002",
                        "PRG-002",
                    ),
                },
            ),
        ),
    )

    evidence = DocumentAIEngine._build_requirement_comparison_evidence(document)

    assert evidence == (
        "REQ-001 | 로그인 기능",
        "REQ-002 | 사용자 조회",
    )
    assert all("UI-" not in item and "PRG-" not in item for item in evidence)


def test_xlsx_comparison_evidence_preserves_empty_cells_before_requirement_columns():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="구분 | 요구사항 ID | 요구사항명 | 화면 ID",
                sheet="요구사항",
                metadata={
                    "cell_values": ("구분", "요구사항 ID", "요구사항명", "화면 ID"),
                },
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="REQ-010 | 로그인 기능 | UI-010",
                sheet="요구사항",
                metadata={
                    "cell_values": ("", "REQ-010", "로그인 기능", "UI-010"),
                },
            ),
        ),
    )

    evidence = DocumentAIEngine._build_requirement_comparison_evidence(document)

    assert evidence == ("REQ-010 | 로그인 기능",)


def test_req002_comparison_prefilter_selects_only_same_normalized_meaning():
    evidence = (
        "REQ-001 | 사용자 로그인 기능",
        "REQ-002 | 사용자 로그인 기능",
        "REQ-003 | 관리자 통계 조회",
    )

    pairs = DocumentAIEngine._build_comparison_pairs(
        evidence,
        rule_code="REQ-002",
    )

    assert pairs == ((
        "REQ-001 | 사용자 로그인 기능",
        "REQ-002 | 사용자 로그인 기능",
    ),)


def test_xlsx_comparison_evidence_includes_explicit_detail_column():
    document = ParsedDocument(
        file_path=Path("요구사항추적표.xlsx"),
        file_type="xlsx",
        blocks=(
            DocumentBlock(
                block_type="sheet_row",
                text="요구사항ID | 요구사항명 | 상세내용 | 비고",
                sheet="PER",
                metadata={
                    "cell_values": (
                        "요구사항ID",
                        "요구사항명",
                        "상세내용",
                        "비고",
                    ),
                },
            ),
            DocumentBlock(
                block_type="sheet_row",
                text="PER-001-CT-01 | 서비스수준보장 | 응답시간은 3초 이내 | 확인",
                sheet="PER",
                metadata={
                    "cell_values": (
                        "PER-001-CT-01",
                        "서비스수준보장",
                        "응답시간은 3초 이내",
                        "확인",
                    ),
                },
            ),
        ),
    )

    evidence = DocumentAIEngine._build_requirement_comparison_evidence(document)

    assert evidence == (
        "PER-001-CT-01 | 서비스수준보장 | 응답시간은 3초 이내",
    )


def test_local_provider_req004_schema_requires_exact_conflict_pairs():
    class RecordingProvider(LlamaCppAIProvider):
        def _complete(self, prompt, response_format=None):
            self.recorded_prompt = prompt
            self.recorded_format = response_format
            return '{"groups":[]}'

    provider = RecordingProvider()
    groups = provider.build_requirement_conflict_groups((
        "REQ-001 | 응답시간은 3초 이내",
        "REQ-002 | 응답시간은 5초 이상",
        "REQ-003 | 관리자 화면을 제공한다",
    ))

    indexes_schema = (
        provider.recorded_format["json_schema"]["schema"]["properties"]["groups"]
        ["items"]["properties"]["indexes"]
    )
    assert groups == ()
    assert indexes_schema["minItems"] == 2
    assert indexes_schema["maxItems"] == 2
    assert indexes_schema["uniqueItems"] is True
    assert "동일 대상/속성" in provider.recorded_prompt
    assert "같은 업무 주제" in provider.recorded_prompt


def test_local_provider_req004_batches_with_overlap():
    class BatchProvider(LlamaCppAIProvider):
        def __init__(self):
            super().__init__()
            self.calls = 0

        def _complete(self, prompt, response_format=None):
            self.calls += 1
            return '{"groups":[]}'

    evidence = tuple(f"REQ-{index:03d} | 일반 기능 {index}" for index in range(1, 14))
    provider = BatchProvider()

    groups = provider.build_requirement_conflict_groups(evidence)

    assert groups == ()
    assert provider.calls == 2
    assert provider.last_requirement_conflict_diagnostics["batch_count"] == 2
    assert provider.last_requirement_conflict_diagnostics["batches"][0]["start"] == 0
    assert provider.last_requirement_conflict_diagnostics["batches"][1]["start"] == 11


def test_req004_uses_provider_semantic_groups_for_conflict_inspection():
    document = ParsedDocument(
        file_path=Path("요구사항정의서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(block_type="paragraph", text="REQ-001 | 응답시간은 3초 이내"),
            DocumentBlock(block_type="paragraph", text="REQ-002 | 응답시간은 5초 이상"),
            DocumentBlock(block_type="paragraph", text="REQ-003 | 관리자 화면을 제공한다"),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "REQ-004")
    engine = DocumentAIEngine((rule,), provider)

    result = engine.inspect_document(document)[0]

    assert len(provider.received_contexts) == 1
    assert provider.received_contexts[0].evidence == (
        "REQ-001 | 응답시간은 3초 이내",
        "REQ-002 | 응답시간은 5초 이상",
    )
    assert result.findings


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


def test_pure_ai_evidence_rule_skips_provider_without_relevant_evidence():
    document = ParsedDocument(
        file_path=Path("일반문서.docx"),
        file_type="docx",
        blocks=(DocumentBlock(block_type="paragraph", text="일반 프로젝트 설명입니다."),),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "AI-005")
    engine = DocumentAIEngine((rule,), provider)

    result = engine.inspect_document(document)[0]

    assert result.findings == ()
    assert provider.received_contexts == []


def test_pure_ai_evidence_rule_passes_relevant_blocks_only():
    document = ParsedDocument(
        file_path=Path("AI설계서.docx"),
        file_type="docx",
        blocks=(
            DocumentBlock(block_type="paragraph", text="일반 프로젝트 설명입니다."),
            DocumentBlock(block_type="paragraph", text="AI 출력의 정확성과 근거성을 검증하고 환각 탐지 후 재검토한다."),
        ),
    )
    provider = FakeAIProvider()
    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "AI-005")
    engine = DocumentAIEngine((rule,), provider)

    engine.inspect_document(document)

    assert len(provider.received_contexts) == 1
    evidence = provider.received_contexts[0].evidence
    assert len(evidence) == 1
    assert "환각" in evidence[0]


def test_base_issue_assessor_batch_falls_back_to_individual_calls():
    from rules.core.issue_assessor import BaseIssueAssessor
    from rules.core.models import RuleIssue
    from rules.core.severity import AssessmentLevel, IssueAssessment, IssueSeverity

    class RecordingAssessor(BaseIssueAssessor):
        def __init__(self):
            self.calls = 0

        def assess(self, issue):
            self.calls += 1
            return IssueAssessment(
                impact=AssessmentLevel.LOW,
                impact_reason="낮음",
                likelihood=AssessmentLevel.LOW,
                likelihood_reason="낮음",
                severity=IssueSeverity.LOW,
                severity_reason="",
            )

    issues = tuple(
        RuleIssue(
            rule_code=f"T-{i}",
            rule_name="테스트",
            category="테스트",
            severity="Low",
            file_path="test.txt",
            line_number=i,
            evidence="근거",
            description="설명",
        )
        for i in range(3)
    )
    assessor = RecordingAssessor()

    results = assessor.assess_many(issues)

    assert len(results) == 3
    assert assessor.calls == 3


def test_comparison_prefilter_does_not_guess_semantic_similarity():
    evidence = (
        "SFR-001 | 사용자는 아이디와 비밀번호로 로그인한다.",
        "SFR-002 | 사용자 ID와 비밀번호로 시스템에 로그인한다.",
        "SFR-003 | 관리자는 월별 통계 보고서를 조회한다.",
    )

    pairs = DocumentAIEngine._build_comparison_pairs(
        evidence,
        rule_code="REQ-002",
    )

    assert pairs == ()


def test_comparison_prefilter_returns_no_pair_for_unrelated_requirements():
    evidence = (
        "SFR-001 | 사용자는 로그인한다.",
        "SFR-002 | 관리자는 통계 보고서를 출력한다.",
    )

    pairs = DocumentAIEngine._build_comparison_pairs(evidence, rule_code="REQ-002")

    assert pairs == ()


class ChangeComparisonProvider(LlamaCppAIProvider):
    def __init__(self):
        super().__init__()
        self.prompts = []

    def _complete(self, prompt, response_format=None):
        self.prompts.append(prompt)
        return '{"findings":["기능 조건이 변경되었습니다."]}'


def test_change_comparison_uses_diff_candidates_instead_of_whole_documents():
    from pathlib import Path
    from app.parsers.models import DocumentBlock, ParsedDocument
    from rules.definitions.document_mvp_rules import get_document_mvp_rules

    rule = next(rule for rule in get_document_mvp_rules() if rule.code == "CHG-001")
    document = ParsedDocument(
        file_path=Path("요구사항_v1.1.hwp"),
        file_type="version_comparison",
        blocks=(
            DocumentBlock(block_type="previous_document", text="[이전 내용]\n로그인 실패 5회 제한\n공통 내용"),
            DocumentBlock(block_type="current_document", text="[현재 내용]\n로그인 실패 3회 제한\n공통 내용"),
        ),
        metadata={"previous_file": "요구사항.hwp", "current_file": "요구사항_v1.1.hwp"},
    )

    provider = ChangeComparisonProvider()
    result = provider.inspect(document, rule)

    assert result.findings == ("기능 조건이 변경되었습니다.",)
    assert len(provider.prompts) == 1
    assert "로그인 실패 5회 제한" in provider.prompts[0]
    assert "로그인 실패 3회 제한" in provider.prompts[0]
    assert "공통 내용" not in provider.prompts[0]
