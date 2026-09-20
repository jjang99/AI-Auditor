from pathlib import Path

from app.parsers.base import BaseDocumentParser
from app.parsers.docx_parser import DocxParser
from app.parsers.doc_parser import DocParser
from app.parsers.xlsx_parser import XlsxParser
from app.parsers.xls_parser import XlsParser
from app.parsers.pdf_parser import PdfParser
from app.parsers.pptx_parser import PptxParser
from app.parsers.ppt_parser import PptParser
from app.parsers.hwpx_parser import HwpxParser
from app.parsers.hwp_parser import HwpParser



PARSERS: tuple[BaseDocumentParser, ...] = (
    DocxParser(),
    DocParser(),
    XlsxParser(),
    XlsParser(),
    PdfParser(),
    PptxParser(),
    PptParser(),
    HwpxParser(),
    HwpParser(),
)


def get_parser(file_path: str | Path) -> BaseDocumentParser:
    """
    파일 확장자에 맞는 Parser를 자동으로 선택한다.
    """
    path = Path(file_path)

    for parser in PARSERS:
        if parser.supports(path):
            return parser

    raise ValueError(
        f"지원하지 않는 문서 형식입니다: {path.suffix.lower() or '확장자 없음'}"
    )


def parse_document(file_path: str | Path):
    """
    파일 형식에 맞는 Parser를 찾아 문서를 파싱한다.
    """
    parser = get_parser(file_path)
    return parser.parse(file_path)


def get_supported_extensions() -> tuple[str, ...]:
    """
    현재 지원하는 모든 문서 확장자를 반환한다.
    """
    return tuple(
        extension
        for parser in PARSERS
        for extension in parser.supported_extensions
    )