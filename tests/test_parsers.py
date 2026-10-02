from pathlib import Path

import pytest
import zipfile
import xlwt
from docx import Document
from pptx import Presentation
from pypdf import PdfWriter
from openpyxl import Workbook

from app.parsers import get_parser, get_supported_extensions, parse_document
from app.parsers.docx_parser import DocxParser
from app.parsers.doc_parser import DocParser
from app.parsers.hwpx_parser import HwpxParser
from app.parsers.hwp_parser import HwpParser
from app.parsers.pdf_parser import PdfParser
from app.parsers.pptx_parser import PptxParser
from app.parsers.ppt_parser import PptParser
from app.parsers.xlsx_parser import XlsxParser
from app.parsers.xls_parser import XlsParser


def test_supported_extensions():
    assert get_supported_extensions() == (
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".pdf",
        ".pptx",
        ".ppt",
        ".hwpx",
        ".hwp",
    )


@pytest.mark.parametrize(
    ("file_name", "parser_type"),
    [
    ("sample.docx", DocxParser),
    ("sample.doc", DocParser),
    ("sample.xlsx", XlsxParser),
    ("sample.xls", XlsParser),
    ("sample.pdf", PdfParser),
    ("sample.pptx", PptxParser),
    ("sample.hwpx", HwpxParser),
    ("sample.hwp", HwpParser),
    ],
)
def test_parser_is_selected_by_extension(
    file_name: str,
    parser_type: type,
):
    parser = get_parser(Path(file_name))

    assert isinstance(parser, parser_type)


def test_unsupported_extension_raises_error():
    with pytest.raises(
        ValueError,
        match="지원하지 않는 문서 형식",
    ):
        get_parser("sample.exe")
        from docx import Document
from openpyxl import Workbook

from app.parsers import parse_document


def test_docx_parser_extracts_paragraph_and_table(tmp_path: Path):
    file_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("AI Auditor 요구사항")

    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "REQ-001"
    table.cell(0, 1).text = "로그인 기능"

    document.save(file_path)

    result = parse_document(file_path)

    assert result.file_type == "docx"
    assert "AI Auditor 요구사항" in result.text
    assert "REQ-001 | 로그인 기능" in result.text
    assert result.block_count == 2


def test_xlsx_parser_extracts_multiple_sheets(tmp_path: Path):
    file_path = tmp_path / "sample.xlsx"

    workbook = Workbook()

    requirements_sheet = workbook.active
    requirements_sheet.title = "요구사항"
    requirements_sheet.append(["요구사항 ID", "요구사항명"])
    requirements_sheet.append(["REQ-001", "로그인 기능"])

    change_sheet = workbook.create_sheet("변경관리")
    change_sheet.append(["변경 ID", "변경내용"])
    change_sheet.append(["CHG-001", "로그인 정책 변경"])

    workbook.save(file_path)
    workbook.close()

    result = parse_document(file_path)

    assert result.file_type == "xlsx"
    assert result.metadata["sheet_count"] == 2
    assert "REQ-001 | 로그인 기능" in result.text
    assert "CHG-001 | 로그인 정책 변경" in result.text


def test_xlsx_parser_preserves_empty_cell_positions(tmp_path: Path):
    file_path = tmp_path / "positions.xlsx"

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "요구사항"
    worksheet.append(["요구사항 ID", "요구사항명", "화면 ID", "프로그램 ID"])
    worksheet.append(["REQ-001", "로그인 기능", None, "PRG-001"])
    workbook.save(file_path)
    workbook.close()

    result = parse_document(file_path)
    data_block = result.blocks[1]

    assert data_block.text == "REQ-001 | 로그인 기능 | PRG-001"
    assert data_block.metadata["cell_values"] == (
        "REQ-001",
        "로그인 기능",
        "",
        "PRG-001",
    )
def test_pptx_parser_extracts_slide_text_and_table(tmp_path: Path):
    file_path = tmp_path / "sample.pptx"

    presentation = Presentation()

    slide = presentation.slides.add_slide(
        presentation.slide_layouts[5]
    )

    title = slide.shapes.title
    title.text = "AI Auditor 검사 결과"

    table_shape = slide.shapes.add_table(
        rows=2,
        cols=2,
        left=0,
        top=0,
        width=5000000,
        height=1000000,
    )

    table = table_shape.table
    table.cell(0, 0).text = "요구사항 ID"
    table.cell(0, 1).text = "상태"
    table.cell(1, 0).text = "REQ-001"
    table.cell(1, 1).text = "정상"

    presentation.save(file_path)

    result = parse_document(file_path)

    assert result.file_type == "pptx"
    assert result.metadata["slide_count"] == 1
    assert "AI Auditor 검사 결과" in result.text
    assert "요구사항 ID | 상태" in result.text
    assert "REQ-001 | 정상" in result.text
def test_pdf_parser_handles_empty_page(tmp_path: Path):
    file_path = tmp_path / "sample.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)

    with open(file_path, "wb") as pdf_file:
        writer.write(pdf_file)

    result = parse_document(file_path)

    assert result.file_type == "pdf"
    assert result.metadata["page_count"] == 1
    assert result.block_count == 0
    assert result.is_empty is True

