---
name: authpt-java-code-impl
description: >-
  Implements Java Spring Boot code from spec.md and code-tasks.md using
  AGENTS.md and project rules (java-package-map.mdc, java-design-patterns.mdc,
  java-spring-properties-injection.mdc)
  as guardrails. Use when implementing authpt Code specs, code-tasks.md
  Implementation phase, aaas-user-middleware APIs or SQS consumers, or when
  the user asks to implement from a spec bundle in a Java middleware repo.
---

# AuthPoint Java Code Implementation

Implements **Code spec** business logic from `spec.md` + `code-tasks.md`, using project rules as guardrails. Covers `## Spec & Alignment` and `## Implementation` only — **not** `unit-tests-tasks.md` or `infra-tasks.md`.

**Gate:** Do **not** write or edit implementation code until Phase 2 has loaded all three project rules **and** `~/.cursor/rules/java-spring-properties-injection.mdc` (properties triad). Re-read that rule when a task adds or changes external keys.

## When to use

- User provides or references a spec bundle folder (`spec.md`, `code-tasks.md`)
- User asks to implement authpt Code tasks in a Java middleware repo
- `java-spring-developer` is invoked with a spec path

## Additional resources

- Guardrail checklist: [reference/guardrail-checklist.md](reference/guardrail-checklist.md)

---

## Phase 1: Parse (mandatory before writing code)

Read files **co-located** with the spec (same folder as `spec.md`):

| File | Extract |
|------|---------|
| `spec.md` | Requirements/scenarios, HTTP paths, SQS queues, SNS topics, persistence, RBAC, `## References` artifacts |
| `proposal.md` | Domain, new artifacts, Code vs Infra scope, **Out of scope** |
| `code-tasks.md` | Checkbox tasks in `## Spec & Alignment` and `## Implementation`; traceability `(Requirement: ...)` / `(Scenario: ...)` |

**Stop** if `spec.md` or `code-tasks.md` is missing — hand off to **authpt-impl** or **ssot-spec-writer**.

**Reject** infra-only tasks in `code-tasks.md` — they belong in the companion Infra spec (`infra-tasks.md`).

Read linked artifacts from `spec.md ## References` when tasks name concrete classes, queues, or property keys.

---

## Phase 2: Repo discovery (via AGENTS.md)

Walk up from the spec path (or workspace root) until you find the target Java repo:

1. Find `AGENTS.md` at repo root — read it for rule paths and flow docs
2. If no `AGENTS.md`: find first `.cursor/rules/java-package-map.mdc` walking up from spec path
3. Read **entirely** (mandatory before any implementation):
   - `.cursor/rules/java-package-map.mdc` — **where** to place code
   - `.cursor/rules/java-design-patterns.mdc` — **how** to implement
   - `~/.cursor/rules/java-spring-properties-injection.mdc` — triad `scripts/run.sh` / `application.properties` / `configuration/` (always; not only for AWS tasks)
   - Or project copy at `.cursor/rules/java-spring-properties-injection.mdc` if present (same content)
4. If the repo has `.cursor/docs/java-properties-registry.md`, skim it for existing ENV → key → config mappings
5. Validate `project-id` / `base-package` in rule frontmatter matches the repo

Conditional flow docs (read by work type):

- `.cursor/docs/api-implementation-flow.md` — REST APIs
- `.cursor/docs/consumer-implementation-flow.md` — SQS consumers

Expanded patterns reference (optional): `.cursor/docs/design-patterns-by-package.md`

---

## Phase 3: Guardrails (mandatory per task)

Before creating or modifying any class, validate against all rules loaded in Phase 2, including `~/.cursor/rules/java-spring-properties-injection.mdc`. Full checklist: [reference/guardrail-checklist.md](reference/guardrail-checklist.md).

**Package map (where):**

- Package matches "Onde colocar código novo" table
- Dependencies respect "Regras de dependência" (`persistence` must not import `api` or `cache`)
- Reuse closest existing domain — no parallel packages

**Design patterns (how):**

- Correct class suffix (`*Controller`, `*Listener`, `*Handler`, `*Publisher`, etc.)
- Correct pipeline for work type
- Parser direction: inbound JSON→object vs outbound object→JSON
- Domain exceptions in `{package}/exception/`; handlers extend `BaseExceptionHandler`
- DI: `@RequiredArgsConstructor`; logging: `@Slf4j`

**Properties injection (always apply rule; deepen checklist when task touches SQS, SNS, DDB, datasource, region, or `@Configuration`):**

- No new hardcoded queue/topic/endpoint/ARN outside `configuration/`
- When adding or changing keys: triad `application.properties` → `scripts/run.sh` (deploy branch) → `@Value` / `@SqsListener` in `configuration/`
- Mirror cloud/local property keys; match `@Profile` to `configuration/cloud` vs `configuration/local`
- Project registry (if present): `.cursor/docs/java-properties-registry.md`

**If a task conflicts with the rules**, do not invent a new package — flag the conflict and align with the rules or ask the user.

---

## Phase 4: Implementation

**Prerequisite:** Phases 1–2 complete and `java-spring-properties-injection.mdc` read. If implementation was started without that rule, stop, read it, then continue.

Execute tasks in order:

1. **`## Spec & Alignment`** — contract alignment, RBAC entries, property keys, reference verification
2. **`## Implementation`** — create/modify Java classes

Per-task rules:

- REST paths → `api/ApiConstants.java` (not hardcoded in controller)
- Public API RBAC → `src/main/resources/rbac.json` (not in controller)
- Thin controllers/listeners — business logic in `*Service` or `*Handler`
- No business logic in `publisher/`, `configuration/`, or `persistence/`
- Never create or modify `src/test/**` (unit tests, integration tests, test builders, fixtures) — out of scope for this skill and for `authpt-code-writer`

Mark each completed task; re-run guardrails after each artifact.

---

## Phase 5: Verify before finishing

- [ ] Every `## Implementation` task addressed or explicitly blocked with reason
- [ ] No classes outside packages allowed by `java-package-map.mdc`
- [ ] Suffixes and pipelines match `java-design-patterns.mdc`
- [ ] Dependency rules not violated
- [ ] No business logic in `publisher/`, `configuration/`, or fat controllers
- [ ] Spec gaps noted — not invented
- [ ] Infra tasks not implemented here (companion Infra spec)
- [ ] Triad aligned for every new external property key (properties → run.sh → configuration)
- [ ] No hardcoded infrastructure identifiers outside `configuration/`

---

## Anti-patterns

- Starting implementation without reading package map, design patterns, and `~/.cursor/rules/java-spring-properties-injection.mdc`
- Skipping the properties-injection rule before Phase 6 (even for “API-only” specs)
- Placing REST controllers in `cache/` or listeners in `api/`
- Creating parallel domains outside the package map
- Copying sibling **package names** instead of **patterns**
- Implementing `unit-tests-tasks.md`, integration tests, or `infra-tasks.md` under this skill
- Creating or editing anything under `src/test/**`
- Inventing requirements not in `spec.md`
- RBAC logic inside controllers instead of `rbac.json` + interceptors
