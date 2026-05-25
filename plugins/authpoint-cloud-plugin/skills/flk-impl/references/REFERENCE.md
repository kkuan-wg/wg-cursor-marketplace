# Feature Plan Reference

Detailed reference for output structure, folder naming, and linking rules.

---

## 1. Output Layout

Change bundles live **co-located with the spec** they belong to, in the same folder:

```
ssot/
  <platform>/              ← folklore | legacy
    domain/
      <domain>/
        specs/
          <spec-id>-<capability>/
            spec.md        ← source spec (read-only from this skill)
            proposal.md      ← required
            infra-tasks.md   ← required for Infra specs
            code-tasks.md    ← required for Code specs
            unit-tests-tasks.md  ← required for Code specs
            design.md      ← optional
```

---

## 2. File Naming

| Item | Convention | Example |
|------|-----------|---------|
| `proposal.md` | Always this exact name | — |
| `infra-tasks.md` | Infra specs: always this exact name | — |
| `code-tasks.md` | Code specs: always this exact name | — |
| `unit-tests-tasks.md` | Code specs: always this exact name | — |
| `design.md` | Always this exact name; only when needed | — |

---

## 3. Relative Path Rules

`proposal.md` and the task files live in the **same folder** as `spec.md`, so the spec link is always a sibling reference:

```
proposal.md    →  ./spec.md
infra-tasks.md →  ./spec.md
code-tasks.md  →  ./spec.md
unit-tests-tasks.md → ./spec.md
```

Always use `./spec.md` when linking to the spec from any output file.

---

## 4. Spec Type and Phase Set

The input `spec.md` declares its type in the `> **Type:**` header. **Read this before writing any output** — it determines which phases appear in the generated task file(s) and what belongs in scope.

| Spec type | `proposal.md` Scope | Task file phases |
|-----------|--------------------|--------------------|
| `Code` | Business logic, hexagonal modules. Infrastructure is **out of scope** (covered by companion Infra spec). | `code-tasks.md`: Spec & Alignment → Implementation → Review; `unit-tests-tasks.md`: Testing → Review |
| `Infra` | SAM resources (queues, tables, Lambda config), IAM, minimal Lambda stub. Business logic is **out of scope**. | `infra-tasks.md`: Spec & Alignment → Infrastructure → Review |

Never mix phases: no `## Infrastructure` in a Code bundle; no `## Implementation` or `## Testing` in an Infra bundle.

---

## 5. `proposal.md` Structure

```markdown
# <Change intent — one line>

**Ticket:** <JIRA-KEY>

## Goal

- <bullet: concrete operational change — include details the spec actually defines, e.g. guard logic, data-write semantics, idempotency contracts, or resource names; only include what the spec states, never assume values not present in the requirements>
- <bullet>

## Scope

- <in-scope bullet — include SQS/DynamoDB/Lambda infra when the change creates those resources>

**Out of scope**

- <out-of-scope bullet>

## Spec

[./spec.md](./spec.md) — satisfies:

- **Requirement: <verbatim heading text>** / Scenario: <verbatim scenario heading text>
- **Requirement: <verbatim heading text>**

> Always use verbatim heading text. Never use bare REQ-N numbers.

## Artifacts

Artifacts are listed in `./spec.md#references`; verify all expected paths exist before starting implementation.

New files this change will create:

- `<path/to/file>` — <one-line description of purpose>
- `<path/to/file>` — <one-line description of purpose>

> Only list files **not** already in `./spec.md#references`. Do not repeat expected artifact paths from the spec.

## Risks / Open questions

- <risk or gap, if any>
```

---

## 6. `code-tasks.md` and `unit-tests-tasks.md` Structure — Code spec

```markdown
# Tasks — <Change intent> (code-tasks.md)

> Spec: [./spec.md](./spec.md)

## Spec & Alignment

- [ ] Confirm artifact paths in `./spec.md#references` resolve to real files
- [ ] Verify event schema defines all event types consumed by this service (Requirement: <REQ heading text>)
- [ ] <any concurrency / design decision to clarify before implementation> (Requirement: <REQ heading text> — Scenario: <scenario heading text>)

## Implementation

- [ ] Create `<module>/configuration.py`: define config DTOs with field mappings (Requirement: <REQ heading text>)
- [ ] Create `<module>/port/repository.py`: abstract `Repository` with methods `<list>` (Requirement: <REQ heading text>)
- [ ] Create `<module>/adapter/ddb_repository.py`: `DynamoDbRepository` implementing `Repository` (Requirement: <REQ heading text>)
- [ ] Create `<module>/domain/service.py`: `Service` routing by entityType / eventType; applies guards; validates before processing (Requirement: <REQ heading text>)
- [ ] Implement handler for `<EVENT_TYPE>` in `service.py` (Requirement: <REQ heading text> — Scenario: <scenario heading text>)
- [ ] Create `app.py` Lambda entry point: wire dependencies and call service (Requirement: <REQ heading text>)

