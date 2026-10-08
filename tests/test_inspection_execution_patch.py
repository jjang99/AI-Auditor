from types import SimpleNamespace
from unittest.mock import Mock, patch

from rules.core.models import RuleExecutionType
from ui.inspection_execution_patch import (
    InspectionExecutionWorker,
    _estimate_inspection_seconds,
    _format_remaining_duration,
    _format_summary_duration,
)


def _rule(execution_type):
    return SimpleNamespace(
        code=f"R-{execution_type.value}",
        name=execution_type.value,
        execution_type=execution_type,
    )


def test_estimate_requires_files_and_rules(tmp_path):
    assert _estimate_inspection_seconds([], [_rule(RuleExecutionType.AI)]) == 0
    sample = tmp_path / "sample.hwp"
    sample.write_bytes(b"x" * 1024)
    assert _estimate_inspection_seconds([str(sample)], []) == 0


def test_estimate_grows_with_local_ai_work(tmp_path):
    sample1 = tmp_path / "a.hwp"
    sample2 = tmp_path / "b.hwp"
    sample1.write_bytes(b"x" * 1024)
    sample2.write_bytes(b"x" * 1024)
    one = _estimate_inspection_seconds(
        [str(sample1)],
        [_rule(RuleExecutionType.RULE), _rule(RuleExecutionType.AI)],
    )
    more = _estimate_inspection_seconds(
        [str(sample1), str(sample2)],
        [
            _rule(RuleExecutionType.RULE),
            _rule(RuleExecutionType.AI),
            _rule(RuleExecutionType.HYBRID),
        ],
    )
    assert more > one > 0


def test_duration_formatting_is_user_facing():
    assert _format_summary_duration(0) == "-"
    assert "초" in _format_summary_duration(40)
    assert "분" in _format_summary_duration(150)
    assert _format_remaining_duration(0) == "마무리 중"
    assert "초" in _format_remaining_duration(25)


def test_cancel_marks_worker_and_stops_owned_local_runtime():
    worker = InspectionExecutionWorker([], None, "전체 검사", [], use_local_ai=True)
    runtime = Mock()
    with patch(
        "ui.inspection_execution_patch.get_local_ai_runtime",
        return_value=runtime,
    ):
        worker.request_cancel()
        assert worker._cancel_runtime_thread is not None
        worker._cancel_runtime_thread.join(timeout=1.0)
    assert worker.is_cancel_requested() is True
    runtime.stop.assert_called_once_with()
