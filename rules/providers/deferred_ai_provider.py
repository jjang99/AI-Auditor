from rules.core.ai_provider import (
    AIInspectionResult,
    BaseAIProvider,
)


class DeferredAIProvider(BaseAIProvider):
    """
    실제 로컬 AI Provider 연결 전 사용하는 임시 Provider.

    AI/Hybrid 실행 경로는 유지하지만,
    실제 AI 판단을 수행하거나 가짜 지적사항을 생성하지 않는다.
    """

    def inspect(self, document, rule, context=None):
        return AIInspectionResult(
            rule_code=rule.code,
            findings=(),
            raw_response="",
        )