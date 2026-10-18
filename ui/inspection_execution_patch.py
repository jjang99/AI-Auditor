import math
import threading
import time
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtWidgets import QLabel, QPushButton

from app.database.repositories.inspection_repository import save_inspection_result
from app.services.inspection_service import InspectionService
from app.services.local_ai_runtime import get_local_ai_runtime
from rules.core.engine import InspectionCancelled
from rules.core.models import RuleExecutionType
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from rules.providers.local_ai_provider import LlamaCppAIProvider
import ui.inspection_runtime as inspection_runtime


def _estimate_inspection_seconds(file_paths, rules):
    file_count = len(file_paths)
    rule_count = len(rules)
    if file_count == 0 or rule_count == 0:
        return 0

    ai_like_count = sum(
        1
        for rule in rules
        if getattr(rule, "execution_type", None)
        in {RuleExecutionType.AI, RuleExecutionType.HYBRID}
    )
    deterministic_count = max(0, rule_count - ai_like_count)

    total_bytes = 0
    for raw_path in file_paths:
        path = Path(raw_path)
        try:
            if path.is_file():
                total_bytes += path.stat().st_size
        except OSError:
            pass

    total_mb = total_bytes / (1024 * 1024)
    seconds = (
        15
        + deterministic_count * 0.5
        + ai_like_count * file_count * 4.0
        + min(90.0, total_mb * 1.5)
        + (25 if ai_like_count else 0)
    )
    return max(20, int(math.ceil(seconds)))


def _format_summary_duration(seconds):
    if seconds <= 0:
        return "-"
    if seconds < 60:
        rounded = max(10, int(round(seconds / 10.0) * 10))
        return f"약 {rounded}초"
    minutes = max(1, int(round(seconds / 60.0)))
    return f"약 {minutes}분"


def _format_remaining_duration(seconds):
    if seconds <= 0:
        return "마무리 중"
    seconds = int(math.ceil(seconds))
    if seconds < 60:
        return f"약 {seconds}초"
    minutes, remain = divmod(seconds, 60)
    if remain < 10:
        return f"약 {minutes}분"
    remain = int(round(remain / 10.0) * 10)
    if remain >= 60:
        minutes += 1
        remain = 0
    return f"약 {minutes}분 {remain}초" if remain else f"약 {minutes}분"


class _ExecutionTracker:
    def __init__(self, rules, callback):
        self.rules = tuple(rules)
        self.callback = callback
        self.total = len(self.rules)
        self.completed_codes = set()
        self._rule_codes = {rule.code for rule in self.rules}
        self._deterministic_codes = {
            rule.code
            for rule in self.rules
            if getattr(rule, "execution_type", None) == RuleExecutionType.RULE
        }
        self._ai_started = False

    def _emit(self, current):
        self.callback(
            min(len(self.completed_codes), self.total),
            self.total,
            current,
        )

    def phase(self, text):
        self._emit(text)

    def rule_started(self, rule):
        if not self._ai_started:
            self.completed_codes.update(self._deterministic_codes)
            self._ai_started = True
        self._emit(f"{rule.code} {rule.name}")

    def rule_finished(self, rule):
        if rule.code in self._rule_codes:
            self.completed_codes.add(rule.code)
        self._emit(f"{rule.code} {rule.name}")

    def complete(self):
        self.completed_codes.update(self._rule_codes)
        self._emit("검사 결과 저장")


class _ProgressLlamaCppAIProvider(LlamaCppAIProvider):
    def __init__(self, tracker, cancel_requested):
        super().__init__()
        self._tracker = tracker
        self._cancel_requested = cancel_requested

    def _raise_if_cancelled(self):
        if self._cancel_requested():
            raise InspectionCancelled("검사가 취소되었습니다.")

    def _complete(self, *args, **kwargs):
        self._raise_if_cancelled()
        try:
            result = super()._complete(*args, **kwargs)
        except Exception:
            if self._cancel_requested():
                raise InspectionCancelled("검사가 취소되었습니다.")
            raise
        self._raise_if_cancelled()
        return result

    def inspect(self, document, rule, context=None):
        self._raise_if_cancelled()
        self._tracker.rule_started(rule)
        result = super().inspect(document, rule, context)
        self._raise_if_cancelled()
        self._tracker.rule_finished(rule)
        return result


