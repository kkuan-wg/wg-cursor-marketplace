---
name: council
description: Broad codebase exploration with parallel agents — SDD-aware. Spawns multiple task agents to investigate an area of interest before answering or planning.
---

# council

Use this command when you need **broad codebase exploration** before answering or planning.

## Context

- **Process:** This project uses **Specs-Driven Design (SDD)** — specs, `REQ-...` IDs, stories, and `plan.md` / `tasks.md` before implementation (see `@wg-sdd-kit-plugin/rules/specs-driven-design.md` and `@wg-sdd-kit-plugin/agents/backlog_architect.md`).
- **Stack:** Detect the stack from the workspace (look for `package.json`, `pyproject.toml`, `pom.xml`, etc.) and tie findings to the relevant architectural layers.

When reporting findings, tie discoveries to **architecture** (frontend modules/routes vs backend services/modules, data layer, infra) and, if relevant, to **traceability** (spec sections, `REQ-...` IDs).

## Steps

Based on the given area of interest:

1. Dig around the codebase for that area; gather keywords and an **architecture overview** (frontend vs backend boundaries, shared contracts).
2. Spawn **n = 10** task agents to dig deeper (unless the user specifies another **n**), with **variety** in exploration paths (e.g. UI, API, data, tests, infra, build/CI).
3. Use the collected information to do what the user requested.
4. If in **plan mode**, use the information to build the plan **in line with SDD** (scope, risks, tasks mapped to specs).

## Example usage

```
/council n=15 how does authentication work?
/council map all ViewModels and their navigation targets
/council n=5 getting this error, investigate
/council Map out the data flow from login to dashboard
/council Show me every place we touch DocumentDb
```

---

## Related: `/council-v2` (persistent project knowledge)

For a **persistent knowledge cache** (`.sdd/docs/project_knowledge.md`, `project_deployment_knowledge.md`) that cheaply answers "where does X live?" between sessions, use [`council-v2.md`](council-v2.md). Supports `--refresh` after major refactors. `/council-v2` complements `/council`; both can be used in the same session.

**Brownfield SDD:** run `/council-v2` once (bootstrap truth docs), then `/sdd-start` for the feature.
