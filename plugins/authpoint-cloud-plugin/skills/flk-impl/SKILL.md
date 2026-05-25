---
name: flk-impl
description: From an existing spec.md, produces a minimal change bundle (proposal.md + tasks split for Code specs, optional design.md) co-located with the spec. Use when turning spec requirements into a reviewable plan and task list.
---

# Feature Planning

Turn **`spec.md` intent** into a **small, reviewable change bundle** so implementers and reviewers see scope and sequencing without reading the whole repo. Output: **proposal**, **tasks**, optional **design** — kept short and tied to the source spec.

## Phase 1: Investigate Before Writing

**Complete all steps before producing any output.**

### 1. Parse the input

- Read the confirmed **`spec.md`** at the provided path — if the file does not exist, **stop**: hand off to **flk-ssot-spec-writer** to draft it first.
- Derive the **platform** (`folklore` or `legacy`), **domain**, and **capability** from the spec path.
- Use the confirmed **change ID** as the output folder name; if none was given, derive it in `kebab-case` from the goal summary or Jira key in the spec path.
- Note the confirmed **goal** — one sentence scoping the change bundle.

### 2. Read the spec and its references

- Read `## References` — note every artifact (events schema, DB model, API contract) and its expected path.
- **Read each linked artifact** (events schema, DB model) — extract names, key fields, and config values needed to write concrete implementation tasks. Do not copy schemas verbatim; extract only what drives task wording (e.g. table name, PK format, TTL attribute names, event type list, GSI names, Lambda config values).
- Read `## Requirements` — note each `REQ-N` heading and every Scenario beneath it.

### 3. Assess scope

- Identify which requirements and scenarios the change bundle will satisfy or extend.
- Flag any gaps — requirements that are vague, contradictory, or missing detail — for `proposal.md`.
- **Read the `> **Type:**` header of the input spec** — it is either `Code` or `Infra`. This drives the entire shape of the output:
  - **Code spec** → scope is business logic only; output is split:
    - `code-tasks.md` with phases `## Spec & Alignment` → `## Implementation`
    - `unit-tests-tasks.md` with phase `## Testing`
    - No `## Infrastructure` phase anywhere in the Code bundle.
  - **Infra spec** → scope is SAM/CloudFormation resources and minimal Lambda scaffold only; `infra-tasks.md` has phases `## Spec & Alignment`, `## Infrastructure`. No `## Implementation` or `## Testing` phases.
- If the work spans multiple domains, plan one `<change-id>` per domain (preferred) or one proposal that lists artifacts per domain explicitly.

### 4. Ask only what you cannot determine

If after steps 1–3 something critical is still unknown (e.g. which requirements are in scope, what the change ID should be), ask in a single message. Never invent scope not present in the spec.

## Phase 2: Write the Output

Output location — **co-located with the spec**, in the same folder:

```
ssot/<platform>/domain/<domain>/specs/<spec-id>-<capability>/
├── spec.md
├── proposal.md      ← required
├── infra-tasks.md   ← required for Infra
├── code-tasks.md    ← required for Code
├── unit-tests-tasks.md  ← required for Code
└── design.md      ← optional
```

Write **`proposal.md`** first, then the appropriate task files (`infra-tasks.md` for Infra, `code-tasks.md` + `unit-tests-tasks.md` for Code). Add **`design.md`** only for a genuine design fork. All files are written directly into `ssot/<platform>/domain/<domain>/specs/<spec-id>-<capability>/` — the same folder as `spec.md`.

### `proposal.md`

Keep to **one screen** when possible. Sections in order:

1. **Title** — one line matching the change intent.
2. **Ticket** — `**Ticket:** <JIRA-KEY>` on its own line immediately after the title, using the Jira key from the spec path or spec content.
3. **Goal** — 2–4 bullets: what changes for users or systems. Include concrete operational details surfaced from the spec's requirements — e.g. guard logic, data-write semantics, idempotency contracts, resource names — so the goal is self-contained without cross-referencing the spec. Only include details the spec actually defines; do not assume or invent values not present in the requirements.
4. **Scope / Non-goals** — explicit bullets, derived from the spec `Type`:
   - **Code spec**: scope is business logic, handlers, and hexagonal architecture modules. Infrastructure provisioning is **out of scope** (covered by the companion Infra spec).
   - **Infra spec**: scope is SAM resources (queues, tables, Lambda config), IAM, and the minimal Lambda stub. Business logic is **out of scope** (covered by the companion Code spec).
   - An **Out of scope** list prevents creep — always name the companion spec explicitly.
