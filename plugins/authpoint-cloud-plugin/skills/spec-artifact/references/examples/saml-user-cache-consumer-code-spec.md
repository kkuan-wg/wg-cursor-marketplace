# SAML User Cache Consumer

> **Spec ID:** aaas-30040  
> **Type:** Code  
> **AWS Services:** Lambda, SQS, DynamoDB, SNS

## References

- SAML event schema (AsyncAPI 3.0.0): `get_events(domain='saml', schema_name='schema')` (`../../event/schema.yaml`) — channel `flk-saml-user-cmd-queue.fifo`, operation `consumeUserCommands`; messages: `AddUserDetail`, `UpdateUserDetail`, `RemoveUserDetail`, `UpdateUserGroupDetail`, `PatchUserGroupDetail`, `PatchUserForgotTokenDetail`, `PatchUserPasskeyDetail`
- Event example: `get_event_example(domain='saml', event_name='ADD_USER_DETAIL')` — relevant to REQ-3
- Event example: `get_event_example(domain='saml', event_name='UPDATE_USER_DETAIL')` — relevant to REQ-3
- Event example: `get_event_example(domain='saml', event_name='REMOVE_USER_DETAIL')` — relevant to REQ-4
- Event example: `get_event_example(domain='saml', event_name='UPDATE_USER_GROUP_DETAIL')` — relevant to REQ-5
- Event example: `get_event_example(domain='saml', event_name='PATCH_USER_GROUP_DETAIL')` — relevant to REQ-5
- Event example: `get_event_example(domain='saml', event_name='PATCH_USER_FORGOT_TOKEN_DETAIL')` — relevant to REQ-6
- Event example: `get_event_example(domain='saml', event_name='PATCH_USER_PASSKEY_DETAIL')` — relevant to REQ-7
- Cache domain event schema (canonical payloads): `get_events(domain='cache', schema_name='add-user-detail.asyncapi')` (`../../../cache/event/add-user-detail.asyncapi.yaml`) — representative per-event AsyncAPI; use `list_events(domain='cache')` for the full set
- Database model: `get_database_model(domain='saml', model_name='flk-saml-user-detail')` (`../../database-model/flk-saml-user-detail.json`) — GSIs: `emailGSI` (`accountId#email`), `usernameGSI` (`accountId#username`); TTL fields: `ttl` (5-min cache TTL, set on upsert), `softDeletedTtl` (300-s soft-delete marker, set on remove); DynamoDB Streams: enabled, `NEW_AND_OLD_IMAGES`; `passkeys` array: WebAuthn credentials (`credentialId`, `friendlyCredentialId`, `status: ACTIVE|INACTIVE|REVOKED`)

## Requirements

### REQ-1: Event source filtering

The SAML consumer MUST subscribe to `flk-user-cmd-topic.fifo` and MUST filter messages using the SNS message attribute `resourceTypes` to those where:

- `ResourceTypes` contains `SAML`.
- `EntityType` is one of: `USER`, `USER_GROUP`, `USER_FORGOT_TOKEN`, `USER_PASSKEY`.

The consumer MUST route processing by `entityType` first, then by `eventType`.

#### Scenario: Non-SAML event is ignored

- **GIVEN** a user cache event where `resourceTypes` does not include `SAML`
- **WHEN** the event is delivered to the SAML consumer
- **THEN** the message is skipped and `flk-saml-user-detail` is not modified

#### Scenario: Unknown entityType is discarded

- **GIVEN** an event with an unrecognised `entityType`
- **WHEN** the consumer processes the event
- **THEN** an error is logged and the message is discarded without modifying `flk-saml-user-detail`

### REQ-2: Input validation

Before processing any event, the consumer MUST validate the incoming message via `UserCommandValidator` scoped to resource type `SAML`. An invalid message MUST be discarded with an error log and MUST NOT be written to `flk-saml-user-detail`.

### REQ-3: User detail upsert