class _ProgressIssueAssessor(LocalAIIssueAssessor):
    def __init__(self, provider, tracker):
        super().__init__(provider)
        self._tracker = tracker

    def assess(self, issue):
        self._tracker.phase("Impact / Likelihood 판정 중")
        return super().assess(issue)

    def assess_many(self, issues, batch_size=2):
        self._tracker.phase("Impact / Likelihood 판정 중")
        # Local AI 호출 수를 줄여 후처리 시간을 단축한다.
        return super().assess_many(issues, batch_size=max(4, batch_size))

    def judge_audit_many(self, issues, batch_size=2):
        self._tracker.phase("감리 개선판정 중")
        # Impact/Likelihood와 동일하게 소규모 묶음 단위를 키워 호출 수를 줄인다.
        return super().judge_audit_many(issues, batch_size=max(4, batch_size))


class InspectionExecutionWorker(QObject):
    finished = Signal(object, object, float)
    failed = Signal(str)
    cancelled = Signal()
    progress = Signal(int, int, str)

    def __init__(
        self,
        file_paths,
        project_id,
        inspection_type,
        rules,
        use_local_ai=False,
    ):
        super().__init__()
        self.file_paths = list(file_paths)
        self.project_id = project_id
        self.inspection_type = inspection_type
        self.rules = list(rules)
        self.use_local_ai = use_local_ai
        self._cancel_requested = False
        self._cancel_runtime_thread = None
        self._tracker = _ExecutionTracker(self.rules, self.progress.emit)

    def request_cancel(self):
        if self._cancel_requested:
            return

        self._cancel_requested = True

        # UI 스레드에서 LocalAIRuntimeManager.stop()을 직접 호출하면
        # process.wait() 동안 창이 '응답 없음'으로 보일 수 있다.
        # 별도 daemon thread에서 llama.cpp를 종료해 UI는 즉시 반응하게 한다.
        runtime = get_local_ai_runtime()
        self._cancel_runtime_thread = threading.Thread(
            target=runtime.stop,
            name="ai-auditor-cancel-local-ai",
            daemon=True,
        )
        self._cancel_runtime_thread.start()

    def is_cancel_requested(self):
        return self._cancel_requested

    def _raise_if_cancelled(self):
        if self._cancel_requested:
            raise InspectionCancelled("검사가 취소되었습니다.")

    def run(self):
        started = time.perf_counter()
        try:
            self._tracker.phase("문서 준비 및 기본 Rule 검사")
            self._raise_if_cancelled()

            if self.use_local_ai:
                runtime = get_local_ai_runtime()
                runtime.start()
                self._raise_if_cancelled()
                ai_provider = _ProgressLlamaCppAIProvider(
                    self._tracker,
                    self.is_cancel_requested,
                )
                issue_assessor = _ProgressIssueAssessor(
                    ai_provider,
                    self._tracker,
                )
                service = InspectionService(
                    rules=self.rules,
                    ai_provider=ai_provider,
                    issue_assessor=issue_assessor,
                )
            else:
                service = InspectionService(rules=self.rules)

            _inspection_id, summary = service.run(
                self.file_paths,
                project_id=None,
                inspection_type=self.inspection_type,
                cancel_requested=self.is_cancel_requested,
            )
            self._raise_if_cancelled()
            self._tracker.complete()

            inspection_id = None
            if self.project_id is not None:
                inspection_id = save_inspection_result(
                    project_id=self.project_id,
                    summary=summary,
                    inspection_type=self.inspection_type,
                )

            self._raise_if_cancelled()
            self.finished.emit(
                inspection_id,
                summary,
                time.perf_counter() - started,
            )
        except InspectionCancelled:
            self.cancelled.emit()
        except Exception as exc:
            if self._cancel_requested:
                self.cancelled.emit()
            else:
                self.failed.emit(str(exc))


