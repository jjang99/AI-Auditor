from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.parsers.models import ParsedDocument
from rules.core.models import DocumentRule


@dataclass(frozen=True)
class AIInspectionResult:
    """AI 또는 Hybrid 검사 1회 실행 결과."""

    rule_code: str
    findings: tuple[str, ...]
    raw_response: str = ""
    execution_type: str = ""
    provider_name: str = ""


@dataclass(frozen=True)
class AIInspectionContext:
    """AI 검사에 전달할 추가 Context."""

    evidence: tuple[str, ...] = ()


class BaseAIProvider(ABC):
    """AI 검사기를 위한 공통 인터페이스."""

    def build_requirement_conflict_groups(
        self,
        evidence: tuple[str, ...],
    ) -> tuple[tuple[str, ...], ...]:
        """REQ-004용 의미 구조 그룹을 만든다.

        Provider가 의미 구조화를 지원하지 않으면 후보를 추정하지 않는다.
        """
        return ()

    @abstractmethod
    def inspect(
        self,
        document: ParsedDocument,
        rule: DocumentRule,
        context: AIInspectionContext | None = None,
    ) -> AIInspectionResult:
        """문서와 검사 Rule, 선택적 Context를 받아 AI 검사를 수행한다."""
        raise NotImplementedError