def test_hwpx_parser_extracts_paragraph_text(tmp_path: Path):
    file_path = tmp_path / "sample.hwpx"

    section_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <hs:sec
        xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"
        xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
        <hp:p>
            <hp:run>
                <hp:t>AI Auditor HWPX 테스트</hp:t>
            </hp:run>
        </hp:p>
        <hp:p>
            <hp:run>
                <hp:t>REQ-001 요구사항 검증</hp:t>
            </hp:run>
        </hp:p>
    </hs:sec>
    """

    with zipfile.ZipFile(file_path, "w") as archive:
        archive.writestr(
            "Contents/section0.xml",
            section_xml.encode("utf-8"),
        )

    result = parse_document(file_path)

    assert result.file_type == "hwpx"
    assert result.metadata["section_count"] == 1
    assert result.block_count == 2
    assert "AI Auditor HWPX 테스트" in result.text
    assert "REQ-001 요구사항 검증" in result.text

def test_xls_parser_extracts_sheet_rows(tmp_path: Path):
    file_path = tmp_path / "sample.xls"

    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet("요구사항")

    data = [
        ["요구사항 ID", "요구사항명", "상태"],
        ["REQ-001", "로그인 기능", "완료"],
        ["REQ-002", "사용자 조회", "진행"],
    ]

    for row_index, row in enumerate(data):
        for column_index, value in enumerate(row):
            worksheet.write(
                row_index,
                column_index,
                value,
            )

    workbook.save(str(file_path))

    result = parse_document(file_path)

    assert result.file_type == "xls"
    assert result.metadata["sheet_count"] == 1
    assert result.metadata["sheet_names"] == ("요구사항",)
    assert result.block_count == 3
    assert "요구사항 ID | 요구사항명 | 상태" in result.text
    assert "REQ-001 | 로그인 기능 | 완료" in result.text
    assert "REQ-002 | 사용자 조회 | 진행" in result.text

def test_hwp_parser_extracts_paragraph_text():
    parser = HwpParser()

    paragraph_text = (
        "捤獥 汤捯 AI Auditor HWP 테스트"
    )

    paragraph_data = paragraph_text.encode(
        "utf-16le"
    )

    record_header = (
        HwpParser.PARA_TEXT_TAG_ID
        | (len(paragraph_data) << 20)
    )

    record_data = (
        record_header.to_bytes(
            4,
            byteorder="little",
        )
        + paragraph_data
    )

    texts = parser._extract_paragraph_texts(
        record_data
    )

    assert texts == [
        "AI Auditor HWP 테스트"
    ]

def test_doc_parser_converts_extracted_text(
    tmp_path: Path,
    monkeypatch,
):
    file_path = tmp_path / "sample.doc"
    file_path.write_bytes(b"dummy doc data")

    class FakeResult:
        text = (
            "AI Auditor DOC 테스트\n"
            "요구사항 ID: REQ-001\n"
            "요구사항명: 로그인 기능\n"
            "상태: 완료"
        )
        parser = "legacy-doc"
        version = "0.2.1"
        warnings = ()

    monkeypatch.setattr(
        "app.parsers.doc_parser.extract_text",
        lambda document_bytes: FakeResult(),
    )

    result = DocParser().parse(file_path)

    assert result.file_type == "doc"
    assert result.metadata["parser"] == "legacy-doc"
    assert result.metadata["parser_version"] == "0.2.1"
    assert result.block_count == 4
    assert "AI Auditor DOC 테스트" in result.text
    assert "요구사항 ID: REQ-001" in result.text
    assert "요구사항명: 로그인 기능" in result.text
    assert "상태: 완료" in result.text

def test_get_parser_selects_ppt_parser():
    parser = get_parser("sample.ppt")

    assert isinstance(parser, PptParser)
    assert ".ppt" in get_supported_extensions()


def test_ppt_parser_converts_and_extracts_text(tmp_path, monkeypatch):
    source_path = tmp_path / "sample.ppt"
    source_path.write_bytes(b"fake-ppt")

    def fake_convert(source, destination):
        presentation = Presentation()
        slide = presentation.slides.add_slide(
            presentation.slide_layouts[6]
        )

        text_box = slide.shapes.add_textbox(
            0, 0, 1000000, 1000000
        )
        text_box.text = (
            "AI Auditor PPT 테스트\n"
            "요구사항 ID: REQ-001\n"
            "요구사항명: 로그인 기능\n"
            "상태: 완료"
        )

        presentation.save(destination)

        class FakeReport:
            warnings = []

        class FakeResult:
            slide_count = 1
            report = FakeReport()

        return FakeResult()

    monkeypatch.setattr(
        "app.parsers.ppt_parser.convert",
        fake_convert,
    )

    result = PptParser().parse(source_path)

    assert result.file_type == "ppt"
    assert result.metadata["converter"] == "ppt2pptx"
    assert result.metadata["slide_count"] == 1
    assert "AI Auditor PPT 테스트" in result.text
    assert "REQ-001" in result.text
    assert "로그인 기능" in result.text

def test_hwp_parser_skips_inline_control_payload():
    parser = HwpParser()

    def control(code: int, payload: str) -> bytes:
        payload_bytes = payload.encode("utf-16le")
        payload_bytes = payload_bytes[:12].ljust(12, b"\\x00")
        return (
            code.to_bytes(2, "little")
            + payload_bytes
            + code.to_bytes(2, "little")
        )

    paragraph_data = (
        "문서번호 : ".encode("utf-16le")
        + control(0x0002, "浲╳")
        + "SAIF3-AD-R0403-01 ".encode("utf-16le")
        + control(0x0002, "浲ࡳ")
    )

    assert parser._clean_paragraph_text(paragraph_data) == (
        "문서번호 : SAIF3-AD-R0403-01"
    )


def test_hwp_parser_preserves_normal_hanja():
    parser = HwpParser()

    paragraph_data = "행정(行政) 요구사항 SFR-001".encode("utf-16le")

    assert parser._clean_paragraph_text(paragraph_data) == (
        "행정(行政) 요구사항 SFR-001"
    )
