# Tasks — SAML User Cache Consumer Unit Tests

> Spec: [./spec.md](./spec.md)

## Testing

- [ ] Unit test: non-SAML event is skipped without a DynamoDB write (Scenario: Non-SAML event is ignored)
- [ ] Unit test: unrecognised `entityType` is logged and discarded without a DynamoDB write (Scenario: Unknown entityType is discarded)
- [ ] Unit test: `ADD_USER_DETAIL` creates a new item with `softDeletedTtl` absent (Scenario: New user added)
- [ ] Unit test: `UPDATE_USER_DETAIL` overwrites the existing item (Scenario: Existing user updated)
- [ ] Unit test: `REMOVE_USER_DETAIL` sets `softDeletedTtl = now + 300 s` and does not call `DeleteItem` (Scenario: User removed)
- [ ] Unit test: `UPDATE_USER_GROUP_DETAIL` replaces group attributes; non-group fields are unchanged (Requirement: Group detail patch)
- [ ] Unit test: `PATCH_USER_GROUP_DETAIL` with user not found logs and discards without a write (Scenario: Group patch — user not found)
- [ ] Unit test: `PATCH_USER_FORGOT_TOKEN_DETAIL` updates only forgot-token attributes; all other fields are unchanged (Requirement: Forgot-token detail patch)
- [ ] Unit test: `PATCH_USER_PASSKEY_DETAIL` replaces the `passkeys` array and does not modify other attributes (Scenario: Passkey updated)
- [ ] Unit test: re-delivering the same event produces the same DynamoDB state (Requirement: Idempotency)
- [ ] Integration test: SNS filter policy drops events not matching `ResourceTypes: SAML` before they reach the queue (Requirement: Event source filtering)
