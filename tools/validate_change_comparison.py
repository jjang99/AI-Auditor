from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.inspection_service import InspectionService, _find_version_pairs
from app.services.local_ai_runtime import get_local_ai_runtime
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: python tools/validate_change_comparison.py <previous> <current>"
        )

    paths = tuple(Path(arg) for arg in sys.argv[1:])
    rules = tuple(
        rule for rule in get_document_mvp_rules()
        if rule.code in {"CHG-001", "CHG-006"}
    )

    runtime = get_local_ai_runtime()
    runtime.start()
    provider = LlamaCppAIProvider(LocalAISettings(base_url=runtime.base_url))
    service = InspectionService(rules=rules, ai_provider=provider)

    try:
        parsed = service.parse_documents(paths)
        pairs = _find_version_pairs(parsed)
        print(f"[DOCUMENTS] {len(parsed)}")
        print(f"[VERSION PAIRS] {len(pairs)}")
        for previous, current in pairs:
            print(f"  previous: {previous.file_path.name}")
            print(f"  current : {current.file_path.name}")

        if len(pairs) != 1:
            raise SystemExit("[FAIL] exactly one explicit version pair was not identified")

        started = time.perf_counter()
        _inspection_id, summary = service.run(paths)
        for rule_code in ("CHG-001", "CHG-006"):
            issues = tuple(
                issue for issue in summary.issues
                if issue.rule_code == rule_code
            )
            print(f"[{rule_code} ISSUES] {len(issues)}")
            for index, issue in enumerate(issues, 1):
                print(f"  [{index}] {issue.description}")
                print(f"      evidence: {issue.evidence}")
        print(f"[ELAPSED] {time.perf_counter() - started:.2f}s")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
