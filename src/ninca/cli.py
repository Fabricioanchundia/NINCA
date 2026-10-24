"""Command-line interface for Ninca."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ninca import __version__
from ninca.guard import guard_tools
from ninca.hybrid import scan_tool_hybrid
from ninca.scanner import Tool


def _load_tools(path: Path) -> list[Tool]:
    """Load MCP tool definitions from a JSON file (static: never executed)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    raw = data.get("tools", data) if isinstance(data, dict) else data
    tools: list[Tool] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                name = str(item.get("name", ""))
                if name:
                    tools.append(Tool(name=name, description=str(item.get("description", ""))))
    return tools


def _scan(path: Path, use_ai: bool) -> int:
    """Scan a file of tool definitions and print a report. Returns an exit code."""
    tools = _load_tools(path)
    total = 0
    for tool in tools:
        findings = scan_tool_hybrid(tool, use_ai=use_ai)
        if not findings:
            continue
        print(f"\n[{tool.name}]")
        for finding in findings:
            total += 1
            print(f"  {finding.severity.upper():8} {finding.rule_id}  {finding.title}")
            print(f"           {finding.detail}")
            print(f"           fix: {finding.remediation}")
    if total == 0:
        print(f"Scanned {len(tools)} tool(s): no issues found.")
        return 0
    print(f"\nScanned {len(tools)} tool(s): {total} finding(s).")
    return 1


def _guard(path: Path, use_ai: bool, strict: bool) -> int:
    """Decide whether a server is safe to connect. Exit 1 means blocked."""
    tools = _load_tools(path)
    decision = guard_tools(tools, use_ai=use_ai, strict=strict)

    if decision.allowed:
        print(f"ALLOW  {len(tools)} tool(s) checked: safe to connect.")
        warned = [v for v in decision.verdicts if v.findings]
        if warned:
            names = ", ".join(v.tool.name for v in warned)
            print(
                f"       note: {len(warned)} tool(s) have non-blocking warnings "
                f"({names}). Run with --strict to block them."
            )
        return 0

    blocked = decision.blocked
    print("BLOCK  do not connect this server to your agent.")
    print(f"       {len(blocked)} of {len(tools)} tool(s) are dangerous:")
    for verdict in blocked:
        print(f"\n  [{verdict.tool.name}]")
        for finding in verdict.findings:
            print(f"    {finding.severity.upper():8} {finding.rule_id}  {finding.title}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the `ninca` command."""
    parser = argparse.ArgumentParser(
        prog="ninca",
        description="Security scanner for MCP (Model Context Protocol) servers.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Scan MCP tool definitions (JSON).")
    scan_parser.add_argument("path", type=Path, help="Path to a JSON file of tools.")
    scan_parser.add_argument(
        "--ai", action="store_true", help="Also use the local AI classifier (needs Ollama)."
    )

    guard_parser = subparsers.add_parser(
        "guard",
        help="Decide if an MCP server is safe to connect (exit 1 = blocked).",
    )
    guard_parser.add_argument("path", type=Path, help="Path to a JSON file of tools.")
    guard_parser.add_argument(
        "--ai", action="store_true", help="Also use the local AI classifier (needs Ollama)."
    )
    guard_parser.add_argument(
        "--strict",
        action="store_true",
        help="Also block on high-severity findings, not only critical ones.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the `ninca` command."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return _scan(args.path, use_ai=args.ai)
    if args.command == "guard":
        return _guard(args.path, use_ai=args.ai, strict=args.strict)
    parser.print_help()
    return 0
