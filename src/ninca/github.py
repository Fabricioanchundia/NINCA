"""Fetch repository metadata from the GitHub API."""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

GITHUB_API = "https://api.github.com/repos"
TIMEOUT = httpx.Timeout(30.0)


class RateLimitError(RuntimeError):
    """Raised when the GitHub API rate limit is exhausted."""


@dataclass(frozen=True, slots=True)
class RepoMetadata:
    """Metadata about a GitHub repository."""

    full_name: str
    stars: int
    language: str
    pushed_at: str
    archived: bool
    license: str


def _owner_repo(repository_url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub URL, or None if it is not one."""
    marker = "github.com/"
    if marker not in repository_url:
        return None
    path = repository_url.split(marker, 1)[1].removesuffix(".git").strip("/")
    parts = path.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


def _token() -> str:
    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set. Add it to your .env file.")
    return token


def github_client() -> httpx.Client:
    """Create an httpx client authenticated for the GitHub API."""
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ninca-scanner",
    }
    return httpx.Client(timeout=TIMEOUT, headers=headers, follow_redirects=True)


def fetch_metadata(repository_url: str, client: httpx.Client) -> RepoMetadata | None:
    """Fetch metadata for one GitHub repo, or None if it cannot be read."""
    owner_repo = _owner_repo(repository_url)
    if owner_repo is None:
        return None
    owner, repo = owner_repo
    response = client.get(f"{GITHUB_API}/{owner}/{repo}")
    if response.status_code == 404:
        return None
    remaining = response.headers.get("x-ratelimit-remaining")
    if response.status_code in (403, 429) and remaining == "0":
        reset = response.headers.get("x-ratelimit-reset", "unknown")
        raise RateLimitError(f"rate limit reached; resets at epoch {reset}")
    response.raise_for_status()
    data = response.json()
    license_info = data.get("license")
    license_name = ""
    if isinstance(license_info, dict):
        license_name = str(license_info.get("spdx_id") or "")
    return RepoMetadata(
        full_name=str(data.get("full_name", f"{owner}/{repo}")),
        stars=int(data.get("stargazers_count", 0)),
        language=str(data.get("language") or ""),
        pushed_at=str(data.get("pushed_at") or ""),
        archived=bool(data.get("archived", False)),
        license=license_name,
    )
