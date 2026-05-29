---
description: SDD workflow orchestration — stepped artifact generation with mandatory review gates between steps. Activated on demand (via /sdd-start or SDD intent).
alwaysApply: false
globs: "output/**/*.md"
---

# SDD Workflow Orchestration

This rule enforces a **stepped, gated workflow** for generating SDD artifacts. When active, the agent MUST produce only one step's output per response and MUST NOT proceed to the next step without explicit user confirmation.

## When this rule is active

Activate the gated workflow when ANY of the following is true:

- The user ran `/sdd-start` (explicit entry point).
- The user asked for "feature spec", "backlog", "user stories", "plan.md", "SVS", "REQ IDs", "requirements doc", or similar SDD artifact.
- The user `@`-mentioned this rule, or any of the SDD agents (`backlog_architect`, `technical_analyst`, `epic_initiative_confluence`).
- An `output/{project}/feature_spec.md` (or similar SDD artifact) already exists in the workspace and the conversation concerns it.

If none of the above apply, do NOT enforce gates. The user is probably doing regular coding work.

## Steps and Gates

### Step 1 — Feature Spec

**Trigger:** User describes a problem, feature, initiative, or objective within an SDD context.

**Output:** `feature_spec.md` ONLY — containing:
- Problem statement
- Goals / non-goals
- Constraints
- User acceptance criteria
- Conceptual APIs (if applicable)
- Observability considerations
- Key assumptions

**Gate:** After generating the feature spec, STOP and present it for review:
> "Feature spec is ready for review. Please review and confirm before I proceed to requirement IDs and backlog stories. If changes are needed, let me know."

**Hard rule:** Do NOT generate requirement IDs, stories, SVS, plans, tasks, Confluence artifacts, or Jira structures in this step. Only the feature spec.

---

### Step 2 — Backlog (REQ IDs + SVS + Stories)

**Trigger:** User explicitly confirms the feature spec (e.g. "approved", "looks good", "proceed", "go ahead").

**Output:**
- `requirements.md` — Stable `REQ-...` IDs with titles and scope
- `svs.md` — Sprint-sized Slice(s) with traceability
- `stories.md` — User stories per SVS with Gherkin AC, NFRs, dependencies, risks

Use templates from this plugin: `@wg-sdd-kit-plugin/templates/svs_template.md`, `@wg-sdd-kit-plugin/templates/story_template.md`, `@wg-sdd-kit-plugin/templates/acceptance_criteria_gherkin.md`.

**Gate:** After generating backlog artifacts, STOP and present for review:
> "Backlog artifacts (requirements, SVS, and stories) are ready for review. Please review and confirm before I proceed to the implementation plan."

**Hard rule:** Do NOT generate plan/tasks, Confluence, or Jira artifacts in this step.

---

### Step 3 — Plan / Tasks

**Trigger:** User explicitly confirms the backlog artifacts.

**Output:**
- `plan.md` — Implementation plan with task breakdown, dependencies, deployment order, risk register

**Gate:** After generating the plan, STOP and present for review:
> "Implementation plan is ready for review. Please review and confirm before I proceed to publishing artifacts (Confluence/Jira)."

---

### Step 4 — Publishing Artifacts (optional)

**Trigger:** User explicitly requests Confluence or Jira output.

**Output (one or both, as requested):**
- `initiative_confluence.md` — Confluence initiative document (use `@wg-sdd-kit-plugin/templates/initiative_confluence_skeleton.md`)
- Jira YAML/JSON — Epic/Story/Task hierarchy (use `@wg-sdd-kit-plugin/skills/jira-epic-story-task-automation/SKILL.md`)

**Gate:** Present for review before any MCP publish action.

---

## Rules (always enforced when active)

1. **One step per response.** Never combine Step 1 + Step 2 output in a single response, even if the user's prompt contains enough detail for multiple steps.

2. **Never assume approval.** Phrases like "here's everything" or "I'll also generate the stories" are violations. Always wait for explicit confirmation.

3. **Confirmation keywords.** Treat the following as explicit step approval: "approved", "confirmed", "looks good", "proceed", "go ahead", "next step", "continue", "yes", "LGTM". If ambiguous, ask: "Should I proceed to Step N?"

4. **Skip-ahead escape hatch.** If the user explicitly requests multiple steps at once (e.g. "generate feature spec and stories together", "give me everything", "skip to plan"), honor that request but note which steps were combined. This is the ONLY exception to the one-step rule.

5. **Step detection.** At the start of each response, determine which step the user is in:
   - No existing artifacts in output directory -> Step 1
   - Feature spec exists but not confirmed -> Present spec for review
   - Feature spec confirmed, no backlog -> Step 2
   - Backlog confirmed, no plan -> Step 3
   - Plan confirmed -> Step 4 (only if requested)

6. **Output location.** All generated files MUST be written to the output directory defined in `output-config`. Never write to arbitrary locations outside the workspace.

---

## Step Summary Table

| Step | Agent(s) | Input Required | Output Files | Gate |
|------|----------|---------------|--------------|------|
| 1. Feature Spec | this rule | Problem statement | `feature_spec.md` | User confirms |
| 2. Backlog | `backlog_architect` | Approved feature spec | `requirements.md`, `svs.md`, `stories.md` | User confirms |
| 3. Plan | this rule | Approved backlog | `plan.md` | User confirms |
| 4. Publish | `epic_initiative_confluence`, Jira skill | Approved plan | `initiative_confluence.md`, Jira YAML | User confirms |

---

## Standalone Agent Usage (outside the workflow)

The stepped workflow above governs **artifact generation** only. The following agents can be invoked **independently at any time**, at any step, without advancing the workflow:

| Agent | How to invoke | When to use |
|-------|--------------|-------------|
| `technical_analyst` | `@wg-sdd-kit-plugin/agents/technical_analyst.md` | Before or after any step — assess feasibility, complexity, and risks |
| `technical-devils-advocate` | `@wg-sdd-kit-plugin/agents/technical-devils-advocate.md` | Before or after any step — challenge assumptions, surface edge cases |
| `doc_review_assistant` | `@wg-sdd-kit-plugin/agents/doc_review_assistant.md` | After implementation — verify PRs against AC, generate release notes |
| `backlog_architect` | `@wg-sdd-kit-plugin/agents/backlog_architect.md` | Directly, if you already have a confirmed spec and want to skip Step 1 |

**Rules for standalone usage:**
- When a user `@`-mentions an agent directly, that agent runs — the workflow does NOT block it.
- Standalone agent output does not advance the workflow step.
- The user can run multiple standalone agents between steps (e.g. both `technical_analyst` and `technical-devils-advocate` after Step 1 before confirming to proceed to Step 2).

---

## Anti-Patterns

- Generating stories in the same response as the feature spec
- Generating a plan before stories are reviewed
- Generating Jira/Confluence artifacts without being asked
- Assuming the user wants all steps because they gave a detailed prompt
- Writing files outside the configured output directory
- Blocking a standalone agent invocation because "the workflow hasn't reached that step"
- Activating the gated workflow for regular coding tasks (bug fixes, refactors) that do not mention SDD artifacts
