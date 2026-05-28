#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
beforeSubmitPrompt hook — Schema Control Layer

Guards:
- If the prompt does NOT contain any slash command from subagentMatchers
  (loaded from control-layer.config.json), pass through silently.
- If a matching slash command is found and has no spec-id:<specId> tag, block with an error message.
- If spec-id:<specId> is present, register conversation_id → { spec_id, model, user_email,
  registered_at, modified_files, finalized, flk_sdd_finalize_ran } in spec_index.json.
- If the conversation is already registered with a different spec_id, block re-tagging.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HOOKS_DIR_ENV = "CURSOR_PROJECT_DIR"
INDEX_SUBPATH = os.path.join(".cursor", "hooks", "spec_index.json")

SPEC_ID_RE = re.compile(r"spec-id\s*:\s*([A-Za-z0-9][A-Za-z0-9_-]*)")

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_SCRIPTS_DIR, "..", "control-layer.config.json")


def _load_slash_command_re() -> re.Pattern:
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
        matchers = config.get("subagentMatchers", [])
    except Exception:
        matchers = []
    if not matchers:
        return re.compile(r"(?!)")  # never matches
    pattern = "|".join(re.escape(m) for m in matchers)
    return re.compile(r"/(" + pattern + r")\b")


SLASH_COMMAND_RE = _load_slash_command_re()


def _hooks_dir() -> str:
    base = os.environ.get(HOOKS_DIR_ENV, ".")
    return os.path.join(base, ".cursor", "hooks")


def _index_path() -> str:
    base = os.environ.get(HOOKS_DIR_ENV, ".")
    return os.path.join(base, INDEX_SUBPATH)


def _load_index() -> dict:
    path = _index_path()
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_index(index: dict) -> None:
    path = _index_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _block(message: str) -> None:
    print(json.dumps({"continue": False, "user_message": message}))
    sys.exit(0)


def _pass() -> None:
    print(json.dumps({}))
    sys.exit(0)


def main() -> None:
    try:
        sys.stdin = open(sys.stdin.fileno(), encoding="utf-8-sig", closefd=False)
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        _pass()

    prompt: str = payload.get("prompt", "") or ""
    conversation_id: str = payload.get("conversation_id", "") or ""
    model: str = payload.get("model", "") or ""
    user_email: str = payload.get("user_email", "") or ""

    spec_match = SPEC_ID_RE.search(prompt)

    index = _load_index()
    existing = index.get(conversation_id)

    if existing and existing.get("spec_id"):
        if spec_match:
            new_spec_id = spec_match.group(1).strip()
            if new_spec_id != existing["spec_id"]:
                _block(
                    f"Re-tagging not allowed. "
                    f"This conversation is already registered as '{existing['spec_id']}'. "
                    f"Cannot change to '{new_spec_id}'."
                )
        changed = False
        if model and model != existing.get("model", ""):
            existing["model"] = model
            changed = True
        slash_matches = SLASH_COMMAND_RE.findall(prompt)
        if slash_matches:
            new_invoked = ",".join(slash_matches)
            if new_invoked != existing.get("invoked_subagent", ""):
                existing["invoked_subagent"] = new_invoked
                changed = True
        if prompt != existing.get("prompt", ""):
            existing["prompt"] = prompt
            changed = True
        if existing.get("modified_files"):
            existing["modified_files"] = []
            changed = True
        if changed:
            _save_index(index)
        _pass()

    if not SLASH_COMMAND_RE.search(prompt):
        if not spec_match:
            _pass()
        spec_id = spec_match.group(1).strip()
        now = datetime.now(timezone.utc).isoformat()
        index[conversation_id] = {
            "spec_id": spec_id,
            "invoked_subagent": "",
            "prompt": prompt,
            "model": model,
            "user_email": user_email,
            "registered_at": now,
            "modified_files": [],
            "finalized": False,
            "flk_sdd_finalize_ran": False,
        }
        _save_index(index)
        _pass()

    if not spec_match:
        _block(
            "Missing spec-id tag. Folklore slash commands require a spec-id:<specId> tag in the prompt.\n"
            "Example: /flk-code-writer spec-id:aaas-123456 implement the login endpoint"
        )

    spec_id = spec_match.group(1).strip()
    invoked_subagent = ",".join(SLASH_COMMAND_RE.findall(prompt))
    now = datetime.now(timezone.utc).isoformat()

    index[conversation_id] = {
        "spec_id": spec_id,
        "invoked_subagent": invoked_subagent,
        "prompt": prompt,
        "model": model,
        "user_email": user_email,
        "registered_at": now,
        "modified_files": [],
        "finalized": False,
        "flk_sdd_finalize_ran": False,
    }
    _save_index(index)

    _pass()


if __name__ == "__main__":
    main()
