from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.local_ai_runtime import get_local_ai_runtime
from rules.core.models import RuleIssue
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings


def main():
    # 서로 성격이 확실히 다른 2건만 한 배치로 검증한다.
    # 1) 계약상 필수 요구사항의 검증 추적성 누락: 감리 개선판정 대상이 되는 강한 사례
    # 2) 표지 날짜 표기 형식 혼재: 감리 개선판정을 강제할 근거가 약한 경미 사례
    issues = (
        RuleIssue(
            rule_code="REQ-018",
            rule_name="양방향 추적성 점검",
            category="요구사항 정합성",
            severity="Medium",
            file_path="validation_required.xlsx",
            line_number=12,
            evidence=(
                "계약상 필수 요구사항 REQ-101의 통합테스트 시나리오 ID가 누락되어 "
                "해당 요구사항의 검증 여부를 추적할 수 없다."
            ),
            description="필수 요구사항의 양방향 추적정보가 누락되어 검증 근거를 확인할 수 없다.",
        ),
        RuleIssue(
            rule_code="AUD-005",
            rule_name="문서 간 용어 일관성 점검",
            category="감리 사전점검",
            severity="Low",
            file_path="validation_minor.hwp",
            line_number=3,
            evidence="문서 표지의 날짜 표기가 '2026.10.01'과 '2026-10-01' 형식으로 혼재한다.",
            description="문서 표지 날짜의 표기 형식이 일부 일치하지 않는다.",
        ),
    )

    runtime = get_local_ai_runtime()
    runtime.start()
    provider = LlamaCppAIProvider(LocalAISettings(base_url=runtime.base_url))
    assessor = LocalAIIssueAssessor(provider)

    try:
        started = time.perf_counter()
        judgments = assessor.judge_audit_many(issues, batch_size=2)
        print(f"[ISSUES] {len(issues)}")
        for issue, judgment in zip(issues, judgments):
            if judgment is None:
                print(f"{issue.rule_code}: audit=None")
                continue
            print(
                f"{issue.rule_code}: "
                f"Recommendation={judgment.recommendation_type.value}, "
                f"Timing={judgment.improvement_timing.value}, "
                f"Important={judgment.important.value}"
            )
        print(f"[ELAPSED] {time.perf_counter() - started:.2f}s")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
