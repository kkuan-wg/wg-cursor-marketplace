# Automated Integration Tests -- Cheat Sheet

Quick reference for writing and reviewing Folklore automated integration tests.

---

## AWS authentication

Always use `daasdeployhelpers` -- never hardcode credentials or create boto3 sessions directly.

```python
from daasdeployhelpers import authentication as wgc_auth

auth = wgc_auth.Authentication()
sts = auth.sts(environment=os.environ["ENVIRONMENT"], account_group=os.environ["ACCOUNT_GROUP"])
ddb_client = auth.clientsetup(client="dynamodb", region=os.environ["AWS_REGION"], sts=sts)
```

In tests, the `aws_auth` session fixture in `conftest.py` wraps this and provides a one-liner:
```python
ddb_client = aws_auth("dynamodb")
sns_client = aws_auth("sns")
```

---

## Required environment variables

Jenkins injects these via `withEnv`. Tests must assert their presence at startup (done in `conftest.py`).

| Variable | Description |
|---|---|
| `AWS_REGION` | AWS region (e.g. `us-west-2`) |
| `ENVIRONMENT` | Deployment environment (always `dev` for integration tests) |
| `ACCOUNT_GROUP` | AWS account group (e.g. `WG-AuthPointSec`) |

Service-specific resource names (table names, topic ARNs, queue URLs, API endpoints) must also be environment variables -- discover their names from `configuration.py` in the service repo.

---

## Naming conventions

| Item | Convention | Example |
|---|---|---|
| Test file | `<service_name>_integration_test.py` | `saml_user_cache_consumer_integration_test.py` |
| Test class | `Test<ServiceName>` (PascalCase) | `TestSamlUserCacheConsumer` |
| Test method | `test_<tc_id>_<short_description>` | `test_tc01_add_saml_user_creates_cache_entry` |
| Test data ID prefix | `test-auto-<spec-id>-<seq>` | `test-auto-aaas30040-001` |
| Plan file | `<SPEC-ID>-auto-integration-test-plan.md` | `AAAS-30040-auto-integration-test-plan.md` |

**Test data ID rules:**
- Lowercase, hyphen-separated
- Always starts with `test-auto-` to distinguish from real data
- Spec ID without hyphens is fine (e.g. `aaas30040`)
- Sequence is zero-padded to 3 digits

---

## JUnit scope separation

Unit tests and integration tests appear as separate suites in Jenkins because:
- They run in different stages (`Unit Tests` vs `Integration Tests`)
- They produce different XML files (`results.xml` vs `integration-test-results.xml`)
- The package path prefix is automatic: `integration_tests.<file>.Test*`

No special class name prefix is needed. The agent only needs to ensure:
1. Files live under `application/integration_tests/`
2. The class is named `Test<ServiceName>`

---

## poll helper signature

```python
wait_for(predicate, timeout=30, interval=2, description="condition") -> any
```

- `predicate`: `callable() -> truthy | falsy` -- called every `interval` seconds
- Returns the truthy value returned by `predicate`
- Raises `AssertionError` if `timeout` seconds elapse without a truthy result
- Always pass `description` for readable CI output

For absence assertions, use a fixed wait + direct check instead of `wait_for`.

---

## Cleanup guidance

Every TC that creates an AWS resource must register a cleanup entry:

```python
cleanup_keys.append((
    lambda k: ddb_client.delete_item(TableName=table, Key=k),
    {"pk": {"S": pk}, "sk": {"S": sk}},
))
```

- Register at the `yield` point of the test -- i.e., before the trigger, not after assertions
- `cleanup_keys` is a function fixture -- resets between tests
- Teardown swallows exceptions; real test failures are reported separately
- TCs that assert absence do not register cleanup

---

## TC card template

Copy this template for each TC in the plan file:

```markdown
### TC-NN: <Short Description>

| Field | Value |
|---|---|
| Spec requirement | REQ-N |
| Manual QA scenario | "<scenario description from test plan>" |
| Input trigger | SNS publish / SQS send / HTTP POST / DDB put_item / StepFunction start / Lambda invoke |
| Input payload | `entityType: USER, eventType: ADD_USER_DETAIL, data.userId: test-auto-aaas30040-NN` (SSOT ref: `asyncapi/...`) |
| Expected output | DDB item at `USER#test-auto-aaas30040-NN / SAML` with `status=ACTIVE` |
| Assertion type | DDB poll / SQS receive / HTTP response / StepFunction poll / CloudWatch log |
| Poll timeout | 30 s |
| Cleanup | Delete DDB item `USER#test-auto-aaas30040-NN / SAML` from `CACHE_TABLE_NAME` |
| pytest name | `test_tcNN_<short_description>` |
| JUnit classname | `integration_tests.<service_name>_integration_test.Test<ServiceName>` |
```

---

## Integration test file skeleton

```python
"""
Integration tests for <ServiceName>.

Exercises the service from its AWS input boundary to its observable output.
Runs after deployment in dev. Requires env vars: AWS_REGION, ENVIRONMENT,
ACCOUNT_GROUP, <SERVICE_SPECIFIC_VARS>.
"""
import json
import os
import pytest
from conftest import wait_for


class Test<ServiceName>:

    def test_tc01_<short_description>(self, aws_auth, cleanup_keys):
        # Arrange
        ddb_client = aws_auth("dynamodb")
        sns_client = aws_auth("sns")
        table_name = os.environ["CACHE_TABLE_NAME"]
        topic_arn = os.environ["USER_CMD_TOPIC_ARN"]
        user_id = "test-auto-aaas30040-001"
        pk = f"USER#{user_id}"
        sk = "SAML"

        cleanup_keys.append((
            lambda k: ddb_client.delete_item(TableName=table_name, Key=k),
            {"pk": {"S": pk}, "sk": {"S": sk}},
        ))

        # Act
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps({
                "entityType": "USER",
                "eventType": "ADD_USER_DETAIL",
                "resourceTypes": ["SAML"],
                "data": {"userId": user_id},
            }),
            MessageAttributes={
                "entityType":    {"DataType": "String", "StringValue": "USER"},
                "eventType":     {"DataType": "String", "StringValue": "ADD_USER_DETAIL"},
                "resourceTypes": {"DataType": "String", "StringValue": "SAML"},
            },
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        # Assert
        def get_item():
            r = ddb_client.get_item(
                TableName=table_name,
                Key={"pk": {"S": pk}, "sk": {"S": sk}},
            )
            return r.get("Item")

        item = wait_for(get_item, timeout=30, description=f"DDB item {pk}/{sk}")
        assert item["status"]["S"] == "ACTIVE"
```
