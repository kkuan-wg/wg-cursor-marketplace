---
name: spec-artifact
description: Produces a concise SDD spec.md for a domain capability. Use when adding or updating spec files, writing SDDs, or when the user mentions spec.md, spec artifacts, or domain specifications.
---

# Spec Artifacts

Produces a `spec.md` for a domain capability inside the SSOT tree where every normative claim links to a real artifact file.

## Phase 1: Investigate Before Writing

**Complete all steps before producing any output.**

### 1. Parse the input
- Extract the **platform** (`folklore` or `legacy`) and **domain name** (e.g. `oidc-api`, `saml-api`)
- Extract the **capability** being specified (e.g. `token-lifecycle`, `user-command-topic`)
- Determine the **spec ID** — this is **mandatory**:
  1. Explicit ID provided by the user (lowercased, kebab-cased; e.g. `aaas-30123`)
  2. None found — **stop and ask the user for the spec ID before proceeding**
- Extract the **implementation type**: `Code` (Lambda functions, business logic) or `Infra` (SAM/CloudFormation templates and/or minimal lambda scaffold only); ask if not stated
- Extract the **AWS services** involved (e.g. Lambda, SQS, DynamoDB, SNS, API Gateway); if none are mentioned and cannot be inferred from artifacts, ask
- Note any explicit scope boundaries

### 2. Discover existing artifacts
Browse `ssot/<platform>/domain/<domain>/` and catalogue what exists:
- `event/schema.yaml` and `event/examples/` — event contracts and sample payloads
- `event/examples/` — event sample payloads
- `api-contract/*.yaml` — OpenAPI specs
- `database-model/*.json` — DynamoDB model definitions
- `sequence-diagram/` — flow diagrams (`.md`, `.mmd`, `.puml`)
- `specs/` — existing spec folders for this domain
- `error-codes.md` — domain-level error catalogue
- `README.md` — domain overview

Only reference files that **actually exist**. Do not assume paths.

### 3. Read the artifacts the capability touches
Extract:
- **Event names and operations** — from the event schema files discovered within the specific domain (may be a single `schema.yaml` or individual per-event AsyncAPI files such as `add-user-detail.asyncapi.yaml`)
- **Endpoint paths and endpoint names** — from OpenAPI contracts
- **Table/entity names and key schemas** — from DynamoDB model JSON
- **Error codes** — from `error-codes.md` if relevant

### 4. Determine capability boundaries
- One capability = one `specs/<folder>/` folder. Split large features across multiple folders.
- Folder name: **always `<spec-id>-<capability>`** — the spec ID prefix is required.
  - Example: `aaas-30123-user-delete-audit-actor/`, `aaas-30040-saml-user-cache-consumer/`

### 5. Ask only what you cannot find
If after steps 1–4 something critical is still unknown, ask the user one targeted question per gap. Never ask about things discoverable from the SSOT tree.

## Phase 2: Write the Output

Produce `spec.md` in this order:

```
# {One-line title}

> **Spec ID:** {spec-id}  
> **Type:** {Code | Infra}  
> **AWS Services:** {comma-separated list}

## References

## Requirements

### REQ-1: {name}
#### Scenario: {name}
```

Requirements MUST be numbered sequentially using the prefix `REQ-N` (e.g. `REQ-1`, `REQ-2`, `REQ-3`). The number is stable — never renumber existing requirements when adding new ones.

**Write using the Write tool** at `ssot/<platform>/domain/<domain>/specs/<spec-id>-<capability>/spec.md`.

**Title is one line only.** No description paragraph after the `#` heading — extra context belongs in the first requirement body.

**References use MCP tool calls as the primary identifier**, with the relative path in parentheses as a secondary note for git/editor use. The MCP calls are written into the spec so that a developer in another repository can use the `ai-tool-authpoint-spec` MCP server to fetch the referenced artifacts directly. Each bullet follows the pattern:

```
- {Label}: `{mcp_tool(domain='...', param='...')}` (`../../{path}`) — {specific names}
```

