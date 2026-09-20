from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DocumentBlock:
    """
    문서에서 추출한 하나의 내용 단위.

    예:
    - DOCX 문단
    - XLSX 셀/행
    - PDF 페이지 텍스트
    - PPTX 슬라이드 텍스트
    - HWPX 문단
    """
    block_type: str
    text: str
    page: int | None = None
    sheet: str | None = None
    slide: int | None = None
    location: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParsedDocument:
    """
    모든 문서 Parser가 공통으로 반환하는 표준 문서 구조.
    """
    file_path: Path
    file_type: str
    blocks: tuple[DocumentBlock, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        """문서 전체 텍스트를 하나로 합쳐 반환한다."""
        return "\n".join(
            block.text
            for block in self.blocks
            if block.text.strip()
        )

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    @property
    def is_empty(self) -> bool:
        return not bool(self.text.strip())