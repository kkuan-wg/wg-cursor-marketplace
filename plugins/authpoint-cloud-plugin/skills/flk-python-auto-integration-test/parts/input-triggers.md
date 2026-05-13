# Input Triggers

Deployment-agnostic patterns for sending data into a service under test. Choose the trigger that matches the service's public input boundary.

All clients are obtained from the `aws_auth` session fixture in `conftest.py`:
```python
sns_client = aws_auth("sns")
sqs_client = aws_auth("sqs")
ddb_client = aws_auth("dynamodb")
sfn_client = aws_auth("stepfunctions")
lambda_client = aws_auth("lambda")
```

---

## SNS publish (SQS consumer, ECS worker triggered by SNS)

Use when the service subscribes to an SNS topic (directly or via SQS).

```python
import json
import os

topic_arn = os.environ["USER_CMD_TOPIC_ARN"]  # env var from configuration.py

response = sns_client.publish(
    TopicArn=topic_arn,
    Message=json.dumps({
        "entityType": "USER",
        "eventType": "ADD_USER_DETAIL",
        "resourceTypes": ["SAML"],
        "data": {
            "userId": "test-auto-aaas30040-001",
            "email": "test-auto-aaas30040-001@test.invalid",
        },
    }),
    MessageAttributes={
        "resourceTypes": {"DataType": "String", "StringValue": "SAML"},
        "entityType":    {"DataType": "String", "StringValue": "USER"},
        "eventType":     {"DataType": "String", "StringValue": "ADD_USER_DETAIL"},
    },
)
assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
```

**Notes:**
- For FIFO topics, add `MessageGroupId` and `MessageDeduplicationId`.
- SNS `MessageAttributes` must match the filter policies on the subscription.
- The `Message` body should be the minimum set of fields needed to exercise the scenario; reference the SSOT AsyncAPI path in the TC card for the full schema.

---

## SQS send (direct SQS consumer, no SNS wrapper)

Use when the service reads directly from an SQS queue without SNS wrapping.

```python
import json
import os

queue_url = os.environ["QUEUE_URL"]

response = sqs_client.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps({
        "entityType": "USER",
        "data": {"userId": "test-auto-aaas30040-001"},
    }),
)
assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
```

---

## HTTP / REST call (API Gateway, ALB, ECS service endpoint)

Use when the service exposes an HTTP endpoint.

```python
import os
import requests

base_url = os.environ["API_BASE_URL"]

response = requests.get(
    f"{base_url}/resources/test-auto-aaas30040-001",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)
```

For POST/PUT with a body:
```python
response = requests.post(
    f"{base_url}/resources",
    json={"id": "test-auto-aaas30040-001", "name": "test"},
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    timeout=10,
)
```

**Notes:**
- Assert HTTP status inline (no polling needed -- HTTP is synchronous).
- Do not follow redirects blindly; set `allow_redirects=False` when testing redirect behavior.

---

## DynamoDB put_item (DDB stream listener)

Use when the service reacts to a DynamoDB Streams event. Write an item to the source table to trigger the stream.

```python
import os

source_table = os.environ["SOURCE_TABLE_NAME"]

ddb_client.put_item(
    TableName=source_table,
    Item={
        "pk":     {"S": f"USER#test-auto-aaas30040-001"},
        "sk":     {"S": "PROFILE"},
        "email":  {"S": "test-auto-aaas30040-001@test.invalid"},
        "status": {"S": "ACTIVE"},
    },
)
```

**Notes:**
- Register the source table item in `cleanup_keys` so it is deleted in teardown.
- The stream event is asynchronous -- always use `wait_for` to poll the side-effect output.
- DDB stream events are delivered with a small delay (typically < 5 s in dev, poll up to 30 s).

---

## Step Function start_execution (state machine)

Use when the service is an AWS Step Functions state machine.

```python
import json
import os

state_machine_arn = os.environ["STATE_MACHINE_ARN"]

response = sfn_client.start_execution(
    stateMachineArn=state_machine_arn,
    input=json.dumps({
        "userId": "test-auto-aaas30040-001",
        "action": "PROVISION",
    }),
)
execution_arn = response["executionArn"]
assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
```

Use the `execution_arn` in the output assertion (see `output-assertions.md` Step Function poll pattern).

---

## Direct Lambda invoke (synchronous Lambda call)

Use when the service is a Lambda that is called synchronously (e.g. an internal API Lambda invoked via `lambda:InvokeFunction`).

```python
import json
import os
import base64

function_name = os.environ["LAMBDA_FUNCTION_NAME"]

response = lambda_client.invoke(
    FunctionName=function_name,
    InvocationType="RequestResponse",
    Payload=json.dumps({
        "httpMethod": "GET",
        "path": f"/resources/test-auto-aaas30040-001",
        "headers": {},
        "body": None,
    }),
)
payload = json.loads(response["Payload"].read())
```

**Notes:**
- `InvocationType="Event"` for fire-and-forget (async); use `wait_for` to poll output.
- `InvocationType="RequestResponse"` for synchronous -- assert the response payload inline.
