---
name: security-threat-model
description: >-
  STRIDE threat model at spec time (stack-agnostic). Detect UI/API/data boundaries
  from the workspace. Gate 2.5 — after feature spec approval, before backlog. Recommended
  for auth, data, PII, payments, external callouts.
---

# security-threat-model

STRIDE-based threat model **before stories are written**. Catches design-level flaws scanners cannot see without business context.

**Invoke:** `@wg-sdd-kit-plugin/skills/security-threat-model/SKILL.md`

Pair with a **stack plugin** (Python, .NET, Angular, JVM) for framework-specific checklists when available.

---

## When to run

After **`feature_spec.md`** is approved, **before** backlog (Gate 2.5 — recommended, not enforced by orchestration). Re-run when spec scope changes materially.

---

## In scope / out of scope

| In scope | Out of scope |
| --- | --- |
| IDOR, tenant scoping, privilege escalation at design level | CVE / dependencies → Snyk, Dependabot |
| Auth/session/OAuth design | Generic OWASP in code → Bandit, SonarQube |
| Data-flow disclosure, audit/repudiation gaps | Secret values in repos → `secrets-audit` |
| DoS surfaces (unbounded queries, missing rate limits) | IaC-only misconfig → separate review |
| Trust boundaries (browser, API, DB, queues, third parties) | |

---

## Inputs

Attach the approved spec and relevant code if brownfield:

```
@output/{project-name}/feature_spec.md                    ← required (plugin default)
@.sdd/features/pending/{slug}/feature_spec.md             ← if team uses WIN layout
@output/{project-name}/requirements.md                    ← if REQ-IDs exist
@src/ @app/ @lib/ @frontend/                              ← as applicable
```

**Detect stack** from the repo and tailor component names (e.g. FastAPI routes, ASP.NET controllers, Angular guards, Spring `@RestController`, Netty handlers).

---

## STRIDE per component

For each component in the spec, produce:

```
### Component: <name>

| STRIDE | Threat | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
| --- | --- | --- | --- | --- |
| Spoofing | ... | | | |
| Tampering | ... | | | |
| Repudiation | ... | | | |
| Information Disclosure | ... | | | |
| Denial of Service | ... | | | |
| Elevation of Privilege | ... | | | |
```

**Cross-stack checks (apply what fits):**

- **Auth:** minimal scopes; `aud`/`iss` for JWT; refresh rotation; API keys only in headers; UI must not be the only authorization layer.
- **IDOR:** resource IDs re-checked in service/repository layer, not only route filters.
- **Mass assignment:** typed DTOs/models — no privileged fields from untyped JSON/dicts.
- **Frontend:** token storage, XSS (`innerHTML`, sanitizer bypass), CSRF for cookie sessions.
- **Data:** tenant filters in persistence layer; pagination limits; PII not in logs/errors.
- **Async:** idempotency, poison messages, retry storms.

---

## Output

Save to:

- `output/{project-name}/security/threat-model.md` (plugin default), or
- `.sdd/features/pending/{slug}/security/threat-model.md` (WIN layout)

Include **Security Acceptance Criteria** bullets the backlog architect can merge into Gherkin.

---

## After running

1. Review Security ACs with the spec owner.
2. Merge ACs into `stories.md` before backlog sign-off.
3. Attach `threat-model.md` for Gate 3.5 (`technical-devils-advocate` on stories).
4. Run `@wg-sdd-kit-plugin/skills/security-code-review/SKILL.md` per story before each PR.
