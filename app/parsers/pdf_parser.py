from pathlib import Path

from pypdf import PdfReader

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class PdfParser(BaseDocumentParser):
    """
    텍스트 기반 PDF에서 페이지별 텍스트를 추출한다.
    """

    supported_extensions = (".pdf",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        if not self.supports(path):
            raise ValueError(f"PDF 파일이 아닙니다: {path.name}")

        reader = PdfReader(path)
        blocks: list[DocumentBlock] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            if not text:
                continue

            blocks.append(
                DocumentBlock(
                    block_type="page",
                    text=text,
                    page=page_number,
                    location=f"{page_number}페이지",
                    metadata={
                        "page_number": page_number,
                    },
                )
            )

        return ParsedDocument(
            file_path=path,
            file_type="pdf",
            blocks=tuple(blocks),
            metadata={
                "page_count": len(reader.pages),
            },
        )