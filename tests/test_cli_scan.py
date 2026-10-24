"""Tests for the `ninca scan` command."""

import json
from pathlib import Path

import pytest

from ninca.cli import main


def test_scan_reports_findings(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "tools.json"
    payload = {"tools": [{"name": "x", "description": "Adds. <IMPORTANT>secret</IMPORTANT>"}]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    exit_code = main(["scan", str(path)])
    assert exit_code == 1
    assert "NINCA-MCP-001" in capsys.readouterr().out


def test_scan_clean_file_returns_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "tools.json"
    payload = {"tools": [{"name": "x", "description": "Adds two numbers."}]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    exit_code = main(["scan", str(path)])
    assert exit_code == 0
    assert "no issues found" in capsys.readouterr().out
