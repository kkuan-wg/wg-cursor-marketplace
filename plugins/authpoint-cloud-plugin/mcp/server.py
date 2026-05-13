#!/usr/bin/env python3
"""
AuthPoint Plugin Updater MCP
On startup:
  1. Checks for remote changes and pulls updates silently.
  2. If the AWS CLI profile "info" exists, checks for an active SSO session and
     runs `aws sso login --profile info` when the session is missing or expired.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

app = Server("authpoint-plugin-updater")


def get_repo_path() -> Path | None:
    if len(sys.argv) < 2:
        return None
    path = Path(sys.argv[1])
    if path.is_dir() and (path / ".git").is_dir():
        return path
    return None


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )


def commits_behind(repo: Path) -> int:
    result = run_git(["rev-list", "--count", "HEAD..@{u}"], repo)
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def check_and_pull() -> str:
    repo = get_repo_path()
    if repo is None:
        return "Repo path not configured. Add it as an arg in mcpServers settings."

    fetch = run_git(["fetch", "--quiet"], repo)
    if fetch.returncode != 0:
        return f"git fetch failed: {fetch.stderr.strip()}"

    behind = commits_behind(repo)
    if behind == 0:
        return "Already up to date."

    pull = run_git(["pull", "--ff-only", "--quiet"], repo)
    if pull.returncode != 0:
        return f"git pull failed: {pull.stderr.strip()}"

    return f"Plugin updated ({behind} commit{'s' if behind > 1 else ''}). Reload Cursor to apply changes."


_AWS_PROFILE = "info"


def _aws_profile_exists() -> bool:
    """Return True if the AWS CLI config file contains a [profile info] section."""
    config_path = Path.home() / ".aws" / "config"
    if not config_path.is_file():
        return False
    content = config_path.read_text(encoding="utf-8", errors="ignore")
    return f"[profile {_AWS_PROFILE}]" in content


def _run_aws(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["aws"] + args + ["--profile", _AWS_PROFILE],
        capture_output=True,
        text=True,
        timeout=15,
    )


def check_aws_sso() -> str:
    """Ensure an active SSO session exists for the configured AWS profile.

    Steps:
    1. If the profile does not exist in ~/.aws/config, skip silently.
    2. Run `aws sts get-caller-identity --profile info` to probe the session.
    3. If the probe succeeds, the session is still valid — nothing to do.
    4. If the probe fails, run `aws sso login --profile info` to refresh it.
    """
    if not _aws_profile_exists():
        return f"AWS profile '{_AWS_PROFILE}' not found in ~/.aws/config — skipping SSO check."

    probe = _run_aws(["sts", "get-caller-identity"])
    if probe.returncode == 0:
        return f"AWS SSO session active (profile: {_AWS_PROFILE})."

    sys.stderr.write(f"[authpoint-updater] AWS session expired or missing — running `aws sso login --profile {_AWS_PROFILE}`\n")
    sys.stderr.flush()

    login = subprocess.run(
        ["aws", "sso", "login", "--profile", _AWS_PROFILE],
        timeout=300,
    )
    if login.returncode == 0:
        return f"AWS SSO login completed (profile: {_AWS_PROFILE})."
    return f"AWS SSO login failed (exit {login.returncode}). Run `aws sso login --profile {_AWS_PROFILE}` manually."


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return []


async def main():
    result = check_and_pull()
    sys.stderr.write(f"[authpoint-updater] {result}\n")
    sys.stderr.flush()

    sso_result = check_aws_sso()
    sys.stderr.write(f"[authpoint-updater] {sso_result}\n")
    sys.stderr.flush()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
