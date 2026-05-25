# Tasks — SAML User Cache Consumer Business Logic Implementation

> Spec: [./spec.md](./spec.md)

## Spec & Alignment

- [ ] Confirm `./database-model/flk-saml-user-detail.json` exists and verify PK format, GSI names, `softDeletedTtl` attribute name, and `passkeys` array schema (Requirement: User detail upsert, Requirement: User detail soft-delete, Requirement: Passkey detail patch)
- [ ] Confirm `./event/schema.yaml` defines all seven event types consumed by this service (Requirement: Event source filtering)
- [ ] Confirm `./event/examples/` contains one example per event type; flag any missing files before implementation starts (Requirement: Input validation)
- [ ] Clarify `PATCH_USER_GROUP_DETAIL` read-modify-write concurrency strategy — document the agreed approach (e.g. conditional expression, optimistic locking) before implementing REQ-5 patch handler (Requirement: Group detail patch — Scenario: Group patch — user not found)

## Implementation

- [ ] Create `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/configuration.py`: define `SqsEventConfig` with DTO field path mappings and `DdbRepositoryConfig` with table name env var, PK schema, entity model mappings, `softDeletedTtl` attribute name (Requirement: Hexagonal architecture)
- [ ] Create `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/port/repository.py`: abstract `Repository` with methods `save`, `soft_delete`, `retrieve`, `update_groups`, `update_forgot_token`, `update_passkeys` (Requirement: Hexagonal architecture)
- [ ] Create `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/adapter/ddb_repository.py`: `DynamoDbRepository` implementing `Repository` using the `DdbRepository` layer base class (Requirement: Hexagonal architecture)
- [ ] Create `saml_user_cmd_invoker_fn/saml_user_cmd_invoker/domain/service.py`: `Service` that routes by `entityType` then `eventType`; applies non-SAML guard; discards unknown types with error log; validates via `UserCommandValidator` before processing (Requirement: Event source filtering, Requirement: Input validation)
- [ ] Implement `ADD_USER_DETAIL` handler in `service.py`: call `repository.save(...)` to create a new user record (Requirement: User detail upsert — Scenario: New user added)
- [ ] Implement `UPDATE_USER_DETAIL` handler in `service.py`: call `repository.save(...)` to overwrite the existing user record (Requirement: User detail upsert — Scenario: Existing user updated)
- [ ] Implement `REMOVE_USER_DETAIL` handler in `service.py`: call `repository.soft_delete(...)` to set `softDeletedTtl = now + 300 s`; do not issue `DeleteItem` (Requirement: User detail soft-delete — Scenario: User removed)
- [ ] Implement `UPDATE_USER_GROUP_DETAIL` handler in `service.py`: call `repository.update_groups(...)` to overwrite group attributes (Requirement: Group detail patch)
- [ ] Implement `PATCH_USER_GROUP_DETAIL` handler in `service.py`: call `repository.retrieve(...)` first; if user not found log and discard; otherwise merge and call `repository.update_groups(...)` using the agreed concurrency strategy (Requirement: Group detail patch — Scenario: Group patch — user not found)
- [ ] Implement `PATCH_USER_FORGOT_TOKEN_DETAIL` handler in `service.py`: call `repository.update_forgot_token(...)` to update only forgot-token attributes (Requirement: Forgot-token detail patch)
- [ ] Implement `PATCH_USER_PASSKEY_DETAIL` handler in `service.py`: call `repository.update_passkeys(...)` to replace the `passkeys` array without touching other attributes (Requirement: Passkey detail patch — Scenario: Passkey updated)
- [ ] Create `saml_user_cmd_invoker_fn/app.py` Lambda entry point: wire `DynamoDbRepository` → `Service`, iterate SQS batch records, call `service.process(dto=dto)` (Requirement: Hexagonal architecture)
- [ ] Verify all write operations are idempotent — re-delivering the same event must produce the same DynamoDB state (Requirement: Idempotency)
