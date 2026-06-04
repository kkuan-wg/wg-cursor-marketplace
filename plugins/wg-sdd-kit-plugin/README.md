# sdd-plugin

> **Specs-Driven Development (SDD) for Cursor** — a gated workflow that forces specs and backlog to be agreed *before* code is written. Stack-agnostic.

Derived from the [`python-sdd-starter-kit`](../python-sdd-starter-kit/) and repackaged as a **Cursor plugin** so teams can install it once, get updates centrally, and stop maintaining N forks of `.cursor/` across repos.

---

## What's in the plugin

```
sdd-plugin/
├── .cursor-plugin/
│   └── plugin.json              Plugin manifest
├── rules/                       Always-on + on-demand rules
│   ├── specs-driven-design.md         (always-on, principles)
│   ├── sdd-workflow-orchestration.md  (on-demand, gated workflow)
│   ├── output-config.md               (always-on, output/ folder)
│   └── documentation.md               (by glob, *.md + openapi)
├── agents/                      SDD roles invoked via @-mention
│   ├── backlog_architect.md           SVS, stories, Gherkin
│   ├── technical_analyst.md           Feasibility, risk, estimates
│   ├── technical-devils-advocate.md   Challenge assumptions
│   ├── prd-gap-analysis.md              Pre-SDD P1 — PRD gap analysis
│   ├── prd-market-owner-devils-advocate.md  Pre-SDD P2 — Market Owner DA
│   ├── prd-product-owner-devils-advocate.md Pre-SDD P3 — Product Owner DA
│   ├── qa_test_design_agent.md        TC-... cases mapped to AC
│   ├── developer_testing_agent.md     UT-... for devs
│   ├── doc_review_assistant.md        PR vs AC, release notes
│   └── epic_initiative_confluence.md  Confluence publish via MCP
├── commands/
│   ├── sdd-start.md             /sdd-start — SDD entry point
│   ├── council-v2.md            /council-v2 — truth docs + refresh (default brownfield)
│   └── council.md               /council — parallel exploration
├── templates/                   Story, SVS, Gherkin, release notes...
├── examples/                    Reference spec, story, SDLC patterns
└── skills/
    ├── jira-epic-story-task-automation/   Jira hierarchy automation
    ├── security-threat-model/             Gate 2.5 STRIDE (stack-agnostic)
    ├── security-code-review/              Per-story review before PR
    └── secrets-audit/                     PR / periodic secrets scan
```

---

## Installation

### Option 1: Local (for testing)

Copy this directory to `~/.cursor/plugins/local/wg-sdd-kit-plugin/`:

```bash
cp -r cursor/sdd-plugin ~/.cursor/plugins/local/wg-sdd-kit-plugin
```

Cursor will auto-discover it on next restart. Verify with **Cursor Settings -> Plugins**.

### Option 2: Internal marketplace / git

If your team publishes Cursor plugins via git or an internal marketplace, point your marketplace manifest at this directory. Versioning is governed by `.cursor-plugin/plugin.json`.

---

## WatchGuard SDLC (at a glance)

| Phase | AI in this plugin |
| --- | --- |
| **Pre-SDD (PRD)** | P1 `prd-gap-analysis`, P2 `prd-market-owner-devils-advocate`, P3 `prd-product-owner-devils-advocate` (chat only) |
| **Feature spec** | `/sdd-start` Step 1; Gate 1.5 `technical-devils-advocate` (recommended) |
| **Backlog** | `backlog_architect`; Gate 2.5 `security-threat-model` (recommended); Gate 3.5 DA on stories |
| **Code & PR** | `security-code-review` per story; `secrets-audit` at PR gate |

Truth docs: **`/council-v2`** maintains `.sdd/docs/project_knowledge.md` + `project_deployment_knowledge.md`. **`/council`** is for one-shot parallel exploration.

---

## Quick start

1. Install the plugin (above).
2. **Brownfield:** run `/council-v2` once to bootstrap truth docs.
3. **With a PRD:** run Pre-SDD agents (`@wg-sdd-kit-plugin/agents/prd-gap-analysis.md`, etc.) before SDD.
4. Start SDD:

   ```
   /sdd-start build a saved-views feature for the reports dashboard
   ```

5. The agent writes `output/saved-views-feature/feature_spec.md` and **stops** for your review.
6. Approve ("looks good", "proceed") and it moves to Step 2 (backlog). And so on through Plan and Publish.

All SDD artifacts land under `<your-project>/output/{project-name}/`. Security threat models go under `output/{project-name}/security/` (or `.sdd/features/pending/.../security/` if your team uses the WIN layout).

---

## The 4-step gated workflow

| Step | Output | Gate |
|---|---|---|
| 1. Feature spec | `feature_spec.md` | Review + confirm |
| 2. Backlog | `requirements.md`, `svs.md`, `stories.md` | Review + confirm |
| 3. Plan | `plan.md` | Review + confirm |
| 4. Publish (optional) | `initiative_confluence.md`, Jira YAML | Review before MCP publish |

