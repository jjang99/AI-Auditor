from unittest.mock import patch

import pytest

from rules.core.issue_assessor import apply_issue_assessments
from rules.core.models import RuleIssue
from rules.core.severity import AssessmentLevel, AuditImportantFlag, AuditRecommendationType, IssueSeverity
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAIProviderError


def _issue():
    return RuleIssue(
        rule_code="REQ-017",
        rule_name="요구사항 추적성 점검",
        category="요구사항 정합성",
        severity="Low",
        file_path="요구사항추적표.xlsx",
        line_number=1,
        evidence="REQ-017 요구사항 ID를 요구사항추적표에서 확인할 수 없다.",
        description="요구사항이 후속 단계까지 추적되었는지 확인하기 어렵다.",
    )


def test_local_ai_issue_assessor_parses_valid_assessment():
    provider = LlamaCppAIProvider()
    assessor = LocalAIIssueAssessor(provider)

    raw = (
        '{"impact":"Medium","likelihood":"High",'
        '"impact_reason":"추적성 확인에 영향을 준다.",'
        '"likelihood_reason":"현재 추적표에서 ID 누락이 확인된다."}'
    )
    with patch.object(provider, "_complete", return_value=raw):
        assessment = assessor.assess(_issue())

    assert assessment.impact == AssessmentLevel.MEDIUM
    assert assessment.likelihood == AssessmentLevel.HIGH
    assert assessment.impact_reason == "추적성 확인에 영향을 준다."
    assert assessment.severity == IssueSeverity.LOW


def test_matrix_overrides_assessor_placeholder_severity():
    provider = LlamaCppAIProvider()
    assessor = LocalAIIssueAssessor(provider)

    raw = (
        '{"assessments":[{'
        '"impact":"High","likelihood":"High",'
        '"impact_reason":"핵심 통제에 중대한 영향이 있다.",'
        '"likelihood_reason":"현재 영향 징후가 확인된다."'
        '}]}'
    )
    with patch.object(provider, "_complete", return_value=raw):
        result = apply_issue_assessments([_issue()], assessor)

    assert result[0].assessment.severity == IssueSeverity.CRITICAL
    assert result[0].severity == "Critical"
    assert (
        result[0].assessment.severity_reason
        == "Impact High × Likelihood High = Severity Critical"
    )


@pytest.mark.parametrize(
    "raw",
    [
        "not-json",
        '{"impact":"High"}',
        '{"impact":"Critical","likelihood":"High","impact_reason":"근거","likelihood_reason":"근거"}',
        '{"impact":"High","likelihood":"High","impact_reason":"","likelihood_reason":"근거"}',
    ],
)
def test_local_ai_issue_assessor_rejects_invalid_output(raw):
    provider = LlamaCppAIProvider()
    assessor = LocalAIIssueAssessor(provider)

    with patch.object(provider, "_complete", return_value=raw):
        with pytest.raises(LocalAIProviderError):
            assessor.assess(_issue())


def test_assessment_prompt_forbids_keyword_only_high_and_invention():
    prompt = LocalAIIssueAssessor._build_prompt(_issue())

    assert "입력에 없는 사실" in prompt
    assert "확인된 사실과 잠재적 영향" in prompt
    assert "단어가 있다는 이유만으로 High" in prompt
    assert '"impact":"Low|Medium|High"' in prompt


def test_batch_prompt_defines_likelihood_as_unresolved_impact_risk():
    prompt = LocalAIIssueAssessor._build_batch_prompt((_issue(),))

    assert "Issue 자체가 존재하거나 다시 발생할 가능성이 아니라" in prompt
    assert "조치하지 않고 그대로 둘 때" in prompt
    assert "다시 나타날 수 있다는 이유만으로 Likelihood를 High" in prompt
    assert "방치 시 후속 영향 가능성" in prompt


def test_issue_assessor_uses_assessment_json_schema():
    response_format = LocalAIIssueAssessor._assessment_response_format()
    schema = response_format["json_schema"]["schema"]

    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    assert schema["properties"]["impact"]["enum"] == ["Low", "Medium", "High"]
    assert schema["properties"]["likelihood"]["enum"] == ["Low", "Medium", "High"]
    assert set(schema["required"]) == {
        "impact",
        "likelihood",
        "impact_reason",
        "likelihood_reason",
    }
    assert schema["additionalProperties"] is False


def test_audit_prompt_uses_official_improvement_judgment_definitions():
    prompt = LocalAIIssueAssessor._build_audit_batch_prompt((_issue(),))

    assert "사업목표를 달성하기 위하여 반드시 개선" in prompt
    assert "발주기관과 피감리인이 상호 협의를 거쳐 반영 여부" in prompt
    assert "감리 대상범위를 벗어나지만 사업목표 달성에 도움이" in prompt
    assert "해당 구축단계 종료 이전" in prompt
    assert "장기적인 관점에서 지속적으로 개선" in prompt
    assert "필수 또는 협의" in prompt
    assert "권고에는 중요 O를 부여하지" in prompt


def test_audit_recommended_judgment_cannot_be_marked_important():
    provider = LlamaCppAIProvider()
    assessor = LocalAIIssueAssessor(provider)
    raw = (
        '{"judgments":[{'
        '"applicable":true,'
        '"recommendation_type":"권고",'
        '"improvement_timing":"장기",'
        '"important":"O"'
        '}]}'
    )

    with patch.object(provider, "_complete", return_value=raw):
        judgment = assessor.judge_audit_many((_issue(),))[0]

    assert judgment.recommendation_type == AuditRecommendationType.RECOMMENDED
    assert judgment.important == AuditImportantFlag.NO