For cross-domain artifacts (a different domain than the spec's own), adjust the relative path depth accordingly — e.g. `../../../{other-domain}/{path}` instead of `../../{path}`.

Use these MCP tools to identify each artifact:

| Artifact | MCP tool | Key parameter |
|---|---|---|
| Event schema | `get_events(domain, schema_name)` | `schema_name` = file stem from `list_events()` — typically `'schema'` for a unified schema, or the individual event file stem (e.g. `'add-user-detail.asyncapi'`) for per-event files |
| Event example | `get_event_example(domain, event_name)` | `event_name` = event type name |
| API contract | `get_api_contract(domain, api_name)` | `api_name` = file stem |
| Database model | `get_database_model(domain, model_name)` | `model_name` = file stem |
| Error codes | `get_error_codes(domain)` | — |
| Sequence diagram | `get_sequence_diagram(domain, diagram_name)` | `diagram_name` = file stem |

List `get_event_example()` only for event types **directly referenced in requirements** — not for every example that exists.

When no domain artifacts exist yet, open `## References` with a single blockquote note that includes a `get_domain_summary(domain='...')` call, then list expected artifact bullets below it — never scatter `(expected)` inline per bullet. See [references/REFERENCE.md](references/REFERENCE.md) for examples.

**Scenarios are descriptive, not normative.** GIVEN / WHEN / THEN bullets describe observable behaviour — no **MUST**, no inline caveats. Reserve **MUST** for the requirement body. Cover the main success path, error paths, and alternative flows where the flow diverges in a way that affects the implementation.

**Never duplicate schemas.** Point to `schema.yaml`, OpenAPI YAML, or `database-model/*.json`; never paste field lists into the spec.

**Scope requirements strictly by type:**

- **Code** — requirements cover only business logic, event/API handling, data processing, and error handling inside the Lambda code. **No infrastructure provisioning, SAM/CloudFormation resources, or deployment configuration** may appear.
- **Infra** — requirements cover only infrastructure provisioning (SAM template resources, IAM policies, environment variables, triggers) and the minimal Lambda scaffold needed for the deploy to work. **No business logic, data-processing rules, or application-layer behaviour** may appear.

## Phase 3: Verify Before Finishing

- [ ] Title is a single `#` line with no paragraph immediately after it
- [ ] Spec header declares **Spec ID**, **Type**, and **AWS Services**
- [ ] Scenario bullets are purely descriptive — no **MUST**, no inline caveats (reserve **MUST** for the requirement body)
- [ ] Scenarios cover the main success path, error paths, and alternative flows (where applicable)
- [ ] `## References` uses MCP tool calls as primary identifiers, with relative paths in parentheses as secondary notes
- [ ] Every MCP call has all parameters filled in with real values (domain, file stem, event name)
- [ ] `get_event_example()` is listed only for event types directly referenced in requirements
- [ ] When no artifacts exist, a single blockquote note + `get_domain_summary()` is used — no per-bullet `(expected)` flags
- [ ] All relative paths in parentheses resolve correctly from `specs/<folder>/spec.md`
- [ ] No schema or attribute catalog duplicated in prose
- [ ] Folder is named `<spec-id>-<capability>` — spec ID prefix is always present
- [ ] Capability is scoped to one concern; split if too broad
- [ ] Requirements are numbered `REQ-1`, `REQ-2`, … with no gaps or renumbering of existing entries
- [ ] **If type is Code** — no infrastructure/SAM/CloudFormation/deployment requirements are present
- [ ] **If type is Infra** — no business logic, data-processing, or application-layer requirements are present; only infrastructure and Lambda scaffold

## Reference

- Artifact locations, folder naming, path rules, spec structure → [references/REFERENCE.md](references/REFERENCE.md)
- Example Code spec → [references/examples/saml-user-cache-consumer-code-spec.md](references/examples/saml-user-cache-consumer-code-spec.md)
- Example Infra spec → [references/examples/saml-user-cache-consumer-infra-spec.md](references/examples/saml-user-cache-consumer-infra-spec.md)
