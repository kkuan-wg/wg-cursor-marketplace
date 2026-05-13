#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
afterFileEdit hook — Schema Control Layer

Guard: if conversation_id is not in spec_index.json, pass silently.

Accumulates file_path (normalized to a path relative to CURSOR_PROJECT_DIR)
in spec_index[conversation_id].modified_files, avoiding duplicates.
"""
import json
import os
import sys

HOOKS_DIR_ENV = "CURSOR_PROJECT_DIR"


def _index_path() -> str:
    base = os.environ.get(HOOKS_DIR_ENV, ".")
    return os.path.join(base, ".cursor", "hooks", "spec_index.json")


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


def _normalize_path(file_path: str) -> str:
    """Return file_path relative to CURSOR_PROJECT_DIR when possible."""
    project_dir = os.environ.get(HOOKS_DIR_ENV, "")
    if project_dir:
        try:
            rel = os.path.relpath(file_path, project_dir)
            # relpath on Windows uses backslashes; normalise to forward slashes
            return rel.replace("\\", "/")
        except ValueError:
            pass
    return file_path.replace("\\", "/")


def main() -> None:
    try:
        sys.stdin = open(sys.stdin.fileno(), encoding="utf-8-sig", closefd=False)
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        sys.exit(0)

    conversation_id: str = payload.get("conversation_id", "") or ""
    file_path: str = payload.get("file_path", "") or ""

    if not conversation_id or not file_path:
        print(json.dumps({}))
        sys.exit(0)

    index_path = _index_path()
    index = _load_json(index_path)

    if conversation_id not in index:
        print(json.dumps({}))
        sys.exit(0)

    rel_path = _normalize_path(file_path)
    entry = index[conversation_id]
    modified_files: list = entry.get("modified_files", [])
    if rel_path not in modified_files:
        modified_files.append(rel_path)
        entry["modified_files"] = modified_files
        _save_json(index_path, index)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
