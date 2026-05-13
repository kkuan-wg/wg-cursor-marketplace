# Folklore Python Unit Tests — Reference

Consolidated reference for Folklore pytest patterns. Read when implementing test fixtures, choosing what to mock, or verifying that a test file follows the conventions.

The detailed per-artefact patterns (with full code samples) live in `parts/`. This file is the cheat sheet — when in doubt, drop into the matching `parts/*.md`, then look at `examples/` for a real production file.

---

## 1. File and class naming

| Artefact | Test file | Constants file | Test class |
|----------|-----------|----------------|-----------|
| `domain/service.py` | `service_test.py` | `service_constants.py` | `TestService` |
| `adapter/ddb_repository.py` | `ddb_repository_test.py` | `ddb_repository_constants.py` | `TestDdbRepositoryConfig` |
| `adapter/api_responder.py` | `api_responder_test.py` | `api_responder_constants.py` | `TestResponder` |
| `adapter/sns_publisher.py` | `sns_publisher_test.py` | `sns_publisher_constants.py` | `TestSnsPublisher` |
| `adapter/sqs_producer.py` | `sqs_producer_test.py` | `sqs_producer_constants.py` | `TestSqsProducer` |
| `adapter/api_gateway_invoker.py` | `api_gateway_invoker_test.py` | `api_gateway_invoker_constants.py` | `TestApiGatewayInvoker` |
| `adapter/lambda_invoker.py` | `lambda_invoker_test.py` | `lambda_invoker_constants.py` | `TestLambdaInvoker` |
| `adapter/comm_crypto.py` | `comm_crypto_test.py` | (constants reused from event/service) | `TestCommCrypto` |
| `HttpEvent` (in `app.py`) | `http_event_test.py` | `http_event_constants.py` | `TestHttpEvent` |
| `SqsEvent` (in `app.py`) | `sqs_message_test.py` | `sqs_message_constants.py` | `TestSqsMessage` |
| `DdbStreamEvent` (in `app.py`) | `ddb_stream_test.py` | `ddb_stream_constants.py` | `TestDdbStreamEvent` |

One class per test file. Test method names follow `test_<scenario>_with_<outcome>` (e.g. `test_process_with_success`, `test_retrieve_policy_with_error`).

---

## 2. Mock-target cheat sheet

Always replace the **layer-method** (the inner attribute used by the adapter), never the adapter method itself.

| Adapter | What to mock | Example |
|---------|--------------|---------|
| `Service` | every collaborator method on the service instance | `service.repository.retrieve_item = mocker.Mock(return_value=...)` |
| `DdbRepository` | the underlying `repository.<layer_method>` | `repo.repository.get_item_by_partition_key = mocker.Mock(...)` |
| `ApiResponder` | nothing — exercise the real responder against expected response constants | — |
| `SnsPublisher` | `publisher.sns_publisher.publish_message` | `publisher.sns_publisher.publish_message = mocker.Mock()` |
| `SqsProducer` | `producer.sqs_producer.send_message` | `producer.sqs_producer.send_message = mocker.Mock()` |
| `ApiGatewayInvoker` | `invoker.api_invoker.execute_request` | `invoker.api_invoker.execute_request = mocker.Mock(return_value=...)` |
| `LambdaInvoker` | `invoker.lambda_invoker.invoke_lambda` | `invoker.lambda_invoker.invoke_lambda = mocker.Mock(...)` |
| `CommCrypto` | `crypto.payload_crypto.decrypt_agent` / `encrypt_agent` (and mock `CommCrypto.initialize_crypto` at class level in the fixture) | see `parts/invoker.md` |

`TemplateParser` is **always** real:

```python
@pytest.fixture
def template_parser(self):
    return TemplateParser()
```

---

## 3. Fixture chain (service tests)

Build bottom-up: `template_parser` → individual adapters → `service`. Inject `_patch_*` fixtures into `service`, never into individual tests.

```
template_parser ─┬─► repository
                 ├─► publisher
                 ├─► producer
                 ├─► invoker
                 └─► crypto
                        │
                        ▼
       _patch_get_timestamp_now ──► service
```

`FAKE_TIME` is a class-level constant on `TestService` (`datetime(2021, 9, 30, 0, 0, tzinfo=timezone.utc)`).

See `parts/service.md` for the full fixture chain with code.

---

## 4. Parametrize and `id`

Use `@pytest.mark.parametrize` whenever 2+ cases share the same structure. Always assign a numeric string `id`:

```python
@pytest.mark.parametrize('input_dto, expected', [
    param(DTO_A, RESPONSE_A, id='1'),
    param(DTO_B, RESPONSE_B, id='2'),
])
```

For error paths, prefer **one** parametrized test covering all invalid variants over one test per missing field.

---

## 5. Required-fields and error-codes guards

Two non-business tests are mandatory whenever the corresponding artefact exists:

