# Setup: requirements.txt, conftest.py, wait_for helper

---

## requirements.txt

Create `application/integration_tests/requirements.txt` if missing. Minimum entries:

```
daasdeployhelpers
pytest
boto3
requests
```

Add any service-specific libraries needed by the test file (e.g. `botocore` is already a `boto3` dependency and does not need a separate line).

---

## conftest.py

Create `application/integration_tests/conftest.py` if missing or incomplete. The file provides two fixtures shared across all integration test files.

```python
import os
import time
import pytest
from daasdeployhelpers import authentication as wgc_auth


@pytest.fixture(scope="session")
def aws_auth():
    """Session-scoped STS auth via daasdeployhelpers. Returns a boto3 client factory."""
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    environment = os.environ.get("ENVIRONMENT", "dev")
    account_group = os.environ.get("ACCOUNT_GROUP", "WG-AuthPointSec")
    assert region, "AWS_REGION or AWS_DEFAULT_REGION must be set."

    auth = wgc_auth.Authentication()
    sts = auth.sts(environment=environment, account_group=account_group)

    def client(service_name):
        return auth.clientsetup(client=service_name, region=region, sts=sts)

    return client


@pytest.fixture()
def cleanup_keys():
    """
    Function-scoped fixture that accumulates (delete_fn, key) pairs and
    calls each delete_fn(key) in teardown regardless of test outcome.

    Usage in test:
        def test_something(self, cleanup_keys, ddb_client):
            cleanup_keys.append((lambda k: ddb_client.delete_item(..., Key=k), pk))
    """
    keys = []
    yield keys
    for delete_fn, key in keys:
        try:
            delete_fn(key)
        except Exception:
            pass
```

**Rules:**
- `aws_auth` is session-scoped -- STS credentials are obtained once per test run.
- `cleanup_keys` is function-scoped -- resets between tests.
- Tests append `(delete_fn, key)` tuples to `cleanup_keys`; teardown calls each regardless of pass/fail.
- TCs that assert absence do not append anything.
- Never catch exceptions from assertions in teardown -- only from cleanup calls (swallowed silently to avoid masking the real failure).

---

## wait_for polling helper

Add this module-level function to `conftest.py` (or import it from there in test files). It replaces all `time.sleep` calls in integration tests.

```python
def wait_for(predicate, timeout=30, interval=2, description="condition"):
    """
    Poll `predicate()` every `interval` seconds until it returns a truthy value
    or `timeout` seconds have elapsed.

    Returns the truthy value returned by `predicate`.
    Raises AssertionError if the timeout is reached.

    Args:
        predicate: callable() -> any truthy/falsy value
        timeout: max seconds to wait (default 30)
        interval: seconds between polls (default 2)
        description: human-readable label used in the timeout error message

    Example:
        item = wait_for(
            lambda: get_ddb_item(ddb_client, table, key),
            timeout=30,
            description=f"DDB item {key} to appear",
        )
        assert item["status"]["S"] == "ACTIVE"
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(interval)
    raise AssertionError(f"Timed out after {timeout}s waiting for: {description}")
```

**Usage rules:**
- Always pass a `description` so timeouts are readable in CI output.
- For absence assertions (asserting something is NOT created), use a fixed wait followed by a direct check -- do not use `wait_for` with a negated predicate, as it would succeed immediately.

```python
# Absence assertion pattern -- fixed wait, then check
time.sleep(15)
response = ddb_client.get_item(TableName=table, Key=key)
assert "Item" not in response, f"Expected no item at {key} but found one"
```

---

## Environment variables

All integration tests read AWS resource identifiers from environment variables -- never hardcode ARNs, table names, or account IDs. The Jenkins `withEnv` block injects the following at runtime:

| Variable | Source | Example |
|---|---|---|
| `AWS_REGION` | Jenkins param | `us-west-2` |
| `ENVIRONMENT` | Jenkins param | `dev` |
| `ACCOUNT_GROUP` | Jenkins param | `WG-AuthPointSec` |

Service-specific resource names (table names, topic ARNs, queue URLs, API endpoints) must also come from environment variables. Discover the env var names from `configuration.py` in the service repo.
