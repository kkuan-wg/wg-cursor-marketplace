---
name: flk-ops-infra-review
description: Reviews Folklore SAM/CloudFormation infrastructure and deploy wiring against the spec and Folklore infra conventions. Produces evidence-based findings and per-issue mini patch proposals (ask user before applying).
---

# Folklore Infra Ops Review

This skill produces a structured review report (and optional mini patch proposals) for infrastructure produced by `flk-ops-writer`.

The report must be evidence-based: if an issue cannot be tied to inspected code/template evidence and a violated checklist rule or spec requirement, it must go to `Questions / Needs Discussion` instead of `Detailed Findings`.

## Always Start Here
1. **Always read `flk-ops-template` first** — authoritative conventions and checklist.
2. **Then read SAM ops references only as needed** for the resources present in the reviewed template slice:
   - `flk-sam-ops-api` references
   - `flk-sam-ops-sqs-consumer` references
   - `flk-sam-ops-ddb-listener` references
3. If `deploy/parameters.py` exists in the target repo, also review:
   - `deploy/parameters.py`
   - referenced config modules imported by `parameters.py` (e.g. `configuration.py`, plus any constants dict modules those config modules import), when those files exist in the repo/workspace.

## Output Location
All outputs are returned as review text only. This skill must not modify any files.

## Expected Input
Inputs are evaluated in this order of precedence:
1. **Spec bundle path**: a folder containing `spec.md`, `proposal.md`, and `infra-tasks.md` (same folder).
2. **Direct infra paths**:
   - the SAM template file(s) (`template.yaml` and nested-stack templates)
   - `infra/Jenkinsfile`
3. If both spec bundle path and direct paths are provided, the spec bundle takes precedence.

Do not produce any output until:
- the spec bundle path is confirmed, OR
- the direct infra paths are confirmed.

## Scope
In-scope (review-only) infra artifacts:
- SAM template YAML files (including nested templates referenced by root template)
- `infra/Jenkinsfile` `lambdaNames` list
- optional `deploy/parameters.py` and referenced configuration modules (when present)
- When infra templates include Lambda resources, also verify the **minimal Lambda scaffold** exists in the workspace so AWS deployment won’t fail:
  - the `CodeUri` target folder exists
  - an `app.py` exists at the expected location
  - the `Handler` target points to a callable (e.g. `app.lambda_handler` resolves to `lambda_handler` in `app.py`)

Strictly out of scope:
- Lambda application code (`app.py`, `configuration.py`, ports, adapters, domain logic)
- Unit tests

## Skill Routing
This skill does not delegate to other skills. It uses them as reference material only (checklists/patterns).

---

## Phase 1: Spec-driven coverage check
Goal: ensure the existing templates cover what the spec/tasks require.

### Phase 1 Inputs
If a spec bundle is provided, read:
- `spec.md` — extract each `REQ-*` requirement and any explicit “Scenario” acceptance conditions
- `proposal.md` — extract `#Artifacts` expected artifact paths/folders and expected boundaries
- `infra-tasks.md` — treat all bullets under `## Spec & Alignment` and `## Infrastructure` as implementation alignment items

### Phase 1: Detect whether we should review Jenkinsfile `lambdaNames`
Define:
- `includesLambda := true` if **any** line in `infra-tasks.md` matches any of:
  - contains `lambda` (case-insensitive), OR
  - contains `AWS::Serverless::Function`, OR
  - contains `AWS::Logs::LogGroup`, OR
  - contains a function-like token ending with `_fn` or containing `-fn` (case-insensitive substring match)

If `includesLambda == false`, then Jenkinsfile `lambdaNames` checks are `NOT_APPLICABLE` (even if Jenkinsfile exists).

### Phase 1: Task-to-template addressing rules
For each infra task bullet:
1. Extract candidate resource identifiers from the task text:
   - backtick-enclosed names (e.g. `gen-settings-branding-topic.fifo`)
   - function names (contain `-fn` or `_fn`)
   - table/stream/topic names (plain identifiers)
2. Search the reviewed template(s) for evidence of those identifiers in plausible places:
   - `Resources` logical IDs/properties
   - `Parameters` usage and `!Ref/!GetAtt` paths
   - event source mapping blocks for DDB streams and other triggers
3. Mark as “addressed” if:
   - the identifier exists in the relevant template/resource slice, OR
   - the identifier exists elsewhere but is clearly the same resource (production reality preference).

**Production reality downgrade rule (severity):**
- Prefer existing deployed/production-shaped resources.
- Downgrade severity unless there is clear evidence of breakage (invalid template structure, missing required parameters/resources, wrong event wiring, invalid intrinsics, etc.).

### Phase 1: Evidence requirement
Each Phase 1 finding (or concern) must include:
- inspected file path(s)
- the specific YAML constructs/properties (or code-level parameter keys if reviewing parameters.py)
- how it maps to the relevant `REQ-*` and/or Scenario (when present)

If you cannot produce evidence, add it under `Questions / Needs Discussion` instead of a finding.

