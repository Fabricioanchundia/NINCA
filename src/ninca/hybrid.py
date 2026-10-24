"""Hybrid scanner: fast rules first, AI for the ambiguous cases."""

from __future__ import annotations

from ninca.ai import classify_description
from ninca.scanner import CRITICAL, Finding, Tool, scan_tool


def scan_tool_hybrid(tool: Tool, use_ai: bool = False) -> list[Finding]:
    """Run rules first; if they find nothing and AI is enabled, ask the model."""
    findings = scan_tool(tool)
    if findings or not use_ai:
        return findings
    verdict = classify_description(tool.description)
    if verdict.malicious:
        findings.append(
            Finding(
                rule_id="NINCA-AI-001",
                severity=CRITICAL,
                title="AI flagged a disguised prompt-injection attempt",
                detail=verdict.reason,
                remediation="Review manually; the wording hides an order to the agent.",
            )
        )
    return findings
