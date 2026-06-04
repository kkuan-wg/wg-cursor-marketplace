---
name: council-v2
description: Maintain and query persistent project truth docs (.sdd/docs). Bootstrap, --refresh, knowledge Q&A, and optional pivot to /sdd-start. Complements /council (parallel exploration). Stack-agnostic.
---

# council-v2

Maintain and query the project's **living truth docs** so other agents and commands do not re-explore the codebase on every call. Complement to (not a replacement for) `/council`.

## When to use which

| Command | Use when |
| --- | --- |
| **`/council-v2`** | Bootstrap or refresh truth docs, routine "where does X live?", cheap knowledge Q&A between sessions |
| **`/council`** | One-shot parallel exploration (unfamiliar code, debugging, deep dives the truth docs do not cover) |

## Context

- **Process:** Specs-Driven Design — see `@wg-sdd-kit-plugin/rules/specs-driven-design.md` and `@wg-sdd-kit-plugin/agents/backlog_architect.md`.
- **Stack:** Detect from the workspace (`package.json`, `pyproject.toml`, `*.csproj`, `pom.xml` / `build.gradle.kts`, etc.) and document boundaries (UI, API, data, infra) without assuming a single framework.

## Truth docs (under `.sdd/docs/`)

- **`project_knowledge.md`** — architecture, modules, contracts, conventions, glossary, existing features.
- **`project_deployment_knowledge.md`** — environments, pipelines, infra, runtime topology, secrets *locations* (never values), rollback.

If the project also uses **`/finish-story`** or **`/finish-task`** commands (from a stack starter kit), those should incrementally update these docs. Otherwise, use **`/council-v2 --refresh`** after major refactors.

## Behaviour (always runs in this order)

### Step 0 — Truth-doc precondition (unconditional)

1. Look for `.sdd/docs/project_knowledge.md` and `.sdd/docs/project_deployment_knowledge.md`.
2. If **either** is missing, explore the codebase and **create the missing doc(s) now**. Announce: *"Project truth docs are missing. Generating `.sdd/docs/project_knowledge.md` and `.sdd/docs/project_deployment_knowledge.md` first (one-time setup) — this informs everything that follows."*
3. If both exist, read them into context.

### Step 1 — Branch on the prompt

| Prompt shape | Action |
| --- | --- |
| No content (just `/council-v2`) | Print a summary: paths to the truth docs and what was created/read. |
| `--refresh`, `--refresh code`, or `--refresh deploy` | **Force regenerate** the named doc(s). Update timestamp + git SHA. |
| Feature-planning intent (see signals below) | **Pivot to `/sdd-start`** (Step 2 below). |
| Knowledge question | Answer from the truth docs. Append only **durable project facts** — not feature-specific detail. |

### Step 2 — Feature-planning pivot (when detected)

**Detection signals:** "I want to build / implement / plan / add a feature…", "thinking about requirements…", "let's build…", etc.

When detected (after Step 0):

1. Announce: *"This looks like a new feature. Running the SDD spec flow per `/sdd-start` so you get a proper `feature_spec.md` and a review gate."*
2. Attach `@wg-sdd-kit-plugin/commands/sdd-start.md`, `@wg-sdd-kit-plugin/rules/sdd-workflow-orchestration.md`, `@wg-sdd-kit-plugin/rules/specs-driven-design.md`, and `@wg-sdd-kit-plugin/examples/example_feature_spec.md`.
3. Execute **Step 1 of the gated workflow** only:
   - Derive `output/{project-name}/` (kebab-case project name from the description; confirm if ambiguous).
   - Write **only** `output/{project-name}/feature_spec.md` (Problem / Goals / Non-Goals / Constraints / User Acceptance / Conceptual APIs / Observability) — informed by truth docs from Step 0.
4. **STOP for review.** Do NOT generate backlog, plan, code, or tests in this turn.
5. Print: *"Feature spec is ready at `output/{project-name}/feature_spec.md`. Confirm to proceed to Step 2 (backlog)."*

**WIN layout:** If the team uses `.sdd/features/pending/<feature-identifier>/` instead of `output/`, write `feature_spec.md` there and state the path clearly.

## Quick reference

| Invocation | What you get |
| --- | --- |
| `/council-v2` (first run) | Both truth docs generated. |
| `/council-v2 "<question>"` | Answers from docs; creates docs if missing. |
| `/council-v2 --refresh` | Regenerate both truth docs. |
| `/council-v2 --refresh code` / `--refresh deploy` | Regenerate one doc only. |
| `/council-v2 I want to build…` | Truth docs + `/sdd-start` Step 1 only → STOP. |

**Stale docs after a major refactor:** `/council-v2 --refresh`.

## Coverage standard

After `--refresh`, a reviewer should answer from the docs alone (no grep): what the project does today; where typical request/handler/UI code lives; auth/RBAC/logging; external integrations and env vars; how to run tests; build/deploy/rollback; domain glossary.

Mark unknown sections **TBD** — do not omit them.

## Doc shapes

Use the section outlines in the stack starter kits' `council-v2` command (Architecture overview, Module map, Existing features, Key contracts, External integrations, Cross-cutting concerns, Testing, Build, Configuration, Conventions, Glossary; plus deployment sections in `project_deployment_knowledge.md`). Link to stack-specific rules/plugins — do not duplicate rule bodies here.

## Routing rules (for finish-story / finish-task if present)

- **Deployment doc:** `infra/**`, `deploy/**`, `terraform/**`, `cdk/**`, `**/k8s/**`, `**/Jenkinsfile*`, `**/Dockerfile*`, `**/.github/workflows/**`.
- **Code doc:** everything else.

## Examples

```
/council-v2
/council-v2 "where is tenant scoping enforced?"
/council-v2 --refresh
/council-v2 --refresh deploy
/council-v2 I want to add saved views to the reports dashboard
```
