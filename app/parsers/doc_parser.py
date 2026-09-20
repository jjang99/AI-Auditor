from pathlib import Path

from legacy_doc import extract_text

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class DocParser(BaseDocumentParser):
    """Word 97-2003 DOC 문서에서 본문 텍스트를 추출한다."""

    supported_extensions = (".doc",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"파일을 찾을 수 없습니다: {path}"
            )

        if not self.supports(path):
            raise ValueError(
                f"DOC 파일이 아닙니다: {path.name}"
            )

        document_bytes = path.read_bytes()

        try:
            result = extract_text(document_bytes)
        except Exception as exc:
            raise ValueError(
                f"DOC 문서를 읽을 수 없습니다: {path.name}"
            ) from exc

        blocks: list[DocumentBlock] = []

        for paragraph_index, text in enumerate(
            result.text.splitlines(),
            start=1,
        ):
            text = text.strip()

            if not text:
                continue

            blocks.append(
                DocumentBlock(
                    block_type="paragraph",
                    text=text,
                    location=f"문단 {paragraph_index}",
                    metadata={
                        "paragraph": paragraph_index,
                    },
                )
            )

        return ParsedDocument(
            file_path=path,
            file_type="doc",
            blocks=tuple(blocks),
            metadata={
                "parser": result.parser,
                "parser_version": result.version,
                "warnings": tuple(result.warnings),
            },
        )