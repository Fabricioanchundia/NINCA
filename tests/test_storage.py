"""Tests for the DuckDB storage layer."""

from pathlib import Path

from ninca.discovery import McpServer
from ninca.storage import connect, count_servers, save_servers


def _server(name: str) -> McpServer:
    return McpServer(
        name=name,
        description="desc",
        repository_url="https://github.com/x/y",
        source="github",
        version="1.0.0",
        is_latest=True,
    )


def test_save_and_count(tmp_path: Path) -> None:
    connection = connect(tmp_path / "test.duckdb")
    written = save_servers(connection, [_server("a"), _server("b")])
    assert written == 2
    assert count_servers(connection) == 2
    connection.close()


def test_upsert_does_not_duplicate(tmp_path: Path) -> None:
    connection = connect(tmp_path / "test.duckdb")
    save_servers(connection, [_server("a")])
    save_servers(connection, [_server("a")])
    assert count_servers(connection) == 1
    connection.close()
