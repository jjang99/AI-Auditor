from pathlib import Path

from openpyxl import load_workbook

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class XlsxParser(BaseDocumentParser):
    """
    XLSX 문서에서 시트별 셀 내용을 행 단위로 추출한다.
    """

    supported_extensions = (".xlsx",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        if not self.supports(path):
            raise ValueError(f"XLSX 파일이 아닙니다: {path.name}")

        workbook = load_workbook(
            filename=path,
            read_only=True,
            data_only=True,
        )

        blocks: list[DocumentBlock] = []

        try:
            for worksheet in workbook.worksheets:
                for row_index, row in enumerate(
                    worksheet.iter_rows(values_only=True),
                    start=1,
                ):
                    cell_values = tuple(
                        "" if value is None else str(value).strip()
                        for value in row
                    )
                    values = [
                        value
                        for value in cell_values
                        if value
                    ]

                    if not values:
                        continue

                    blocks.append(
                        DocumentBlock(
                            block_type="sheet_row",
                            text=" | ".join(values),
                            sheet=worksheet.title,
                            location=f"{worksheet.title} / 행 {row_index}",
                            metadata={
                                "sheet_name": worksheet.title,
                                "row_index": row_index,
                                "cell_values": cell_values,
                            },
                        )
                    )

            return ParsedDocument(
                file_path=path,
                file_type="xlsx",
                blocks=tuple(blocks),
                metadata={
                    "sheet_count": len(workbook.sheetnames),
                    "sheet_names": tuple(workbook.sheetnames),
                },
            )

        finally:
            workbook.close()