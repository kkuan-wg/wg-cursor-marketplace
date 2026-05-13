#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["boto3"]
# ///
"""
stop hook — Schema Control Layer

Guard: if conversation_id is not in spec_index.json, pass silently.

- Writes a new logs/<spec_id>_conv_<conv8>_gen<N>.json envelope per generation:
    {
      "conversation": { ...generation fields... },
      "subagents": [ ...all subagent_index entries for this conversation... ]
    }
  N is the next available index (1-based, no overwrites).
- POSTs the envelope to the control-layer API (AWS SigV4, profile: info):
    success → file stays in logs/ as-is
    failure → file is moved to logs/pending/ for retry on next sessionStart
- Removes all subagent_index entries where parent_conversation_id == conversation_id.
- Resets spec_index[conversation_id].modified_files to [].
- Marks spec_index[conversation_id].finalized = True ONLY if
  spec_index[conversation_id].flk_sdd_finalize_ran == True.
"""
import glob
import json
import logging
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from urllib.error import URLError

HOOKS_DIR_ENV = "CURSOR_PROJECT_DIR"

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
    """POST the envelope to the control-layer API using AWS SigV4 signing.

    Returns None on success, or an error string describing the failure.
    """
    try:
        import boto3
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest

        session = boto3.Session(profile_name=_AWS_PROFILE, region_name=_AWS_REGION)
        credentials = session.get_credentials()
        if credentials is None:
            msg = f"no AWS credentials found for profile '{_AWS_PROFILE}'"
            logging.warning("control_layer_stop: %s, skipping upload", msg)
            return msg

        url = f"{_API_BASE_URL}{_API_EVENTS_PATH}"
        body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")

        aws_request = AWSRequest(method="POST", url=url, data=body, headers={"Content-Type": "application/json"})
        SigV4Auth(credentials, "execute-api", _AWS_REGION).add_auth(aws_request)

        req = urllib.request.Request(url, data=body, headers=dict(aws_request.headers), method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                msg = f"unexpected HTTP status {resp.status}"
                logging.warning("control_layer_stop: %s", msg)
                return msg
        return None
    except URLError as exc:
        msg = f"network error: {exc}"
        logging.warning("control_layer_stop: %s", msg)
        return msg
    except Exception as exc:
        msg = f"unexpected error: {exc}"
        logging.warning("control_layer_stop: %s", msg)
        return msg


def main() -> None:
    try:
        sys.stdin = open(sys.stdin.fileno(), encoding="utf-8-sig", closefd=False)
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        sys.exit(0)

    conversation_id: str = payload.get("conversation_id", "") or ""
    status: str = payload.get("status", "") or ""
    loop_count: int = payload.get("loop_count", 0) or 0
    input_tokens: int = payload.get("input_tokens", 0) or 0
    output_tokens: int = payload.get("output_tokens", 0) or 0
    cache_read_tokens: int = payload.get("cache_read_tokens", 0) or 0
    cache_write_tokens: int = payload.get("cache_write_tokens", 0) or 0

    spec_index = _load_json(_index_path("spec_index.json"))

    if conversation_id not in spec_index:
        print(json.dumps({}))
        sys.exit(0)

    spec_entry = spec_index[conversation_id]

    spec_id = spec_entry.get("spec_id", "")

    logs_dir = _logs_dir()
    os.makedirs(logs_dir, exist_ok=True)

    conv_short = conversation_id.replace("-", "")[:8]
    existing_gen_files = glob.glob(os.path.join(logs_dir, f"{spec_id}_conv_{conv_short}_gen*.json"))
    existing_gen_files += glob.glob(os.path.join(_pending_dir(), f"{spec_id}_conv_{conv_short}_gen*.json"))
    next_gen = len(existing_gen_files) + 1
    conv_log_path = os.path.join(logs_dir, f"{spec_id}_conv_{conv_short}_gen{next_gen}.json")

    subagent_index = _load_json(_index_path("subagent_index.json"))
    subagents = [
        {
            "subagent_id": sid,
            "subagent_type": entry.get("subagent_type", ""),
            "subagent_model": entry.get("subagent_model", ""),
            "is_parallel_worker": entry.get("is_parallel_worker", False),
            "status": entry.get("status", ""),
            "duration_ms": entry.get("duration_ms", 0),
            "tool_call_count": entry.get("tool_call_count", 0),
            "message_count": entry.get("message_count", 0),
            "modified_files": entry.get("modified_files", []),
        }
        for sid, entry in subagent_index.items()
        if entry.get("parent_conversation_id") == conversation_id
    ]

    envelope = {
        "conversation": {
            "spec_id": spec_id,
            "invoked_subagent": spec_entry.get("invoked_subagent", ""),
            "prompt": spec_entry.get("prompt", ""),
            "conversation_id": conversation_id,
            "generation": next_gen,
            "model": spec_entry.get("model", ""),
            "user_email": spec_entry.get("user_email", ""),
            "status": status,
            "loop_count": loop_count,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read_tokens,
            "cache_write_tokens": cache_write_tokens,
            "modified_files": spec_entry.get("modified_files", []),
            "event_date": datetime.now(timezone.utc).isoformat(),
        },
        "subagents": subagents,
    }
    _save_json(conv_log_path, envelope)

    upload_error = _post_envelope(envelope)
    if upload_error is not None:
        pending_dir = _pending_dir()
        os.makedirs(pending_dir, exist_ok=True)
        try:
            shutil.move(conv_log_path, os.path.join(pending_dir, os.path.basename(conv_log_path)))
        except Exception as exc:
            logging.warning("control_layer_stop: could not move file to pending/: %s", exc)

    pruned_subagent_index = {
        sid: entry
        for sid, entry in subagent_index.items()
        if entry.get("parent_conversation_id") != conversation_id
    }
    _save_json(_index_path("subagent_index.json"), pruned_subagent_index)

    if spec_entry.get("flk_sdd_finalize_ran"):
        spec_entry["finalized"] = True
    _save_json(_index_path("spec_index.json"), spec_index)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
