#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
subagentStop hook — Schema Control Layer

Guard: if parent_conversation_id is not in spec_index.json, pass silently.

- Completes the subagent_index entry with status, duration_ms, tool_call_count,
  message_count, modified_files.
- Does NOT write a log file here; subagent data is embedded in the conversation
  envelope written by the stop hook.
- If subagent_type == "flk-sdd-finalize", sets
  spec_index[parent_conversation_id].flk_sdd_finalize_ran = true.
"""
import json
import os
import sys

HOOKS_DIR_ENV = "CURSOR_PROJECT_DIR"


def _hooks_base() -> str:
    base = os.environ.get(HOOKS_DIR_ENV, ".")
    return os.path.join(base, ".cursor", "hooks")


def _index_path(filename: str) -> str:
    return os.path.join(_hooks_base(), filename)


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

    subagent_id: str = payload.get("subagent_id", "") or ""
    parent_conversation_id: str = payload.get("parent_conversation_id", "") or ""
    subagent_type: str = payload.get("subagent_type", "") or ""
    status: str = payload.get("status", "") or ""

    if subagent_type == "general-purpose":
        print(json.dumps({}))
        sys.exit(0)
    duration_ms: int = payload.get("duration_ms", 0) or 0
    tool_call_count: int = payload.get("tool_call_count", 0) or 0
    message_count: int = payload.get("message_count", 0) or 0
    modified_files: list = payload.get("modified_files", []) or []

    spec_index = _load_json(_index_path("spec_index.json"))

    if parent_conversation_id not in spec_index:
        print(json.dumps({}))
        sys.exit(0)

    subagent_index = _load_json(_index_path("subagent_index.json"))
    entry = subagent_index.get(subagent_id, {})

    entry.update({
        "status": status,
        "duration_ms": duration_ms,
        "tool_call_count": tool_call_count,
        "message_count": message_count,
        "modified_files": modified_files,
        "finalized": False,
    })
    subagent_index[subagent_id] = entry
    _save_json(_index_path("subagent_index.json"), subagent_index)

    if entry.get("subagent_type") == "flk-sdd-finalize":
        spec_index[parent_conversation_id]["flk_sdd_finalize_ran"] = True
        _save_json(_index_path("spec_index.json"), spec_index)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
