---
name: security-code-review
description: >-
  Deep security code review on story/PR diffs (stack-agnostic). IDOR, authz, tenant
  scope, mass assignment, race conditions, trust boundaries. Per story before PR; pair
  with stack plugins for framework-specific patterns.
---

# security-code-review

Logic-level security review on the **current story diff** before opening a PR. Targets issues static tools miss without business context.

**Invoke:** `@wg-sdd-kit-plugin/skills/security-code-review/SKILL.md`

---

## When to run

- **Per story** — after dev, before PR.
- **On full PR diff** — before merge (with team CI: Snyk, SonarQube, etc.).
- **High-risk paths** flagged in `threat-model.md`.

---

## In scope / out of scope

| In scope | Out of scope |
| --- | --- |
| IDOR, broken authz, missing tenant scope | Dependency CVEs → Snyk |
| Mass assignment / over-posting | Style/dead code → SonarQube |
| Race conditions / TOCTOU | Known secrets → `secrets-audit` |
| Logic vs story AC / threat model | |
| Unsafe deserialization, weak crypto usage | |
| Client-side trust-boundary mistakes | |

---

## Inputs

```
@output/{project-name}/stories.md or story file          ← required
@output/{project-name}/security/threat-model.md          ← if Gate 2.5 ran
@.sdd/features/pending/{slug}/...                        ← WIN layout if used
<changed source files>                                   ← diff scope
```

Detect stack from file types and apply the relevant checklist from your stack plugin when installed.

---

## Review checklist

### 1. IDOR & authorization

- Every fetch/update/delete by ID: is ownership/tenant enforced in **service/data** layer?
- Can list/filter parameters bypass scoping?
- Admin-only operations: protected on server, not only hidden in UI?

### 2. Authentication & session

- Tokens/cookies: httpOnly vs localStorage per threat model.
- Session fixation, logout invalidation, clock skew on JWT `exp`.

### 3. Input & mass assignment

- Request bodies map only to allowed fields; privileged columns not client-writable.
- File upload: type/size/path; virus scan if required by spec.

### 4. Data & errors

- Production errors do not leak stack traces, SQL, or internal IDs.
- Logs avoid passwords, tokens, full PII/payment payloads.

### 5. Concurrency & DoS

- Idempotent writes where retries exist; optimistic locking where needed.
- Queries bounded (limit/pagination); expensive endpoints rate-limited.

### 6. Client / API contract

- Sensitive operations require same auth as API (not UI-only).
- CORS, CSP, and redirect URLs match spec.

---

## Output format

```markdown
## Security code review — {story/PR}

| Severity | Finding | Location | Recommendation |
| --- | --- | --- | --- |
| BLOCKER | ... | file:line | ... |
| SUGGESTION | ... | | |

### Threat model AC coverage
- [x] AC-SEC-001 — ...
- [ ] AC-SEC-002 — MISSING: ...
```

**BLOCKER** must be fixed before merge unless explicitly accepted with sign-off.

---

## After running

Fix BLOCKERs, update tests, reference review in PR description. Run `@wg-sdd-kit-plugin/skills/secrets-audit/SKILL.md` at PR gate.
