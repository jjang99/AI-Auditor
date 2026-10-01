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

    with patch("ui.inspection_runtime.InspectionService", side_effect=fake_service):
        with patch.object(worker.failed, "emit"):
            worker.run()

    provider = captured["ai_provider"]
    assessor = captured["issue_assessor"]

    assert isinstance(provider, LlamaCppAIProvider)
    assert isinstance(assessor, LocalAIIssueAssessor)
    assert assessor.provider is provider
