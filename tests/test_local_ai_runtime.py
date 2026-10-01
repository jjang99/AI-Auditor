from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.services.local_ai_runtime import LocalAIRuntimeError, LocalAIRuntimeManager


def test_runtime_paths_are_relative_to_product_root(tmp_path):
    manager = LocalAIRuntimeManager(base_dir=tmp_path)

    assert manager.server_path == tmp_path / "runtime" / "llama.cpp" / "llama-server.exe"
    assert manager.model_path == tmp_path / "models" / "Qwen3-4B-Q4_K_M.gguf"
    assert manager.base_url == "http://127.0.0.1:8080"


def test_start_reuses_already_ready_server_without_spawning(tmp_path):
    manager = LocalAIRuntimeManager(base_dir=tmp_path)

    with patch.object(manager, "is_ready", return_value=True), patch(
        "app.services.local_ai_runtime.subprocess.Popen"
    ) as popen:
        manager.start()

    popen.assert_not_called()


def test_start_fails_cleanly_when_runtime_is_missing(tmp_path):
    manager = LocalAIRuntimeManager(base_dir=tmp_path)

    with patch.object(manager, "is_ready", return_value=False):
        with pytest.raises(LocalAIRuntimeError, match="실행파일"):
            manager.start()


def test_start_uses_bundled_runtime_and_model(tmp_path):
    server = tmp_path / "runtime" / "llama.cpp" / "llama-server.exe"
    model = tmp_path / "models" / "Qwen3-4B-Q4_K_M.gguf"
    server.parent.mkdir(parents=True)
    model.parent.mkdir(parents=True)
    server.write_bytes(b"runtime")
    model.write_bytes(b"model")

    manager = LocalAIRuntimeManager(base_dir=tmp_path)
    process = Mock()
    process.poll.return_value = None

    with patch.object(manager, "is_ready", side_effect=[False, True]), patch(
        "app.services.local_ai_runtime.subprocess.Popen", return_value=process
    ) as popen:
        manager.start()

    args = popen.call_args.args[0]
    assert args[0] == str(server)
    assert args[1:3] == ["-m", str(model)]
    assert "--reasoning" in args
    assert "off" in args
    assert manager._owns_process is True


def test_stop_terminates_only_owned_process(tmp_path):
    manager = LocalAIRuntimeManager(base_dir=tmp_path)
    process = Mock()
    process.poll.return_value = None
    manager.process = process
    manager._owns_process = True

    manager.stop()

    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=5)
    assert manager.process is None
    assert manager._owns_process is False
