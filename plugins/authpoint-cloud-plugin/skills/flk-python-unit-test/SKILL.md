---
name: flk-python-unit-test
description: Generate and validate pytest unit tests for Folklore Python Lambda projects following hexagonal architecture (service, repository, publisher, producer, invoker, http/sqs/ddb event adapters, crypto). Use when creating tests for a Service, Repository, Publisher, Producer, Invoker, Responder, Crypto adapter, or when the user mentions pytest, unit tests, test fixtures, test constants, or coverage setup.
---

# Folklore Python Unit Tests

Creates pytest unit tests (test files + matching constants files) for Folklore Lambda functions following hexagonal architecture. Covers service, repository, publisher/producer, invoker, responder, crypto and event-adapter tests — plus the project-level test setup (`pytest.ini`, `.coveragerc`, `sonar-project.properties`, `tests/requirements.txt`) when missing or incomplete.

`flk-python-hexagonal` is always loaded alongside this skill — layer/port/adapter conventions defined there are assumed and never repeated here.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

Inputs are evaluated in the following order of precedence:

1. **Spec path** (primary). When `spec.md` is provided, also read `proposal.md` and `unit-tests-tasks.md` from the **same folder** as `spec.md`:
   - `spec.md` — extract: REQ descriptions, port method names, DTO fields, error codes, table names.
   - `proposal.md` — extract: scope boundaries (which fn(s) the testing covers).
   - `unit-tests-tasks.md` — extract: ordered unit-test tasks to implement for this spec.
2. **Source code under `src/`** (always). Before writing a test, read the corresponding `src/<fn>/<module>/` to extract real method names, port signatures, adapter dependencies, and config classes.
3. **Existing tests** (when present). If `application/tests/<...>/<fn>/` already has files, read them first to inherit local style (constant naming, fixture chains, `_BASE_*` prefixes) and **extend** instead of duplicating. Pre-existing tests are reference, not authority — when they conflict with this skill, the skill wins, but never refactor tests outside the current scope.
4. **Direct fn path** (no spec). Without a spec, the user supplies `src/<fn>/`; ask only for that path.

### 2. Browse the codebase

**All browsing and writing is scoped to the current workspace.** Never navigate into sibling repositories to locate references or to place output files.

For the target fn, identify which artefacts exist (and therefore need tests):

| Found in `src/<fn>/<module>/` | Test artefact |
|---|---|
| `domain/service.py` | `service_test.py` + `service_constants.py` |
| `adapter/ddb_repository.py` | `ddb_repository_test.py` + `ddb_repository_constants.py` |
| `adapter/api_responder.py` | `api_responder_test.py` + `api_responder_constants.py` |
| `adapter/sns_publisher.py` | `sns_publisher_test.py` + `sns_publisher_constants.py` |
| `adapter/sqs_producer.py` | `sqs_producer_test.py` + `sqs_producer_constants.py` |
| `adapter/api_gateway_invoker.py` | `api_gateway_invoker_test.py` + `api_gateway_invoker_constants.py` |
| `adapter/lambda_invoker.py` | `lambda_invoker_test.py` + `lambda_invoker_constants.py` |
| `adapter/comm_crypto.py` | `comm_crypto_test.py` |
| `app.py` uses `HttpEvent` | `http_event_test.py` + `http_event_constants.py` |
| `app.py` uses `SqsEvent` | `sqs_message_test.py` + `sqs_message_constants.py` |
| `app.py` uses `DdbStreamEvent` | `ddb_stream_test.py` + `ddb_stream_constants.py` |

Check `application/pytest.ini`, `application/.coveragerc`, `application/sonar-project.properties`, and `application/tests/requirements.txt`. If any is missing or does not include the new fn / its env vars / its dependencies, the project setup must be updated (see `parts/setup.md`).

### 3. Load skill parts progressively

Read only the parts relevant to the artefacts being generated:

