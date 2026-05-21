# Spec Artifacts Reference

Detailed reference for artifact locations, `spec.md` structure, and linking rules.

---

## 1. SSOT Tree Layout

Specs live inside the single source of truth tree. Both platforms share the same structure:

```
ssot/
  <platform>/              ← folklore | legacy
    docs/                  ← platform-specific documentation
    domain/
      <domain>/            ← e.g. oidc, saml
        api-contract/      ← OpenAPI specs (.yaml)
        database-model/    ← DynamoDB model definitions (.json)
        event/
          schema.yaml      ← AsyncAPI event schemas (unified) or per-event AsyncAPI files
          examples/        ← JSON event examples
        sequence-diagram/  ← .md, .mmd, .puml
        specs/
          <spec-id>-<capability>/  ← e.g. aaas-30123-user-delete-audit-actor
            spec.md                ← the human-readable spec
          <capability>/            ← used only when no spec ID is available
        error-codes.md
        README.md
```

---

## 2. Artifact Location Table

References in `spec.md` use **MCP tool calls as the primary identifier** so that developers working in another repository can fetch the artifact directly. The relative path follows in parentheses as a secondary note for git/editor use.

| Artifact | MCP tool (primary) | Relative path (secondary) | Notes |
|----------|-------------------|--------------------------|-------|
| Event schema | `get_events(domain='<domain>', schema_name='schema')` | `../../event/schema.yaml` | Add relevant message/channel/operation names as a comment |
| Event example | `get_event_example(domain='<domain>', event_name='<EVENT_TYPE>')` | `../../event/examples/<EVENT_TYPE>.json` | List only event types directly referenced in requirements |
| HTTP API | `get_api_contract(domain='<domain>', api_name='openapi')` | `../../api-contract/openapi.yaml` | Add relevant path + endpoint name |
| DynamoDB model | `get_database_model(domain='<domain>', model_name='<name>')` | `../../database-model/<name>.json` | Add table/entity name if relevant |
| Sequence diagram | `get_sequence_diagram(domain='<domain>', diagram_name='<name>')` | `../../sequence-diagram/<name>.md` | — |
| Error codes | `get_error_codes(domain='<domain>')` | `../../error-codes.md` | Add relevant error code(s) |
| Domain overview | `get_domain_summary(domain='<domain>')` | `README.md` | Only for "see also" or pending-artifacts fallback |

Replace `<domain>` with the actual domain name (e.g. `saml`), `<name>` with the file stem, and `<EVENT_TYPE>` with the exact event type string. If a path differs in a specific domain, **use what actually exists** — list only files present in the repo.

---

## 3. Spec ID and Folder Naming

Every capability folder is named **`<spec-id>-<capability>`** when a spec ID is present, or **`<capability>`** alone when there is none.

**Spec ID precedence:**
1. Explicit ID supplied by the user (lowercased, kebab-cased as-is)
2. Jira ticket key inferred from a Jira URL or mention in the input (e.g. `AAAS-30123` → `aaas-30123`)
3. No ID — omit the prefix

**Examples:**

| Input | Spec ID | Capability | Folder |
|-------|---------|------------|--------|
| Jira URL `…/AAAS-30123` | `aaas-30123` | `user-delete-audit-actor` | `aaas-30123-user-delete-audit-actor/` |
| User says "use id my-feature" | `my-feature` | `token-lifecycle` | `my-feature-token-lifecycle/` |
| No ID given | — | `token-lifecycle` | `token-lifecycle/` |

---

## 4. Relative Path Rules

Regardless of whether the folder has a spec ID prefix, a spec at `specs/<folder>/spec.md` is always **two levels deep** inside the domain folder. Relative paths to domain-root artifacts are the same:

```
specs/<folder>/spec.md  →  ../../event/schema.yaml
                        →  ../../api-contract/openapi.yaml
                        →  ../../database-model/<name>.json
                        →  ../../error-codes.md
```

Always verify the path resolves before including it.

---

## 5. `spec.md` Structure

### Title

One line — what this capability is for. The `#` heading is the title. **Do not add a description paragraph immediately after it.** Any extra context belongs in the first requirement body.

```markdown
# Token Lifecycle
```

### References (mandatory)

Bullet list where each entry leads with the **MCP tool call** (inline code, all parameters filled in) so a developer in another repository can fetch the artifact immediately. The relative path follows in parentheses as a secondary note for git/editor use.

**Pattern per bullet:**

```
- {Label}: `{mcp_tool(domain='...', param='...')}` (`../../{path}`) — {specific names or notes}
```

