---
description: Specs-Driven Design (SDD) workflow — specs before code, traceability end-to-end. Stack-agnostic.
alwaysApply: true
---

# Specs-Driven Design (SDD)

This plugin enables **SDD**: product intent and contracts are captured in **specs** and **backlog artifacts** before implementation. The coding agent implements against **approved scope**, not ad-hoc assumptions.

## Artifact chain (stepped, gated)

Each step requires **explicit user approval** before the agent proceeds. The stepped workflow is activated by:

- Running `/sdd-start` (recommended entry point), OR
- `@`-mentioning `sdd-workflow-orchestration` rule, OR
- The user explicitly asking to "write a feature spec", "create a backlog", or similar SDD intent.

For everyday coding tasks (bug fixes, small changes), the gated workflow stays dormant — this rule only establishes principles.

**Before SDD (optional):** PRD quality — `@wg-sdd-kit-plugin/agents/prd-gap-analysis.md`, `prd-market-owner-devils-advocate.md`, `prd-product-owner-devils-advocate.md` (chat critique on PRD content; no repo artefacts). PRDs are typically MO/PO-led; **engineering may draft** when needed.

1. **Feature spec** — Problem, goals/non-goals, constraints, conceptual APIs. **-> STOP for review.** *(Recommended Gate 1.5: `@wg-sdd-kit-plugin/agents/technical-devils-advocate.md` on draft spec.)*
2. **Security threat model** *(recommended Gate 2.5)* — `@wg-sdd-kit-plugin/skills/security-threat-model/SKILL.md` after spec approval, before backlog; merge Security ACs into stories.
3. **Requirement IDs + SVS + Stories** — Stable `REQ-...` IDs, sprint-sized slices, Gherkin AC, NFRs. **-> STOP for review.**
4. **Plan / tasks** — Implementation steps derived from spec; link **REQ-...** IDs. **-> STOP for review.**
5. **Publishing** — Confluence initiative doc, Jira hierarchy (optional, user-initiated).
6. **Code + tests** — Map changes to the same IDs in commit messages or PR descriptions when the team requires it. *(Per story: `security-code-review` before PR; PR gate: `secrets-audit`.)*

All artifacts are written to the output directory defined in the `output-config` rule.

## Principles for the coding agent

- **Do not expand scope** beyond the spec's goals and the story's AC without explicit user/product confirmation.
- **Prefer additive, backward-compatible** API and schema changes; version or flag breaking changes.
- **Contracts stay in sync** (OpenAPI / Pydantic / TypeScript types) with implemented behavior; update spec snippets when contracts change.
- If the spec is **missing or ambiguous**, list **assumptions** and **questions** before large implementations — do not invent product requirements.

## Traceability

- Reference **REQ-...** (or project IDs) when editing files tied to a feature.
- After implementation, the **doc_review_assistant** agent maps PRs to AC; keep tests and diffs as evidence.

## Where to look

- `sdd-workflow-orchestration` rule — Stepped workflow with review gates (activated on demand).
- `output-config` rule — Output directory configuration (always applied).
- `@wg-sdd-kit-plugin/agents/backlog_architect.md` — SVS, stories, Gherkin, task breakdown.
- `@wg-sdd-kit-plugin/agents/technical_analyst.md` — Feasibility and risk before build.
- `@wg-sdd-kit-plugin/skills/security-threat-model/SKILL.md` — Gate 2.5 threat model (recommended).
- `@wg-sdd-kit-plugin/skills/security-code-review/SKILL.md` — Per-story review before PR.
- `@wg-sdd-kit-plugin/skills/secrets-audit/SKILL.md` — PR / periodic secrets scan.
- `@wg-sdd-kit-plugin/commands/council-v2.md` — Truth docs bootstrap and refresh.
- `@wg-sdd-kit-plugin/examples/example_feature_spec.md` — Example feature spec shape.
