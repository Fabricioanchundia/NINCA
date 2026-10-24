"""Tests for GitHub URL parsing."""

from ninca.github import _owner_repo


def test_parses_standard_url() -> None:
    assert _owner_repo("https://github.com/owner/repo") == ("owner", "repo")


def test_strips_git_suffix() -> None:
    assert _owner_repo("https://github.com/owner/repo.git") == ("owner", "repo")


def test_rejects_non_github() -> None:
    assert _owner_repo("https://gitlab.com/owner/repo") is None


def test_rejects_incomplete() -> None:
    assert _owner_repo("https://github.com/owner") is None