```

```markdown
# Tasks — <Change intent> (unit-tests-tasks.md)

> Spec: [./spec.md](./spec.md)

## Testing

- [ ] Unit test: <verbatim scenario heading text> (Scenario: <verbatim scenario heading text>)
- [ ] Unit test: <verbatim scenario heading text> (Scenario: <verbatim scenario heading text>)
- [ ] Integration test: <specific integration concern> (Requirement: <REQ heading text>)


```

---

## 7. `infra-tasks.md` Structure — Infra spec

```markdown
# Tasks — <Change intent>

> Spec: [./spec.md](./spec.md)

## Spec & Alignment

- [ ] Confirm artifact paths in `./spec.md#references` resolve to real files
- [ ] Confirm cross-account / cross-service dependencies (e.g. SNS topic ARN, account IDs) before writing SAM template (Requirement: <REQ heading text>)
- [ ] Confirm per-environment config values (e.g. ReservedConcurrentExecutions) with the team (Requirement: <REQ heading text>)

## Infrastructure

- [ ] Define `<dlqueue-name>` SQS FIFO DLQ in `template.yaml`: `ContentBasedDeduplication`, `MessageRetentionPeriod`, `maxReceiveCount` (Requirement: <REQ heading text>)
- [ ] Define `<queue-name>` SQS FIFO main queue in `template.yaml`: `VisibilityTimeout`, redrive policy pointing to DLQ (Requirement: <REQ heading text>)
- [ ] Add SNS subscription in `template.yaml` with filter policy (Requirement: <REQ heading text>)
- [ ] Define `<table-name>` DynamoDB global table in `template.yaml`: PK, GSIs, streams, TTL attributes (Requirement: <REQ heading text>)
- [ ] Define `<lambda-name>` Lambda in `template.yaml`: runtime, arch, MemorySize, Timeout, layers, event source mapping (Requirement: <REQ heading text>)
- [ ] Set per-environment `ReservedConcurrentExecutions` mapping in `template.yaml` (Requirement: <REQ heading text>)
- [ ] Add IAM policy to Lambda in `template.yaml`: SQS read permissions, DynamoDB write permissions (Requirement: <REQ heading text>)
- [ ] Create minimal `app.py` Lambda stub sufficient for SAM deployment (Requirement: <REQ heading text>)

```

---

## 9. `design.md` Structure (optional)

Add only when a real architectural decision must be recorded.

```markdown
# Design — <decision topic>

## Decision

<One paragraph describing the chosen approach.>

## Alternatives

- <Alternative A> — <why rejected>
- <Alternative B> — <why rejected>

## Consequences

- <Trade-off or follow-up task>
- <Trade-off or follow-up task>
```

---

## 11. Examples

| Spec type | proposal.md | code-tasks.md | unit-tests-tasks.md | infra-tasks.md |
|-----------|------------|----------------|----------------------|----------------|
| Code | [saml-user-cache-consumer-code-proposal.md](examples/saml-user-cache-consumer-code-proposal.md) | [saml-user-cache-consumer-code-tasks.md](examples/saml-user-cache-consumer-code-tasks.md) | [saml-user-cache-consumer-unit-tests-tasks.md](examples/saml-user-cache-consumer-unit-tests-tasks.md) | — |
| Infra | [saml-user-cache-consumer-infra-proposal.md](examples/saml-user-cache-consumer-infra-proposal.md) | — | — | [saml-user-cache-consumer-infra-tasks.md](examples/saml-user-cache-consumer-infra-tasks.md) |

---

## 10. Anti-Patterns

- Linking to `spec.md` by absolute path — always use `./spec.md`.
- Creating a `changes/` subfolder — output files go directly alongside `spec.md`.
- Naming tasks with no file, module, config key, or requirement reference — every task must be verifiable.
- A single "Add unit tests" task — write one task per scenario, naming the scenario explicitly.
- Adding `design.md` for every change — only when there is a genuine decision fork.
- Pasting JSON Schema, DynamoDB attribute lists, or OpenAPI parameter tables into any output file.
- Tasks that paraphrase a requirement without naming a specific file, method, or config value.
- Using bare `REQ-N` numbers in the `## Spec` section of `proposal.md` — always use verbatim heading text.
- Omitting `**Ticket:** <JIRA-KEY>` from `proposal.md` — every proposal must be traceable.
- Including `## Infrastructure` tasks in a Code spec bundle — infrastructure belongs in the companion Infra spec bundle.
- Including `## Implementation` or `## Testing` tasks in an Infra spec bundle — business logic belongs in the companion Code spec bundle.
- Putting infrastructure in scope for a Code spec, or business logic in scope for an Infra spec.
- Leaving the Artifacts section as only a deferral note when new files will be created — list every new output file explicitly.
