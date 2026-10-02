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
        # PARA_TEXT의 인라인 제어 payload가 일반 문자로
        # 디코딩되어 깨진 문자열이 되지 않도록 먼저 건너뛴다.
        units = [
            struct.unpack_from("<H", data, offset)[0]
            for offset in range(0, len(data) - 1, 2)
        ]

        inline_control_codes = {
            0x0001, 0x0002, 0x0003, 0x0004,
            0x0005, 0x0006, 0x0007, 0x0008,
            0x000B, 0x000C,
            0x000E, 0x000F, 0x0010, 0x0011,
            0x0012, 0x0013, 0x0014, 0x0015,
            0x0016, 0x0017,
        }

        characters: list[str] = []
        index = 0

        while index < len(units):
            code = units[index]

            if code in inline_control_codes:
                # 인라인 제어문자는 총 8 UTF-16 code unit이다.
                index += 8
                characters.append(" ")
                continue

            if code < 0x0020:
                characters.append(" ")
                index += 1
                continue

            characters.append(chr(code))
            index += 1

        text = " ".join("".join(characters).split())

        # 기존 HWP prefix 정리 동작을 유지한다.
        match = re.search(r"[A-Za-z0-9가-힣]", text)
        if match:
            text = text[match.start():]

        return text
