"""Tests for the rayforce console entry point (#L1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from rayforce import cli


def test_find_rayforce_executable_returns_existing(monkeypatch, tmp_path):
    # A bundled, executable binary is returned.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    exe = bin_dir / "rayforce"
    exe.write_text("#!/bin/sh\n")
    exe.chmod(0o755)

    monkeypatch.setattr(cli, "__file__", str(tmp_path / "cli.py"))
    assert cli.find_rayforce_executable() == str(exe)


def test_find_rayforce_executable_missing_raises(monkeypatch, tmp_path):
    # Neither bundled nor dev binary exists → FileNotFoundError.
    monkeypatch.setattr(cli, "__file__", str(tmp_path / "pkg" / "cli.py"))
    (tmp_path / "pkg").mkdir()
    with pytest.raises(FileNotFoundError, match="executable not found"):
        cli.find_rayforce_executable()


def test_main_exits_when_executable_missing(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "find_rayforce_executable",
        lambda: (_ for _ in ()).throw(FileNotFoundError("Rayforce executable not found")),
    )
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    assert "Error:" in capsys.readouterr().err


def test_main_invokes_executable(monkeypatch):
    calls = {}
    monkeypatch.setattr(cli, "find_rayforce_executable", lambda: "/fake/rayforce")
    monkeypatch.setattr(cli.sys, "argv", ["rayforce", "--flag", "x"])
    monkeypatch.setattr(cli.subprocess, "call", lambda argv: calls.setdefault("argv", argv))
    cli.main()
    assert calls["argv"] == ["/fake/rayforce", "--flag", "x"]
