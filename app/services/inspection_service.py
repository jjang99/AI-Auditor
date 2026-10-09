from pathlib import Path
import re

from app.database.repositories.inspection_repository import save_inspection_result
from app.parsers import get_supported_extensions, parse_document
from app.parsers.models import DocumentBlock, ParsedDocument
from rules.core.engine import RuleEngine
from rules.definitions.default_rules import get_default_rules
from rules.core.document_result_adapter import (
    adapt_ai_result,
    adapt_document_issue,
)
from rules.core.inspection_engine import DocumentInspectionEngine
from rules.core.ai_provider import AIInspectionContext, AIInspectionResult
from rules.core.issue_assessor import DeferredIssueAssessor, apply_issue_assessments
from rules.core.ai_strategy import AIProcessingStrategy, get_ai_processing_strategy
from rules.core.requirement_design_alignment import build_requirement_design_batches
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

_VERSION_SUFFIX_RE = re.compile(
    r"(?i)(?:[_\- ](?:v|ver)?\d+(?:\.\d+)*|[_\- ]\d{6,8})$"
)


def _artifact_family(path: Path) -> str:
    """Return a conservative family key for explicit versioned artifacts."""
    return _VERSION_SUFFIX_RE.sub("", path.stem).strip().lower()


def _version_rank(path: Path):
    stem = path.stem
    version = re.search(r"(?i)(?:^|[_\- ])(?:v|ver)?(\d+(?:\.\d+)*)$", stem)
    if version:
        return (2, tuple(int(part) for part in version.group(1).split(".")))
    dated = re.search(r"(?:^|[_\- ])(\d{6,8})$", stem)
    if dated:
        return (1, (int(dated.group(1)),))
    return (0, ())


def _find_version_pairs(documents):
    """Pair only same-type artifacts where at least one filename has a version marker."""
    groups = {}
    for document in documents:
        key = (document.file_type, _artifact_family(document.file_path))
        groups.setdefault(key, []).append(document)

    pairs = []
    for group in groups.values():
        if len(group) < 2:
            continue
        ranked = sorted(group, key=lambda doc: _version_rank(doc.file_path))
        if not any(_version_rank(doc.file_path)[0] > 0 for doc in ranked):
            continue
        pairs.append((ranked[-2], ranked[-1]))
    return tuple(pairs)


def _is_test_document(document: ParsedDocument) -> bool:
    name = document.file_path.stem.lower()
    return any(term in name for term in ("테스트", "시험", "test", "시나리오", "결과"))


