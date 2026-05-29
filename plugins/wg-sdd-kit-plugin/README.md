# wg-sdd-kit-plugin

> **Specs-Driven Development (SDD) for Cursor** — a gated workflow that forces specs and backlog to be agreed *before* code is written. Stack-agnostic.

Repackaged from the WGC Platform common guidelines as a **Cursor plugin** so teams can install it once, get updates centrally, and stop maintaining N forks of `.cursor/` across repos.

---

## What's in the plugin

```
wg-sdd-kit-plugin/
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
│   ├── qa_test_design_agent.md        TC-... cases mapped to AC
│   ├── developer_testing_agent.md     UT-... for devs
│   ├── doc_review_assistant.md        PR vs AC, release notes
│   └── epic_initiative_confluence.md  Confluence publish via MCP
├── commands/
│   ├── sdd-start.md             /sdd-start — entry point
│   └── council.md               /council — parallel exploration
├── templates/                   Story, SVS, Gherkin, release notes...
├── examples/                    Reference spec, story, SDLC patterns
└── skills/
    └── jira-epic-story-task-automation/   Jira hierarchy automation
```

---

## Installation

### Option 1: Local (for testing)

Copy this directory to `~/.cursor/plugins/local/wg-sdd-kit-plugin/`:

```bash
cp -r . ~/.cursor/plugins/local/wg-sdd-kit-plugin
```

Cursor will auto-discover it on next restart. Verify with **Cursor Settings -> Plugins**.

### Option 2: Internal marketplace / git

If your team publishes Cursor plugins via git or an internal marketplace, point your marketplace manifest at this directory. Versioning is governed by `.cursor-plugin/plugin.json`.

---

## Quick start

1. Install the plugin (above).
2. In any project in Cursor, open the chat and run:

   ```
   /sdd-start build a saved-views feature for the reports dashboard
   ```

3. The agent writes `output/saved-views-feature/feature_spec.md` and **stops** for your review.
4. Approve ("looks good", "proceed") and it moves to Step 2 (backlog). And so on through Plan and Publish.

All artifacts land under `<your-project>/output/{project-name}/`.

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

## Agents (standalone usage)

You can invoke any agent independently, even mid-workflow:

```
@wg-sdd-kit-plugin/agents/technical_analyst.md can this be done in one sprint?
@wg-sdd-kit-plugin/agents/technical-devils-advocate.md what am I missing?
@wg-sdd-kit-plugin/agents/doc_review_assistant.md check this PR against AC
```

See `rules/sdd-workflow-orchestration.md` for the full agent reference.

---

## Pairing with stack plugins

This plugin is **intentionally stack-agnostic**. It covers *process* (spec -> backlog -> plan -> publish), not *how to write code*. Pair it with a stack plugin for coding conventions:

- **Python (Folklore hexagonal)** — use alongside `folklore-plugin` (or equivalent) for `flk-python-hexagonal`, `flk-python-tests`, `flk-ops-template`.
- **Angular / Python (opinionated starter)** — consider extracting stack-specific concerns to a separate `wgc-stack-plugin` if your team wants both.

Plugins compose: a dev can have `wg-sdd-kit-plugin` + `folklore-plugin` active at the same time.

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