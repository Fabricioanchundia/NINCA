"""Command-line interface for Ninca."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ninca import __version__
from ninca.scanner import Tool, scan_tool


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


def _scan(path: Path) -> int:
    """Scan a file of tool definitions and print a report. Returns an exit code."""
    tools = _load_tools(path)
    total = 0
    for tool in tools:
        findings = scan_tool(tool)
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
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the `ninca` command."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return _scan(args.path)
    parser.print_help()
    return 0
