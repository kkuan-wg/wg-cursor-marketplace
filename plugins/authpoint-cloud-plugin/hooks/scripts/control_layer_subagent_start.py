#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
subagentStart hook — Schema Control Layer

Guard: if parent_conversation_id is not in spec_index.json, pass silently.

Registers subagent_id → {
    parent_conversation_id, subagent_type, subagent_model,
    is_parallel_worker, spec_id, started_at
} in subagent_index.json.
"""
import json
import os
import sys
from datetime import datetime, timezone

HOOKS_DIR_ENV = "CURSOR_PROJECT_DIR"


def _index_path(filename: str) -> str:
    base = os.environ.get(HOOKS_DIR_ENV, ".")
    return os.path.join(base, ".cursor", "hooks", filename)


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


def main() -> None:
    try:
        sys.stdin = open(sys.stdin.fileno(), encoding="utf-8-sig", closefd=False)
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        sys.exit(0)

    parent_conversation_id: str = payload.get("parent_conversation_id", "") or ""
    subagent_id: str = payload.get("subagent_id", "") or ""
    subagent_type: str = payload.get("subagent_type", "") or ""

    if subagent_type == "general-purpose":
        print(json.dumps({}))
        sys.exit(0)
    subagent_model: str = payload.get("subagent_model", "") or ""
    is_parallel_worker: bool = payload.get("is_parallel_worker", False)
    user_email: str = payload.get("user_email", "") or ""

    spec_index = _load_json(_index_path("spec_index.json"))

    if parent_conversation_id not in spec_index:
        print(json.dumps({}))
        sys.exit(0)

    spec_id = spec_index[parent_conversation_id].get("spec_id", "")

    subagent_index = _load_json(_index_path("subagent_index.json"))
    subagent_index[subagent_id] = {
        "parent_conversation_id": parent_conversation_id,
        "subagent_type": subagent_type,
        "subagent_model": subagent_model,
        "is_parallel_worker": is_parallel_worker,
        "spec_id": spec_id,
        "user_email": user_email,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_json(_index_path("subagent_index.json"), subagent_index)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
