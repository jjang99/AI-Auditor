import re
import struct
import zlib
from pathlib import Path

import olefile

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class HwpParser(BaseDocumentParser):
    """HWP 5.x 문서에서 본문 텍스트를 추출한다."""

    supported_extensions = (".hwp",)

    PARA_TEXT_TAG_ID = 67

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"파일을 찾을 수 없습니다: {path}"
            )

        if not self.supports(path):
            raise ValueError(
                f"HWP 파일이 아닙니다: {path.name}"
            )

        if not olefile.isOleFile(path):
            raise ValueError(
                f"HWP 5.x OLE 문서가 아닙니다: {path.name}"
            )

        ole = olefile.OleFileIO(path)

        try:
            if not ole.exists("FileHeader"):
                raise ValueError(
                    f"HWP FileHeader가 없습니다: {path.name}"
                )

            header = ole.openstream("FileHeader").read()

            if not header.startswith(b"HWP Document File"):
                raise ValueError(
                    f"지원하지 않는 HWP 형식입니다: {path.name}"
                )

            flags = struct.unpack_from("<I", header, 36)[0]
            is_compressed = bool(flags & 1)

            section_names = self._get_section_names(ole)
            blocks: list[DocumentBlock] = []

            for section_index, section_name in enumerate(
                section_names,
                start=1,
            ):
                data = ole.openstream(section_name).read()

                if is_compressed:
                    data = zlib.decompress(data, -15)

                texts = self._extract_paragraph_texts(data)

                for paragraph_index, text in enumerate(
                    texts,
                    start=1,
                ):
                    blocks.append(
                        DocumentBlock(
                            block_type="paragraph",
                            text=text,
                            location=(
                                f"Section {section_index} / "
                                f"문단 {paragraph_index}"
                            ),
                            metadata={
                                "section": section_index,
                                "paragraph": paragraph_index,
                            },
                        )
                    )

            return ParsedDocument(
                file_path=path,
                file_type="hwp",
                blocks=tuple(blocks),
                metadata={
                    "section_count": len(section_names),
                    "compressed": is_compressed,
                    "format": "HWP 5.x",
                },
            )

        finally:
            ole.close()

    @staticmethod
    def _get_section_names(
        ole: olefile.OleFileIO,
    ) -> list[str]:
        sections = []

        for item in ole.listdir():
            if (
                len(item) == 2
                and item[0] == "BodyText"
                and item[1].startswith("Section")
            ):
                sections.append("/".join(item))

        def section_number(name: str) -> int:
            try:
                return int(name.split("Section")[-1])
            except ValueError:
                return 0

        return sorted(
            sections,
            key=section_number,
        )

    def _extract_paragraph_texts(
        self,
        data: bytes,
    ) -> list[str]:
        position = 0
        texts: list[str] = []

        while position + 4 <= len(data):
            record_header = struct.unpack_from(
                "<I",
                data,
                position,
            )[0]

            position += 4

            tag_id = record_header & 0x3FF
            size = (record_header >> 20) & 0xFFF

            if size == 0xFFF:
                if position + 4 > len(data):
                    break

                size = struct.unpack_from(
                    "<I",
                    data,
                    position,
                )[0]

                position += 4

            if position + size > len(data):
                break

            record_data = data[
                position:position + size
            ]

            position += size

            if tag_id != self.PARA_TEXT_TAG_ID:
                continue

            text = self._clean_paragraph_text(
                record_data
            )

            if text:
                texts.append(text)

        return texts

    @staticmethod
    def _clean_paragraph_text(
        data: bytes,
    ) -> str:
        text = data.decode(
            "utf-16le",
            errors="ignore",
        )

        # HWP 문단 내부 제어문자 제거
        text = re.sub(
            r"[\x00-\x1f]",
            " ",
            text,
        )

        # HWP 인라인 제어 데이터에서 발생하는
        # 문단 앞쪽의 비정상 제어 데이터 제거
        match = re.search(
            r"[A-Za-z0-9가-힣]",
            text,
        )

        if match:
            text = text[match.start():]

        return " ".join(text.split())