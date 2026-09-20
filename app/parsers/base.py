from abc import ABC, abstractmethod
from pathlib import Path

from app.parsers.models import ParsedDocument


class BaseDocumentParser(ABC):
    """
    모든 문서 Parser가 공통으로 따라야 하는 기본 인터페이스.
    """

    supported_extensions: tuple[str, ...] = ()

    def supports(self, file_path: str | Path) -> bool:
        """
        해당 Parser가 전달받은 파일 형식을 지원하는지 확인한다.
        """
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions

    @abstractmethod
    def parse(self, file_path: str | Path) -> ParsedDocument:
        """
        문서를 읽어 ParsedDocument 형식으로 반환한다.
        """
        raise NotImplementedError