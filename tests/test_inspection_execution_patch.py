from types import SimpleNamespace
import threading
from unittest.mock import Mock, patch

import pytest

from rules.core.models import RuleExecutionType
from ui.inspection_execution_patch import (
    InspectionExecutionWorker,
    _estimate_inspection_seconds,
    _format_remaining_duration,
    _format_summary_duration,
    _requires_local_ai,
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


def test_local_ai_requirement_follows_execution_type():
    assert _requires_local_ai([_rule(RuleExecutionType.RULE)]) is False
    assert _requires_local_ai(
        [_rule(RuleExecutionType.RULE), _rule(RuleExecutionType.AI)]
    ) is True
    assert _requires_local_ai([_rule(RuleExecutionType.HYBRID)]) is True


def test_rule_only_worker_disables_local_ai_even_when_caller_requests_it():
    worker = InspectionExecutionWorker(
        [],
        None,
        "전체 검사",
        [_rule(RuleExecutionType.RULE)],
        use_local_ai=True,
    )
    assert worker.use_local_ai is False


def test_ai_worker_keeps_local_ai_enabled():
    worker = InspectionExecutionWorker(
        [],
        None,
        "전체 검사",
        [_rule(RuleExecutionType.AI)],
        use_local_ai=True,
    )
    assert worker.use_local_ai is True


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


@pytest.mark.parametrize("outcome", ["finished", "failed", "cancelled"])
def test_runtime_queues_patched_callbacks_on_page_thread(monkeypatch, outcome):
    from PySide6.QtCore import QEventLoop, QThread, QTimer
    from PySide6.QtWidgets import QApplication, QFrame, QLabel, QLineEdit, QProgressBar, QWidget

    from rules.definitions.document_rule_registry import get_implemented_document_rules
    import ui.inspection_runtime as runtime

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    loop = QEventLoop()
    progress_delivered = threading.Event()
    records = []
    delivered_during_work = []
    rules = [
        rule for rule in get_implemented_document_rules()
        if rule.code in {"REQ-001", "REQ-003", "REQ-006"}
    ]
    summary = SimpleNamespace(rule_count=3)

    class ProbeWorker(InspectionExecutionWorker):
        def run(self):
            self.progress.emit(1, 3, "REQ-006")
            # A callback incorrectly queued on this worker cannot run until
            # run() returns. Require delivery while work is still in progress.
            delivered_during_work.append(progress_delivered.wait(timeout=1.0))
            if outcome == "finished":
                self.finished.emit(9, summary, 0.1)
            elif outcome == "failed":
                self.failed.emit("startup failed")
            else:
                self.cancelled.emit()

    class Page(QWidget):
        def create_progress_card(self):
            return QFrame(self)

        def create_complete_card(self):
            return QFrame(self)

    # Instantiate before applying the runtime so this transport test needs only
    # the widgets read by the production start_real_inspection method.
    page = Page()
    runtime.apply_inspection_runtime(Page)

    # These different function/attribute names reproduce the real patch chain.
    # Do not decorate them as Qt slots: the production callbacks are not slots.
    def progress_callback(self, completed, total, current):
        records.append(("progress", QThread.currentThread() == app.thread(),
                        completed, total, current))
        progress_delivered.set()

    def success_callback(self, inspection_id, result, elapsed):
        records.append(("finished", QThread.currentThread() == app.thread(),
                        inspection_id, result, elapsed))

    def failure_callback(self, message):
        records.append(("failed", QThread.currentThread() == app.thread(), message))

    def cancellation_callback(self):
        records.append(("cancelled", QThread.currentThread() == app.thread()))

    Page._on_execution_progress = progress_callback
    Page._inspection_succeeded = success_callback
    Page._inspection_failed = failure_callback
    Page._inspection_cancelled = cancellation_callback
    page.project_name = QLineEdit("signal delivery regression", page)
    page.selected_files = ["요구사항정의서.docx"]
    page.selected_rule_categories = {rule.category for rule in rules}
    page.existing_project_id = 1
    page.summary_card = QFrame(page)
    page.complete_card = QFrame(page)
    page.progress_card = QFrame(page)
    page.runtime_progress_bar = QProgressBar(page)
    for name in ("percent", "count", "rule", "time", "status"):
        setattr(page, f"runtime_progress_{name}", QLabel(page))

    monkeypatch.setattr(runtime, "InspectionWorker", ProbeWorker)
    monkeypatch.setattr(runtime, "get_default_rules", lambda: rules)
    monkeypatch.setattr(runtime, "get_project_by_name", lambda _name: {"id": 1})
    page.start_real_inspection()
    worker = page._inspection_worker
    thread = page._inspection_thread
    thread.finished.connect(loop.quit)
    watchdog = QTimer()
    watchdog.setSingleShot(True)
    watchdog.timeout.connect(loop.quit)
    watchdog.start(3000)
    try:
        loop.exec()
    finally:
        watchdog.stop()
        try:
            thread.quit()
            assert thread.wait(2000), "inspection thread did not stop"
        except RuntimeError:
            pass  # The production finished -> deleteLater connection ran.
        page.close()

    assert [rule.code for rule in worker.rules] == [rule.code for rule in rules]
    assert delivered_during_work == [True]
    assert [record[0] for record in records] == ["progress", outcome]
    assert all(record[1] for record in records), records
    assert records[0][2:] == (1, 3, "REQ-006")
    if outcome == "finished":
        assert records[1][2:] == (9, summary, 0.1)
    elif outcome == "failed":
        assert records[1][2:] == ("startup failed",)
