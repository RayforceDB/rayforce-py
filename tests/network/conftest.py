from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time

import pytest


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_port(host: str, port: int, timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"server on {host}:{port} did not become reachable")


@pytest.fixture
def rayforce_binary() -> str:
    """Path to a rayforce binary that can serve IPC. Skip if unavailable."""
    candidates = [
        os.environ.get("RAYFORCE_BINARY"),
        "/Users/karim/rayforce/rayforce",
        shutil.which("rayforce"),
    ]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    pytest.skip("rayforce binary not available — set RAYFORCE_BINARY or install it")


@pytest.fixture
def rayforce_ipc_server(rayforce_binary):
    """Spawn a rayforce IPC server bound to a free port; tear down after."""
    port = _find_free_port()
    proc = subprocess.Popen(
        [rayforce_binary, "-p", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_port("127.0.0.1", port)
        yield "127.0.0.1", port
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
