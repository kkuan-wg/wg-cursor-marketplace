#!/usr/bin/env python3
"""
Deterministic validator for SSOT spec.md files.

Scope: only files at ssot/**/domain/**/specs/**/spec.md
It is intentionally generic and does not depend on domain-specific vocabulary.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_GLOB = "ssot/*/domain/*/specs/*/spec.md"


@dataclass(frozen=True)
class ValidationError:
    spec_path: str
    check_id: str
    message: str
    line: Optional[int] = None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _next_non_empty_line(lines: list[str], start_idx: int) -> tuple[Optional[int], Optional[str]]:
    for i in range(start_idx, len(lines)):
        if lines[i].strip():
            return i, lines[i]
    return None, None


def _find_header_index(lines: list[str], header: str) -> Optional[int]:
    target = header.strip()
    for i, line in enumerate(lines):
        if line.strip() == target:
            return i
    return None


def _extract_blockquote_meta(lines: list[str]) -> dict[str, str]:
    """
    Extracts values from the metadata block:
      > **Spec ID:** ...
      > **Type:** Code|Infra
      > **AWS Services:** ...
    """

    meta: dict[str, str] = {}
    patterns = {
        "spec_id": re.compile(r"^\s*>\s*\*\*Spec ID:\*\*\s*(.+?)\s*$"),
        "type": re.compile(r"^\s*>\s*\*\*Type:\*\*\s*(.+?)\s*$"),
        "aws_services": re.compile(r"^\s*>\s*\*\*AWS Services:\*\*\s*(.+?)\s*$"),
    }

    for line in lines:
        for key, pat in patterns.items():
            m = pat.match(line)
            if m:
                meta[key] = m.group(1).strip()

    return meta


def _collect_section_lines(lines: list[str], start_idx: int, end_idx: Optional[int]) -> list[str]:
    if end_idx is None:
        return lines[start_idx + 1 :]
    return lines[start_idx + 1 : end_idx]


def _extract_inline_backtick_calls(line: str) -> list[str]:
    # Inline code spans: `...`
    # This is a simple deterministic parse; we don't attempt nested backticks.
    return re.findall(r"`([^`]+)`", line)


def _parse_reference_bullet(line: str) -> Optional[tuple[str, Optional[str], bool]]:
    """
    Returns (tool_call_inline_code, relative_path_in_parentheses_or_none, is_expected).

    Some specs omit the relative path for event examples (e.g. `get_event_example(...)`).
    Some specs use labels like "**Events (expected):**" to indicate the artifacts are not
    present yet; in those cases we should not fail on missing files.
    """
    if not line.lstrip().startswith("-"):
        return None

    is_expected = "expected" in line.lower()

    tool_calls = _extract_inline_backtick_calls(line)
    tool_call = None
    for call in tool_calls:
        if "get_" in call or "mcp_tool" in call:
            tool_call = call
            break
    if not tool_call:
        return None

    # Parentheses path: (`../../event/schema.yaml`)
    m = re.search(r"\(\s*`?(\.\./[^)]+?)`?\s*\)", line)
    rel_path = m.group(1).strip() if m else None

    return tool_call, rel_path, is_expected


def _check_scenario_bullets_no_must(spec_path: Path, errors: list[ValidationError], lines: list[str]) -> None:
    """
    SSOT rule: scenarios are descriptive; GIVEN/WHEN/THEN bullet text must not include MUST/MUST NOT.
    """
    scenario_start_re = re.compile(r"^\s*####\s+Scenario:")
    req_heading_re = re.compile(r"^\s*###\s+REQ-\d+:")
    giwt_re = re.compile(r"^\s*-\s+(\*\*GIVEN\*\*|\*\*WHEN\*\*|\*\*THEN\*\*|\*\*AND\*\*)\s+")

    in_scenario = False
    for i, line in enumerate(lines):
        # A new scenario heading starts (or restarts) the scenario context.
        if scenario_start_re.match(line):
            in_scenario = True
            continue

        # Any higher-level heading exits scenario context.
        if req_heading_re.match(line) or line.strip().startswith("## ") or line.strip().startswith("### "):
            in_scenario = False
            continue

        if in_scenario and giwt_re.match(line):
            if re.search(r"\bMUST NOT\b|\bMUST\b", line, flags=re.IGNORECASE):
                errors.append(
                    ValidationError(
                        spec_path=str(spec_path),
                        check_id="scenario.no_must_in_bullets",
                        message="Scenario bullet contains MUST/MUST NOT; normative language must be in requirement body.",
                        line=i + 1,
                    )
                )


def _check_requirements_numbering(spec_path: Path, errors: list[ValidationError], lines: list[str]) -> None:
    req_heading_re = re.compile(r"^\s*###\s+REQ-(\d+):\s*(.+?)\s*$")
    reqs: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        m = req_heading_re.match(line)
        if m:
            reqs.append((i, int(m.group(1))))

    if not reqs:
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="requirements.missing",
                message="No '### REQ-N:' headings found under ## Requirements.",
            )
        )
        return

    nums = [n for _, n in reqs]
    expected = list(range(1, len(nums) + 1))
    if nums != expected:
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="requirements.req_numbering",
                message=f"REQ numbering must be sequential starting at 1 with no gaps. Found: {nums}; expected: {expected}.",
                line=reqs[0][0] + 1 if reqs else None,
            )
        )


def _check_references_section(spec_path: Path, errors: list[ValidationError], spec_dir: Path, lines: list[str]) -> None:
    refs_i = _find_header_index(lines, "## References")
    reqs_i = _find_header_index(lines, "## Requirements")
    if refs_i is None:
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="references.missing",
                message="Missing '## References' section.",
            )
        )
        return

    end_i = reqs_i if reqs_i is not None else None
    refs_lines = _collect_section_lines(lines, refs_i, end_i)

    any_bullets = False
    for offset, line in enumerate(refs_lines):
        i = refs_i + 1 + offset
        if not line.lstrip().startswith("-"):
            continue
        any_bullets = True

        parsed = _parse_reference_bullet(line)
        if parsed is None:
            errors.append(
                ValidationError(
                    spec_path=str(spec_path),
                    check_id="references.bullet_parse",
                    message="Reference bullet must contain an inline MCP tool call.",
                    line=i + 1,
                )
            )
            continue

        tool_call_inline, rel_path, is_expected = parsed

        # Reject placeholders in tool call.
        if "<" in tool_call_inline or ">" in tool_call_inline:
            errors.append(
                ValidationError(
                    spec_path=str(spec_path),
                    check_id="references.tool_placeholders",
                    message="MCP tool call contains placeholder-like '<...>' content; replace with real values.",
                    line=i + 1,
                )
            )
            continue

        if not rel_path:
            # Some specs omit relative path for some calls (e.g. get_event_example()).
            # If the bullet is expected and has no path, we cannot deterministically
            # verify existence, so we accept it.
            continue

        # Validate that relative path resolves and exists (unless marked expected).
        resolved = (spec_dir / rel_path).resolve()
        try:
            resolved.relative_to(REPO_ROOT.resolve())
        except ValueError:
            errors.append(
                ValidationError(
                    spec_path=str(spec_path),
                    check_id="references.path_outside_repo",
                    message="Reference relative path resolves outside repo; check relative path.",
                    line=i + 1,
                )
            )
            continue

        if not resolved.exists() and not is_expected:
            errors.append(
                ValidationError(
                    spec_path=str(spec_path),
                    check_id="references.path_missing",
                    message=f"Referenced file does not exist: {rel_path}",
                    line=i + 1,
                )
            )

    if not any_bullets:
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="references.no_bullets",
                message="References section has no '-' bullets; expected MCP tool call bullets.",
            )
        )


def _check_title_and_metadata(spec_path: Path, errors: list[ValidationError], lines: list[str], meta: dict[str, str]) -> None:
    # Title: first non-empty line
    title_i, title_line = _next_non_empty_line(lines, 0)
    if title_i is None or title_line is None:
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="title.missing",
                message="File is empty; expected a '# Title' line.",
            )
        )
        return

    if not title_line.startswith("# ") or title_line.startswith("## "):
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="title.format",
                message="Title must be the first non-empty line and be a single '# Title' heading.",
                line=title_i + 1,
            )
        )
    # Title adjacency rule: next non-empty line should be the metadata block (blockquote), not a paragraph.
    next_i, next_line = _next_non_empty_line(lines, title_i + 1)
    if next_i is not None and next_line is not None:
        if not next_line.lstrip().startswith(">"):
            errors.append(
                ValidationError(
                    spec_path=str(spec_path),
                    check_id="title.no_paragraph_after",
                    message="No paragraph should appear immediately after the '# Title' heading; metadata should follow (blockquote).",
                    line=next_i + 1,
                )
            )

    missing = [k for k in ("spec_id", "type", "aws_services") if k not in meta]
    if missing:
        errors.append(
            ValidationError(
                spec_path=str(spec_path),
                check_id="metadata.missing_fields",
                message=f"Missing required metadata fields: {', '.join(missing)}.",
            )
        )


def _check_type_scoping(spec_path: Path, errors: list[ValidationError], lines: list[str], spec_type: Optional[str]) -> None:
    """
    Lightweight heuristic checks; generic because we cannot infer full domain semantics.
    """
    if not spec_type:
        return

    spec_type_norm = spec_type.strip().lower()
    code_bad_tokens = [
        "aws::",
        "cloudformation",
        "serverless::function",
        "sam ",
        "sam/ cloudformation",
        "template.yaml",
        "iam policy",
        "resources:",
        "parameter overrides",
        "environment variable",
    ]
    # Narrowly-scoped patterns: words that are strong signals of application/business
    # logic that should live in Code specs, not Infra ones. Generic AWS/infra words
    # (dynamodb, sns, message, publish, routing) are intentionally excluded because
    # they appear legitimately in Infra requirement text.
    infra_bad_patterns = [
        r"\bvalidate\b",
        r"\bpayload\b",
        r"\bentitytype\b",
        r"\bbusiness logic\b",
    ]

    req_section_re = re.compile(r"^##\s+Requirements\s*$")
    other_section_re = re.compile(r"^##\s+")

    in_requirements = False
    req_lines: list[str] = []
    for line in lines:
        if req_section_re.match(line.strip()):
            in_requirements = True
            continue
        if in_requirements and other_section_re.match(line.strip()):
            break
        if in_requirements:
            req_lines.append(line)

    req_text = "\n".join(req_lines)

    if spec_type_norm == "code":
        lowered = req_text.lower()
        for token in code_bad_tokens:
            if token in lowered:
                errors.append(
                    ValidationError(
                        spec_path=str(spec_path),
                        check_id="type_scoping.code_contains_infra_tokens",
                        message=f"Type is Code but requirements mention infrastructure token/pattern: {token}",
                    )
                )
                return
    elif spec_type_norm == "infra":
        # Infra should not express business logic. Only flag normative sentences that
        # combine MUST with clearly app-logic verbs, narrowed to avoid false positives
        # on legitimate Infra topics (e.g. "the queue MUST receive messages from SNS").
        for pat in infra_bad_patterns:
            # Require the pattern to appear on the same line as a MUST to reduce noise.
            for req_line in req_lines:
                if re.search(pat, req_line, flags=re.IGNORECASE) and re.search(r"\bMUST\b", req_line, flags=re.IGNORECASE):
                    errors.append(
                        ValidationError(
                            spec_path=str(spec_path),
                            check_id="type_scoping.infra_contains_app_logic",
                            message=f"Type is Infra but a requirement line combines MUST with an application-logic keyword (matched pattern: {pat}).",
                        )
                    )
                    return


def validate_spec_file(spec_path: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    spec_text = _read_text(spec_path)
    # Keep deterministic line numbering: 1-based.
    lines = spec_text.splitlines()
    spec_dir = spec_path.parent

    meta = _extract_blockquote_meta(lines)

    _check_title_and_metadata(spec_path, errors, lines, meta)
    _check_scenario_bullets_no_must(spec_path, errors, lines)
    _check_requirements_numbering(spec_path, errors, lines)
    _check_references_section(spec_path, errors, spec_dir, lines)
    _check_type_scoping(spec_path, errors, lines, meta.get("type"))

    return errors


def iter_spec_paths(root: Path) -> list[Path]:
    # Deterministic order.
    return sorted(root.glob(SPEC_GLOB))


def main(argv: Optional[list[str]] = None) -> int:
    """
    Exit codes:
      0 — all specs passed.
      1 — one or more validation errors found.
      2 — no spec.md files were found to validate.
    """
    parser = argparse.ArgumentParser(
        description="Validate SSOT spec.md files deterministically.",
        epilog="Exit codes: 0=pass, 1=validation errors, 2=no specs found.",
    )
    parser.add_argument("--root", type=str, default=str(REPO_ROOT), help="Repo root to scan (default: repo root).")
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        help="Validate specific spec.md file(s) instead of scanning --root.",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable text.")
    args = parser.parse_args(argv)

    if args.files:
        spec_paths = sorted(Path(f).resolve() for f in args.files)
    else:
        root = Path(args.root).resolve()
        spec_paths = iter_spec_paths(root)

    if not spec_paths:
        print(f"No spec.md files found matching {SPEC_GLOB} under {args.root}")
        return 2

    all_errors: list[ValidationError] = []
    for spec_path in spec_paths:
        all_errors.extend(validate_spec_file(spec_path))

    if args.json:
        payload = {
            "root": args.root,
            "spec_glob": SPEC_GLOB,
            "error_count": len(all_errors),
            "errors": [asdict(e) for e in all_errors],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if not all_errors:
            print(f"PASS: {len(spec_paths)} spec(s) validated.")
        else:
            print(f"FAIL: {len(all_errors)} validation error(s) across {len(spec_paths)} spec(s).\n")
            for e in all_errors:
                loc = f":{e.line}" if e.line else ""
                print(f"{e.check_id}{loc}  {e.spec_path}\n  {e.message}\n")

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

