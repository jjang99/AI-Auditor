import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from app.parsers.base import BaseDocumentParser
from app.parsers.models import DocumentBlock, ParsedDocument


class HwpxParser(BaseDocumentParser):
    """
    HWPX 문서 내부의 section XML에서 문단 텍스트를 추출한다.
    """

    supported_extensions = (".hwpx",)

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

        if not self.supports(path):
            raise ValueError(f"HWPX 파일이 아닙니다: {path.name}")

        blocks: list[DocumentBlock] = []

        try:
            with zipfile.ZipFile(path, "r") as archive:
                section_names = [
                    name
                    for name in archive.namelist()
                    if re.fullmatch(
                        r"Contents/section\d+\.xml",
                        name,
                        flags=re.IGNORECASE,
                    )
                ]

                section_names.sort(
                    key=lambda name: int(
                        re.search(r"section(\d+)", name, re.IGNORECASE).group(1)
                    )
                )

                for section_index, section_name in enumerate(
                    section_names,
                    start=1,
                ):
                    xml_data = archive.read(section_name)
                    root = ElementTree.fromstring(xml_data)

                    paragraph_index = 0

                    for element in root.iter():
                        if self._local_name(element.tag) != "p":
                            continue

                        texts = [
                            node.text
                            for node in element.iter()
                            if self._local_name(node.tag) == "t"
                            and node.text
                        ]

                        text = "".join(texts).strip()

                        if not text:
                            continue

                        paragraph_index += 1

                        blocks.append(
                            DocumentBlock(
                                block_type="paragraph",
                                text=text,
                                location=(
                                    f"섹션 {section_index} "
                                    f"/ 문단 {paragraph_index}"
                                ),
                                metadata={
                                    "section_index": section_index,
                                    "paragraph_index": paragraph_index,
                                },
                            )
                        )

        except zipfile.BadZipFile as exc:
            raise ValueError(
                f"올바른 HWPX 파일이 아닙니다: {path.name}"
            ) from exc

        return ParsedDocument(
            file_path=path,
            file_type="hwpx",
            blocks=tuple(blocks),
            metadata={
                "section_count": len(section_names),
            },
        )

    @staticmethod
    def _local_name(tag: str) -> str:
        """
        XML Namespace를 제거하고 실제 태그 이름만 반환한다.
        """
        return tag.rsplit("}", 1)[-1]