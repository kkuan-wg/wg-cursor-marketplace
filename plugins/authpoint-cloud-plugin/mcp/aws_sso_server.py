#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""
AuthPoint AWS SSO MCP

On startup checks for an active SSO session for the 'info' AWS profile.
If the session is missing or expired, runs `aws sso login --profile info`.
Exposes no tools — side-effect only.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

app = Server("authpoint-aws-sso")

_AWS_PROFILE = "info"
_LOGIN_COOLDOWN_SECONDS = 60  # 1 minute between login attempts
_LOCK_FILE = Path(__file__).parent / ".sso_login_attempt"


def _aws_profile_exists() -> bool:
    config_path = Path.home() / ".aws" / "config"
    if not config_path.is_file():
        return False
    return f"[profile {_AWS_PROFILE}]" in config_path.read_text(encoding="utf-8", errors="ignore")


def _run_aws(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["aws"] + args + ["--profile", _AWS_PROFILE],
        capture_output=True,
        text=True,
        timeout=15,
    )


def _login_attempted_recently() -> bool:
    """Returns True if a login was attempted within the cooldown window."""
    if not _LOCK_FILE.exists():
        return False
    try:
        last_attempt = float(_LOCK_FILE.read_text().strip())
        return (time.time() - last_attempt) < _LOGIN_COOLDOWN_SECONDS
    except (ValueError, OSError):
        return False


def _record_login_attempt() -> None:
    try:
        _LOCK_FILE.write_text(str(time.time()))
    except OSError:
        pass


def check_aws_sso() -> str:
    if not _aws_profile_exists():
        return f"AWS profile '{_AWS_PROFILE}' not found in ~/.aws/config — skipping SSO check."

    probe = _run_aws(["sts", "get-caller-identity"])
    if probe.returncode == 0:
        return f"AWS SSO session active (profile: {_AWS_PROFILE})."

    if _login_attempted_recently():
        remaining = int(
            _LOGIN_COOLDOWN_SECONDS - (time.time() - float(_LOCK_FILE.read_text().strip()))
        )
        return (
            f"AWS SSO session expired. Login already attempted recently — "
            f"skipping to avoid repeated browser popups (retry in ~{remaining}s). "
            f"Run `aws sso login --profile {_AWS_PROFILE}` manually if needed."
        )

    sys.stderr.write(
        f"[authpoint-aws-sso] Session expired or missing — running `aws sso login --profile {_AWS_PROFILE}`\n"
    )
    sys.stderr.flush()
    _record_login_attempt()

    login = subprocess.run(
        ["aws", "sso", "login", "--profile", _AWS_PROFILE],
        timeout=300,
    )
    if login.returncode == 0:
        _LOCK_FILE.unlink(missing_ok=True)
        return f"AWS SSO login completed (profile: {_AWS_PROFILE})."
    return f"AWS SSO login failed (exit {login.returncode}). Run `aws sso login --profile {_AWS_PROFILE}` manually."


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return []


async def main():
    result = check_aws_sso()
    sys.stderr.write(f"[authpoint-aws-sso] {result}\n")
    sys.stderr.flush()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
