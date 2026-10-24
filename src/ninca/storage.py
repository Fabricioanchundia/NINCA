"""Store discovered MCP servers and their metadata in a local DuckDB database."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import duckdb

from ninca.discovery import McpServer
from ninca.github import RepoMetadata

DEFAULT_DB_PATH = Path("data/ninca.duckdb")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
    name           TEXT PRIMARY KEY,
    description    TEXT,
    repository_url TEXT,
    source         TEXT,
    version        TEXT,
    discovered_at  TIMESTAMP DEFAULT current_timestamp,
    stars          INTEGER,
    language       TEXT,
    pushed_at      TEXT,
    archived       BOOLEAN,
    license        TEXT
)
"""

_UPSERT = """
INSERT INTO servers (name, description, repository_url, source, version)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT (name) DO UPDATE SET
    description = excluded.description,
    repository_url = excluded.repository_url,
    source = excluded.source,
    version = excluded.version
"""

_UPDATE_METADATA = """
UPDATE servers
SET stars = ?, language = ?, pushed_at = ?, archived = ?, license = ?
WHERE name = ?
"""


def connect(db_path: Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    """Open (or create) the database and make sure the schema exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(db_path))
    connection.execute(_SCHEMA)
    return connection


def save_servers(
    connection: duckdb.DuckDBPyConnection, servers: Iterable[McpServer]
) -> int:
    """Insert or update servers (parameterized, no SQL injection). Returns the count."""
    written = 0
    for server in servers:
        connection.execute(
            _UPSERT,
            [
                server.name,
                server.description,
                server.repository_url,
                server.source,
                server.version,
            ],
        )
        written += 1
    return written


def update_metadata(
    connection: duckdb.DuckDBPyConnection, name: str, metadata: RepoMetadata
) -> None:
    """Attach GitHub metadata to an already-stored server."""
    connection.execute(
        _UPDATE_METADATA,
        [
            metadata.stars,
            metadata.language,
            metadata.pushed_at,
            metadata.archived,
            metadata.license,
            name,
        ],
    )


def servers_without_metadata(
    connection: duckdb.DuckDBPyConnection, limit: int | None = None
) -> list[tuple[str, str]]:
    """Return (name, repository_url) for GitHub servers that lack metadata yet."""
    query = (
        "SELECT name, repository_url FROM servers "
        "WHERE stars IS NULL AND repository_url LIKE '%github.com/%'"
    )
    if limit is not None:
        query += f" LIMIT {int(limit)}"
    rows = connection.execute(query).fetchall()
    return [(str(row[0]), str(row[1])) for row in rows]


def count_servers(connection: duckdb.DuckDBPyConnection) -> int:
    """Return how many servers are stored."""
    row = connection.execute("SELECT count(*) FROM servers").fetchone()
    return int(row[0]) if row is not None else 0