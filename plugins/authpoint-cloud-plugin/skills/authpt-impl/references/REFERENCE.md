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
            spec.md              ← source spec (read-only from this skill)
            proposal.md          ← required
            infra-tasks.md       ← required for Infra specs
            code-tasks.md        ← required for Code specs
            unit-tests-tasks.md  ← required for Code specs
            design.md            ← optional
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
proposal.md          →  ./spec.md
infra-tasks.md       →  ./spec.md
code-tasks.md        →  ./spec.md
unit-tests-tasks.md  →  ./spec.md
```

Always use `./spec.md` when linking to the spec from any output file.

---

## 4. Spec Type and Phase Set

The input `spec.md` declares its type in the `> **Type:**` header. **Read this before writing any output** — it determines which phases appear in the generated task file(s) and what belongs in scope.

| Spec type | `proposal.md` Scope | Task file phases |
|-----------|--------------------|--------------------|
| `Code` | Business logic, MVC, Service Layer, Repository, DTO, validators, publishers, consumers. Infrastructure is **out of scope** (covered by companion Infra spec). | `code-tasks.md`: Spec & Alignment → Implementation; `unit-tests-tasks.md`: Testing |
| `Infra` | CloudFormation resources (ECS task/service definitions, CloudWatch alarms, IAM roles), deploy layer (`run.py` + `daasdeployhelpers`). Business logic is **out of scope**. | `infra-tasks.md`: Spec & Alignment → Infrastructure |

Never mix phases: no `## Infrastructure` in a Code bundle; no `## Implementation` or `## Testing` in an Infra bundle. No `## Review` phase in any task file.

---

## 5. `proposal.md` Structure

```markdown
# <Change intent — one line>

**Ticket:** <JIRA-KEY>

## Goal

- <bullet: concrete operational change — include details the spec actually defines, e.g. guard logic, data-write semantics, idempotency contracts, or resource names; only include what the spec states, never assume values not present in the requirements>
- <bullet>

## Scope

- <in-scope bullet — include ECS/CloudWatch/IAM infra when the change creates those resources>

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

- [ ] Create `<package>/config/<Name>Config.java`: define Spring configuration with @ConfigurationProperties or @Value bindings (Requirement: <REQ heading text>)
- [ ] Create `<package>/controller/<Name>Controller.java`: REST controller with endpoint mappings (Requirement: <REQ heading text>)
- [ ] Create `<package>/service/<Name>Service.java`: service interface (Requirement: <REQ heading text>)
- [ ] Create `<package>/service/<Name>ServiceImpl.java`: service implementation with business logic (Requirement: <REQ heading text>)
- [ ] Create `<package>/repository/<Name>Repository.java`: JPA repository interface (Requirement: <REQ heading text>)
- [ ] Create `<package>/dto/<Name>Request.java`: request DTO (Requirement: <REQ heading text>)
- [ ] Create `<package>/dto/<Name>Response.java`: response DTO (Requirement: <REQ heading text>)
- [ ] Create `<package>/publisher/<Name>Publisher.java`: SNS topic publisher (Requirement: <REQ heading text>)
- [ ] Create `<package>/listener/<Name>Listener.java`: SQS message listener (Requirement: <REQ heading text>)
- [ ] Implement handler for `<EVENT_TYPE>` in `<Name>ServiceImpl.java` (Requirement: <REQ heading text> — Scenario: <scenario heading text>)

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
- [ ] Confirm cross-account / cross-service dependencies before writing CloudFormation template (Requirement: <REQ heading text>)
- [ ] Confirm per-environment config values with the team (Requirement: <REQ heading text>)

## Infrastructure

- [ ] Define ECS task definition in CloudFormation: container image, CPU/memory, environment variables (Requirement: <REQ heading text>)
- [ ] Define ECS service in CloudFormation: desired count, load balancer target group, deployment configuration (Requirement: <REQ heading text>)
- [ ] Define CloudWatch alarms: CPU/memory utilization thresholds, error rate alarms (Requirement: <REQ heading text>)
- [ ] Define IAM roles and policies: task execution role, task role with required permissions (Requirement: <REQ heading text>)
- [ ] Update `run.py` deploy script with new service configuration (Requirement: <REQ heading text>)
- [ ] Add profile-based property file entries (e.g. `application-<env>.properties`) for new configuration keys (Requirement: <REQ heading text>)

```

---

## 8. `design.md` Structure (optional)

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

## 9. Anti-Patterns

- Linking to `spec.md` by absolute path — always use `./spec.md`.
- Creating a `changes/` subfolder — output files go directly alongside `spec.md`.
- Naming tasks with no file, module, config key, or requirement reference — every task must be verifiable.
- A single "Add unit tests" task — write one task per scenario, naming the scenario explicitly.
- Writing a single `tasks.md` for a Code spec — Code bundles must split into `code-tasks.md` + `unit-tests-tasks.md`.
- Including a `## Testing` section in `code-tasks.md` — tests belong only in `unit-tests-tasks.md`.
- Including a `## Review` section in any task file — Review is not part of the phase set.
- Adding `design.md` for every change — only when there is a genuine decision fork.
- Pasting JSON Schema, DynamoDB attribute lists, or OpenAPI parameter tables into any output file.
- Tasks that paraphrase a requirement without naming a specific file, method, or config value.
- Using bare `REQ-N` numbers in the `## Spec` section of `proposal.md` — always use verbatim heading text.
- Omitting `**Ticket:** <JIRA-KEY>` from `proposal.md` — every proposal must be traceable.
- Including `## Infrastructure` tasks in a Code spec bundle — infrastructure belongs in the companion Infra spec bundle.
- Including `## Implementation` or `## Testing` tasks in an Infra spec bundle — business logic belongs in the companion Code spec bundle.
- Putting infrastructure in scope for a Code spec, or business logic in scope for an Infra spec.
- Leaving the Artifacts section as only a deferral note when new files will be created — list every new output file explicitly.
