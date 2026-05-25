# SAML User Cache Consumer — Business Logic Implementation

**Ticket:** AAAS-30040

## Goal

- Introduce `flk-saml-user-cmd-invoker` Lambda business logic that reads from `flk-saml-user-cmd-queue.fifo` and keeps `flk-saml-user-detail` in sync with Folklore Cache events.
- Route seven event types (`ADD_USER_DETAIL`, `UPDATE_USER_DETAIL`, `REMOVE_USER_DETAIL`, `UPDATE_USER_GROUP_DETAIL`, `PATCH_USER_GROUP_DETAIL`, `PATCH_USER_FORGOT_TOKEN_DETAIL`, `PATCH_USER_PASSKEY_DETAIL`) to per-operation handlers following hexagonal architecture.
- Enforce SAML-only entity-type guard in-Lambda; discard unrecognised `entityType` without retry.
- All writes are idempotent; soft-deleted items set `softDeletedTtl = now + 300 s`.

## Scope

- Business logic handler following hexagonal architecture (ports, adapters, domain service).
- Input validation via `UserCommandValidator` scoped to resource type `SAML` (REQ-2).
- Handlers for all seven event types including the `PATCH_USER_GROUP_DETAIL` read-modify-write path (REQ-3 through REQ-7).

**Out of scope**

- SAM template and infrastructure provisioning (SQS queues, DynamoDB table, Lambda resource definition) — covered by the companion Infra spec.
- Changes to the Folklore Cache producer or `flk-user-cmd-topic.fifo`.
- Schema changes to the shared Folklore Cache event envelope.

## Spec

[./spec.md](./spec.md) — satisfies:

- **Requirement: Event source filtering** / Scenario: Non-SAML event is ignored / Scenario: Unknown entityType is discarded
- **Requirement: Input validation**
- **Requirement: User detail upsert** / Scenario: New user added / Scenario: Existing user updated
- **Requirement: User detail soft-delete** / Scenario: User removed
- **Requirement: Group detail patch** / Scenario: Group patch — user not found
- **Requirement: Forgot-token detail patch**
- **Requirement: Passkey detail patch** / Scenario: Passkey updated
- **Requirement: Hexagonal architecture**
- **Requirement: Idempotency**

## Artifacts

Artifacts are listed in `./spec.md#references`; verify all expected paths exist before starting implementation.

New files this change will create:

- `saml_user_cmd_invoker_fn/app.py` — Lambda entry point; wires `DynamoDbRepository` → `Service`, calls `service.process(dto=dto)` per SQS batch record
- `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/configuration.py` — `SqsEventConfig` (DTO field path mappings) and `DdbRepositoryConfig` (table name env var, PK schema, entity model mappings, `softDeletedTtl` attribute name)
- `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/domain/service.py` — `Service` class; routes by `entityType` then `eventType`; applies non-SAML guard; validates before processing
- `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/port/repository.py` — abstract `Repository` with methods `save`, `soft_delete`, `retrieve`, `update_groups`, `update_forgot_token`, `update_passkeys`
- `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/adapter/ddb_repository.py` — `DynamoDbRepository` implementing `Repository` using `DdbRepository` base class

## Risks / Open questions

- `PATCH_USER_GROUP_DETAIL` requires a read-modify-write; a concurrency strategy (e.g. optimistic locking via DynamoDB condition expressions) must be agreed before implementing this handler (Requirement: Group detail patch — Scenario: Group patch — user not found).
