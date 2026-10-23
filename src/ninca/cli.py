"""Command-line interface for Ninca."""

import argparse

from ninca import __version__


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the `ninca` command."""
    parser = argparse.ArgumentParser(
        prog="ninca",
        description="Security scanner for MCP (Model Context Protocol) servers.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the `ninca` command."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