class InspectionService:
    def __init__(self, rules=None, ai_provider=None, issue_assessor=None):
        self.rules = rules or get_default_rules()
        self.issue_assessor = issue_assessor or DeferredIssueAssessor()

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

            # REQ-009/CHG-001/CHG-012는 개별 문서 자체를 검사하지 않는다.
            # REQ-009는 아래에서 요구사항 문서와 설계 산출물을 교차 비교하고,
            # CHG-001은 명시적인 동일 산출물 버전쌍을 비교하며,
            # CHG-012는 확인된 변경 + 시험자료가 있을 때 후처리한다.
            hybrid_skip_codes = frozenset({"REQ-009", "CHG-001", "CHG-012"})

            for document in parsed_documents:
                if cancel_requested is not None and cancel_requested():
                    from rules.core.engine import InspectionCancelled
                    raise InspectionCancelled("검사가 취소되었습니다.")

                ai_results = self.document_engine.ai_engine.inspect_document(
                    document
                )

                hybrid_results = self.document_engine.hybrid_engine.inspect_document(
                    document,
                    skip_rule_codes=hybrid_skip_codes,
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

            # REQ-009: 요구사항 문서와 화면/인터페이스/데이터/프로그램 등
            # 설계 산출물을 실제로 함께 입력받은 경우에만 교차검증한다.
            # 연결 근거가 전혀 없는 경우는 REQ-009에서 즉시 미반영으로 단정하지 않고
            # 추적성 계열 Rule의 판단영역으로 남긴다.
            alignment_rule = rule_by_code.get("REQ-009")
            if alignment_rule is not None:
                alignment_batches = build_requirement_design_batches(parsed_documents)
                for batch_index, batch in enumerate(alignment_batches, start=1):
                    if cancel_requested is not None and cancel_requested():
                        from rules.core.engine import InspectionCancelled
                        raise InspectionCancelled("검사가 취소되었습니다.")

                    alignment_document = ParsedDocument(
                        file_path=Path(f"REQ-009-cross-document-{batch_index}.txt"),
                        file_type="requirement_design_comparison",
                        blocks=tuple(
                            DocumentBlock(
                                block_type="requirement_design_case",
                                text=evidence,
                            )
                            for evidence in batch.evidence
                        ),
                        metadata={
                            "source": "requirement_and_design_documents",
                            "case_count": batch.case_count,
                        },
                    )
                    alignment_result = self.ai_provider.inspect(
                        alignment_document,
                        alignment_rule,
                        AIInspectionContext(evidence=batch.evidence),
                    )
                    all_issues.extend(
                        adapt_ai_result(
                            alignment_result,
                            alignment_document,
                            alignment_rule,
                        )
                    )

            # CHG-001: 동일 산출물의 명시적 버전쌍만 이전/현재로 비교한다.
            change_rule = rule_by_code.get("CHG-001")
            if change_rule is not None:
                for previous, current in _find_version_pairs(parsed_documents):
                    comparison_document = ParsedDocument(
                        file_path=current.file_path,
                        file_type="version_comparison",
                        blocks=(
                            DocumentBlock(
                                block_type="comparison_header",
                                text=(
                                    f"[이전 산출물] {previous.file_path.name}\n"
                                    f"[현재 산출물] {current.file_path.name}"
                                ),
                            ),
                            DocumentBlock(
                                block_type="previous_document",
                                text=f"[이전 내용]\n{previous.text}",
                            ),
                            DocumentBlock(
                                block_type="current_document",
                                text=f"[현재 내용]\n{current.text}",
                            ),
                        ),
                        metadata={
                            "comparison": "previous_current",
                            "previous_file": str(previous.file_path),
                            "current_file": str(current.file_path),
                        },
                    )
                    change_result = self.ai_provider.inspect(
                        comparison_document,
                        change_rule,
                    )
                    all_issues.extend(
                        adapt_ai_result(
                            change_result,
                            comparison_document,
                            change_rule,
                        )
                    )

            # CHG-012: 실제 변경이 확인됐고 시험자료도 함께 입력된 경우에만
            # 변경내용과 시험자료를 하나의 근거 컨텍스트로 검사한다.
            test_documents = tuple(
                document for document in parsed_documents
                if _is_test_document(document)
            )
            change_issues = tuple(
                issue for issue in all_issues
                if issue.rule_code == "CHG-001"
            )
            test_change_rule = rule_by_code.get("CHG-012")
            if test_change_rule is not None and change_issues and test_documents:
                test_context = ParsedDocument(
                    file_path=test_documents[0].file_path,
                    file_type="change_test_comparison",
                    blocks=tuple(
                        [
                            DocumentBlock(
                                block_type="confirmed_change",
                                text=f"[확인된 변경] {issue.evidence}",
                            )
                            for issue in change_issues
                        ]
                        + [
                            DocumentBlock(
                                block_type="test_document",
                                text=(
                                    f"[시험 산출물] {document.file_path.name}\n"
                                    f"{block.location or block.block_type} | {block.text}"
                                ),
                            )
                            for document in test_documents
                            for block in document.blocks
                            if block.text and block.text.strip()
                        ]
                    ),
                    metadata={"source": "confirmed_changes_and_test_documents"},
                )
                test_change_result = self.ai_provider.inspect(
                    test_context,
                    test_change_rule,
                )
                all_issues.extend(
                    adapt_ai_result(
                        test_change_result,
                        test_context,
                        test_change_rule,
                    )
                )

            # CHG-006/CHG-018은 원문 직접검사가 아니라 앞 단계에서
            # 확인된 변경 관련 지적사항을 종합하는 후처리 Rule로 실행한다.
            for synthesis_code in ("CHG-006", "CHG-018"):
                synthesis_rule = rule_by_code.get(synthesis_code)
                if synthesis_rule is None:
                    continue

                source_codes = (
                    {"CHG-001"}
                    if synthesis_code == "CHG-006"
                    else {"CHG-001", "CHG-006", "CHG-012"}
                )
                source_issues = tuple(
                    issue for issue in all_issues
                    if issue.rule_code in source_codes
                )
                if not source_issues:
                    continue

                synthesis_document = ParsedDocument(
                    file_path=Path(source_issues[0].file_path),
                    file_type="inspection_findings",
                    blocks=tuple(
                        DocumentBlock(
                            block_type="inspection_finding",
                            text=(
                                f"{issue.rule_code} | {issue.rule_name} | "
                                f"{issue.evidence}"
                            ),
                        )
                        for issue in source_issues
                    ),
                    metadata={"source": "change_inspection_results"},
                )
                synthesis_result = self.ai_provider.inspect(
                    synthesis_document,
                    synthesis_rule,
                )
                all_issues.extend(
                    adapt_ai_result(
                        synthesis_result,
                        synthesis_document,
                        synthesis_rule,
                    )
                )

            # AUD-024는 원문 전체가 아니라 앞 단계에서 실제로 확인된
            # 개별 지적사항만 종합하여 마지막에 실행한다.
            audit_rule = rule_by_code.get("AUD-024")
            if audit_rule is not None and all_issues:
                audit_evidence = tuple(
                    DocumentBlock(
                        block_type="inspection_finding",
                        text=(
                            f"{issue.rule_code} | {issue.rule_name} | "
                            f"{issue.evidence}"
                        ),
                    )
                    for issue in all_issues
                    if issue.rule_code != "AUD-024"
                )
                if audit_evidence:
                    audit_document = ParsedDocument(
                        file_path=Path("inspection_findings.txt"),
                        file_type="inspection_findings",
                        blocks=audit_evidence,
                        metadata={"source": "inspection_results"},
                    )
                    audit_result = self.ai_provider.inspect(
                        audit_document,
                        audit_rule,
                    )
                    all_issues.extend(
                        adapt_ai_result(
                            audit_result,
                            audit_document,
                            audit_rule,
                        )
                    )

            all_issues = apply_issue_assessments(
                all_issues,
                self.issue_assessor,
                include_audit_judgment=True,
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