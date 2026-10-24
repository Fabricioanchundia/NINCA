"""Run the discovery and enrichment pipeline end to end."""

from __future__ import annotations

from ninca.discovery import github_servers
from ninca.github import RateLimitError, fetch_metadata, github_client
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
    pending = servers_without_metadata(connection)
    print(f"Enriching {len(pending)} servers...")
    enriched = 0
    with github_client() as client:
        for index, (name, repository_url) in enumerate(pending, start=1):
            try:
                metadata = fetch_metadata(repository_url, client)
            except RateLimitError as error:
                print(f"Stopped at GitHub rate limit after {enriched} repos ({error}).")
                break
            if metadata is not None:
                update_metadata(connection, name, metadata)
                enriched += 1
            if index % 50 == 0:
                print(f"  ...processed {index}/{len(pending)}")
    print(f"Enriched {enriched} servers with GitHub metadata.")
    connection.close()
