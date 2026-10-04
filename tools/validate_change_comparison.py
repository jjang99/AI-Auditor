from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.inspection_service import InspectionService, _find_version_pairs
from app.services.local_ai_runtime import get_local_ai_runtime
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings



def diagnose_chg012(paths):
    rules = tuple(
        rule for rule in get_document_mvp_rules()
        if rule.code in {"CHG-001"}
    )
    service = InspectionService(rules=rules)
    parsed = service.parse_documents(paths)
    pairs = _find_version_pairs(parsed)
    if len(pairs) != 1:
        raise SystemExit("[FAIL] exactly one explicit version pair was not identified")
    previous, current = pairs[0]
    test_documents = tuple(
        document for document in parsed
        if document not in {previous, current}
    )
    if not test_documents:
        raise SystemExit("[FAIL] test document was not identified")

    # CHG-001의 실 AI 결과를 재호출하지 않고, 이번 실문서에서 이미 확인된 변경근거를 사용한다.
    confirmed_changes = (
        "V1.0에서 V1.1로 버전업데이트됨",
        "SFR-043-ID-02 및 SFR-044-ID-01 등 요구사항 분리 및 취합됨",
        "이용기관·보유기관 서비스 이용현황 대시보드 기능 구현으로 기능 범위 확장됨",
        "수행방안 및 보안항목식별 내용이 삭제됨",
        "현재 문서에 '이용/제공현황 모니터링 기능, 기관 담당자에게 서비스 제공'이 추가됨.",
    )
    from app.parsers.models import DocumentBlock, ParsedDocument
    context = ParsedDocument(
        file_path=test_documents[0].file_path,
        file_type="change_test_comparison",
        blocks=tuple(
            [DocumentBlock(block_type="confirmed_change", text=item) for item in confirmed_changes]
            + [
                DocumentBlock(
                    block_type="test_document",
                    text=f"[시험 산출물] {document.file_path.name}\n{block.location or block.block_type} | {block.text}",
                )
                for document in test_documents
                for block in document.blocks
                if block.text and block.text.strip()
            ]
        ),
    )
    provider = LlamaCppAIProvider()
    print("[CHG-012 EVIDENCE DIAGNOSTICS]")
    for index, item in enumerate(provider.diagnose_change_test_evidence(context), 1):
        print(f"\n[{index}] CHANGE: {item['change']}")
        print(f"    IDS: {', '.join(item['requirement_ids']) or '-'}")
        print(f"    DELETION: {item['is_deletion']}")
        for row_index, row in enumerate(item["rows"], 1):
            print(f"    ROW {row_index}: {row}")


def main():
    if len(sys.argv) < 3:
        raise SystemExit(
            "usage: python tools/validate_change_comparison.py <previous> <current> [test_document ...]"
        )

    diagnose_only = "--diagnose-chg012" in sys.argv[1:]
    paths = tuple(Path(arg) for arg in sys.argv[1:] if arg != "--diagnose-chg012")
    if diagnose_only:
        diagnose_chg012(paths)
        return
    rules = tuple(
        rule for rule in get_document_mvp_rules()
        if rule.code in {"CHG-001", "CHG-006", "CHG-012"}
    )

    runtime = get_local_ai_runtime()
    runtime.start()
    provider = LlamaCppAIProvider(LocalAISettings(base_url=runtime.base_url))
    service = InspectionService(rules=rules, ai_provider=provider)

    try:
        parsed = service.parse_documents(paths)
        pairs = _find_version_pairs(parsed)
        print(f"[DOCUMENTS] {len(parsed)}")
        print(f"[VERSION PAIRS] {len(pairs)}")
        for previous, current in pairs:
            print(f"  previous: {previous.file_path.name}")
            print(f"  current : {current.file_path.name}")

        if len(pairs) != 1:
            raise SystemExit("[FAIL] exactly one explicit version pair was not identified")

        started = time.perf_counter()
        _inspection_id, summary = service.run(paths)
        for rule_code in ("CHG-001", "CHG-006", "CHG-012"):
            issues = tuple(
                issue for issue in summary.issues
                if issue.rule_code == rule_code
            )
            print(f"[{rule_code} ISSUES] {len(issues)}")
            for index, issue in enumerate(issues, 1):
                print(f"  [{index}] {issue.description}")
                print(f"      evidence: {issue.evidence}")
        print(f"[ELAPSED] {time.perf_counter() - started:.2f}s")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
