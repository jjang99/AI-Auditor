from docx import Document

from app.services.inspection_service import InspectionService


def test_validate_files_accepts_text_and_document_files(tmp_path):
    text_path = tmp_path / "sample.txt"
    text_path.write_text("AI Auditor", encoding="utf-8")

    document_path = tmp_path / "sample.docx"
    document = Document()
    document.add_paragraph("요구사항 ID: REQ-001")
    document.save(document_path)

    service = InspectionService()

    valid_paths, errors = service.validate_files(
        [text_path, document_path]
    )

    assert errors == []
    assert valid_paths == [text_path, document_path]


def test_parse_documents_parses_supported_document(tmp_path):
    document_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("AI Auditor 문서 검사")
    document.add_paragraph("요구사항 ID: REQ-001")
    document.add_paragraph("요구사항명: 로그인 기능")
    document.save(document_path)

    service = InspectionService()

    parsed_documents = service.parse_documents([document_path])

    assert len(parsed_documents) == 1

    parsed = parsed_documents[0]

    assert parsed.file_type == "docx"
    assert "AI Auditor 문서 검사" in parsed.text
    assert "REQ-001" in parsed.text
    assert "로그인 기능" in parsed.text


def test_parse_documents_ignores_existing_text_files(tmp_path):
    text_path = tmp_path / "sample.txt"
    text_path.write_text("기존 Rule Engine 테스트", encoding="utf-8")

    service = InspectionService()

    parsed_documents = service.parse_documents([text_path])

    assert parsed_documents == []

def test_single_document_change_rules_require_comparison_context(tmp_path):
    from rules.core.ai_provider import AIInspectionResult, BaseAIProvider
    from rules.definitions.document_mvp_rules import get_document_mvp_rules

    class RecordingProvider(BaseAIProvider):
        def __init__(self):
            self.calls = []

        def inspect(self, document, rule, context=None):
            self.calls.append(rule.code)
            return AIInspectionResult(
                rule_code=rule.code,
                findings=(),
                raw_response="",
                provider_name=self.__class__.__name__,
            )

    document_path = tmp_path / "current.docx"
    document = Document()
    document.add_paragraph("변경된 화면과 시험 항목을 확인한다.")
    document.save(document_path)

    provider = RecordingProvider()
    service = InspectionService(
        rules=get_document_mvp_rules(),
        ai_provider=provider,
    )

    _inspection_id, summary = service.run([document_path])

    assert "CHG-001" not in provider.calls
    assert "CHG-012" not in provider.calls
    assert "CHG-006" not in provider.calls
    assert "CHG-018" not in provider.calls
    assert not any(issue.rule_code.startswith("CHG-") for issue in summary.issues)
