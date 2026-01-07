"""Tests for network utilities."""

from __future__ import annotations

import pytest

from rayforce import String, Table, errors
from rayforce import _rayforce_c as r
from rayforce.network.utils import python_to_ipc


class TestPythonToIPC:
    def test_python_to_ipc_string(self):
        result = python_to_ipc("test_string")
        assert String(ptr=result).to_python() == "test_string"

    def test_python_to_ipc_query(self):
        result = python_to_ipc(Table({"col": []}).select("col"))
        assert isinstance(result, r.RayObject)

    def test_python_to_ipc_unsupported_type(self):
        with pytest.raises(errors.RayforceTCPError, match="Unsupported IPC data"):
            python_to_ipc(123)