| Need | Part to read |
|------|--------------|
| Project setup (pytest.ini / .coveragerc / sonar / requirements) | `parts/setup.md` |
| Constants file structure and import chain | `parts/constants.md` |
| Event adapter tests (HttpEvent / SqsEvent / DdbStreamEvent) | `parts/http-event.md` |
| Service tests (fixture chain, parametrize, error paths) | `parts/service.md` |
| Repository tests (PK/SK/GSI schema, method coverage) | `parts/repository.md` |
| Publisher / Producer / Responder tests | `parts/publisher.md` |
| Invoker / Crypto tests | `parts/invoker.md` |

### 4. Ask only what you cannot find

One targeted question per gap. Never ask about things discoverable from the spec, the `src/` code, or existing tests.

---

## Phase 2: Write the Files

### Order of writing

For each fn in scope, write files in this order so that constants are available when the next test imports them:

1. `http_event_constants.py` (or `sqs_message_constants.py` / `ddb_stream_constants.py`) — base of the import chain.
2. `http_event_test.py` (or `sqs_message_test.py` / `ddb_stream_test.py`).
3. `ddb_repository_constants.py` (imports from `http_event_constants`); then `ddb_repository_test.py`.
4. Adapter constants + tests (`api_responder`, `sns_publisher`, `sqs_producer`, `api_gateway_invoker`, `lambda_invoker`, `comm_crypto`).
5. `service_constants.py` (imports from event + repository constants); then `service_test.py`.

### Folder layout

Tests mirror the `src/` lambda function hierarchy exactly:

```
application/
├── tests/
│   ├── requirements.txt
│   ├── api/<fn_name>/
│   │   ├── http_event_test.py + http_event_constants.py
│   │   ├── service_test.py + service_constants.py
│   │   ├── ddb_repository_test.py + ddb_repository_constants.py
│   │   ├── sns_publisher_test.py + sns_publisher_constants.py
│   │   ├── api_responder_test.py + api_responder_constants.py
│   │   ├── api_gateway_invoker_test.py + api_gateway_invoker_constants.py
│   │   └── comm_crypto_test.py
│   ├── cache/<category>/<fn_name>/      (same pattern)
│   ├── transaction/<category>/<fn_name>/
│   └── data/<category>/<fn_name>/
├── pytest.ini
├── .coveragerc
└── sonar-project.properties
```

- Test files: `*_test.py` — one class per file (`TestService`, `TestDdbRepositoryConfig`, `TestHttpEvent`, etc.).
- Constants files: `*_constants.py` — pure modules (no classes, no functions).
- An empty `__init__.py` exists in every test directory.

### Hard rules (no exceptions)

- **Given/When/Then** — every test method has the three inline comments, in that order.
- **Mocking** — replace methods directly on the instantiated object (`service.repository.foo = mocker.Mock(...)`); never `@patch(...)` decorators.
- **`TemplateParser` is never mocked** — always a real instance via fixture.
- **Env vars** — declared only in `pytest.ini` under `[env]`. Never `os.environ[...]` in tests.
- **Not tested** — `app.py` (entry point), `port/*.py` (ABCs), and validation rule duplication.
- **Parametrize** — use `@pytest.mark.parametrize` whenever 2+ cases share the same structure; every `param(...)` has `id='N'` (numeric string).
- **`_patch_*` fixtures** — injected into the `service` fixture (or its peers), never into individual tests.
- **`assert_not_called()`** — used to verify branches that should not be taken in a given parametrized case.
- **Constants reuse** — follow the import chain `http_event_constants → ddb_repository_constants → service_constants`.

See [references/REFERENCE.md](references/REFERENCE.md) for the consolidated rules-by-layer view, and [references/examples/](references/examples/) for real working test files extracted from production Lambdas.

---

## Phase 3: Verify Before Finishing

### Project setup
- [ ] `pytest.ini` `pythonpath` includes the new fn `src/` dir + both layers
- [ ] `pytest.ini` `[env]` includes every env var read by the fn under test
- [ ] `.coveragerc` omits `*/port/*`, `*/app.py`, `tests/*`
- [ ] `tests/requirements.txt` includes every library imported by the fn (including layer dependencies)
- [ ] `sonar-project.properties` exists with the standard exclusions

