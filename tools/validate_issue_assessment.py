from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.local_ai_runtime import get_local_ai_runtime
from rules.core.models import RuleIssue
from rules.core.severity import calculate_severity
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings


def main():
    issues = (
        RuleIssue(
            rule_code="REQ-018",
            rule_name="양방향 추적성 점검",
            category="요구사항 정합성",
            severity="Medium",
            file_path="validation_fixture.xlsx",
            line_number=12,
            evidence="REQ-101의 통합테스트 시나리오 ID가 비어 있음",
            description="요구사항 REQ-101에 대응하는 통합테스트 추적정보가 누락됨",
        ),
        RuleIssue(
            rule_code="AUD-007",
            rule_name="미확정 표현 점검",
            category="감리 사전점검",
            severity="Low",
            file_path="validation_fixture.hwp",
            line_number=34,
            evidence="세부 적용방안은 추후 협의하여 확정한다.",
            description="산출물에 미확정 표현 '추후 협의'가 남아 있음",
        ),
    )

    runtime = get_local_ai_runtime()
    runtime.start()
    provider = LlamaCppAIProvider(LocalAISettings(base_url=runtime.base_url))
    assessor = LocalAIIssueAssessor(provider)

    try:
        started = time.perf_counter()
        assessments = assessor.assess_many(issues, batch_size=2)
        print(f"[ISSUES] {len(issues)}")
        for issue, assessment in zip(issues, assessments):
            if assessment is None:
                print(f"{issue.rule_code}: assessment=None")
                continue
            severity = calculate_severity(assessment.impact, assessment.likelihood)
            print(
                f"{issue.rule_code}: Impact={assessment.impact.value}, "
                f"Likelihood={assessment.likelihood.value}, Severity={severity.value}"
            )
            print(f"  Impact reason: {assessment.impact_reason}")
            print(f"  Likelihood reason: {assessment.likelihood_reason}")
        print(f"[ELAPSED] {time.perf_counter() - started:.2f}s")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
