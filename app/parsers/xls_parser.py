from pathlib import Path

import xlrd

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class XlsParser(BaseDocumentParser):
    """구형 XLS 문서에서 시트별 셀 내용을 행 단위로 추출한다."""

    supported_extensions = (".xls",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"파일을 찾을 수 없습니다: {path}"
            )

        if not self.supports(path):
            raise ValueError(
                f"XLS 파일이 아닙니다: {path.name}"
            )

        workbook = xlrd.open_workbook(path)
        blocks: list[DocumentBlock] = []

        for worksheet in workbook.sheets():
            for row_index in range(worksheet.nrows):
                values = []

                for column_index in range(worksheet.ncols):
                    cell = worksheet.cell(
                        row_index,
                        column_index,
                    )

                    value = self._format_cell_value(
                        cell,
                        workbook,
                    )

                    if value:
                        values.append(value)

                if not values:
                    continue

                blocks.append(
                    DocumentBlock(
                        block_type="sheet_row",
                        text=" | ".join(values),
                        sheet=worksheet.name,
                        location=(
                            f"{worksheet.name} / "
                            f"행 {row_index + 1}"
                        ),
                        metadata={
                            "sheet_name": worksheet.name,
                            "row_index": row_index + 1,
                        },
                    )
                )

        return ParsedDocument(
            file_path=path,
            file_type="xls",
            blocks=tuple(blocks),
            metadata={
                "sheet_count": workbook.nsheets,
                "sheet_names": tuple(workbook.sheet_names()),
            },
        )

    @staticmethod
    def _format_cell_value(
        cell,
        workbook,
    ) -> str:
        if cell.ctype in (
            xlrd.XL_CELL_EMPTY,
            xlrd.XL_CELL_BLANK,
        ):
            return ""

        if cell.ctype == xlrd.XL_CELL_DATE:
            value = xlrd.xldate_as_datetime(
                cell.value,
                workbook.datemode,
            )
            return value.isoformat(sep=" ")

        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            return "TRUE" if cell.value else "FALSE"

        if cell.ctype == xlrd.XL_CELL_NUMBER:
            number = cell.value

            if float(number).is_integer():
                return str(int(number))

            return str(number)

        return str(cell.value).strip()