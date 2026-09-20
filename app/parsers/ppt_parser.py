from pathlib import Path
from tempfile import TemporaryDirectory

from ppt2pptx import convert

from app.parsers.base import BaseDocumentParser
from app.parsers.models import ParsedDocument
from app.parsers.pptx_parser import PptxParser


class PptParser(BaseDocumentParser):
    """PowerPoint 97-2003 PPT 문서를 PPTX로 변환한 뒤 내용을 추출한다."""

    supported_extensions = (".ppt",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        if not self.supports(path):
            raise ValueError(f"PPT 파일이 아닙니다: {path.name}")

        with TemporaryDirectory(prefix="ai_auditor_ppt_") as temp_dir:
            converted_path = Path(temp_dir) / f"{path.stem}.pptx"

            try:
                result = convert(path, converted_path)
            except Exception as exc:
                raise ValueError(
                    f"PPT 문서를 변환할 수 없습니다: {path.name}"
                ) from exc

            if not converted_path.is_file():
                raise ValueError(
                    f"PPT 변환 결과 파일이 생성되지 않았습니다: {path.name}"
                )

            parsed = PptxParser().parse(converted_path)

            return ParsedDocument(
                file_path=path,
                file_type="ppt",
                blocks=parsed.blocks,
                metadata={
                    **parsed.metadata,
                    "converted_from": "ppt",
                    "converter": "ppt2pptx",
                    "slide_count": result.slide_count,
                    "warnings": tuple(result.report.warnings),
                },
            )