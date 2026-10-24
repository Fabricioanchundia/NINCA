"""Rule-based scanner for MCP tool definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass

CRITICAL = "critical"
HIGH = "high"
MEDIUM = "medium"
LOW = "low"


@dataclass(frozen=True, slots=True)
class Tool:
    """An MCP tool as the agent sees it."""

    name: str
    description: str


@dataclass(frozen=True, slots=True)
class Finding:
    """A security issue detected in a tool definition."""

    rule_id: str
    severity: str
    title: str
    detail: str
    remediation: str


@dataclass(frozen=True, slots=True)
class _Rule:
    rule_id: str
    pattern: re.Pattern[str]
    severity: str
    title: str
    remediation: str


_RULES: list[_Rule] = [
    _Rule(
        "NINCA-MCP-001",
        re.compile(r"<\s*(important|system|secret|instructions?|admin)\b", re.IGNORECASE),
        CRITICAL,
        "Hidden instruction tags in tool description",
        "Remove tag-like instructions; a description documents, it does not command.",
    ),
    _Rule(
        "NINCA-MCP-002",
        re.compile(
            r"(do not tell|don't tell|do not mention|don't mention|no le menciones)",
            re.IGNORECASE,
        ),
        CRITICAL,
        "Request for secrecy toward the user",
        "A legitimate tool never asks the agent to hide actions from the user.",
    ),
    _Rule(
        "NINCA-MCP-003",
        re.compile(
            r"(ignore (all )?previous|disregard previous|before using this tool)",
            re.IGNORECASE,
        ),
        HIGH,
        "Attempt to steer or override the agent",
        "Descriptions must not redirect or override the agent's behavior.",
    ),
    _Rule(
        "NINCA-MCP-004",
        re.compile(
            r"(\.ssh|id_rsa|id_ed25519|\.env|/etc/passwd|credential|api.?key|password)",
            re.IGNORECASE,
        ),
        HIGH,
        "Reference to sensitive files or secrets",
        "Review why this tool references secrets unrelated to its purpose.",
    ),
    _Rule(
        "NINCA-MCP-005",
        re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]"),
        HIGH,
        "Invisible Unicode characters in description",
        "Remove zero-width/invisible characters hidden in the text.",
    ),
]


def scan_tool(tool: Tool) -> list[Finding]:
    """Scan one MCP tool definition and return any security findings."""
    findings: list[Finding] = []
    for rule in _RULES:
        match = rule.pattern.search(tool.description)
        if match is None:
            continue
        findings.append(
            Finding(
                rule_id=rule.rule_id,
                severity=rule.severity,
                title=rule.title,
                detail=f"Matched {match.group(0)!r} in tool {tool.name!r}.",
                remediation=rule.remediation,
            )
        )
    return findings
