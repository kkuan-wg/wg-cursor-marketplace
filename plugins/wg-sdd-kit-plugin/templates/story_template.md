# Story Template (Angular + Python)

> **Used by:** `agents/backlog_architect.md` — fill each user story using this structure.  
> **Filled example:** `examples/example_story.md`.  
> **Other stacks:** use **TBD** under Dependencies and NFRs where Angular/Python do not apply; list **Open Questions** instead of force-fitting.

---

**Title:** \<clear, concise\>

---

## Traceability

| Field | Value |
|-------|--------|
| Requirement ID | `REQ-…` |
| Spec / PRD | §… or path to `spec.md` / doc |

---

## User Story

As a \<role>, I want \<capability>, so that \<outcome>.

---

## INVEST check

Short note: **I**ndependent / **N**egotiable / **V**aluable / **E**stimable / **S**mall / **T**estable — call out any concern or split suggestion.

---

## Acceptance Criteria (Gherkin)

- Given \<precondition\>
  When \<action\>
  Then \<result\>
- Given …

---

## Non-Functional Requirements

- **Performance:** additional FE bundle (e.g. gzip KB); TTI/LCP if UI-heavy; API p95; pagination/caching
- **Security / Privacy:** auth model, PII, audit, CSRF if cookies
- **Reliability:** retries/timeouts; idempotency for writes
- **Observability:** FE events; API logs/metrics/traces
- **Accessibility:** keyboard, focus, ARIA, contrast (WCAG 2.1 AA target)

---

## Dependencies

- **Angular:** modules/components/services/routes; interceptors; state (NgRx/Signals) — or **TBD**
- **Python:** endpoints/models/schemas; migrations (Alembic); feature flags/config — or **TBD**
- **Feature flags / config:** …

---

## Risks & Mitigations

- …

---

## Open Questions

- …

---

## Blockers for spec sign-off

**None** — or list must-resolve items (legal, security architecture, data/UX contract) before dev commits.

---

## Suggested Task Breakdown

- **Dev:** FE component/service/route + API endpoint/model + wiring/flags
- **Test:** unit (FE+API), integration, e2e; **contract tests** if API is shared/consumed elsewhere
- **Docs:** user help, API (OpenAPI), ADR
- **Data / Migration:** design, Alembic script, backfill
- **Feature Flag:** rollout plan + metrics

---

## Validation Notes (optional)

Use for handoff to `tasks.md` or epic rollup.

- **Repo references:** files/dirs/PRs (or TBD)
- **Confidence:** High / Med / Low
- **Traceability summary:** story title ↔ `REQ-…`
