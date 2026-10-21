from PySide6.QtCore import Qt


def apply_inspection_thread_safety_patch(InspectionPage):
    """Force worker progress delivery onto the GUI thread.

    The execution patch connects worker.progress while the worker later runs on a
    QThread. Reconnecting explicitly with QueuedConnection prevents progress UI
    updates (including QTimer/progress-bar repaint work) from ever executing on
    the worker thread.
    """
    if getattr(InspectionPage, "_thread_safety_patch_applied", False):
        return

    original_start = InspectionPage.start_real_inspection

    def patched_start_real_inspection(self):
        original_start(self)

        worker = getattr(self, "_inspection_worker", None)
        if worker is None or not hasattr(worker, "progress"):
            return

        try:
            worker.progress.disconnect(self._on_execution_progress)
        except (RuntimeError, TypeError):
            pass

        worker.progress.connect(
            self._on_execution_progress,
            Qt.QueuedConnection,
        )

    InspectionPage.start_real_inspection = patched_start_real_inspection
    InspectionPage._thread_safety_patch_applied = True