### Phase 1: `deploy/parameters.py` parameter key alignment (when present)
If `deploy/parameters.py` exists:
1. Collect all `Parameters:` keys expected by the reviewed templates.
2. Collect the parameter keys produced by `ApplicationParameters.get_sam_params()` output dictionary:
   - from direct literal keys and
   - from merged dicts: `**self.get_params_from_stacks(...)`, `**self.get_params_from_tables(...)`, and `**notification_log_groups`, and `**self._get_functions_params()`
3. For each template parameter key:
   - if missing from `get_sam_params()` result, raise a finding
   - if present but produced conditionally, treat as `NEEDS_DISCUSSION` unless conditions are evidenced from the spec inputs

Also review referenced config dict modules imported by `parameters.py` (only if they exist in the repo/workspace).

---

## Phase 2: Traditional infra compliance review
Goal: check Folklore infra conventions and deployment wiring correctness.

### Phase 2 Checklist sources
- `flk-ops-template` (general SAM conventions + checklist)
- applicable SAM ops reference docs (api/sqs/ddb) based on resource triggers present
- `deploy/parameters.py` only when it exists in the target repo

### Phase 2 Common review checks (always)
1. Tags: all resources use WG 2.1.0 tag set; include `wg:compliance:*` and required alarm tags where expected.
2. Encryption:
   - SQS: `SqsManagedSseEnabled: true` on queues
   - SNS: KMS master key ID rules as required by conventions
3. Lambdas:
   - Explicit `AWS::Logs::LogGroup` with `RetentionInDays: 14`
   - `ReservedConcurrentExecutions` mapping used via `!FindInMap`
   - tracing disabled per Globals expectations
4. IAM least privilege:
   - policies exist and are scoped to required actions/resources
5. Template hygiene:
   - no unused parameters
   - all `!Ref/!GetAtt` resolve to real resources/parameters
6. Nested stacks:
   - sub-stacks contain only resources (no nested application constructs in sub-stacks)
7. Minimal Lambda scaffold presence (only when `includesLambda == true`):
   - For each `AWS::Serverless::Function` resource in the reviewed templates:
     - the template `CodeUri` path exists in the workspace and points to a folder
     - an `app.py` exists under that folder (or at the path implied by the handler target)
     - the template `Handler` points to a function that exists in `app.py` (e.g. `app.lambda_handler` -> `def lambda_handler(...)`)
   - This check is a deployment-safety gate; it does not validate business logic.
7. Jenkinsfile `lambdaNames`:
   - only run this check when `includesLambda == true`

### Phase 2 Validation commands (if available)
If the commands are available in the environment, attempt:
- `sam validate` for changed or targeted templates
- `cfn-lint` for targeted templates

If commands are not available, skip and fall back to static validation:
- YAML structure checks
- required key presence checks based on checklist evidence

---

## Phase 3: Verify before finishing (report consistency)
Before outputting the final report, verify:
- report contains all required sections from Output Format
- every Detailed Finding includes:
  - evidence
  - violated rule reference (from `flk-ops-template` checklist parts and/or SAM ops reference patterns)
  - impact
  - concrete fix suggestion
- findings are ordered by severity

---

## Output Format
Use the exact `Output Format` headings and section order defined in `flk-python-code-review` (`skills/flk-python-code-review/SKILL.md`) and adapt the infra checklist wording.

### 1. Verification Summary
Status: `APPROVED` | `APPROVED_WITH_CONCERNS` | `CONCERNS_RAISED`
Overall Assessment: 1-2 sentences
Files Reviewed:
- `<file path>` — `<brief description>`
Assumptions / Missing Inputs:
- list review limitations; mark missing related checks as `NOT_APPLICABLE`

### 2. Detailed Findings
Severity: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
For each finding include:
- `file path` + exact YAML resource/property location (as precise as possible)
- Evidence
- violated rule (from `flk-ops-template` checklist items and/or SAM ops reference rules)
- impact
- concrete fix suggestion

### 3. Questions / Needs Discussion
Only questions that block evidence-based approval or require confirming ambiguous deployment wiring.

### 4. Action Items
Critical/High findings checkbox list
Medium findings checkbox list
Low findings checkbox list

### 5. Proposed Fixes
For each fixable finding propose a **per-issue mini patch**:
- Patch summary
- Target file(s)
- Patch (unified diff)
- Ask: `Apply this patch? (y/n)`

### 6. Final Verdict
Recommendation: `APPROVE` | `APPROVE_WITH_CONCERNS` | `NEEDS_DISCUSSION`
Rationale: 2-4 sentences
Confidence Level: `High` | `Medium` | `Low`
Regression Risk: `Low` | `Medium` | `High`
Reason: 1-2 sentences

### 7. Code-Review Checklist
Use PASS/FAIL/NOT_APPLICABLE for:
- SAM template structure and Globals
- Tags + alarm flags
- Encryption and SSE/KMS rules
- Lambda log groups + concurrency + tracing disabled expectations
- IAM least privilege and correct resources scoping
- Event source wiring correctness (DDB stream / SQS / SNS / API Gateway as applicable)
- Nested stacks discipline
- Jenkinsfile `lambdaNames` correctness (only if `includesLambda == true`)
- `deploy/parameters.py` parameter key alignment (only if file exists)
- referenced config modules review (only if they exist)

