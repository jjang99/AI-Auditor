from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.parsers.parser_factory import parse_document


KNOWN_GARBAGE = (
    "捤獥",
    "汤捯",
    "浲",
    "漠杳",
    "錌",
    "蹔",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect extracted HWP text without running AI rules."
    )
    parser.add_argument("document", type=Path)
    parser.add_argument(
        "--limit",
        type=int,
        default=120,
        help="Number of non-empty extracted blocks to print.",
    )
    args = parser.parse_args()

    document = parse_document(args.document)

    print(f"[DOCUMENT] {args.document}")
    print(f"[PARSER] type={document.file_type}, blocks={document.block_count}")
    print(f"[METADATA] {document.metadata}")

    print("\n[EXTRACTED TEXT]")
    printed = 0
    for index, block in enumerate(document.blocks):
        text = block.text.strip()
        if not text:
            continue
        print(f"{index:05d}: {text}")
        printed += 1
        if printed >= args.limit:
            break

    suspicious = []
    for index, block in enumerate(document.blocks):
        text = block.text
        matched = tuple(token for token in KNOWN_GARBAGE if token in text)
        if matched:
            suspicious.append((index, matched, text))

    print("\n[KNOWN GARBAGE CHECK]")
    if suspicious:
        print(f"FOUND: {len(suspicious)} block(s)")
        for index, matched, text in suspicious[:50]:
            print(f"{index:05d}: tokens={','.join(matched)} | {text}")
    else:
        print("PASS: previously observed garbage tokens were not found.")


if __name__ == "__main__":
    main()
