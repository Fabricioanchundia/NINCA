# ADR 0002: Scope and differentiation

- **Status:** Accepted
- **Date:** 2026-10-23

## Context

MCP server security is a crowded but immature space. Existing tooling falls into
four groups, and each leaves a gap:

| Group | Examples | What they do | Limitation |
|-------|----------|--------------|------------|
| Runtime gateways | Salt, Kong AI Gateway, Docker MCP Toolkit | Inspect live traffic | Commercial; require a running server in production |
| Active scanners | Invariant MCP-Scan, MCPSafetyScanner, CyberMCP | Query a running server | Must execute/host the server (risky, slow) |
| Attack emulators | MasterMCP, MCP for Security | Attack a system to test it | Offensive; do not analyze code |
| Config scanners | mcpguard (PyPI) | Scan `mcp.json` for secrets | Only the config, not the server's source |

OWASP has published the **MCP Top 10**, which we adopt as our reference taxonomy
instead of inventing categories.

## Decision

Ninca occupies the gap none of the above fill: **static, ecosystem-scale source
analysis**. Specifically:

1. **Static analysis of source code and tool descriptions.** Ninca never runs the
   analyzed server. It inspects the implementation and the natural-language tool
   descriptions, where tool poisoning lives. This is safe by design.
2. **Ecosystem scale.** Ninca discovers thousands of public MCP servers and scans
   them in batches, producing aggregate data (the "State of MCP Server Security"
   report) that single-target scanners cannot.
3. **Hybrid rules + AI, rigorously evaluated.** Fast MCP-specific rules first, an
   AI classifier for ambiguous cases, measured with precision, recall, false
   positives and cost (rules-only vs AI-only vs hybrid).
4. **Self-defending scanner.** Because Ninca uses an LLM to read untrusted text,
   it must resist prompt-injection aimed at its own analyzer, with tests that
   prove it.

Every finding maps to an OWASP MCP Top 10 category.

## Consequences

- Clear, defensible niche versus existing tools; honest about not being "first".
- Static-only means some runtime-only risks (e.g. live auth, telemetry) are only
  partially covered; documented as a known limitation.
- The evaluation burden (labeled dataset, metrics) is higher, but it is the main
  differentiator.