### Per fn
- [ ] Event adapter test + constants exist (one of `http_event` / `sqs_message` / `ddb_stream`)
- [ ] `service_test.py` + `service_constants.py` exist
- [ ] One `*_test.py` + `*_constants.py` per adapter present in `src/<fn>/<module>/adapter/`
- [ ] No tests for `app.py` or `port/*.py`

### Test quality
- [ ] One class per test file
- [ ] Every test has Given/When/Then inline comments
- [ ] `TemplateParser` is real, never mocked
- [ ] `@pytest.mark.parametrize` used when 2+ cases share structure; all `param` have `id='N'`
- [ ] `_patch_*` fixtures injected into `service` fixture, not into individual tests
- [ ] `assert_not_called()` used to verify untaken branches
- [ ] Constants files are pure modules (no classes, no functions)
- [ ] Constants reused via import chain (`http_event` → `repository` → `service`)
- [ ] `test_required_fields` present for every `Validator` class with `REQUIRED_FIELDS`
- [ ] `test_api_error_codes` present whenever `API_ERROR_CODES` exists in `configuration.py`
- [ ] Invoker tests cover the `{}`-on-error path
- [ ] Repository tests cover `test_build_key` (PK/SK) and `test_build_gsi_key` for every GSI

---

## Phase 4: Run, Analyse, Fix, Repeat

After the Phase 3 checklist passes, **run the tests and iterate until the full suite is green**. This phase is mandatory — never skip it.

### 4.1 Run the suite

From `application/`:

```bash
python -m pytest --cov-report term-missing
```

### 4.2 Classify each failure

For every failing test or error in the output, determine the root cause:

| Category | Examples | Action |
|----------|----------|--------|
| **Test bug** | wrong mock target, missing fixture, bad constant, incorrect assertion | Fix the test / constants file |
| **Setup issue** | missing env var in `pytest.ini`, missing dependency in `tests/requirements.txt`, wrong `pythonpath` | Fix the project setup file |
| **Business logic concern** | the production code appears to have a bug; the test correctly exposes it | **Do not change the test** — surface the concern to the user (see 4.3) |

**Assume the production (business logic) code is correct.** Only fix test code and project-setup files. Never modify pre-existing `src/` files to make tests pass, unless specified by the user.

### 4.3 Surface concerns to the user

If you identify a failure that cannot be fixed without changing production code, or a result that looks like a real business-logic defect, output a clearly labelled block **before finishing**:

```
⚠ CONCERN: <test_file>::<TestClass>::<test_method>
  Symptom  : <one-line description of the failure>
  Suspicion: <why this might be a real bug in the source code>
  Suggested: <what the developer should investigate>
```

### 4.4 Loop until green (or only concerns remain)

Repeat steps 4.1 → 4.2 → fix → 4.1 until one of:

- **All tests pass** — report the final coverage summary.
- **Only concerns remain** — all remaining failures have been logged as concerns in 4.3; report them and stop.

Do not give up after a single failed attempt. Each iteration must make measurable progress (at least one fewer failure). If two consecutive runs produce identical failure counts with no new fixes applied, treat the remaining failures as concerns and stop.

## Reference

- Rules-by-layer cheat sheet, fixture chains, naming conventions → [references/REFERENCE.md](references/REFERENCE.md)
- Real working test files (service, repository, http/sqs/ddb event, sns publisher, sqs producer, api responder, api gateway invoker) → [references/examples/](references/examples/)
- Detailed patterns per artefact (with full code samples) → [parts/setup.md](parts/setup.md), [parts/constants.md](parts/constants.md), [parts/http-event.md](parts/http-event.md), [parts/service.md](parts/service.md), [parts/repository.md](parts/repository.md), [parts/publisher.md](parts/publisher.md), [parts/invoker.md](parts/invoker.md)
