from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import get_connection
from app.parsers.parser_factory import parse_document

ID_PATTERN = re.compile(
    r"\b(?:REQ-\d+|(?:UI-)?[A-Z]{2,}-\d+-ID-\d+(?:-\d+)*)\b",
    re.IGNORECASE,
)
SOURCE_PATTERN = re.compile(
    r"(?i)^(.+?\.(?:hwp|hwpx|docx?|xlsx?|xls|pdf|pptx?|ppt))(?::\d+)?$"
)
DUP_PATTERN = re.compile(r"중복 요구사항 ID:\s*(\S+)", re.IGNORECASE)


def _compact(text: str, limit: int = 150) -> str:
    value = " ".join(str(text or "").split())
    return value if len(value) <= limit else value[: limit - 3] + "..."


def _source_path(evidence: str) -> Path | None:
    source = str(evidence or "").split(" | ", 1)[0].strip()
    match = SOURCE_PATTERN.match(source)
    return Path(match.group(1)) if match else None


def main() -> None:
    connection = get_connection()
    latest = connection.execute(
        """
        SELECT id, inspected_at, total_issues
        FROM inspections
        ORDER BY inspected_at DESC, id DESC
        LIMIT 1
        """
    ).fetchone()
    if latest is None:
        print("[LATEST INSPECTION] none")
        connection.close()
        return

    rows = connection.execute(
        """
        SELECT id, evidence
        FROM issues
        WHERE inspection_id = ? AND rule_code = 'REQ-001'
        ORDER BY id ASC
        """,
        (latest["id"],),
    ).fetchall()
    connection.close()

    duplicate_ids: set[str] = set()
    sources: set[Path] = set()
    for row in rows:
        evidence = str(row["evidence"] or "")
        duplicate_match = DUP_PATTERN.search(evidence)
        if duplicate_match:
            duplicate_ids.add(duplicate_match.group(1).upper())
        source = _source_path(evidence)
        if source is not None:
            sources.add(source)

    print(
        f'[LATEST INSPECTION] id={latest["id"]} at={latest["inspected_at"]} '
        f'total_issues={latest["total_issues"]}'
    )
    print(f"[REQ-001 ROWS] {len(rows)}")
    print(f"[FLAGGED DUPLICATE IDS] {len(duplicate_ids)}")
    print(f"[SOURCE DOCUMENTS] {len(sources)}")

    if not duplicate_ids:
        print("No duplicate-ID REQ-001 findings in the latest inspection.")
        return

    for source in sorted(sources, key=lambda item: str(item).lower()):
        print(f"\n=== {source} ===")
        if not source.exists():
            print("  [MISSING FILE]")
            continue

        document = parse_document(source)
        occurrences: dict[str, list[tuple[int, object]]] = defaultdict(list)
        for index, block in enumerate(document.blocks, 1):
            for match in ID_PATTERN.findall(block.text or ""):
                normalized = match.upper()
                if normalized in duplicate_ids:
                    occurrences[normalized].append((index, block))

        source_ids = sorted(occurrences)
        print(f"[PARSED BLOCKS] {document.block_count}")
        print(f"[FLAGGED IDS FOUND HERE] {len(source_ids)}")

        for requirement_id in source_ids:
            found = occurrences[requirement_id]
            distinct_texts = {
                " ".join(str(block.text or "").split()).lower()
                for _, block in found
            }
            print(
                f"\n{requirement_id}: occurrences={len(found)}, "
                f"distinct_block_texts={len(distinct_texts)}"
            )
            for index, block in found[:4]:
                location_parts = [f"block={index}", f"type={block.block_type}"]
                if block.location:
                    location_parts.append(f"location={block.location}")
                if block.page is not None:
                    location_parts.append(f"page={block.page}")
                if block.sheet:
                    location_parts.append(f"sheet={block.sheet}")
                if block.slide is not None:
                    location_parts.append(f"slide={block.slide}")
                print(f"  - {', '.join(location_parts)}")
                print(f"    text: {_compact(block.text)}")
            if len(found) > 4:
                print(f"  ... {len(found) - 4} more occurrence(s)")


if __name__ == "__main__":
    main()
