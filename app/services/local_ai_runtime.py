import os
import subprocess
import sys
import time
from pathlib import Path
from urllib import error, request


class LocalAIRuntimeError(RuntimeError):
    """Bundled llama.cpp runtime/model startup failure."""


class LocalAIRuntimeManager:
    """Start and stop the bundled llama-server used by AI Auditor."""

    def __init__(
        self,
        base_dir: Path | None = None,
        host: str = "127.0.0.1",
        port: int = 8080,
        startup_timeout: float = 60.0,
    ):
        self.base_dir = Path(base_dir) if base_dir else self._default_base_dir()
        self.host = host
        self.port = port
        self.startup_timeout = startup_timeout
        self.process: subprocess.Popen | None = None
        self._owns_process = False

    @staticmethod
    def _default_base_dir() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def _recommended_thread_count() -> int:
        """Leave CPU capacity for the Qt GUI while local inference is running."""
        cpu_count = os.cpu_count() or 4
        return max(2, min(6, cpu_count - 2 if cpu_count > 2 else cpu_count))

    @property
    def server_path(self) -> Path:
        return self.base_dir / "runtime" / "llama.cpp" / "llama-server.exe"

    @property
    def model_path(self) -> Path:
        return self.base_dir / "models" / "Qwen3-4B-Q4_K_M.gguf"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def is_ready(self) -> bool:
        try:
            with request.urlopen(f"{self.base_url}/health", timeout=1.0) as response:
                return 200 <= response.status < 300
        except (error.URLError, TimeoutError, OSError):
            return False

    def start(self) -> None:
        if self.is_ready():
            return

        if not self.server_path.is_file():
            raise LocalAIRuntimeError(
                f"로컬 AI 실행파일을 찾을 수 없습니다: {self.server_path}"
            )
        if not self.model_path.is_file():
            raise LocalAIRuntimeError(
                f"로컬 AI 모델을 찾을 수 없습니다: {self.model_path}"
            )

        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            # Local inference is CPU-heavy. Run llama.cpp below the GUI process
            # priority so Windows keeps the application message loop responsive.
            creationflags |= getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)

        thread_count = self._recommended_thread_count()

        self.process = subprocess.Popen(
            [
                str(self.server_path),
                "-m",
                str(self.model_path),
                "--host",
                self.host,
                "--port",
                str(self.port),
                "--threads",
                str(thread_count),
                "--threads-batch",
                str(thread_count),
                "--reasoning",
                "off",
            ],
            cwd=str(self.server_path.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        self._owns_process = True

        deadline = time.monotonic() + self.startup_timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise LocalAIRuntimeError(
                    "로컬 AI 서버가 준비되기 전에 종료되었습니다."
                )
            if self.is_ready():
                return
            time.sleep(0.25)

        self.stop()
        raise LocalAIRuntimeError(
            f"로컬 AI 서버 준비시간이 {self.startup_timeout:.0f}초를 초과했습니다."
        )

    def stop(self) -> None:
        if not self._owns_process or self.process is None:
            return

        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

        self.process = None
        self._owns_process = False


_shared_runtime: LocalAIRuntimeManager | None = None


def get_local_ai_runtime() -> LocalAIRuntimeManager:
    """Return the process-wide local AI runtime manager."""
    global _shared_runtime
    if _shared_runtime is None:
        _shared_runtime = LocalAIRuntimeManager()
    return _shared_runtime
