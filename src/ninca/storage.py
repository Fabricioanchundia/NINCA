"""Store discovered MCP servers in a local DuckDB database."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import duckdb

from ninca.discovery import McpServer

DEFAULT_DB_PATH = Path("data/ninca.duckdb")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
    name           TEXT PRIMARY KEY,
    description    TEXT,
    repository_url TEXT,
    source         TEXT,
    version        TEXT,
    discovered_at  TIMESTAMP DEFAULT current_timestamp
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


def connect(db_path: Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    """Open (or create) the database and make sure the schema exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(db_path))
    connection.execute(_SCHEMA)
    return connection


def save_servers(connection: duckdb.DuckDBPyConnection, servers: Iterable[McpServer]) -> int:
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


def count_servers(connection: duckdb.DuckDBPyConnection) -> int:
    """Return how many servers are stored."""
    row = connection.execute("SELECT count(*) FROM servers").fetchone()
    return int(row[0]) if row is not None else 0
