import time

from app.database.repositories.inspection_repository import save_inspection_result
from app.services.inspection_service import InspectionService
from app.services.local_ai_runtime import get_local_ai_runtime
from rules.core.engine import InspectionCancelled
from ui.inspection_execution_patch import (
    InspectionExecutionWorker,
    _ProgressIssueAssessor,
    _ProgressLlamaCppAIProvider,
)
import ui.inspection_runtime as inspection_runtime


def format_inspection_error(exc):
    """Return a non-empty, user-facing diagnostic message for any exception."""
    error_type = type(exc).__name__ or "Exception"
    detail = str(exc).strip()
    if not detail:
        detail = "상세 오류 메시지가 제공되지 않았습니다."
    return f"오류 유형: {error_type}\n상세 내용: {detail}"


class DiagnosticInspectionExecutionWorker(InspectionExecutionWorker):
    """Execution worker that never emits an empty failure message."""

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
                self.failed.emit(format_inspection_error(exc))


def apply_inspection_error_patch(InspectionPage):
    """Install diagnostic execution and guarantee a visible fallback message."""
    inspection_runtime.InspectionWorker = DiagnosticInspectionExecutionWorker

    if getattr(InspectionPage, "_diagnostic_error_patch_applied", False):
        return

    original_failed = InspectionPage._inspection_failed

    def patched_failed(self, message):
        visible_message = (message or "").strip()
        if not visible_message:
            visible_message = (
                "오류 유형: UnknownError\n"
                "상세 내용: 검사 중 오류가 발생했지만 상세 메시지를 확인할 수 없습니다."
            )
        original_failed(self, visible_message)

    InspectionPage._inspection_failed = patched_failed
    InspectionPage._diagnostic_error_patch_applied = True
