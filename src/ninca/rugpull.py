"""Detect rug pulls: tool descriptions that change to a malicious version."""

from __future__ import annotations

from dataclasses import dataclass

from ninca.scanner import Finding, Tool, scan_tool


@dataclass(frozen=True, slots=True)
class RugPullAlert:
    """Raised when a tool description changed into a suspicious version."""

    name: str
    became_malicious: bool
    new_findings: list[Finding]


def check_rug_pull(name: str, old_description: str, new_description: str) -> RugPullAlert | None:
    """Compare two versions of a description; flag a change that turned malicious."""
    if old_description == new_description:
        return None
    new_findings = scan_tool(Tool(name, new_description))
    if not new_findings:
        return None
    old_findings = scan_tool(Tool(name, old_description))
    return RugPullAlert(
        name=name,
        became_malicious=not old_findings,
        new_findings=new_findings,
    )
