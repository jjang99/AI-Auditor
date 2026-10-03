from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.parsers.models import DocumentBlock, ParsedDocument
from app.services.local_ai_runtime import get_local_ai_runtime
from rules.definitions.document_mvp_rules import get_document_mvp_rules
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings


CONFIRMED_FINDINGS = (
    "CHG-001 | 변경사항 식별 점검 | SFR-043-ID-02 및 SFR-044-ID-01 등 요구사항 분리 및 취합됨",
    "CHG-001 | 변경사항 식별 점검 | 이용기관·보유기관 서비스 이용현황 대시보드 기능 구현으로 기능 범위 확장됨",
    "CHG-001 | 변경사항 식별 점검 | 수행방안 및 보안항목식별 내용이 삭제됨",
    "CHG-001 | 변경사항 식별 점검 | 현재 문서에 '이용/제공현황 모니터링 기능, 기관 담당자에게 서비스 제공'이 추가됨",
    "CHG-006 | 변경 영향대상 식별 | 이용기관·보유기관 서비스 이용현황 대시보드 기능 확장은 화면 영향 후보임",
    "CHG-012 | 관련 시험 변경 미반영 점검 | 이용기관·보유기관 서비스 이용현황 대시보드 기능이 시험항목에 반영되지 않은 후보",
)


def main():
    rule = next(
        rule for rule in get_document_mvp_rules()
        if rule.code == "CHG-018"
    )
    document = ParsedDocument(
        file_path=Path("chg-018-confirmed-findings.txt"),
        file_type="inspection_findings",
        blocks=tuple(
            DocumentBlock(block_type="inspection_finding", text=item)
            for item in CONFIRMED_FINDINGS
        ),
        metadata={"source": "confirmed_change_validation_results"},
    )

    runtime = get_local_ai_runtime()
    runtime.start()
    provider = LlamaCppAIProvider(LocalAISettings(base_url=runtime.base_url))
    try:
        started = time.perf_counter()
        result = provider.inspect(document, rule)
        print(f"[CHG-018 ISSUES] {len(result.findings)}")
        for index, finding in enumerate(result.findings, 1):
            print(f"  [{index}] {finding}")
        print(f"[ELAPSED] {time.perf_counter() - started:.2f}s")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
