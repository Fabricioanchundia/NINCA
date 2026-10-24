"""Connection guard: a go/no-go decision for an MCP server's tools.

This is the active-protection layer. An agent host (or a CI pipeline) runs the
guard *before* trusting a server and refuses to connect when it is blocked.

Ninca only reads the tool definitions (static analysis); it never runs the
server, so this stays safe even for untrusted code.
"""

from __future__ import annotations

from dataclasses import dataclass

from ninca.hybrid import scan_tool_hybrid
from ninca.scanner import CRITICAL, HIGH, LOW, MEDIUM, Finding, Tool

_SEVERITY_ORDER = {LOW: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3}


@dataclass(frozen=True, slots=True)
class ToolVerdict:
    """The findings for a single tool."""

    tool: Tool
    findings: list[Finding]

    @property
    def worst(self) -> str | None:
        """The highest severity among this tool's findings, or None if clean."""
        if not self.findings:
            return None
        return max(
            (f.severity for f in self.findings),
            key=lambda s: _SEVERITY_ORDER.get(s, 0),
        )


@dataclass(frozen=True, slots=True)
class GuardDecision:
    """The overall decision for a server's set of tools."""

    allowed: bool
    verdicts: list[ToolVerdict]
    blocking: frozenset[str]

    @property
    def blocked(self) -> list[ToolVerdict]:
        """Tools whose findings cross the blocking threshold."""
        return [v for v in self.verdicts if any(f.severity in self.blocking for f in v.findings)]


def guard_tools(
    tools: list[Tool],
    *,
    use_ai: bool = False,
    strict: bool = False,
) -> GuardDecision:
    """Scan every tool and decide whether the server is safe to connect.

    Blocks on CRITICAL findings by default; with ``strict`` it also blocks on
    HIGH. Returns a :class:`GuardDecision` whose ``allowed`` flag is the go/no-go.
    """
    blocking = frozenset({CRITICAL, HIGH}) if strict else frozenset({CRITICAL})
    verdicts = [ToolVerdict(tool, scan_tool_hybrid(tool, use_ai=use_ai)) for tool in tools]
    allowed = not any(f.severity in blocking for v in verdicts for f in v.findings)
    return GuardDecision(allowed=allowed, verdicts=verdicts, blocking=blocking)
