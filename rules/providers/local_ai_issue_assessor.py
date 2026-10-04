import json

from rules.core.issue_assessor import BaseIssueAssessor
from rules.core.models import RuleIssue
from rules.core.severity import (
    AssessmentLevel,
    AuditImprovementJudgment,
    AuditImprovementTiming,
    AuditImportantFlag,
    AuditRecommendationType,
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

    def assess_many(
        self,
        issues: tuple[RuleIssue, ...],
        batch_size: int = 2,
    ) -> tuple[IssueAssessment | None, ...]:
        """여러 Issue를 소규모 배치로 평가해 로컬 AI 호출 횟수를 줄인다."""
        if not issues:
            return ()

        assessments = []
        for start in range(0, len(issues), batch_size):
            batch = issues[start:start + batch_size]
            raw_response = self.provider._complete(
                self._build_batch_prompt(batch),
                response_format=self._batch_response_format(len(batch)),
            )
            payload = self._parse_batch_assessment(raw_response, len(batch))
            for item in payload["assessments"]:
                assessments.append(
                    IssueAssessment(
                        impact=AssessmentLevel(item["impact"]),
                        impact_reason=item["impact_reason"].strip(),
                        likelihood=AssessmentLevel(item["likelihood"]),
                        likelihood_reason=item["likelihood_reason"].strip(),
                        severity=IssueSeverity.LOW,
                        severity_reason="Impact × Likelihood Matrix로 최종 Severity를 계산한다.",
                    )
                )

        return tuple(assessments)

    def judge_audit_many(
        self,
        issues: tuple[RuleIssue, ...],
        batch_size: int = 2,
    ) -> tuple[AuditImprovementJudgment | None, ...]:
        """감리 대응 관점의 개선판정을 Severity와 독립적으로 평가한다."""
        if not issues:
            return ()

        judgments = []
        for start in range(0, len(issues), batch_size):
            batch = issues[start:start + batch_size]
            raw_response = self.provider._complete(
                self._build_audit_batch_prompt(batch),
                response_format=self._audit_batch_response_format(len(batch)),
            )
            payload = json.loads(raw_response)
            items = payload.get("judgments", [])
            if len(items) != len(batch):
                raise LocalAIProviderError("감리 개선판정 결과 수가 올바르지 않습니다.")
            for item in items:
                if not item.get("applicable", False):
                    judgments.append(None)
                    continue
                recommendation_type = AuditRecommendationType(item["recommendation_type"])
                # 정보시스템 감리기준 제8조: 중요 표시는 필수/협의 중 중대한 사항에만 적용한다.
                important = AuditImportantFlag(item["important"])
                if recommendation_type == AuditRecommendationType.RECOMMENDED:
                    important = AuditImportantFlag.NO
                judgments.append(
                    AuditImprovementJudgment(
                        recommendation_type=recommendation_type,
                        improvement_timing=AuditImprovementTiming(item["improvement_timing"]),
                        important=important,
                    )
                )
        return tuple(judgments)

    @staticmethod
    def _build_audit_batch_prompt(issues: tuple[RuleIssue, ...]) -> str:
        items = "\n".join(
            (
                f"[{index}] Rule={issue.rule_code} {issue.rule_name}; "
                f"Category={issue.category}; Description={issue.description}; "
                f"Evidence={issue.evidence}"
            )
            for index, issue in enumerate(issues)
        )
        return (
            "당신은 정보시스템 감리 개선판정 보조 AI입니다.\n"
            "Severity와 감리 개선판정은 서로 독립적입니다. Severity를 근거로 자동 매핑하지 마세요.\n"
            "입력 Issue만 근거로 감리 대응 관점의 개선판정이 의미 있는지 먼저 판단하세요.\n"
            "의미가 없거나 근거가 부족하면 applicable=false로 반환하세요.\n"
            "[개선권고유형 - 정보시스템 감리기준 제8조]\n"
            "필수: 사업목표를 달성하기 위하여 반드시 개선하여야 할 사항.\n"
            "협의: 사업목표 달성을 위하여 개선하는 것이 바람직한 사항 중 발주기관과 피감리인이 "
            "상호 협의를 거쳐 반영 여부를 결정할 수 있는 사항.\n"
            "권고: 감리 대상범위를 벗어나지만 사업목표 달성에 도움이 되는 사항.\n"
            "[개선시점]\n"
            "단기: 해당 구축단계 종료 이전에 개선하여야 하는 사항.\n"
            "장기: 장기적인 관점에서 지속적으로 개선하여야 하는 사항.\n"
            "[중요 여부]\n"
            "O: 필수 또는 협의 사항 중 사업목표 달성에 영향을 미칠 수 있는 중대한 사항에만 부여.\n"
            "-: 그 밖의 경우. 권고에는 중요 O를 부여하지 마세요.\n"
            "각 Issue를 서로 독립적으로 판정하고 입력에 없는 사실은 추측하지 마세요. "
            "단순히 Issue가 발견되었다는 이유만으로 필수/단기/O를 선택하지 마세요.\n\n"
            f"{items}"
        )

    @staticmethod
    def _audit_batch_response_format(item_count: int) -> dict:
        item_schema = {
            "type": "object",
            "properties": {
                "applicable": {"type": "boolean"},
                "recommendation_type": {"type": "string", "enum": ["필수", "협의", "권고"]},
                "improvement_timing": {"type": "string", "enum": ["단기", "장기"]},
                "important": {"type": "string", "enum": ["O", "-"]},
            },
            "required": ["applicable", "recommendation_type", "improvement_timing", "important"],
            "additionalProperties": False,
        }
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "audit_improvement_judgments",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "judgments": {
                            "type": "array",
                            "minItems": item_count,
                            "maxItems": item_count,
                            "items": item_schema,
                        }
                    },
                    "required": ["judgments"],
                    "additionalProperties": False,
                },
            },
        }

    @staticmethod
    def _build_batch_prompt(issues: tuple[RuleIssue, ...]) -> str:
        items = "\n".join(
            (
                f"[{index}] Rule={issue.rule_code} {issue.rule_name}; "
                f"Category={issue.category}; Description={issue.description}; "
                f"Evidence={issue.evidence}; File={issue.file_path}"
            )
            for index, issue in enumerate(issues)
        )
        return (
            "당신은 정보시스템 프로젝트 품질점검 보조 AI입니다.\n"
            "각 지적사항을 서로 독립적으로 평가하고 입력에 없는 사실은 추측하지 마세요.\n"
            "Impact와 Likelihood만 Low/Medium/High로 평가합니다.\n"
            "Impact: Low=국소적 문서/표현 문제, Medium=품질·관리·검증 영향, "
            "High=핵심 기능·보안·중요 검증 또는 광범위한 중대 영향 근거가 있음.\n"
            "Likelihood는 Issue 자체가 존재하거나 다시 발생할 가능성이 아니라, "
            "발견된 Issue를 조치하지 않고 그대로 둘 때 그로 인한 부정적 영향이 현실화될 가능성입니다.\n"
            "Issue가 이미 발견되었다는 사실, 문제 표현이 문서에 존재한다는 사실, 또는 같은 표현이 "
            "다시 나타날 수 있다는 이유만으로 Likelihood를 High로 평가하지 마세요.\n"
            "Likelihood: Low=현재 부정적 영향의 징후가 없고 영향 현실화에 추가 조건이 필요함, "
            "Medium=방치 시 후속 영향 가능성이 있으나 직접적인 징후가 없거나 근거가 부분적임, "
            "High=방치한 현재 상태로 진행하면 부정적 영향이 현실화될 가능성이 높거나 이미 그 징후가 확인됨.\n"
            "입력 순서와 동일한 순서로 모든 항목을 빠짐없이 반환하세요.\n\n"
            f"{items}\n\n"
            "각 항목의 impact_reason과 likelihood_reason은 입력에 근거한 한국어 한 문장으로 작성하세요."
        )

    @staticmethod
    def _batch_response_format(item_count: int) -> dict:
        item_schema = {
            "type": "object",
            "properties": {
                "impact": {"type": "string", "enum": ["Low", "Medium", "High"]},
                "likelihood": {"type": "string", "enum": ["Low", "Medium", "High"]},
                "impact_reason": {"type": "string"},
                "likelihood_reason": {"type": "string"},
            },
            "required": ["impact", "likelihood", "impact_reason", "likelihood_reason"],
            "additionalProperties": False,
        }
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "issue_assessments",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "assessments": {
                            "type": "array",
                            "minItems": item_count,
                            "maxItems": item_count,
                            "items": item_schema,
                        }
                    },
                    "required": ["assessments"],
                    "additionalProperties": False,
                },
            },
        }

    @staticmethod
    def _parse_batch_assessment(raw_response: str, expected_count: int) -> dict:
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise LocalAIProviderError("Issue 일괄 판정 응답이 유효한 JSON이 아닙니다.") from exc

        if not isinstance(payload, dict) or set(payload) != {"assessments"}:
            raise LocalAIProviderError("Issue 일괄 판정 JSON 구조가 올바르지 않습니다.")

        items = payload["assessments"]
        if not isinstance(items, list) or len(items) != expected_count:
            raise LocalAIProviderError("Issue 일괄 판정 결과 수가 올바르지 않습니다.")

        required = {"impact", "likelihood", "impact_reason", "likelihood_reason"}
        allowed = {level.value for level in AssessmentLevel}
        for item in items:
            if not isinstance(item, dict) or set(item) != required:
                raise LocalAIProviderError("Issue 일괄 판정 필드가 올바르지 않습니다.")
            if item["impact"] not in allowed or item["likelihood"] not in allowed:
                raise LocalAIProviderError("Impact/Likelihood는 Low/Medium/High만 허용됩니다.")
            if not item["impact_reason"].strip() or not item["likelihood_reason"].strip():
                raise LocalAIProviderError("Issue 일괄 판정근거는 비어 있을 수 없습니다.")

        return payload

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
