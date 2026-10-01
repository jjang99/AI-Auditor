from unittest.mock import patch

from app.services.inspection_service import InspectionService
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from rules.providers.local_ai_provider import LlamaCppAIProvider
from ui.inspection_runtime import InspectionWorker


def test_worker_keeps_deferred_path_when_local_ai_disabled():
    worker = InspectionWorker([], None, "전체 검사", [], use_local_ai=False)
    assert worker.use_local_ai is False


def test_worker_builds_shared_local_provider_and_assessor():
    captured = {}

    class StopHere(Exception):
        pass

    def fake_service(*args, **kwargs):
        captured.update(kwargs)
        raise StopHere

    worker = InspectionWorker([], None, "전체 검사", [], use_local_ai=True)

    failed_messages = []
    worker.failed.connect(failed_messages.append)

    with patch("ui.inspection_runtime.get_local_ai_runtime") as get_runtime, patch(
        "ui.inspection_runtime.InspectionService", side_effect=fake_service
    ):
        worker.run()

    get_runtime.assert_called_once()
    get_runtime.return_value.start.assert_called_once()

    assert failed_messages

    provider = captured["ai_provider"]
    assessor = captured["issue_assessor"]

    assert isinstance(provider, LlamaCppAIProvider)
    assert isinstance(assessor, LocalAIIssueAssessor)
    assert assessor.provider is provider