- `test_required_fields` — asserts `Validator.REQUIRED_FIELDS == EXPECTED_REQUIRED_FIELDS`. Forces an explicit update whenever the validator changes.
- `test_api_error_codes` — asserts `API_ERROR_CODES == EXPECTED_API_ERROR_CODES`. Catches accidental error-code changes.

`EXPECTED_REQUIRED_FIELDS` lives in `service_constants.py`; `EXPECTED_API_ERROR_CODES` lives in `api_responder_constants.py`.

---

## 6. Constants — import chain

```
http_event_constants.py        ← raw event + parsed DTO (base)
        ↓
ddb_repository_constants.py    ← + DDB keys, GSI keys, DB items
        ↓
service_constants.py           ← + client config, expected responses, EXPECTED_REQUIRED_FIELDS
```

- Constants files are pure modules — no classes, no functions.
- Use `deepcopy(_BASE_X) | {overrides}` for variants.
- `_BASE_*` prefix marks file-private base dicts.
- `service_constants.py` may shadow an imported constant with an enriched version (e.g. add `swaEnabled` to `HTTP_EVENT_DTO`).

---

## 7. AWS error simulation

Simulate transport failures with `botocore` errors and successive responses with `side_effect`:

```python
service.publisher.transaction_created = mocker.Mock(side_effect=BotoCoreError())
service.repository.retrieve_item = mocker.Mock(side_effect=[{}, USER_DETAIL_DB])
```

For invokers, the contract is "return `{}` on error, never raise":

```python
invoker.api_invoker.execute_request = mocker.Mock(side_effect=Exception)
assert adapter.retrieve_policy(dto=DTO) == {}
```

---

## 8. Project setup files

| File | Purpose | Cheat |
|------|---------|-------|
| `application/pytest.ini` | `pythonpath` (every fn `src/` + both layers), `[env]` (every env var the fn reads), `--cov=src` | env vars must include all values the fn calls `getenv(...)` for |
| `application/.coveragerc` | omits `*/port/*`, `*/app.py`, `tests/*`; `branch = True` | |
| `application/sonar-project.properties` | sonar exclusions for `port/`, `app.py`, `configure_newrelic.py` | |
| `application/tests/requirements.txt` | every library imported by any fn under test | layer dependencies count too |

Detailed templates live in `parts/setup.md`.

---

## 9. Real examples — when to read each

| Example | What it shows |
|---------|--------------|
| [examples/oidc_discovery_api/](examples/oidc_discovery_api/) | Minimal API Lambda — fixture chain (`template_parser` → `repository` → `responder` → `service`), `test_required_fields`, single-GSI `test_client_config_build_key`, compact `http_event` test with DTO log assertion |
| [examples/oidc_user_detail_listener/](examples/oidc_user_detail_listener/) | DDB stream listener — `ddb_stream_test.py` event-adapter test, multi-branch service routing with `assert_not_called` on untaken branches, repository test covering soft-delete |
| [examples/oidc_tx_request_consumer/](examples/oidc_tx_request_consumer/) | SQS consumer — `sqs_message_test.py` with `eventExpired` variant, `service_test.py` with `BotoCoreError` fallback to producer, `sqs_producer_test.py` with `_patch_datetime_now` (`monkeypatch.setattr`) and dynamic `getattr(producer, method_called)` dispatch, repository covering multiple GSIs and `model_mappings_entity_key` |
| [examples/oidc_authn_api/](examples/oidc_authn_api/) | Full API Lambda — single parametrized `test_publish_message` covering all SNS event types, one test per response method + `test_api_error_codes`, `api_gateway_invoker` success + error returning `{}` + `test_invoker_response_mapping` validating `responseDataMappings` |

The files keep the original naming used in `folklore-service` (e.g. `db_repository_config_test.py`, `api_request_test.py`). The canonical naming that **your** new suites must follow is in section 1 — the examples are pattern references, not naming references. Imports inside these files point to the original `folklore-service` package layout, so **do not execute them** — open them only to read the patterns, then adapt the DTOs, configs and module names to the workspace you are writing tests for.

---

## 10. Decisions & gotchas

| Decision | Rule |
|----------|------|
| `app.py` tests | None — `app.py` is wiring only |
| `port/*.py` tests | None — pure ABCs; excluded from coverage |
| `os.environ` in tests | Forbidden — declare in `pytest.ini` `[env]` |
| `@patch` decorators | Forbidden — replace methods on the instance |
| `TemplateParser` mocking | Forbidden — always real |
| Mock target | Layer method (`adapter.<inner>.<method>`), never the adapter method |
| `param(...)` `id` | Always a numeric string |
| `_patch_*` fixtures | Injected into `service` fixture, not individual tests |
| Constants imports | Always upward in the chain (`http_event` → `repository` → `service`) |
| Invoker on error | Returns `{}`, never raises — assert `{}` is returned |
