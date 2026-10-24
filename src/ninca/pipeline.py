"""Run the discovery and enrichment pipeline end to end."""

from __future__ import annotations

from ninca.discovery import github_servers
from ninca.github import fetch_metadata, github_client
from ninca.storage import (
    connect,
    save_servers,
    servers_without_metadata,
    update_metadata,
)


def run(limit: int | None = None) -> None:
    """Discover servers, store them, and enrich them with GitHub metadata."""
    connection = connect()
    saved = save_servers(connection, github_servers(limit=limit))
    print(f"Discovered and stored {saved} servers.")
    enriched = 0
    with github_client() as client:
        for name, repository_url in servers_without_metadata(connection):
            metadata = fetch_metadata(repository_url, client)
            if metadata is not None:
                update_metadata(connection, name, metadata)
                enriched += 1
    print(f"Enriched {enriched} servers with GitHub metadata.")
    connection.close()