**When all artifacts exist:**

```markdown
## References

- Events: `get_events(domain='oidc', schema_name='schema')` (`../../event/schema.yaml`) — `CREATE_TOKEN`, `REVOKE_TOKEN`
- Event example: `get_event_example(domain='oidc', event_name='CREATE_TOKEN')` — relevant to REQ-2
- Event example: `get_event_example(domain='oidc', event_name='REVOKE_TOKEN')` — relevant to REQ-3
- API: `get_api_contract(domain='oidc', api_name='openapi')` (`../../api-contract/openapi.yaml`) — `POST /tokens`, `DELETE /tokens/{id}`
- Model: `get_database_model(domain='oidc', model_name='flk-core-tokens')` (`../../database-model/flk-core-tokens.json`)
```

`get_event_example()` is listed only for event types **directly referenced in requirements** — not for every example in the directory.

**When the domain has no artifacts yet**, add a single blockquote note at the top of the section and use `get_domain_summary()` as the single pending reference. Do **not** scatter `(expected)` inline per bullet.

```markdown
## References

> No machine-readable contracts exist yet for this domain. Call `get_domain_summary(domain='oidc')` to check for newly added artifacts. The paths below are **expected** artifact locations following the standard SSOT layout. Update this block once the domain is implemented.

- **Events (expected):** `get_events(domain='oidc', schema_name='schema')` (`../../event/schema.yaml`)
- **HTTP API (expected):** `get_api_contract(domain='oidc', api_name='openapi')` (`../../api-contract/openapi.yaml`)
- **Persistence (expected):** `get_database_model(domain='oidc', model_name='<name>')` (`../../database-model/`) ← replace `<name>` once the model file exists
```

### Requirements

Each requirement gets its own `### REQ-N:` heading, numbered sequentially from `REQ-1`. Numbers are stable — never renumber existing requirements when adding new ones. Normative statements use **MUST** and belong in the requirement body.

**Scenarios are descriptive, not normative.** GIVEN / WHEN / THEN bullets describe observable behaviour. They do **not** use **MUST** or **MUST NOT**, and they do not contain inline caveats (`once published`, `once defined`). If a condition is uncertain, state it in the requirement body above the scenario, not inside the bullet.

```markdown
## Requirements

### REQ-1: Token creation

The system **MUST** create a new token record in `flk-core-tokens` when a `CREATE_TOKEN` event is received with a valid payload as defined in the event schema (`get_events(domain='oidc', schema_name='schema')`).

#### Scenario: Successful token creation

- **GIVEN** a valid `CREATE_TOKEN` event payload
- **WHEN** the event is processed
- **THEN** a new record is created in the tokens table with status `ACTIVE`
```

Keep each requirement traceable to a referenced file. Keep scenarios short — bullet format only.

---

## 6. Anti-Patterns

- Capability folder named `<capability>` when a spec ID was provided or could be inferred from the input — always prefix with `<spec-id>-`.
- Missing `> **Type:**` / `> **AWS Services:**` header block beneath the `#` title.
- Requirements headed `### Requirement: {name}` instead of `### REQ-N: {name}` — always use the numbered prefix.
- Renumbering existing `REQ-N` entries when adding new requirements — append at the end instead.
- Spec without a `## References` block with MCP tool calls pointing to real artifacts.
- References that use only relative paths without the MCP tool call as the primary identifier.
- MCP tool calls with placeholder values (e.g. `domain='<domain>'`) for artifacts that already exist — all parameters must be filled in with real values. Placeholders are only acceptable in the pending-artifacts blockquote, with an inline note to replace them once the file exists.
- Listing `get_event_example()` for every example in the directory instead of only those directly referenced in requirements.
- A description paragraph placed directly below the `#` title heading.
- Using **MUST** or **MUST NOT** inside GIVEN / WHEN / THEN scenario bullets — normative language belongs in the requirement body only.
- Scattering `(expected)` inline per reference bullet when no domain artifacts exist — use a single blockquote note at the top of `## References` instead.
- Inline caveats (`once published`, `once defined`) inside scenario bullets — state uncertainty in the requirement body or the References note.
- Copy-pasting JSON Schema, DynamoDB attribute lists, or OpenAPI parameter tables into the spec.
- One oversized `spec.md` for the whole domain — **split by capability**.
- Inventing events, endpoints, or tables not grounded in existing artifacts or user input.
- Requirements that cannot be tied to a referenced file or an obvious capability boundary.
