from PySide6.QtCore import Qt

import ui.inspection_runtime as inspection_runtime


_active_page = None


def apply_inspection_progress_preconnect_patch(InspectionPage):
    """Connect worker progress before QThread.start().

    inspection_runtime creates the worker and starts its QThread inside one
    method. Later execution/thread-safety patches connect progress only after
    that method returns, so early progress events can be missed. This patch
    attaches a queued GUI connection at worker construction time, before the
    thread starts. The existing thread-safety patch may reconnect it later; the
    queued connection is already present from the first emitted progress event.
    """
    if getattr(InspectionPage, "_progress_preconnect_patch_applied", False):
        return

    worker_cls = inspection_runtime.InspectionWorker
    original_worker_init = worker_cls.__init__
    original_start = InspectionPage.start_real_inspection

    def patched_worker_init(self, *args, **kwargs):
        original_worker_init(self, *args, **kwargs)
        page = _active_page
        if page is not None and hasattr(self, "progress"):
            self.progress.connect(
                page._on_execution_progress,
                Qt.QueuedConnection,
            )

    def patched_start(self):
        global _active_page
        _active_page = self
        try:
            return original_start(self)
        finally:
            _active_page = None

    worker_cls.__init__ = patched_worker_init
    InspectionPage.start_real_inspection = patched_start
    InspectionPage._progress_preconnect_patch_applied = True
