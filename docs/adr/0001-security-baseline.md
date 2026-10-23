# ADR 0001: Security baseline for the project

- **Status:** Accepted
- **Date:** 2026-10-23

## Context

Ninca is a security tool. Its own repository and supply chain must follow the practices it recommends to others.

## Decisions

1. **Minimal dependencies.** The CLI uses `argparse` from the standard library. Every dependency is a potential supply-chain entry point.
2. **Locked dependencies.** `uv.lock` is committed and CI installs with `uv sync --locked`.
3. **Least-privilege CI.** Workflows run with `permissions: contents: read` and `persist-credentials: false`.
4. **Actions pinned to full commit SHAs.** Tags can be moved; SHAs cannot. Dependabot keeps them updated.
5. **Protected `main`.** Changes only through pull requests, signed commits, linear history (squash merge only), and required CI checks.
6. **Secure coding rules.** Never pass untrusted input to a shell (`shell=True`); prefer standard-library code over external programs; end options with `--` when calling external programs; resolve paths before validating them against an allowed directory.

## Consequences

- Slightly more friction when contributing (signed commits, PRs).
- Ruff's `S` rules (Bandit) catch insecure patterns before merge.
