#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["boto3"]
# ///
"""
sessionStart hook — Schema Control Layer

Always runs (no SDD guard needed — only reads existing indexes).

Prune rules:
- subagent_index.json: remove orphan entries (no stop received) older than 48h
  based on started_at.
- spec_index.json: remove entries with finalized == True that are older than 48h
  based on registered_at.
- logs/: delete *_conv_*_gen*.json files older than 14 days based on file mtime.
- logs/pending/: not subject to the 14-day TTL — files stay until successfully uploaded.

Upload retry:
- logs/pending/: any *_conv_*_gen*.json is re-posted to the control-layer API.
    success → file is moved to logs/ (consistent with normal successful uploads)
    failure → file stays in logs/pending/ for the next sessionStart retry
"""
import glob
import json
import logging
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.error import URLError

HOOKS_DIR_ENV = "CURSOR_PROJECT_DIR"
TTL_HOURS = 48
LOGS_TTL_DAYS = 14

_API_BASE_URL = "https://ai-tool.authptinfo.dev.usa.cloud.watchguard.com/agent-control-layer"
_API_EVENTS_PATH = "/events"
_AWS_PROFILE = "info"
_AWS_REGION = "us-west-2"  # region where the API Gateway is deployed


def _hooks_base() -> str:
    base = os.environ.get(HOOKS_DIR_ENV, ".")
    return os.path.join(base, ".cursor", "hooks")


def _index_path(filename: str) -> str:
    return os.path.join(_hooks_base(), filename)


def _logs_dir() -> str:
    return os.path.join(_hooks_base(), "logs")


def _pending_dir() -> str:
    return os.path.join(_hooks_base(), "logs", "pending")


def _load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _post_envelope(envelope: dict) -> str | None:
    """POST an envelope to the control-layer API using AWS SigV4 signing.

    Returns None on success, or an error string describing the failure.
    """
    try:
        import boto3
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest

        session = boto3.Session(profile_name=_AWS_PROFILE, region_name=_AWS_REGION)
        credentials = session.get_credentials()
        if credentials is None:
            return f"no AWS credentials found for profile '{_AWS_PROFILE}'"

        url = f"{_API_BASE_URL}{_API_EVENTS_PATH}"
        body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")

        aws_request = AWSRequest(method="POST", url=url, data=body, headers={"Content-Type": "application/json"})
        SigV4Auth(credentials, "execute-api", _AWS_REGION).add_auth(aws_request)

        req = urllib.request.Request(url, data=body, headers=dict(aws_request.headers), method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return f"unexpected HTTP status {resp.status}"
        return None
    except URLError as exc:
        return f"network error: {exc}"
    except Exception as exc:
        return f"unexpected error: {exc}"


def _retry_pending_uploads(pending_dir: str, logs_dir: str) -> None:
    """Re-upload every file in logs/pending/.

    On success the file is moved to logs/ (same location as normal successful uploads).
    On failure the file stays in logs/pending/ for the next sessionStart retry.
    """
    if not os.path.isdir(pending_dir):
        return

    for log_file in glob.glob(os.path.join(pending_dir, "*_conv_*_gen*.json")):
        try:
            with open(log_file, encoding="utf-8") as f:
                envelope = json.load(f)
        except Exception as exc:
            logging.warning("control_layer_session_start: could not read pending file %s: %s", log_file, exc)
            continue

        error = _post_envelope(envelope)
        if error is None:
            try:
                shutil.move(log_file, os.path.join(logs_dir, os.path.basename(log_file)))
                logging.info("control_layer_session_start: retry succeeded, moved %s to logs/", os.path.basename(log_file))
            except Exception as exc:
                logging.warning("control_layer_session_start: could not move %s to logs/ after upload: %s", log_file, exc)
        else:
            logging.warning("control_layer_session_start: retry failed for %s: %s", os.path.basename(log_file), error)


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def main() -> None:
    try:
        sys.stdin = open(sys.stdin.fileno(), encoding="utf-8-sig", closefd=False)
        sys.stdin.read()
    except Exception:
        pass

    _retry_pending_uploads(_pending_dir(), _logs_dir())

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=TTL_HOURS)
    logs_cutoff = now - timedelta(days=LOGS_TTL_DAYS)

    subagent_index_path = _index_path("subagent_index.json")
    subagent_index = _load_json(subagent_index_path)
    if subagent_index:
        pruned = {}
        for sid, entry in subagent_index.items():
            started_at = _parse_dt(entry.get("started_at", ""))
            is_orphan = "status" not in entry or not entry.get("status")
            if is_orphan and started_at and started_at < cutoff:
                continue
            pruned[sid] = entry
        if len(pruned) != len(subagent_index):
            _save_json(subagent_index_path, pruned)

    spec_index_path = _index_path("spec_index.json")
    spec_index = _load_json(spec_index_path)
    if spec_index:
        pruned_spec = {}
        for conv_id, entry in spec_index.items():
            registered_at = _parse_dt(entry.get("registered_at", ""))
            is_finalized = entry.get("finalized", False)
            if is_finalized and registered_at and registered_at < cutoff:
                continue
            pruned_spec[conv_id] = entry
        if len(pruned_spec) != len(spec_index):
            _save_json(spec_index_path, pruned_spec)

    logs_dir = _logs_dir()
    if os.path.isdir(logs_dir):
        for log_file in glob.glob(os.path.join(logs_dir, "*_conv_*_gen*.json")):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file), tz=timezone.utc)
                if mtime < logs_cutoff:
                    os.remove(log_file)
            except Exception:
                pass

    print(json.dumps({}))


if __name__ == "__main__":
    main()