The gates are enforced by `rules/sdd-workflow-orchestration.md`. They only activate when:

- You run `/sdd-start`, OR
- You `@`-mention an SDD agent, OR
- You ask for an SDD artifact by name ("feature spec", "backlog", "plan.md", etc.), OR
- There is already an `output/{project}/feature_spec.md` in the workspace.

Outside those triggers, the plugin stays out of your way. Bug fixes and small edits are unaffected.

---

## When to use `/council` vs `/council-v2`

| Command | Use when |
| --- | --- |
| **`/council-v2`** | Bootstrap or refresh `.sdd/docs/` truth docs; routine knowledge questions; default before `/sdd-start` on brownfield repos |
| **`/council`** | Parallel deep exploration when truth docs are thin or you are debugging unfamiliar code |

`/council-v2 --refresh` rebuilds truth docs after a major refactor. Do **not** use `/council --refresh` — refresh is **`/council-v2`** only in this plugin.

---

## Agents (standalone usage)

You can invoke any agent independently, even mid-workflow:

```
@wg-sdd-kit-plugin/agents/prd-gap-analysis.md review this PRD draft
@wg-sdd-kit-plugin/agents/technical_analyst.md can this be done in one sprint?
@wg-sdd-kit-plugin/agents/technical-devils-advocate.md what am I missing?
@wg-sdd-kit-plugin/agents/doc_review_assistant.md check this PR against AC
```

Security skills (invoke by path):

```
@wg-sdd-kit-plugin/skills/security-threat-model/SKILL.md  (after spec approval)
@wg-sdd-kit-plugin/skills/security-code-review/SKILL.md (per story, before PR)
@wg-sdd-kit-plugin/skills/secrets-audit/SKILL.md        (PR gate)
```

See `rules/sdd-workflow-orchestration.md` for the full agent reference.

---

## Pairing with stack plugins

This plugin is **intentionally stack-agnostic**. It covers *process* (spec -> backlog -> plan -> publish), not *how to write code*. Pair it with a stack plugin for coding conventions:

- **Python (Folklore hexagonal)** — use alongside `folklore-plugin` (or equivalent) for `flk-python-hexagonal`, `flk-python-tests`, `flk-ops-template`.
- **Angular / Python (opinionated starter)** — the original [`python-sdd-starter-kit`](../python-sdd-starter-kit/) also ships Angular/Python rules; consider extracting those to a separate `wgc-stack-plugin` if your team wants both.

Plugins compose: a dev can have `sdd-plugin` + `folklore-plugin` active at the same time.

---

## Traceability

Every SDD artifact is anchored by `REQ-...` IDs. The chain is:

```
feature_spec.md -> requirements.md (REQ-...) -> stories.md -> plan.md -> Jira tickets -> PR/commits
```

If you skip the IDs, you get the process overhead without the auditability payoff — don't skip them.

---

## Output directory

All generated artifacts go to `output/{project-name}/` in the **current workspace** (not in the plugin directory). Add `output/` to `.gitignore` if you don't want the artifacts committed, or commit them to keep spec history alongside code. See `rules/output-config.md`.

---

## Versioning

This plugin follows semantic versioning (see `.cursor-plugin/plugin.json`). Breaking changes to always-on rules (especially `sdd-workflow-orchestration`) will bump the major version with a migration note.

---

## Differences from the starter-kit

The [`python-sdd-starter-kit`](../python-sdd-starter-kit/) remains the canonical **onboarding and documentation** reference. This plugin is the **operational distribution**:

| Concern | starter-kit | sdd-plugin |
|---|---|---|
| Distribution | Copy whole `.cursor/` into each repo | Install once, used everywhere |
| Updates | Manual per-repo merge | Central version bump |
| Stack coupling | Ships Angular + Python rules | Stack-agnostic (process only) |
| Workflow activation | `alwaysApply: true` everywhere | On-demand via `/sdd-start` or SDD intent |
| Entry point | Discover via `AGENTS.md` | `/sdd-start`, `/council-v2`, `/council` |
| PRD + security | Full kit in-repo | Same agents + security skills (stack-agnostic) |
| Docs footprint | 80 KB (README + USAGE_GUIDE) | Minimal README; docs stay in starter-kit |

Both can coexist: teams can read the starter-kit to *learn* SDD, and install the plugin to *run* SDD.

---

## Roadmap

- [x] PRD agents, security skills, `/council-v2` (v0.2.0).
- [ ] Pilot with 1-2 teams for 2 sprints; collect friction points with the gated workflow.
- [ ] Optional hook: pre-commit check for `REQ-...` in branch/commit message on feature branches.
- [ ] Split any stack-specific concerns into companion plugins.
- [ ] Publish to internal Cursor marketplace.

Feedback welcome — open an issue or DM the platform team.
