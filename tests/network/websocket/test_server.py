from __future__ import annotations

import pytest

from rayforce import errors
from rayforce.network.websocket import WSServer


@pytest.mark.asyncio
async def test_server_starts_and_stops(free_port: int):
    server = WSServer(port=free_port)
    await server.start()
    assert server._server is not None
    await server.stop()
    assert server._server is None
    assert len(server._connections) == 0


def test_invalid_port():
    with pytest.raises(errors.RayforceValueError):
        WSServer(port=0)

    with pytest.raises(errors.RayforceValueError):
        WSServer(port=65536)

    with pytest.raises(errors.RayforceValueError):
        WSServer(port=-1)
