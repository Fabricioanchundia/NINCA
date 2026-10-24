"""Discover public MCP servers from the official MCP registry."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import httpx

REGISTRY_URL = "https://registry.modelcontextprotocol.io/v0/servers"
PAGE_SIZE = 100
TIMEOUT = httpx.Timeout(30.0)


@dataclass(frozen=True, slots=True)
class McpServer:
    """A public MCP server discovered from the registry."""

    name: str
    description: str
    repository_url: str
    source: str
    version: str


def _parse_entry(entry: dict[str, object]) -> McpServer | None:
    """Turn one raw registry entry into an McpServer, or None if invalid."""
    raw = entry.get("server", entry)
    if not isinstance(raw, dict):
        return None
    repository_url = ""
    source = ""
    repository = raw.get("repository")
    if isinstance(repository, dict):
        repository_url = str(repository.get("url", ""))
        source = str(repository.get("source", ""))
    name = str(raw.get("name", ""))
    if not name:
        return None
    return McpServer(
        name=name,
        description=str(raw.get("description", "")),
        repository_url=repository_url,
        source=source,
        version=str(raw.get("version", "")),
    )


def iter_servers(limit: int | None = None) -> Iterator[McpServer]:
    """Yield MCP servers from the official registry, following pagination."""
    cursor: str | None = None
    seen = 0
    headers = {"User-Agent": "ninca-scanner (https://github.com/Fabricioanchundia/NINCA)"}
    with httpx.Client(timeout=TIMEOUT, headers=headers) as client:
        while True:
            params: dict[str, str | int] = {"limit": PAGE_SIZE}
            if cursor:
                params["cursor"] = cursor
            response = client.get(REGISTRY_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            servers = payload.get("servers", []) if isinstance(payload, dict) else []
            for entry in servers:
                if not isinstance(entry, dict):
                    continue
                server = _parse_entry(entry)
                if server is None:
                    continue
                yield server
                seen += 1
                if limit is not None and seen >= limit:
                    return
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            cursor = metadata.get("nextCursor") if isinstance(metadata, dict) else None
            if not cursor:
                return