def apply_inspection_execution_patch(InspectionPage):
    if getattr(InspectionPage, "_execution_patch_applied", False):
        return

    inspection_runtime.InspectionWorker = InspectionExecutionWorker

    original_init = InspectionPage.__init__
    original_refresh_rule_summary = InspectionPage._refresh_rule_summary
    original_start = InspectionPage.start_real_inspection
    original_success = InspectionPage._inspection_succeeded
    original_cancelled = InspectionPage._inspection_cancelled
    original_failed = InspectionPage._inspection_failed

    def update_estimate_summary(self):
        rules = list(self._selected_executable_rules())
        estimate = _estimate_inspection_seconds(
            getattr(self, "selected_files", []),
            rules,
        )
        self._inspection_estimated_seconds = estimate

        values = self.findChildren(QLabel, "inspectionSummaryValue")
        details = self.findChildren(QLabel, "inspectionSummaryDetail")
        if len(values) > 2:
            values[2].setText(_format_summary_duration(estimate))
        if len(details) > 2:
            details[2].setText(
                "(Local AI 기준 추정)" if estimate else "(파일 등록 후 계산)"
            )

    def patched_init(self):
        original_init(self)
        self._inspection_started_at = None
        self._inspection_estimated_seconds = 0
        self._inspection_completed_rules = 0
        self._inspection_total_rules = 0
        self._inspection_postprocessing = False

        percent = getattr(self, "runtime_progress_percent", None)
        if percent is not None:
            percent.hide()
            percent.setMinimumWidth(0)
            percent.setMaximumWidth(0)

        bar = getattr(self, "runtime_progress_bar", None)
        if bar is not None:
            bar.setRange(0, 100)
            bar.setValue(0)

        self._execution_progress_timer = QTimer(self)
        self._execution_progress_timer.setInterval(500)
        self._execution_progress_timer.timeout.connect(
            self._tick_execution_progress
        )
        update_estimate_summary(self)

    def patched_refresh_rule_summary(self):
        original_refresh_rule_summary(self)
        update_estimate_summary(self)

    def set_progress_state(self, status):
        total = len(self._selected_executable_rules())
        self._inspection_completed_rules = 0
        self._inspection_total_rules = total
        self._inspection_postprocessing = False

        self.runtime_progress_bar.setRange(0, 100)
        self.runtime_progress_bar.setValue(0)
        self.runtime_progress_count.setText(f"0 / {total}개")
        self.runtime_progress_rule.setText("검사 준비 중")
        self.runtime_progress_time.setText(
            _format_remaining_duration(
                getattr(self, "_inspection_estimated_seconds", 0)
            )
        )
        self.runtime_progress_status.setText(status)

    def on_execution_progress(self, completed, total, current):
        self._inspection_completed_rules = completed
        self._inspection_total_rules = total
        self.runtime_progress_count.setText(f"{completed} / {total}개")
        if current:
            self.runtime_progress_rule.setText(current)

        postprocessing_markers = (
            "검사 규칙 실행 완료",
            "Impact / Likelihood",
            "감리 개선판정",
            "검사 결과 저장",
        )
        self._inspection_postprocessing = (
            completed >= total
            and any(marker in (current or "") for marker in postprocessing_markers)
        )
        if self._inspection_postprocessing:
            self.runtime_progress_status.setText("결과 판정 중")
            self.runtime_progress_time.setText("AI 후처리 중")

        self._tick_execution_progress()

    def tick_execution_progress(self):
        if self._inspection_started_at is None:
            return

        elapsed = max(0.0, time.perf_counter() - self._inspection_started_at)
        estimate = max(
            1.0,
            float(getattr(self, "_inspection_estimated_seconds", 0) or 1),
        )
        total = max(1, self._inspection_total_rules)
        completed = min(self._inspection_completed_rules, total)

        if getattr(self, "_inspection_postprocessing", False):
            self.runtime_progress_bar.setRange(0, 100)
            self.runtime_progress_bar.setValue(95)
            self.runtime_progress_time.setText("AI 후처리 중")
            return

        time_percent = min(90.0, (elapsed / estimate) * 90.0)
        rule_percent = min(95.0, (completed / total) * 100.0)
        percent = int(max(time_percent, rule_percent))

        self.runtime_progress_bar.setRange(0, 100)
        self.runtime_progress_bar.setValue(percent)
        remaining = estimate - elapsed
        self.runtime_progress_time.setText(
            _format_remaining_duration(remaining)
            if remaining > 0
            else "예상시간 초과"
        )

    def patched_start_real_inspection(self):
        rules = list(self._selected_executable_rules())
        self._inspection_estimated_seconds = _estimate_inspection_seconds(
            getattr(self, "selected_files", []),
            rules,
        )
        self._inspection_started_at = time.perf_counter()
        self._inspection_completed_rules = 0
        self._inspection_total_rules = len(rules)
        self._inspection_postprocessing = False

        original_start(self)

        worker = getattr(self, "_inspection_worker", None)
        if worker is None:
            self._inspection_started_at = None
            return

        # Monkey-patched Python callbacks can otherwise be invoked in the worker
        # thread on some PySide6/Qt builds. Force all UI mutations onto the GUI
        # thread to avoid recursive repaint/timer-thread violations.
        for signal, slot in (
            (worker.finished, self._inspection_succeeded),
            (worker.failed, self._inspection_failed),
            (worker.cancelled, self._inspection_cancelled),
        ):
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass
            signal.connect(slot, Qt.ConnectionType.QueuedConnection)

        if hasattr(worker, "progress"):
            worker.progress.connect(
                self._on_execution_progress,
                Qt.ConnectionType.QueuedConnection,
            )

        self._execution_progress_timer.start()
        self._tick_execution_progress()

    def patched_cancel_real_inspection(self):
        worker = getattr(self, "_inspection_worker", None)
        thread = getattr(self, "_inspection_thread", None)
        if worker is None or thread is None:
            return

        self.runtime_progress_status.setText("검사 취소 중")
        self.runtime_progress_rule.setText("현재 작업 중단 중")

        button = self.progress_card.findChild(
            QPushButton,
            "inspectionCancelButton",
        )
        if button is not None:
            button.setEnabled(False)
            button.setText("취소 중...")

        worker.request_cancel()

    def reset_execution_ui(self):
        self._execution_progress_timer.stop()
        self._inspection_started_at = None
        self._inspection_postprocessing = False
        button = self.progress_card.findChild(
            QPushButton,
            "inspectionCancelButton",
        )
        if button is not None:
            button.setEnabled(True)
            button.setText("검사 취소")

    def patched_success(self, inspection_id, summary, elapsed):
        self.runtime_progress_bar.setRange(0, 100)
        self.runtime_progress_bar.setValue(100)
        self.runtime_progress_count.setText(
            f"{summary.rule_count} / {summary.rule_count}개"
        )
        reset_execution_ui(self)
        original_success(self, inspection_id, summary, elapsed)

    def patched_cancelled(self):
        reset_execution_ui(self)
        original_cancelled(self)

    def patched_failed(self, message):
        reset_execution_ui(self)
        original_failed(self, message)

    InspectionPage.__init__ = patched_init
    InspectionPage._refresh_rule_summary = patched_refresh_rule_summary
    InspectionPage._set_progress_state = set_progress_state
    InspectionPage._on_execution_progress = on_execution_progress
    InspectionPage._tick_execution_progress = tick_execution_progress
    InspectionPage.start_real_inspection = patched_start_real_inspection
    InspectionPage.cancel_real_inspection = patched_cancel_real_inspection
    InspectionPage._inspection_succeeded = patched_success
    InspectionPage._inspection_cancelled = patched_cancelled
    InspectionPage._inspection_failed = patched_failed
    InspectionPage._execution_patch_applied = True
