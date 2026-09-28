from pathlib import Path

from app.database.repositories.inspection_repository import save_inspection_result
from app.parsers import get_supported_extensions, parse_document
from rules.core.engine import RuleEngine
from rules.definitions.default_rules import get_default_rules
from rules.core.document_result_adapter import (
    adapt_ai_result,
    adapt_document_issue,
)
from rules.core.inspection_engine import DocumentInspectionEngine
from rules.core.ai_provider import AIInspectionResult
from rules.core.models import (
    DocumentRuleIssue,
    InspectionSummary,
)
from rules.providers.deferred_ai_provider import DeferredAIProvider

SUPPORTED_TEXT_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".yml", ".yaml", ".xml",
    ".json", ".md", ".txt", ".properties", ".sql",
}

SUPPORTED_DOCUMENT_EXTENSIONS = set(get_supported_extensions())

class InspectionService:
    def __init__(self, rules=None, ai_provider=None):
        self.rules = rules or get_default_rules()

        self.is_document_inspection = bool(
            self.rules
            and hasattr(self.rules[0], "execution_type")
        )

        if self.is_document_inspection:
            self.ai_provider = ai_provider or DeferredAIProvider()

            self.document_engine = DocumentInspectionEngine(
                self.rules,
                self.ai_provider,
            )

            self.engine = None
        else:
            self.engine = RuleEngine(self.rules)
            self.document_engine = None

    def validate_files(self, file_paths):
        valid_paths = []
        errors = []

        for raw_path in file_paths:
            path = Path(raw_path)
            if not path.is_file():
                errors.append(f"파일을 찾을 수 없습니다: {path}")
                continue
            extension = path.suffix.lower()

            if (
                extension not in SUPPORTED_TEXT_EXTENSIONS
                and extension not in SUPPORTED_DOCUMENT_EXTENSIONS
            ):
                errors.append(f"지원하지 않는 파일 형식입니다: {path.name}")
                continue
            valid_paths.append(path)

        return valid_paths, errors

    def parse_documents(self, file_paths):
        parsed_documents = []

        for file_path in file_paths:
            path = Path(file_path)

            if path.suffix.lower() not in SUPPORTED_DOCUMENT_EXTENSIONS:
                continue

            parsed_documents.append(parse_document(path))

        return parsed_documents

    def run(self, file_paths, project_id=None, inspection_type="전체 검사", cancel_requested=None):
        valid_paths, errors = self.validate_files(file_paths)

        if errors:
            raise ValueError("\n".join(errors))

        if not valid_paths:
            raise ValueError("검사할 파일이 없습니다.")

        if self.is_document_inspection:
            parsed_documents = self.parse_documents(valid_paths)

            if not parsed_documents:
                raise ValueError("문서 검사 대상 파일이 없습니다.")

            all_issues = []

            # Rule 방식 검사
            rule_results = self.document_engine.rule_engine.inspect_documents(
                parsed_documents
            )

            for result in rule_results:
                all_issues.append(
                    adapt_document_issue(result)
                )

            # AI / Hybrid 방식 검사
            rule_by_code = {
                rule.code: rule
                for rule in self.rules
            }

            for document in parsed_documents:
                if cancel_requested is not None and cancel_requested():
                    from rules.core.engine import InspectionCancelled
                    raise InspectionCancelled("검사가 취소되었습니다.")

                ai_results = self.document_engine.ai_engine.inspect_document(
                    document
                )

                hybrid_results = self.document_engine.hybrid_engine.inspect_document(
                    document
                )

                for result in (*ai_results, *hybrid_results):
                    rule = rule_by_code[result.rule_code]

                    all_issues.extend(
                        adapt_ai_result(
                            result,
                            document,
                            rule,
                        )
                    )

            summary = InspectionSummary(
                file_count=len(parsed_documents),
                rule_count=len(self.rules),
                executed_rule_count=len(self.rules),
                issues=tuple(all_issues),
            )

        else:
            # 기존 소스코드 정적분석 경로는 그대로 유지
            summary = self.engine.inspect_files(
                valid_paths,
                cancel_requested=cancel_requested,
            )

        inspection_id = None

        if project_id is not None:
            inspection_id = save_inspection_result(
                project_id=project_id,
                summary=summary,
                inspection_type=inspection_type,
            )

        return inspection_id, summary
