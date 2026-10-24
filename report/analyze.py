"""Analyze the discovered MCP ecosystem and print real numbers for the report.

Reads the local DuckDB (read-only), computes ecosystem / supply-chain risk
stats, and statically scans every server description with Ninca's rules.
It never connects to or runs any server.

Usage:
    uv run python report/analyze.py [path/to/ninca.duckdb]
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path

import duckdb

from ninca.scanner import CRITICAL, Tool, scan_tool

DB_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/ninca.duckdb")
OUT_DIR = Path("report")


def pct(part: int, whole: int) -> str:
    return f"{(100 * part / whole):.1f}%" if whole else "0.0%"


def main() -> int:
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run the pipeline first.")
        return 1

    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        "SELECT name, description, repository_url, stars, language, pushed_at, "
        "archived, license FROM servers"
    ).fetchall()
    total = len(rows)

    with_repo = with_meta = github = archived = no_license = unmaintained = zero_stars = 0
    languages: Counter[str] = Counter()
    cutoff = (datetime.now(UTC) - timedelta(days=365)).isoformat()

    rule_hits: Counter[str] = Counter()
    severity_hits: Counter[str] = Counter()
    flagged: list[tuple[str, str, str, str]] = []  # name, repo, severity, rules
    flagged_count = 0

    for name, description, repo, stars, language, pushed_at, archived_flag, lic in rows:
        repo = repo or ""
        if repo:
            with_repo += 1
        if "github.com/" in repo:
            github += 1
        if stars is not None:
            with_meta += 1
            if stars == 0:
                zero_stars += 1
            if not lic:
                no_license += 1
        if language:
            languages[language] += 1
        if archived_flag:
            archived += 1
        if pushed_at and str(pushed_at) < cutoff:
            unmaintained += 1

        findings = scan_tool(Tool(name=str(name), description=str(description or "")))
        if findings:
            flagged_count += 1
            ids = sorted({f.rule_id for f in findings})
            worst = CRITICAL if any(f.severity == CRITICAL for f in findings) else "high"
            for f in findings:
                rule_hits[f.rule_id] += 1
                severity_hits[f.severity] += 1
            flagged.append((str(name), repo, worst, ", ".join(ids)))

    top_stars = sorted(
        ((str(n), s) for n, _, _, s, *_ in rows if s is not None),
        key=lambda x: x[1],
        reverse=True,
    )[:5]

    print("=" * 60)
    print("NINCA — STATE OF MCP SERVER SECURITY (real data)")
    print("=" * 60)
    print(f"\nTotal servers discovered: {total}")
    print(f"  with a repository link : {with_repo} ({pct(with_repo, total)})")
    print(f"  hosted on GitHub       : {github} ({pct(github, total)})")
    print(f"  with GitHub metadata   : {with_meta} ({pct(with_meta, total)})")

    print("\n-- Supply-chain / maintenance risk --")
    print(f"  archived repositories  : {archived} ({pct(archived, total)})")
    print(f"  not updated in 1y+     : {unmaintained} ({pct(unmaintained, total)})")
    print(f"  no license (of w/meta) : {no_license} ({pct(no_license, with_meta)})")
    print(f"  zero stars (of w/meta) : {zero_stars} ({pct(zero_stars, with_meta)})")

    print("\n-- Top languages --")
    for lang, n in languages.most_common(10):
        print(f"  {lang:16} {n:6}  ({pct(n, with_meta)})")

    print("\n-- Most-starred servers --")
    for srv_name, star_count in top_stars:
        print(f"  {star_count:7} stars  {srv_name}")

    print("\n-- Static security scan of server descriptions --")
    print(f"  descriptions scanned   : {total}")
    print(f"  flagged (>=1 rule)     : {flagged_count} ({pct(flagged_count, total)})")
    print("  by rule:")
    for rid, n in rule_hits.most_common():
        print(f"    {rid}  {n}")
    print("  by severity:")
    for sev, n in severity_hits.most_common():
        print(f"    {sev:10} {n}")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "flagged_servers.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["name", "repository_url", "worst_severity", "rules"])
        writer.writerows(flagged)
    print(f"\nSaved {len(flagged)} flagged servers to {out} (for responsible disclosure).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
