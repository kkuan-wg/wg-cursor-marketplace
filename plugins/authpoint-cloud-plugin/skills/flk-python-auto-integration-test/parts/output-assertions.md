# Output Assertions

Deployment-agnostic patterns for reading and asserting the observable output of a service under test. Choose the assertion that matches the service's observable output boundary.

All clients are obtained from the `aws_auth` session fixture in `conftest.py`.

Always use the `wait_for` helper from `conftest.py` for asynchronous assertions -- never `time.sleep`.

---

## DynamoDB poll (item created / updated / deleted)

Use when the service writes to a DynamoDB table and the expected output is an item or attribute value.

```python
import os

def get_ddb_item(ddb_client, table_name, pk_value, sk_value=None):
    """Returns the Item dict if found, None otherwise."""
    key = {"pk": {"S": pk_value}}
    if sk_value:
        key["sk"] = {"S": sk_value}
    response = ddb_client.get_item(TableName=table_name, Key=key)
    return response.get("Item")


# In the test method:
table_name = os.environ["CACHE_TABLE_NAME"]
pk = f"USER#test-auto-aaas30040-001"
sk = "SAML"

item = wait_for(
    lambda: get_ddb_item(ddb_client, table_name, pk, sk),
    timeout=30,
    description=f"DDB item {pk}/{sk} to appear in {table_name}",
)
assert item["status"]["S"] == "ACTIVE"
assert item["email"]["S"] == "test-auto-aaas30040-001@test.invalid"
```

**For deletion assertions** (item must disappear):
```python
# Fixed wait then direct check -- do NOT use wait_for with negated predicate
import time
time.sleep(15)
response = ddb_client.get_item(TableName=table_name, Key={"pk": {"S": pk}})
assert "Item" not in response, f"Expected item {pk} to be deleted but it still exists"
```

**Cleanup registration** (register at yield point so teardown always fires):
```python
pk_key = {"pk": {"S": pk}, "sk": {"S": sk}}
cleanup_keys.append((
    lambda k: ddb_client.delete_item(TableName=table_name, Key=k),
    pk_key,
))
```

---

## SQS receive (from a subscribed test queue or DLQ)

Use when the service publishes to an SNS topic and you subscribe a dedicated test SQS queue, or when asserting DLQ behavior.

```python
import json
import os

test_queue_url = os.environ["TEST_OUTPUT_QUEUE_URL"]  # dedicated test queue subscribed to output topic


def receive_matching_message(sqs_client, queue_url, match_fn):
    """Poll the queue and return the first message body matching match_fn, or None."""
    resp = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=2,
    )
    for msg in resp.get("Messages", []):
        body = json.loads(msg["Body"])
        # SNS wraps the payload in an outer envelope; unwrap if needed
        inner = json.loads(body.get("Message", "{}")) if "Message" in body else body
        if match_fn(inner):
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )
            return inner
    return None


# In the test method:
message = wait_for(
    lambda: receive_matching_message(
        sqs_client,
        test_queue_url,
        lambda m: m.get("userId") == "test-auto-aaas30040-001",
    ),
    timeout=30,
    description="output message for test-auto-aaas30040-001 to appear in test queue",
)
assert message["status"] == "ACTIVE"
```

**Notes:**
- The test SQS queue must be pre-provisioned and subscribed to the output topic. Reference its URL via env var.
- Always delete consumed messages so they do not interfere with subsequent test runs.
- Long polling (`WaitTimeSeconds=2`) reduces empty receives and API calls.

---

## HTTP response assertion (synchronous API)

Use when the service returns a synchronous HTTP response. Assert directly -- no polling needed.

```python
import requests
import os

base_url = os.environ["API_BASE_URL"]
response = requests.get(
    f"{base_url}/resources/test-auto-aaas30040-001",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)

assert response.status_code == 200
body = response.json()
assert body["userId"] == "test-auto-aaas30040-001"
assert body["status"] == "ACTIVE"
```

For absence / 404 assertions:
```python
response = requests.get(f"{base_url}/resources/test-auto-aaas30040-999", timeout=10)
assert response.status_code == 404
```

---

## Step Function execution poll (state machine terminal state)

Use when the service is a Step Functions state machine and you need to assert the final execution status or output.

```python
import json

def get_execution_status(sfn_client, execution_arn):
    """Returns the execution dict if in a terminal state, None otherwise."""
    resp = sfn_client.describe_execution(executionArn=execution_arn)
    if resp["status"] in ("SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"):
        return resp
    return None


# In the test method (execution_arn from start_execution call):
execution = wait_for(
    lambda: get_execution_status(sfn_client, execution_arn),
    timeout=60,
    description=f"Step Function execution {execution_arn} to reach terminal state",
)
assert execution["status"] == "SUCCEEDED"
output = json.loads(execution.get("output", "{}"))
assert output.get("result") == "OK"
```

**Notes:**
- Use a longer timeout (60-120 s) for state machines; they have higher latency than Lambda.
- For `FAILED` executions, `execution["cause"]` contains the error detail.

---

## CloudWatch log scan (Lambda or ECS log group)

Use only as a last resort when no structured output boundary is observable (e.g. asserting that an error was logged, or that a specific processing step was reached). Prefer DDB/SQS/HTTP assertions over log scanning.

```python
import os
import time

log_group = os.environ["LOG_GROUP_NAME"]


def find_log_event(logs_client, log_group, filter_pattern, start_time_ms):
    """Returns the first matching log event or None."""
    resp = logs_client.filter_log_events(
        logGroupName=log_group,
        filterPattern=filter_pattern,
        startTime=start_time_ms,
        limit=10,
    )
    events = resp.get("events", [])
    return events[0] if events else None


# In the test method:
start_ms = int(time.time() * 1000)

# ... trigger the service here ...

logs_client = aws_auth("logs")
event = wait_for(
    lambda: find_log_event(logs_client, log_group, '"test-auto-aaas30040-001"', start_ms),
    timeout=30,
    description="log event containing test-auto-aaas30040-001",
)
assert event is not None
```

**Notes:**
- Always capture `start_ms` BEFORE triggering the service to avoid matching pre-existing log events.
- CloudWatch Logs Insights has higher latency than filter_log_events; use `filter_log_events` for polling.
- Log group names come from env vars; never hardcode them.