On receiving `ADD_USER_DETAIL` or `UPDATE_USER_DETAIL` (`EntityType: USER`), the consumer MUST write or overwrite the user record in `flk-saml-user-detail`.

#### Scenario: New user added

- **GIVEN** an `ADD_USER_DETAIL` event for a SAML resource
- **WHEN** the consumer processes the event
- **THEN** a new item is created in `flk-saml-user-detail`

#### Scenario: Existing user updated

- **GIVEN** an `UPDATE_USER_DETAIL` event for an existing user
- **WHEN** the consumer processes the event
- **THEN** the existing item is overwritten in `flk-saml-user-detail`

### REQ-4: User detail soft-delete

On receiving `REMOVE_USER_DETAIL` (`EntityType: USER`), the consumer MUST soft-delete the corresponding item in `flk-saml-user-detail` by setting `softDeletedTtl` to `now + 300 seconds`. The item MUST NOT be immediately removed from DynamoDB; it expires via DynamoDB TTL. The regular `ttl` attribute MUST NOT be updated on a remove event.

#### Scenario: User removed

- **GIVEN** a `REMOVE_USER_DETAIL` event for a SAML resource
- **WHEN** the consumer processes the event
- **THEN** the item's `softDeletedTtl` is set to `now + 300s` in `flk-saml-user-detail`
- **AND** the item is physically removed by DynamoDB TTL expiry, not by an explicit `DeleteItem`

### REQ-5: Group detail patch

On receiving `UPDATE_USER_GROUP_DETAIL` or `PATCH_USER_GROUP_DETAIL` (`EntityType: USER_GROUP`), the consumer MUST update only the group-related attributes of the existing user record in `flk-saml-user-detail`.

For `PATCH_USER_GROUP_DETAIL`, the consumer MUST read the current user record first and merge the patch into the existing groups data.

#### Scenario: Group patch — user not found

- **GIVEN** a `PATCH_USER_GROUP_DETAIL` event for a SAML resource
- **WHEN** the consumer reads `flk-saml-user-detail` and the user record does not exist
- **THEN** an error is logged and the patch is discarded without writing to `flk-saml-user-detail`

### REQ-6: Forgot-token detail patch

On receiving `PATCH_USER_FORGOT_TOKEN_DETAIL` (`EntityType: USER_FORGOT_TOKEN`), the consumer MUST update only the forgot-token attributes of the existing user record in `flk-saml-user-detail`.

### REQ-7: Passkey detail patch

On receiving `PATCH_USER_PASSKEY_DETAIL` (`EntityType: USER_PASSKEY`), the consumer MUST update only the `passkeys` array of the existing user record in `flk-saml-user-detail`. See `get_database_model(domain='saml', model_name='flk-saml-user-detail')` for the `passkeys` attribute schema and `get_event_example(domain='saml', event_name='PATCH_USER_PASSKEY_DETAIL')` for an example payload.

#### Scenario: Passkey updated

- **GIVEN** a `PATCH_USER_PASSKEY_DETAIL` event for a SAML resource
- **WHEN** the consumer processes the event
- **THEN** the `passkeys` array is replaced in the existing user record in `flk-saml-user-detail`
- **AND** no other attributes of the user record are modified

### REQ-8: Hexagonal architecture

The consumer MUST follow a hexagonal (Ports & Adapters) structure:

- **Domain layer** (`service.py`): `Service` class — event routing by `entityType` then `eventType`; contains all business logic.
- **Port layer** (`port/repository.py`): `Repository` abstract class — defines `save`, `soft_delete`, `retrieve`, `update_groups`, `update_forgot_token`, `update_passkeys`.
- **Adapter layer** (`adapter/dynamodb_repository.py`): `DynamoDbRepository` — implements `Repository` using `flk-saml-user-detail`.
- **Lambda entry** (`app.py`): wires dependencies and calls `service.process(dto=dto)` per message.

### REQ-9: Idempotency

All write operations MUST be idempotent. Re-delivery of the same event MUST produce the same final state in `flk-saml-user-detail` without error.
