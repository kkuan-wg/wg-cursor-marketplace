---
name: sdd-start
description: Start the Specs-Driven Development (SDD) workflow for a new feature or initiative. Activates the stepped gated workflow (feature spec -> backlog -> plan -> publish) with mandatory review between steps.
---

# sdd-start

Begin a **Specs-Driven Development** cycle for a new feature, initiative, or large change.

This command activates the **gated workflow** defined in `@wg-sdd-kit-plugin/rules/sdd-workflow-orchestration.md`: the agent will produce **one artifact at a time** and STOP for review between steps. No code is written until the spec and plan are approved.

## Usage

```
/sdd-start <short feature description>
```

Examples:

```
/sdd-start internal AI agent portal with SSO and public/private agents
/sdd-start per-tenant data residency for MySQL-backed APIs
/sdd-start saved views for the reports dashboard
```

## What happens

1. **Step 1 — Feature spec.** The agent writes `output/{project-name}/feature_spec.md` with problem, goals/non-goals, constraints, user acceptance criteria, conceptual APIs, observability, and assumptions. Then **stops** for your review.

2. **Step 2 — Backlog.** After you confirm the spec (e.g. "approved", "looks good"), the agent writes `requirements.md` (REQ-... IDs), `svs.md` (Smallest Valuable Slice), and `stories.md` (user stories with Gherkin AC, NFRs). Then **stops**.

3. **Step 3 — Plan.** After you confirm the backlog, the agent writes `plan.md` (task breakdown, dependencies, deployment order, risks). Then **stops**.

4. **Step 4 — Publish (optional).** If you request it, the agent generates `initiative_confluence.md` and/or Jira YAML via `@wg-sdd-kit-plugin/skills/jira-epic-story-task-automation/SKILL.md`.

All artifacts go to `output/{project-name}/` in the current workspace.

## Escape hatches

- **Skip steps:** Tell the agent explicitly, e.g. "skip to plan", "generate everything at once".
- **Standalone agents:** You can `@`-mention any SDD agent at any time without advancing the workflow. See `@wg-sdd-kit-plugin/rules/sdd-workflow-orchestration.md` for the full list.
- **Brownfield:** Run `/council-v2` once to bootstrap `.sdd/docs/` truth docs (or `/council` for a one-shot deep dive), then `/sdd-start` with that context.

## When NOT to use this

- One-line bug fixes, config tweaks, or research spikes — just code.
- Small stories where you already have AC and just need to implement.

For small work, the SDD ceremony is pure overhead. Use this command for **mid-to-large features** where scope is expensive to get wrong.
