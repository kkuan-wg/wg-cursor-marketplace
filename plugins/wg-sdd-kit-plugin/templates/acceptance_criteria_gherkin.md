
# Acceptance Criteria – Gherkin Patterns (Angular + Python)

## Happy Path
- Given a valid authenticated user with a fresh JWT
  When they perform <action> in the Angular app
  Then the Python API returns <result> within <p95 ms> and the UI reflects the change

## Validation / Error
- Given invalid input <field/format>
  When the request is sent
  Then the API responds with 4xx and the UI shows an accessible error (aria-live)

## Permission / AuthZ
- Given a user with <role/permission>
  When they attempt <action>
  Then the action succeeds and an audit event is recorded
- Given a user without <role/permission>
  When they attempt <action>
  Then access is denied and no state change occurs

## Idempotency / Retry
- Given a write is retried due to timeout
  When the same request is received within <window>
  Then the operation is applied once (idempotency key) and a metric is emitted

## Observability
- Given the operation completes
  When success/failure occurs
  Then emit FE event <name> and API logs/metrics/traces with correlation IDs

## Accessibility
- Given a screen reader user
  When the UI updates
  Then focus is managed correctly and ARIA labels describe the change
