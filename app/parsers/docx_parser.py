from pathlib import Path

from docx import Document

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class DocxParser(BaseDocumentParser):
    """
    DOCX 문서에서 문단과 표의 텍스트를 추출한다.
    """

    supported_extensions = (".docx",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        if not self.supports(path):
            raise ValueError(f"DOCX 파일이 아닙니다: {path.name}")

        document = Document(path)
        blocks: list[DocumentBlock] = []

        # 문단 추출
        for index, paragraph in enumerate(document.paragraphs, start=1):
            text = paragraph.text.strip()

            if not text:
                continue

            blocks.append(
                DocumentBlock(
                    block_type="paragraph",
                    text=text,
                    location=f"문단 {index}",
                    metadata={
                        "paragraph_index": index,
                    },
                )
            )

        # 표 추출
        for table_index, table in enumerate(document.tables, start=1):
            for row_index, row in enumerate(table.rows, start=1):
                cell_texts = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if not cell_texts:
                    continue

                blocks.append(
                    DocumentBlock(
                        block_type="table_row",
                        text=" | ".join(cell_texts),
                        location=f"표 {table_index} / 행 {row_index}",
                        metadata={
                            "table_index": table_index,
                            "row_index": row_index,
                        },
                    )
                )

        return ParsedDocument(
            file_path=path,
            file_type="docx",
            blocks=tuple(blocks),
            metadata={
                "paragraph_count": len(document.paragraphs),
                "table_count": len(document.tables),
            },
        )