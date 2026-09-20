from pathlib import Path

from pptx import Presentation

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class PptxParser(BaseDocumentParser):
    """
    PPTX 문서에서 슬라이드별 텍스트와 표 내용을 추출한다.
    """

    supported_extensions = (".pptx",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        if not self.supports(path):
            raise ValueError(f"PPTX 파일이 아닙니다: {path.name}")

        presentation = Presentation(path)
        blocks: list[DocumentBlock] = []

        for slide_number, slide in enumerate(
            presentation.slides,
            start=1,
        ):
            for shape_index, shape in enumerate(
                slide.shapes,
                start=1,
            ):
                # 일반 텍스트 영역
                if hasattr(shape, "text"):
                    text = shape.text.strip()

                    if text:
                        blocks.append(
                            DocumentBlock(
                                block_type="slide_text",
                                text=text,
                                slide=slide_number,
                                location=(
                                    f"슬라이드 {slide_number} "
                                    f"/ 개체 {shape_index}"
                                ),
                                metadata={
                                    "slide_number": slide_number,
                                    "shape_index": shape_index,
                                },
                            )
                        )

                # 표 영역
                if shape.has_table:
                    table = shape.table

                    for row_index, row in enumerate(
                        table.rows,
                        start=1,
                    ):
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
                                slide=slide_number,
                                location=(
                                    f"슬라이드 {slide_number} "
                                    f"/ 표 행 {row_index}"
                                ),
                                metadata={
                                    "slide_number": slide_number,
                                    "shape_index": shape_index,
                                    "row_index": row_index,
                                },
                            )
                        )

        return ParsedDocument(
            file_path=path,
            file_type="pptx",
            blocks=tuple(blocks),
            metadata={
                "slide_count": len(presentation.slides),
            },
        )