5. **Spec** — link to `./spec.md`. List every requirement and scenario this change satisfies, using the **verbatim heading text** from the spec — never `REQ-N` shorthands alone. Format: `Requirement: <heading text>` / `Scenario: <scenario heading text>`.
6. **Artifacts** — start with the standard deferral note: *"Artifacts are listed in `./spec.md#references`; verify all expected paths exist before starting implementation."* Then **explicitly list every new file the change will create** (e.g. `template.yaml`, `app.py`, `configuration.py`, `service.py`, `repository.py`, `adapter/ddb_repository.py`) with a one-line description of its purpose. Do not repeat paths already in the spec's `## References`; only add paths for outputs that do not exist there.
7. **Risks / Open questions** — include only if non-obvious; flag spec gaps here.

### Task files (Code split)

For **Code specs**, write:
- `code-tasks.md` (business logic / implementation only)
- `unit-tests-tasks.md` (test scenarios only)

Do **not** write `infra-tasks.md` for Code specs.

For **Infra specs**, write a single `infra-tasks.md` (infrastructure only), following the Infra phase rules.

### `code-tasks.md`

- **Phases** with `##` headings:
  - `## Spec & Alignment` → `## Implementation`
- Never include any `## Testing` or `## Review` section in `code-tasks.md`.
- Under each phase: checkbox tasks `- [ ]` that are **single-step** and **verifiable**.
- **Granularity**: tasks must name **specific files, modules, or config keys** — not just paraphrase a requirement. Use values extracted from artifacts in Phase 1 (e.g. table name, PK format, TTL attribute, event type names, Lambda timeout).
- **Traceability**: suffix tasks with `(Requirement: <REQ heading text>)` or `(Scenario: <scenario heading text>)` where it helps tie back to `./spec.md`. Prefer the heading text over `REQ-N` numbers so tasks remain readable without cross-referencing.

### `unit-tests-tasks.md`

- **Phase** with `##` heading:
  - `## Testing`
- Never include a `## Review` section in `unit-tests-tasks.md`.
- Under `## Testing`: produce one checkbox per scenario from the spec (unit test tasks). Include any additional test tasks explicitly required by the spec (including integration concerns if they are explicitly stated).
- **Traceability**: suffix tasks with `(Scenario: <scenario heading text>)` or `(Requirement: <REQ heading text>)` where helpful.

### `infra-tasks.md` (Infra only)

- **Phases** with `##` headings:
  - `## Spec & Alignment` → `## Infrastructure`
- Never include `## Implementation`, `## Testing`, or `## Review` for an Infra spec.
- Under each phase: checkbox tasks `- [ ]` that are **single-step** and **verifiable**.
- **Granularity** and **Traceability** requirements match the Code task files.
- Order tasks **dependency-first**: spec/contract alignment before infrastructure.

### `design.md` (optional)

Add only when there is a **genuine fork** — two viable approaches, a security trade-off, or a compatibility constraint. Format:

- **Decision** — one paragraph.
- **Alternatives** — bullets.
- **Consequences** — bullets (trade-offs, follow-up tasks).

Omit `design.md` for straightforward additions.

## Phase 3: Verify Before Finishing

