---
name: authpt-java-code-impl
description: >-
  Implements Java Spring Boot code from spec.md and code-tasks.md using
  AGENTS.md, repo rules (java-package-map.mdc, java-design-patterns.mdc), and
  authpoint-cloud-plugin rule java-spring-properties-injection.mdc. Use for
  authpt Code specs, code-tasks.md Implementation phase, or Java middleware
  implementation from a spec bundle.
---

# AuthPoint Java Code Implementation

Code spec implementation from `spec.md` + `code-tasks.md` only (`## Spec & Alignment`, `## Implementation`). Out of scope: `unit-tests-tasks.md`, `infra-tasks.md`, `src/test/**`.

**Gate:** No implementation edits until Phase 2 completes: all three guardrail rules read entirely and applied from Phase 3 onward. Re-read [`java-spring-properties-injection.mdc`](../../rules/java-spring-properties-injection.mdc) when external keys change. If code was edited before the gate, stop, finish Phase 2, then continue.

Checklist: [reference/guardrail-checklist.md](reference/guardrail-checklist.md)

---

## Phase 1: Parse

Read co-located with `spec.md`: `spec.md`, `proposal.md`, `code-tasks.md`.

| File | Extract |
|------|---------|
| `spec.md` | Requirements/scenarios, HTTP/SQS/SNS/persistence/RBAC, `## References` |
| `proposal.md` | Domain, artifacts, scope, out of scope |
| `code-tasks.md` | Tasks under `## Spec & Alignment` and `## Implementation` |

**Stop** without `spec.md` or `code-tasks.md` → **authpt-impl** / **ssot-spec-writer**. Reject infra-only tasks (→ Infra spec). Follow `## References` for named classes, queues, or keys.

---

## Phase 2: Repo discovery and guardrails

Walk up from spec path to the target Java repo. **Read entirely** every rule below before Phase 4; **apply** them in Phases 3–5 via [guardrail-checklist.md](reference/guardrail-checklist.md).

| Source | Rule | Apply as |
|--------|------|----------|
| Target repo `.cursor/rules/` | `java-package-map.mdc` | packages, dependencies |
| Target repo `.cursor/rules/` | `java-design-patterns.mdc` | suffixes, pipelines, parsers |
| **authpoint-cloud-plugin** `rules/` | [`java-spring-properties-injection.mdc`](../../rules/java-spring-properties-injection.mdc) | property triad |

1. Read `AGENTS.md` (or locate `.cursor/rules/java-package-map.mdc`)
2. Read all three rules in the table (full file, not skim)
3. Skim `java-properties-registry.md` if present; validate rule `project-id` / `base-package`

Optional by work type: `api-implementation-flow.md`, `consumer-implementation-flow.md`, `design-patterns-by-package.md`

---

## Phase 3: Apply guardrails (per artifact)

Before each create/edit, apply the Phase 2 rules using [guardrail-checklist.md](reference/guardrail-checklist.md). On conflict, do not invent packages — align with the rules or ask the user.

---

## Phase 4: Implementation

Execute `code-tasks.md` in order:

1. `## Spec & Alignment` — contracts, RBAC, property keys, references
2. `## Implementation` — Java classes

- Paths → `api/ApiConstants.java`; public RBAC → `rbac.json`
- Thin controllers/listeners; logic in `*Service` / `*Handler`
- No business logic in `publisher/`, `configuration/`, `persistence/`
- Re-run guardrails after each artifact

---

## Phase 5: Verify

- [ ] All `## Implementation` tasks done or blocked with reason
- [ ] `java-package-map.mdc`, `java-design-patterns.mdc`, and plugin properties rule satisfied
- [ ] No business logic in `publisher/`, `configuration/`, fat controllers
- [ ] Property triad for every new external key (see plugin rule)
- [ ] No infra/unit/integration test work; spec gaps not invented

---

## Anti-patterns

- Editing code before Phase 2 completes (`.cursor/rules/java-package-map.mdc`, `.cursor/rules/java-design-patterns.mdc`, plugin [`java-spring-properties-injection.mdc`](../../rules/java-spring-properties-injection.mdc) not read in full)
- Skipping Phase 3 checklist application (including “API-only” specs without the properties rule)
- REST in `cache/`, listeners in `api/`, parallel domains, copied package names instead of patterns
- RBAC in controllers; requirements not in `spec.md`; `unit-tests-tasks.md`, `infra-tasks.md`, or anything under `src/test/**`
