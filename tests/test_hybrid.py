"""Tests for the hybrid scanner."""

import pytest

from ninca import hybrid
from ninca.ai import AiVerdict
from ninca.scanner import Tool


def test_rules_findings_skip_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fail(_: str) -> AiVerdict:
        raise AssertionError("AI must not run when rules already flag")

    monkeypatch.setattr(hybrid, "classify_description", _fail)
    tool = Tool("x", "Adds. <IMPORTANT>secret</IMPORTANT>")
    findings = hybrid.scan_tool_hybrid(tool, use_ai=True)
    assert any(f.rule_id == "NINCA-MCP-001" for f in findings)


def test_ai_catches_disguised(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        hybrid,
        "classify_description",
        lambda _: AiVerdict(malicious=True, reason="hidden order"),
    )
    tool = Tool("x", "innocent looking text")
    findings = hybrid.scan_tool_hybrid(tool, use_ai=True)
    assert any(f.rule_id == "NINCA-AI-001" for f in findings)


def test_clean_without_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fail(_: str) -> AiVerdict:
        raise AssertionError("AI must not run when use_ai is False")

    monkeypatch.setattr(hybrid, "classify_description", _fail)
    tool = Tool("x", "Adds two numbers.")
    assert hybrid.scan_tool_hybrid(tool, use_ai=False) == []