- [ ] `proposal.md` has a `**Ticket:** <JIRA-KEY>` line immediately after the title
- [ ] `proposal.md` Goal bullets include concrete operational details surfaced from the spec's requirements — not just a paraphrase of the spec title; details are drawn only from what the spec actually defines
- [ ] `proposal.md` links to `./spec.md` and names requirements and scenarios using **verbatim heading text** — no bare `REQ-N` numbers
- [ ] `proposal.md` Scope matches the input spec `Type`: business logic for Code specs; SAM resources + scaffold for Infra specs
- [ ] `proposal.md` has an explicit **Out of scope** section that names the companion spec (Code ↔ Infra)
- [ ] `proposal.md` Artifacts section lists every new file the change will create, with a one-line description
- [ ] No schema, attribute catalog, or duplicate artifact paths (already in spec references) are pasted into `proposal.md`
- [ ] For Code specs: `code-tasks.md` has phases `Spec & Alignment / Implementation` (no `## Testing` or `## Review`), and `unit-tests-tasks.md` has phase `Testing` only (no `## Review`)
- [ ] For Infra specs: `infra-tasks.md` phase set matches `Spec & Alignment / Infrastructure` (no `## Review`)
- [ ] Every task in the generated task files names a specific file, module, config key, or artifact — no task is a bare paraphrase of a requirement
- [ ] Every task in the generated task files is a single-step, verifiable checkbox item
- [ ] At least one task per in-scope requirement or scenario references that requirement by heading text
- [ ] `unit-tests-tasks.md` has one task per spec scenario (scenario explicitly named)
- [ ] `proposal.md` must not contain any `test` / `tests` / `tests/` wording anywhere
- [ ] No vague tasks with no file, requirement, or verification angle
- [ ] `spec.md` is **not** duplicated — it is linked from `proposal.md` and the Code task files as `./spec.md`
- [ ] `design.md` is present only if a real design decision was needed
- [ ] Output files (`proposal.md`, Code split task files or Infra `infra-tasks.md`, optional `design.md`) are written directly alongside `spec.md` — no `changes/` subfolder

## When the spec must change

If planning reveals new **MUST** statements or missing scenarios, note them in `proposal.md` under **Risks / Open questions** and add a task in the `## Spec & Alignment` phase. The **flk-ssot-spec-writer** agent should update `spec.md` before or alongside implementation.

## Anti-patterns

- Tasks with no link to a requirement or file — floating busywork.
- `proposal.md` that repeats the whole spec — link and point to sections.
- Empty phases or duplicate tasks across phases.
- Creating a `changes/` subfolder — output files go directly alongside `spec.md`.
- Pasting full AsyncAPI/OpenAPI/DynamoDB definitions into any output file.
- Repeating artifact paths already present in `spec.md#references` — the **Artifacts** section should point there, not duplicate them.
- A single oversized `proposal.md` that mixes unrelated capabilities.
- Using `REQ-N` numbers in the **Spec** section of `proposal.md` instead of verbatim heading text — requirement numbers are fragile and unreadable without the spec open.
- Omitting the `**Ticket:**` line from `proposal.md` — every change bundle must be traceable to a Jira ticket.
- Including `## Infrastructure` tasks in a Code spec change bundle — infrastructure belongs in the companion Infra spec change bundle.
- Including `## Implementation` or `## Testing` tasks in an Infra spec change bundle — business logic belongs in the companion Code spec change bundle.
- Putting infrastructure in scope for a Code spec, or business logic in scope for an Infra spec — keep them cleanly separated.
- Leaving the **Artifacts** section as a bare deferral note when the change will create new files — list every new file explicitly.

## Reference

- Output structure, folder naming, path rules → [references/REFERENCE.md](references/REFERENCE.md)
- Example `proposal.md` for a **Code spec** → [references/examples/saml-user-cache-consumer-code-proposal.md](references/examples/saml-user-cache-consumer-code-proposal.md)
- Example `code-tasks.md` for a **Code spec** → [references/examples/saml-user-cache-consumer-code-tasks.md](references/examples/saml-user-cache-consumer-code-tasks.md)
- Example `unit-tests-tasks.md` for a **Code spec** → [references/examples/saml-user-cache-consumer-unit-tests-tasks.md](references/examples/saml-user-cache-consumer-unit-tests-tasks.md)
- Example `proposal.md` for an **Infra spec** → [references/examples/saml-user-cache-consumer-infra-proposal.md](references/examples/saml-user-cache-consumer-infra-proposal.md)
- Example `infra-tasks.md` for an **Infra spec** → [references/examples/saml-user-cache-consumer-infra-tasks.md](references/examples/saml-user-cache-consumer-infra-tasks.md)
