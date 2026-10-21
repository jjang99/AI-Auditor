import time

from ui.inspection_execution_patch import _ExecutionTracker


def apply_inspection_progress_display_patch(InspectionPage):
    """Stabilize progress display without changing inspection execution.

    The worker's tracker remains the single source of truth. The GUI timer reads
    its latest snapshot every 500 ms, so transient queued signal timing cannot
    leave the count/current item stuck. The progress bar itself is time-based to
    avoid large jumps when a rule completes.
    """
    if getattr(InspectionPage, "_progress_display_patch_applied", False):
        return

    original_emit = _ExecutionTracker._emit

    def tracked_emit(self, current):
        self.current_text = current or getattr(self, "current_text", "검사 진행 중")
        self.completed_count = min(len(self.completed_codes), self.total)
        original_emit(self, current)

    _ExecutionTracker._emit = tracked_emit

    def tick_execution_progress(self):
        if self._inspection_started_at is None:
            return

        worker = getattr(self, "_inspection_worker", None)
        tracker = getattr(worker, "_tracker", None) if worker is not None else None

        if tracker is not None:
            completed = min(len(tracker.completed_codes), tracker.total)
            total = tracker.total
            current = getattr(tracker, "current_text", None)

            self._inspection_completed_rules = completed
            self._inspection_total_rules = total
            self.runtime_progress_count.setText(f"{completed} / {total}개")
            if current:
                self.runtime_progress_rule.setText(current)

        elapsed = max(0.0, time.perf_counter() - self._inspection_started_at)
        estimate = max(
            1.0,
            float(getattr(self, "_inspection_estimated_seconds", 0) or 1),
        )

        # Smooth time-based bar. Rule completion no longer causes 30~50% jumps.
        percent = int(min(95.0, (elapsed / estimate) * 95.0))
        self.runtime_progress_bar.setRange(0, 100)
        self.runtime_progress_bar.setValue(percent)
        self.runtime_progress_time.setText(
            self._format_progress_remaining(estimate - elapsed)
            if hasattr(self, "_format_progress_remaining")
            else _format_remaining(estimate - elapsed)
        )

    def _format_remaining(seconds):
        if seconds <= 0:
            return "마무리 중"
        seconds = int(seconds + 0.999)
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

    InspectionPage._tick_execution_progress = tick_execution_progress
    InspectionPage._progress_display_patch_applied = True
