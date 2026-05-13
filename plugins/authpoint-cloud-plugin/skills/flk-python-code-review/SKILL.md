---
name: flk-python-code-review
description: Reviews Folklore Python Lambda code (hexagonal boundaries, quality conventions, DTO/logging/error-handling rules) and produces a structured reviewer report. Use when the user requests a code-review pass for existing Folklore Python Lambda code.
---
# Folklore Python Code Review

The report must not be a catalogue of style opinions or pattern preferences. Every finding must justify why it matters functionally. The final verdict is advisory — the human reviewer decides what to act on.


## Always Start Here

**Always read `flk-python-hexagonal` first** — it is the authoritative reference for architecture principles, layer contracts, quality standards, and the general checklist.

**Then read `references/REFERENCE.md`** — the reviewer-specific reference for this skill.

## Output Location

All outputs are returned as review text only. This skill must not modify any files.

## Expected Input

You receive one of the following:

1. **Spec bundle path** (optional): either
   - a folder that contains `spec.md`, `code-tasks.md`, and `proposal.md`, or
   - a `spec.md` file where `code-tasks.md` and `proposal.md` exist alongside it (same folder).
2. **Direct function source path** (primary if no spec): a folder containing existing Folklore Lambda code to review (e.g. `application/src/<category>/<lambda_name>_fn/`).

If a target path is missing or ambiguous, ask for it in a single message.

## Scope

Review only Folklore Python Lambda application code:

- `app.py` handler and wiring
- `configuration.py` env vars, constants, dto mapping, and error codes (when applicable)
- `domain/service.py` (business logic, validators, exceptions)
- `port/*.py` (ABC contracts, method signatures)
- `adapter/*.py` (AWS adapter implementations)
- module/package integrity: `__init__.py` in every directory of the module tree

Strictly out of scope (do not review / do not produce findings for them):

- SAM templates / infrastructure
- Unit tests
- Any non-Python artifacts

## Phase 1: Spec-driven coverage check (when a spec bundle is provided)

Before performing the traditional code review, compare the existing implementation against the spec bundle:

1. **Read the spec**: extract each `REQ-*` requirement and any explicit "Scenario" acceptance conditions.
2. **Read the proposal**: from `proposal.md#Artifacts`, extract the expected artifact file paths/folders and ensure they exist in the reviewed code slice.
3. **Read code review guidance**: from `code-tasks.md#Review` (when present), follow its checklist to detect gaps that would mean "implementation does not cover the spec".

Coverage outcomes must be represented as findings (same severity scheme) when the implementation fails a requirement/scenario or is missing a required artifact. Each such finding must explicitly cite the failing `REQ-*` id and/or the affected "Scenario" acceptance condition text.

## Phase 2: Traditional code review

After Phase 1 (or immediately when no spec bundle is provided), perform a reviewer pass over the code slice in scope, focusing on issues that are functionally significant:
- `app.py` handler + wiring — wrong event parsing, missing error paths, incorrect dependency wiring
- `configuration.py` — missing required env vars that would cause runtime failures
- `domain/service.py` — wrong business logic, wrong decision paths, missing required exception types
- `port/*.py` — interface contracts that the implementation contradicts
- `adapter/*.py` — adapter calls that would fail at runtime or silently produce wrong results
- package integrity: `__init__.py` in every directory

Do not raise findings for stylistic preferences, naming conventions, or pattern choices that have no functional impact. If something looks unusual but does not break behaviour, add it to "Questions / Needs Discussion" instead of a finding.

## Skill Routing

This skill produces a single structured review report as plain text and does not route to any other skills.

## Phase 3: Verify before finishing

Before outputting the final report, verify:
- The report contains **all required sections** from `Output Format` (Verification Summary → Detailed Findings → Questions → Action Items → Final Verdict → Code-Review Checklist)
- Every finding includes: `file path` + exact module/class/function, `Evidence`, violated rule reference, impact, and a concrete fix suggestion
- Any missing code/artifacts in the reviewed slice are treated as `NOT_APPLICABLE` (or as required-failure findings in Phase 1 when a spec bundle is provided)

## No Generic Fault Language (report-quality gate)
The final report must focus on logical, code-evidenced gaps. It must not include speculative "AI guessed there might be a fault"-style wording, and must not flag style deviations as findings.
- If you cannot tie an issue to inspected code evidence and a violated rule/spec requirement, do not raise it as a finding; add it to "Questions / Needs Discussion" instead.
- If something looks like a pattern deviation but you have no evidence it breaks behaviour in this context, put it in "Questions / Needs Discussion" — never in Detailed Findings.
- Every finding must include `Evidence` and a concrete fix suggestion (no purely rhetorical feedback).
- Never use language that implies the PR must be rejected or that a specific action is mandatory. The human reviewer owns that decision.

## Reviewer Checklist (derived)

- Treat `references/REFERENCE.md` as the primary "priority rules" source (architecture boundaries, DTO/signature conventions, logging + exception routing, and configuration hygiene).
- Treat `flk-python-hexagonal` as the authoritative architecture/quality contract.

When you find an issue, reference the violated rule as it appears in `references/REFERENCE.md` (or `flk-python-hexagonal` if it is a general architecture/quality rule).

## Output Format

### 1. Verification Summary

**Status**: `APPROVED` | `APPROVED_WITH_CONCERNS` | `CONCERNS_RAISED`

**Overall Assessment**: 1-2 sentences.

**Files Reviewed**:
- `<file path>` — `<brief description>`

**Assumptions / Missing Inputs**:
- List review limitations (e.g., partial slice, missing files). For any missing code, mark the related checks as `NOT_APPLICABLE` rather than inferring.

### 2. Detailed Findings

Findings are ordered by severity:

- `CRITICAL` — likely functional bug or spec requirement clearly violated; human reviewer should prioritise
- `HIGH` — strong evidence of incorrect behaviour or architectural contract violation
- `MEDIUM` — quality/maintainability issue that is likely to cause future bugs
- `LOW` — minor inconsistency worth noting; human reviewer decides whether it needs addressing

All findings are advisory. The human reviewer makes the final call on what to act on.

For each finding include:
- `file path` + exact module/class/function
- `Evidence` (what you inspected: import/name/method/block; keep it short)
- violated rule (from `references/REFERENCE.md` and/or `flk-python-hexagonal`; when Phase 1 is involved, include the specific `REQ-*` id or Scenario acceptance condition)
- impact
- concrete fix suggestion

### 3. Questions / Needs Discussion

List any unresolved ambiguities or requirements that prevent approval, plus what you need to confirm.

### 4. Action Items

**Critical / High findings** (human reviewer decides if blocking):
1. [ ] ...

**Medium findings** (recommended to address):
1. [ ] ...

**Low findings** (optional):
1. [ ] ...

### 5. Final Verdict

**Recommendation**: `APPROVE` | `APPROVE_WITH_CONCERNS` | `NEEDS_DISCUSSION`

> Note: the recommendation is advisory. The human reviewer decides whether any concern is a blocker.

**Rationale**: 2-4 sentences.

**Confidence Level**: `High` | `Medium` | `Low`

**Regression Risk**: `Low` | `Medium` | `High`

**Reason**: 1-2 sentences (why this is low/medium/high risk given the findings).

### 6. Code-Review Checklist

Mark each section as `PASS`, `FAIL`, or `NOT_APPLICABLE`:
- Hexagonal boundaries
- Method signatures & DTO conventions
- Logging context lifecycle & error-handling conventions
- DTO mapping plumbing & event parsing/wiring correctness
- Configuration hygiene (env var usage + key constants location)
- Python package integrity (`__init__.py`)
