from __future__ import annotations

import pytest

from rayforce import errors
from rayforce.network import TCPClient


def test_client_evaluates_arithmetic(rayforce_ipc_server):
    host, port = rayforce_ipc_server
    with TCPClient(host, port) as c:
        assert c.execute("(+ 1 2)") == 3
        assert c.execute("(* 6 7)") == 42


def test_client_evaluates_aggregation(rayforce_ipc_server):
    host, port = rayforce_ipc_server
    with TCPClient(host, port) as c:
        assert c.execute("(sum (til 100))") == 4950


def test_client_returns_vector(rayforce_ipc_server):
    host, port = rayforce_ipc_server
    with TCPClient(host, port) as c:
        result = c.execute("(til 5)")
        assert [v.value for v in result] == [0, 1, 2, 3, 4]


def test_client_close_blocks_subsequent_send(rayforce_ipc_server):
    host, port = rayforce_ipc_server
    c = TCPClient(host, port)
    c.close()
    with pytest.raises(errors.RayforceTCPError, match="closed connection"):
        c.execute("(+ 1 2)")


def test_client_invalid_port_rejected(rayforce_ipc_server):
    host, _ = rayforce_ipc_server
    with pytest.raises(errors.RayforceValueError):
        TCPClient(host, 0)
    with pytest.raises(errors.RayforceValueError):
        TCPClient(host, 70000)


def test_tcp_classes_exported_top_level():
    """TCPClient/TCPServer are importable from the top-level rayforce namespace."""
    import rayforce

    assert "TCPClient" in rayforce.__all__
    assert "TCPServer" in rayforce.__all__
    from rayforce import TCPClient as TC
    from rayforce import TCPServer as TS

    assert TC is not None and TS is not None
