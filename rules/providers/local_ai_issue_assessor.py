import json

from rules.core.issue_assessor import BaseIssueAssessor
from rules.core.models import RuleIssue
from rules.core.severity import (
    AssessmentLevel,
    IssueAssessment,
    IssueSeverity,
)
from rules.providers.local_ai_provider import (
    LlamaCppAIProvider,
    LocalAIProviderError,
)


class LocalAIIssueAssessor(BaseIssueAssessor):
    """발견된 Issue의 Impact/Likelihood만 로컬 AI로 평가한다."""

    def __init__(self, provider: LlamaCppAIProvider | None = None):
        self.provider = provider or LlamaCppAIProvider()

    def assess(self, issue: RuleIssue) -> IssueAssessment:
        raw_response = self.provider._complete(
            self._build_prompt(issue),
            response_format=self._assessment_response_format(),
        )
        payload = self._parse_assessment(raw_response)

        impact = AssessmentLevel(payload["impact"])
        likelihood = AssessmentLevel(payload["likelihood"])

        return IssueAssessment(
            impact=impact,
            impact_reason=payload["impact_reason"],
            likelihood=likelihood,
            likelihood_reason=payload["likelihood_reason"],
            # 최종 Severity는 apply_issue_assessments()의 Matrix가 반드시 재계산한다.
            severity=IssueSeverity.LOW,
            severity_reason="Impact × Likelihood Matrix로 최종 Severity를 계산한다.",
        )

    @staticmethod
    def _assessment_response_format() -> dict:
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "issue_assessment",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "impact": {"type": "string", "enum": ["Low", "Medium", "High"]},
                        "likelihood": {"type": "string", "enum": ["Low", "Medium", "High"]},
                        "impact_reason": {"type": "string"},
                        "likelihood_reason": {"type": "string"},
                    },
                    "required": [
                        "impact",
                        "likelihood",
                        "impact_reason",
                        "likelihood_reason",
                    ],
                    "additionalProperties": False,
                },
            },
        }

    @staticmethod
    def _build_prompt(issue: RuleIssue) -> str:
        return (
            "당신은 정보시스템 프로젝트 품질점검 보조 AI입니다.\n"
            "다음 지적사항만을 근거로 Impact와 Likelihood를 평가하세요.\n"
            "입력에 없는 사실은 추측하거나 실제 발생한 것으로 만들지 마세요.\n"
            "확인된 사실과 잠재적 영향을 구분하세요.\n"
            "단순히 '추적성', '보안' 같은 단어가 있다는 이유만으로 High를 선택하지 마세요.\n\n"
            "[Impact 기준]\n"
            "Low = 국소적 문서/표현 수준의 문제이며 핵심 기능·통제·검증 영향 근거가 없음\n"
            "Medium = 품질·관리·검증에 영향이 있으나 범위가 제한적이거나 핵심 기능 영향이 확인되지 않음\n"
            "High = 핵심 기능·접근통제/보안·중요 검증 또는 여러 단계/범위에 중대한 영향이 있다는 근거가 있음\n\n"
            "[Likelihood 기준]\n"
            "Low = 현재 부정적 영향의 징후가 없고 영향 현실화에 추가 조건이 필요함\n"
            "Medium = 후속 단계에서 영향이 현실화될 가능성이 있으나 직접적인 징후가 없거나 근거가 부분적임\n"
            "High = 현재 상태로 진행하면 부정적 영향이 현실화될 가능성이 높거나 이미 그 징후가 확인됨\n\n"
            f"[Rule] {issue.rule_code} {issue.rule_name}\n"
            f"[Category] {issue.category}\n"
            f"[Description] {issue.description}\n"
            f"[Evidence] {issue.evidence}\n"
            f"[File] {issue.file_path}\n\n"
            "반드시 아래 네 필드만 가진 JSON 객체 하나만 출력하세요.\n"
            '{"impact":"Low|Medium|High",'
            '"likelihood":"Low|Medium|High",'
            '"impact_reason":"입력에 근거한 한국어 한 문장",'
            '"likelihood_reason":"입력에 근거한 한국어 한 문장"}'
        )

    @staticmethod
    def _parse_assessment(raw_response: str) -> dict[str, str]:
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise LocalAIProviderError("Issue 판정 응답이 유효한 JSON이 아닙니다.") from exc

        required = {
            "impact",
            "likelihood",
            "impact_reason",
            "likelihood_reason",
        }
        if not isinstance(payload, dict) or set(payload) != required:
            raise LocalAIProviderError("Issue 판정 JSON 필드가 올바르지 않습니다.")

        allowed = {level.value for level in AssessmentLevel}
        if payload["impact"] not in allowed or payload["likelihood"] not in allowed:
            raise LocalAIProviderError("Impact/Likelihood는 Low/Medium/High만 허용됩니다.")

        for key in ("impact_reason", "likelihood_reason"):
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise LocalAIProviderError("Issue 판정근거는 비어 있지 않은 문자열이어야 합니다.")
            payload[key] = payload[key].strip()

        return payload
