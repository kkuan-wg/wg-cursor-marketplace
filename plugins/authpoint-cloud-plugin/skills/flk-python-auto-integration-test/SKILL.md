---
name: flk-python-auto-integration-test
description: Generates automated integration test plans and pytest integration test files for Folklore services deployed on AWS (Lambda, ECS, Step Functions, etc.). Use when writing or reviewing integration tests, creating an auto-integration-test-plan, implementing integration_test.py files, or when the user mentions integration tests, deployed tests, automation QA tests, auto-integration-test-plan, or integration_tests/.
---

# Folklore Automated Integration Tests

Generates automated integration test plans and pytest test files that exercise deployed AWS services from their public input boundary to their observable output. Tests run after deployment in `dev`, are deployment-type agnostic, and report to Jenkins as a separate JUnit suite from unit tests.

This skill is always used in the context of the `flk-auto-integration-test-writer` agent, which supplies the spec ID and operation (`plan` or `implement`).

---

## Phase 1 (plan): Produce the Auto-Integration-Test Plan

**Complete all investigation before writing any output.**

### 1. Resolve the spec

Given the spec ID from `spec-id:` tag, locate the spec folder:
`ssot/folklore/domain/<domain>/specs/<spec-id>-<capability>/`

Read in this order:
- `spec.md` -- extract service name, AWS services involved, REQ-N acceptance criteria and GIVEN/WHEN/THEN scenarios
- `tasks.md` -- extract tasks under `## Integration Testing` only; these are the authoritative scope
- `proposal.md` -- extract artifact list and service boundary description
- `<SPEC-ID>-test-plan.md` (manual QA test strategy, co-located) -- **read when present**; use its scenario rows as the primary source for TC derivation so automated tests cover the same scenarios the QA team validated manually. If absent, derive TCs from `spec.md` scenarios directly and note the absence in the plan.

### 2. Discover resource names from the service repo

Browse the service repo to discover the concrete AWS resource identifiers needed for test payloads and assertions:

| Artefact | What to extract |
|---|---|
| `configuration.py` | Table env var names, topic ARN env var names, queue env var names, key derivation patterns |
| `template.yaml` | Logical resource names, SNS topic names, SQS queue names, API Gateway base path |
| ECS task definition | Task name, cluster, ALB endpoint |
| State machine definition | State machine ARN env var |

### 3. Identify input trigger and output observable per scenario

For each scenario from step 1, identify:
- **Input trigger** -- which AWS action sends data into the service (see `parts/input-triggers.md`)
- **Output observable** -- where to read the result (see `parts/output-assertions.md`)

### 4. Draft test cases

For each scenario derive one TC card. A TC is automatable if the input can be injected via an AWS API and the output can be read via an AWS API within a reasonable timeout. Mark scenarios as **Not automatable** or **Out of scope** when they cannot meet this bar -- document the reason.

Assign test data IDs using the prefix `test-auto-<spec-id>-<seq>` (e.g. `test-auto-aaas30040-001`). This prefix prevents collision with real data and makes cleanup unambiguous.

### 5. Write the plan file

Write `<SPEC-ID>-auto-integration-test-plan.md` to the spec repo at:
`ssot/folklore/domain/<domain>/specs/<spec-id>-<capability>/`

Follow the canonical structure from `references/examples/aaas-30040-auto-integration-test-plan.md` exactly.

The plan must include:
- Service Under Test table
- Test File path
- Shared Fixtures table
- Test Data Conventions
- Cleanup Strategy
- One TC card per automatable scenario
- Coverage Summary section (see below)

**Coverage Summary** maps every manual QA scenario to one of three statuses and computes the automation coverage percentage:

| Status | Meaning |
|---|---|
| Automated | Has a TC card in this plan |
| Not automatable | Cannot be triggered/asserted via AWS APIs within this service's boundary |
| Out of scope | Crosses the service boundary into end-to-end territory |

After writing the plan, **stop and tell the user** the plan has been written and must be reviewed before `implement` is run. Do not produce any test code.

---

## Phase 2 (implement): Write the Pytest Files

**Read the approved plan first. Do not produce any output until the plan file is confirmed.**

### 1. Read the plan

Locate `<SPEC-ID>-auto-integration-test-plan.md` in the spec repo at:
`ssot/folklore/domain/<domain>/specs/<spec-id>-<capability>/`

If the file does not exist, stop and tell the user to run the `plan` operation first.

### 2. Load the relevant parts

Read only what you need:
- `parts/setup.md` -- always; provides `conftest.py`, `requirements.txt`, `wait_for` helper
- `parts/input-triggers.md` -- for each trigger type used in the TC cards
- `parts/output-assertions.md` -- for each observable type used in the TC cards

### 3. Write test files

Write to the service repo under `application/integration_tests/`:

| File | Rule |
|---|---|
| `<service_name>_integration_test.py` | One class `Test<ServiceName>`; one method per TC card |
| `conftest.py` | Shared session-scoped `aws_auth` fixture + `cleanup_keys` function fixture; create only if missing or incomplete |
| `requirements.txt` | Add `daasdeployhelpers`, `pytest`, `boto3`, `requests`; create only if missing |

**Hard rules:**
- Each test method name matches the `pytest name` field in the TC card exactly
- Each test follows Arrange / Act / Assert with inline comments
- `cleanup_keys` fixture registers keys in `yield`; teardown deletes them regardless of pass/fail
- TCs that assert absence (nothing created) register nothing in cleanup
- No hardcoded ARNs, table names, or credentials -- always read from `os.environ`
- `wait_for` polling helper from `parts/setup.md` is always used for async assertions; never `time.sleep`

### 4. Verify before finishing

- [ ] One test method per TC card in the plan
- [ ] Test method names match `pytest name` fields exactly
- [ ] All AWS resource names read from `os.environ` (never hardcoded)
- [ ] `conftest.py` has `aws_auth` (session) and `cleanup_keys` (function) fixtures
- [ ] `requirements.txt` includes `daasdeployhelpers`, `pytest`, `boto3`, `requests`
- [ ] `wait_for` used for all async assertions
- [ ] `cleanup_keys` used for all TCs that create AWS resources
- [ ] Test file lives under `application/integration_tests/`
- [ ] Class name is `Test<ServiceName>`
- [ ] No test code written for `Not automatable` or `Out of scope` TCs

---

## Reference

- Setup, conftest, polling helper -> [parts/setup.md](parts/setup.md)
- Input trigger patterns (SNS, SQS, HTTP, DDB, StepFunction, Lambda) -> [parts/input-triggers.md](parts/input-triggers.md)
- Output assertion patterns (DDB poll, SQS receive, HTTP response, StepFunction poll, CloudWatch) -> [parts/output-assertions.md](parts/output-assertions.md)
- Cheat-sheet: AWS auth, env vars, naming, JUnit rules, TC-NN template -> [references/REFERENCE.md](references/REFERENCE.md)
- Canonical plan example (AAAS-30040 SAML user cache consumer) -> [references/examples/aaas-30040-auto-integration-test-plan.md](references/examples/aaas-30040-auto-integration-test-plan.md)
- Illustrative test file -> [references/examples/dummy_operations_test.py](references/examples/dummy_operations_test.py)
