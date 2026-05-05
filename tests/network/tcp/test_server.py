from __future__ import annotations

import os
import socket
import subprocess
import sys
import time

import pytest

from rayforce.network import TCPClient, TCPServer


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
    raise RuntimeError(f"server never bound to {host}:{port}")


@pytest.fixture
def python_ipc_server():
    """Spawn a TCPServer in a subprocess so its main-thread blocking loop is
    isolated from the test process."""
    port = _find_free_port()
    code = (
        "from rayforce.network import TCPServer; "
        f"TCPServer({port}).listen()"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ},
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


def test_server_accepts_client_and_evaluates(python_ipc_server):
    host, port = python_ipc_server
    with TCPClient(host, port) as c:
        assert c.execute("(+ 2 3)") == 5
        assert c.execute("(sum (til 10))") == 45


def test_server_invalid_port_rejected():
    from rayforce import errors

    with pytest.raises(errors.RayforceValueError):
        TCPServer(0)
    with pytest.raises(errors.RayforceValueError):
        TCPServer(70000)


def test_server_idempotent_close():
    port = _find_free_port()
    server = TCPServer(port)
    server.close()
    server.close()  # second close is a no-op
