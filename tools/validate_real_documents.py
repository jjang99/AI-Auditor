from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.parsers.parser_factory import parse_document
from app.services.local_ai_runtime import get_local_ai_runtime
from rules.core.ai_provider import AIInspectionResult
from rules.core.inspection_engine import DocumentInspectionEngine
from rules.core.models import DocumentRuleIssue, RuleIssue
from rules.core.severity import calculate_severity
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings


DEFAULT_RULES = {
    "hwp": ("REQ-003",),
    "xlsx": ("REQ-018",),
}


def select_rules(path: Path):
    codes = DEFAULT_RULES.get(path.suffix.lower().lstrip("."), ())
    all_rules = {rule.code: rule for rule in get_document_mvp_rules()}
    return tuple(all_rules[code] for code in codes)


def to_rule_issues(results):
    issues = []
    for result in results:
        if isinstance(result, DocumentRuleIssue):
            issues.append(
                RuleIssue(
                    rule_code=result.rule_code,
                    rule_name=result.rule_name,
                    category=result.category,
                    severity=result.severity,
                    file_path=result.file_path,
                    line_number=result.page or 0,
                    evidence=result.evidence,
                    description=result.description,
                )
            )
        elif isinstance(result, AIInspectionResult):
            for finding in result.findings:
                issues.append(
                    RuleIssue(
                        rule_code=result.rule_code,
                        rule_name=result.rule_code,
                        category="AI/Hybrid",
                        severity="Medium",
                        file_path="",
                        line_number=0,
                        evidence=finding,
                        description=finding,
                    )
                )
    return tuple(issues)


def main():
    parser = argparse.ArgumentParser(description="AI Auditor real-document MVP validation")
    parser.add_argument("documents", nargs="+", type=Path)
    args = parser.parse_args()

    runtime = get_local_ai_runtime()
    runtime.start()
    provider = LlamaCppAIProvider(LocalAISettings(base_url=runtime.base_url))
    assessor = LocalAIIssueAssessor(provider)

    try:
        all_issues = []
        for path in args.documents:
            started = time.perf_counter()
            document = parse_document(path)
            rules = select_rules(path)
            if not rules:
                print(f"[SKIP] {path.name}: no representative validation rule")
                continue

            engine = DocumentInspectionEngine(rules, provider)
            results = engine.inspect_document(document)
            issues = to_rule_issues(results)
            all_issues.extend(issues)

            print(f"\n[DOCUMENT] {path}")
            print(f"[PARSER] type={document.file_type}, blocks={len(document.blocks)}")
            print(f"[RULES] {', '.join(rule.code for rule in rules)}")
            print(f"[ISSUES] {len(issues)}")
            for result in results:
                if isinstance(result, AIInspectionResult):
                    print(f"  {result.rule_code}: findings={len(result.findings)}, provider={result.provider_name}")
                    for finding in result.findings:
                        print(f"    - {finding}")
                elif isinstance(result, DocumentRuleIssue):
                    print(f"  {result.rule_code}: {result.description}")
            print(f"[ELAPSED] {time.perf_counter() - started:.2f}s")

        if all_issues:
            print(f"\n[ASSESSMENT] batch Impact/Likelihood for {len(all_issues)} issue(s)")
            assessments = assessor.assess_many(tuple(all_issues), batch_size=2)
            for issue, assessment in zip(all_issues, assessments):
                if assessment is None:
                    continue
                severity = calculate_severity(assessment.impact, assessment.likelihood)
                print(
                    f"  {issue.rule_code}: Impact={assessment.impact.value}, "
                    f"Likelihood={assessment.likelihood.value}, Severity={severity.value}"
                )
                print(f"    Impact reason: {assessment.impact_reason}")
                print(f"    Likelihood reason: {assessment.likelihood_reason}")
        else:
            print("\n[ASSESSMENT] no issue found; batch assessment skipped")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
