from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time

import pytest

from rayforce.plugins import errors
from rayforce.plugins.kdb import KDBConnection, KDBEngine

pytestmark = pytest.mark.plugin


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_port(host: str, port: int, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"q server on {host}:{port} did not become reachable")


@pytest.fixture(scope="module")
def q_binary() -> str:
    candidates = [
        os.environ.get("Q_BINARY"),
        "/Users/karim/q/m64/q",
        shutil.which("q"),
    ]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    pytest.skip("q binary not available — set Q_BINARY or install kdb+")


@pytest.fixture
def q_server(q_binary):
    port = _find_free_port()
    qhome = os.environ.get("QHOME") or os.path.dirname(os.path.dirname(q_binary))
    env = {
        **os.environ,
        "QHOME": qhome,
        "QLIC": os.environ.get("QLIC", qhome),
    }
    proc = subprocess.Popen(
        [q_binary, "-p", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        env=env,
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


def test_kdb_arithmetic(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        assert c.execute("1+2") == 3
        assert c.execute("first 1 2 3") == 1


def test_kdb_int_vector(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        result = c.execute("til 5")
        assert [v.value for v in result] == [0, 1, 2, 3, 4]


def test_kdb_float_vector(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        result = c.execute("1.5 2.5 3.5")
        assert [v.value for v in result] == [1.5, 2.5, 3.5]


def test_kdb_string(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        # KDB returns "hello" as a KC vector → rayforce decodes as RAY_STR
        assert c.execute('"hello"') == "hello"


def test_kdb_symbol(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        # `abc returns a symbol atom; rayforce surfaces it as a Symbol value.
        result = c.execute("`abc")
        assert str(result) == "abc"


def test_kdb_table(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        result = c.execute("([] a:1 2 3; b:`x`y`z)")
        column_names = [str(c) for c in result.columns()]
        assert column_names == ["a", "b"]
        assert [v.value for v in result["a"]] == [1, 2, 3]




def test_kdb_close_blocks_subsequent_send(q_server):
    host, port = q_server
    conn = KDBEngine(host, port).acquire()
    conn.close()
    with pytest.raises(errors.KDBConnectionAlreadyClosedError):
        conn.execute("1+2")


def test_kdb_engine_dispose_connections(q_server):
    host, port = q_server
    engine = KDBEngine(host, port)
    c1 = engine.acquire()
    c2 = engine.acquire()
    assert len(engine.pool) == 2
    engine.dispose_connections()
    assert engine.pool == {}
    assert c1.is_closed and c2.is_closed


def test_kdb_connect_to_nothing_raises():
    with pytest.raises(errors.KDBConnectionError):
        KDBEngine("127.0.0.1", _find_free_port()).acquire()


def test_kdb_connection_repr(q_server):
    host, port = q_server
    with KDBEngine(host, port).acquire() as c:
        assert "established at" in repr(c)
        assert isinstance(c, KDBConnection)
    assert "disposed at" in repr(c)
