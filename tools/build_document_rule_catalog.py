from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "RULE_DESIGN.md"
TARGET_PATH = ROOT / "rules" / "definitions" / "document_rule_catalog.py"

EXPECTED_COUNTS = {
    "AUD": 24,
    "REQ": 28,
    "CHG": 18,
    "FP": 12,
    "AI": 23,
}

CATEGORY_NAMES = {
    "AUD": "감리 사전점검",
    "REQ": "요구사항 정합성",
    "CHG": "변경영향도",
    "FP": "FP 검증",
    "AI": "AI 특화 검증",
}

VALID_EXECUTION_TYPES = {"Rule", "AI", "Hybrid"}

START_MARKER = "# === GENERATED DOCUMENT RULE DETAILS START ==="
END_MARKER = "# === GENERATED DOCUMENT RULE DETAILS END ==="


def parse_rule_design():
    if not SOURCE_PATH.exists():
        raise RuntimeError(f"원본 문서를 찾을 수 없습니다: {SOURCE_PATH}")

    text = SOURCE_PATH.read_text(encoding="utf-8")

    pattern = re.compile(
        r"^\|\s*"
        r"((?:AUD|REQ|CHG|FP|AI)-\d{3})"
        r"\s*\|\s*([^|]+?)"
        r"\s*\|\s*([^|]+?)"
        r"\s*\|\s*(Rule|AI|Hybrid)"
        r"\s*\|$",
        re.MULTILINE,
    )

    rules = []

    for match in pattern.finditer(text):
        code, name, description, execution_type = (
            value.strip() for value in match.groups()
        )

        category_code = code.split("-", 1)[0]

        rules.append(
            {
                "code": code,
                "name": name,
                "category_code": category_code,
                "category": CATEGORY_NAMES[category_code],
                "description": description,
                "execution_type": execution_type,
            }
        )

    return rules


def validate_rules(rules):
    if len(rules) != 105:
        raise RuntimeError(
            f"검사기준 수 오류: 예상 105개 / 실제 {len(rules)}개"
        )

    codes = [rule["code"] for rule in rules]

    if len(codes) != len(set(codes)):
        duplicates = sorted(
            code for code in set(codes) if codes.count(code) > 1
        )
        raise RuntimeError(
            f"중복 Rule ID 발견: {', '.join(duplicates)}"
        )

    for category_code, expected_count in EXPECTED_COUNTS.items():
        category_rules = [
            rule
            for rule in rules
            if rule["category_code"] == category_code
        ]

        if len(category_rules) != expected_count:
            raise RuntimeError(
                f"{category_code} 수량 오류: "
                f"예상 {expected_count}개 / 실제 {len(category_rules)}개"
            )

        expected_codes = [
            f"{category_code}-{number:03d}"
            for number in range(1, expected_count + 1)
        ]
        actual_codes = [rule["code"] for rule in category_rules]

        if actual_codes != expected_codes:
            missing = sorted(set(expected_codes) - set(actual_codes))
            unexpected = sorted(set(actual_codes) - set(expected_codes))

            raise RuntimeError(
                f"{category_code} ID 연속성 오류\n"
                f"누락: {missing or '없음'}\n"
                f"예상 외 ID: {unexpected or '없음'}"
            )

    for rule in rules:
        if rule["execution_type"] not in VALID_EXECUTION_TYPES:
            raise RuntimeError(
                f"{rule['code']} 실행방식 오류: "
                f"{rule['execution_type']}"
            )

        if not rule["name"]:
            raise RuntimeError(f"{rule['code']} 규칙명이 비어 있습니다.")

        if not rule["description"]:
            raise RuntimeError(f"{rule['code']} 설명이 비어 있습니다.")


def build_generated_block(rules):
    lines = [
        "",
        "",
        START_MARKER,
        "",
        "",
        "@dataclass(frozen=True)",
        "class DocumentRuleCatalogItem:",
        "    code: str",
        "    name: str",
        "    category_code: str",
        "    category: str",
        "    description: str",
        "    execution_type: str",
        "",
        "",
        "DOCUMENT_RULES = (",
    ]

    for rule in rules:
        lines.extend(
            [
                "    DocumentRuleCatalogItem(",
                f"        code={rule['code']!r},",
                f"        name={rule['name']!r},",
                f"        category_code={rule['category_code']!r},",
                f"        category={rule['category']!r},",
                f"        description={rule['description']!r},",
                f"        execution_type={rule['execution_type']!r},",
                "    ),",
            ]
        )

    lines.extend(
        [
            ")",
            "",
            "",
            "def get_document_rules():",
            '    """제품 전체 105개 문서 검사기준을 반환한다."""',
            "    return DOCUMENT_RULES",
            "",
            "",
            "def get_document_rules_by_category(category_code):",
            '    """영역 코드에 해당하는 문서 검사기준을 반환한다."""',
            "    return tuple(",
            "        rule",
            "        for rule in DOCUMENT_RULES",
            "        if rule.category_code == category_code",
            "    )",
            "",
            "",
            "def get_document_rule(code):",
            '    """Rule 코드에 해당하는 검사기준 하나를 반환한다."""',
            "    for rule in DOCUMENT_RULES:",
            "        if rule.code == code:",
            "            return rule",
            "    return None",
            "",
            END_MARKER,
            "",
        ]
    )

    return "\n".join(lines)


def update_catalog(rules):
    if not TARGET_PATH.exists():
        raise RuntimeError(f"대상 파일을 찾을 수 없습니다: {TARGET_PATH}")

    current = TARGET_PATH.read_text(encoding="utf-8")

    if START_MARKER in current or END_MARKER in current:
        raise RuntimeError(
            "이미 105개 상세 Catalog가 생성되어 있습니다. "
            "중복 생성을 중단합니다."
        )

    generated = build_generated_block(rules)

    TARGET_PATH.write_text(
        current.rstrip() + generated,
        encoding="utf-8",
    )


def main():
    print("[1/3] RULE_DESIGN.md에서 검사기준을 읽습니다.")
    rules = parse_rule_design()

    print(f"[2/3] 추출된 검사기준: {len(rules)}개")
    validate_rules(rules)

    print("      AUD: 24")
    print("      REQ: 28")
    print("      CHG: 18")
    print("      FP : 12")
    print("      AI : 23")
    print("      합계: 105")
    print("      중복/누락/ID 연속성: 정상")

    print("[3/3] document_rule_catalog.py를 갱신합니다.")
    update_catalog(rules)

    print()
    print("완료: 105개 상세 Rule Catalog 생성 성공")


if __name__ == "__main__":
    main()