---
name: flk-sam-ops-ddb-listener
description: Creates and updates SAM template resources for Folklore DynamoDB stream listener Lambda functions (AWS::Serverless::Function, DDB stream event, FilterCriteria, SNS publish policy, optional SQS fallback policy, LogGroup). Use when writing or reviewing SAM templates for DDB stream listener Lambdas, or when the user mentions template.yaml, SAM, infrastructure, deploy, CloudFormation, or infra for a DDB stream listener. Does NOT cover Python application code — use flk-python-lambda-ddb-listener for that.
---

# Folklore SAM Ops — DDB Stream Listener

Creates and updates the SAM/CloudFormation infrastructure for Folklore DynamoDB stream listener Lambda functions. Covers `template.yaml` resources only — no Python application code.

`flk-ops-template` is always loaded alongside this skill — all general SAM conventions, tagging rules, encryption requirements, IAM least-privilege patterns, and the general checklist defined there apply here without repetition.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

**If a spec path was provided**, read the following files:
- `spec.md` — extract: env var names, DynamoDB table/stream names, SNS topic names, FilterCriteria fields, whether SQS fallback is needed
- `proposal.md` — extract: the exact infra artifacts to create and scope boundaries (same folder as `spec.md`)
- `infra-tasks.md` — extract: infra tasks under **Implementation** (same folder as `spec.md`)

From these extract: function name, env vars, table/stream/topic names, FilterCriteria events, whether SQS fallback producer exists in the code.

**If no spec was provided**, extract from the user's direct input.

### 2. Browse the codebase

**All browsing is scoped to the current workspace.**

Locate the nearest sibling DDB stream listener's `template.yaml` **within the workspace**. Extract:
- `FunctionName` naming convention
- Whether SAM policy templates (`DynamoDBReadPolicy`) or explicit `Version: 2012-10-17` statements are used — match the pattern already in the target template
- The `template.yaml` file path where the new resources should be added

### 3. Load flk-ops-template parts progressively

| Need | Part to read |
|------|-------------|
| Lambda resource definition | `parts/lambda.md` |
| SNS topic | `parts/sns.md` |
| Globals, tags | `parts/globals.md` |
| Template validation | `parts/template-validation.md` |
| Jenkinsfile `lambdaNames` | `parts/jenkinsfile.md` |

Read only parts relevant to the resources being added.

### 4. Ask only what you cannot find

One targeted question per gap. Never ask about things discoverable from the spec or existing templates.

---

## Phase 2: Write the Resources

### Function + LogGroup

```yaml
Flk{Feature}ListenerFn:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: {function_name}_fn
    FunctionName: !Ref Flk{Feature}ListenerFnName
    MemorySize: 256
    Timeout: 3
    ReservedConcurrentExecutions: !FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]
    Environment:
      Variables:
        {TABLE}_TABLE_NAME: !Ref Flk{Feature}TableName
        MAIN_REGION: !Ref MainRegion
        # SNS topic ARN — use !Sub when constructed from topic name + region + account
        DATA_TOPIC_ARN: !Sub 'arn:aws:sns:${MainRegion}:${AWS::AccountId}:${FlkDataTopicName}'
        # SQS fallback env var — include only when a fallback queue exists
        EVENT_REPLAY_QUEUE_URL: !Ref FlkEventReplayQueueUrl
    Events:
      Stream:
        Type: DynamoDB
        Properties:
          Stream: !Ref Flk{Feature}StreamArn
          BatchSize: 1
          MaximumBatchingWindowInSeconds: 1
          MaximumRetryAttempts: 3
          StartingPosition: LATEST
          FilterCriteria:
            Filters:
              - Pattern: "{\"eventName\":[\"INSERT\",\"MODIFY\"]}"
    Tags:
      Name: !Ref Flk{Feature}ListenerFnName
    Policies:
      - DynamoDBReadPolicy:
          TableName: !Ref Flk{Feature}TableName
      - Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - sns:Publish
            Resource: !Sub 'arn:aws:sns:${MainRegion}:${AWS::AccountId}:${FlkDataTopicName}'
      # SQS fallback policy — include only when needed
      - SQSSendMessagePolicy:
          QueueName: !Ref FlkEventReplayQueueName

Flk{Feature}ListenerFnLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub '/aws/lambda/${Flk{Feature}ListenerFn}'
    RetentionInDays: 14
```

#### FilterCriteria syntax

| Pattern | Syntax |
|---------|--------|
| Single event type | `"{\"eventName\":[\"INSERT\"]}"` |
| Multiple event types | `"{\"eventName\":[\"INSERT\",\"MODIFY\"]}"` |
| String field match | `"{\"eventName\":[\"INSERT\",\"MODIFY\"],\"dynamodb\":{\"NewImage\":{\"field\":{\"S\":[\"value\"]}}}}"` |
| Number field match | `"{\"dynamodb\":{\"NewImage\":{\"count\":{\"N\":[\"42\"]}}}}"` |

Multiple `Filters` entries are OR-evaluated — any matching filter triggers the Lambda.

### Step 3 — Jenkinsfile `lambdaNames`

Add the resolved function name to `lambdaNames` in `infra/Jenkinsfile`. See `flk-ops-template parts/jenkinsfile.md` for the exact format.

---

## Phase 3: Verify Before Finishing

The `flk-ops-template` general checklist applies in full. Additionally verify:

- [ ] `CodeUri` matches the actual `{function_name}_fn` folder in the workspace (no `./` prefix)
- [ ] `FunctionName` uses `!Ref` to a Parameter — never hardcoded
- [ ] `ReservedConcurrentExecutions` uses `!FindInMap [ReservedConcurrentExecutions, ...]`
- [ ] `MaximumRetryAttempts: 3`, `StartingPosition: LATEST`, `BatchSize: 1`, `MaximumBatchingWindowInSeconds: 1` on DDB stream event
- [ ] `FilterCriteria` Pattern is a valid JSON-escaped string
- [ ] SNS topic ARN uses `!Sub` with `MainRegion` (not `AWS::Region`)
- [ ] SQS fallback env var and policy included only when the listener code uses a producer
- [ ] `AWS::Logs::LogGroup` with `RetentionInDays: 14` for every function
- [ ] Function name added to `lambdaNames` in `Jenkinsfile`
- [ ] All WG 2.1.0 tags present (see `flk-ops-template parts/globals.md`)

## Reference

- SAM template patterns, SNS, tags, encryption, Jenkinsfile → `flk-ops-template` skill parts
- Full DDB stream listener template example, FilterCriteria patterns, IAM policy patterns → [references/REFERENCE.md](references/REFERENCE.md)
- Lambda code (configuration, ports, adapters, service, app.py) → `flk-python-lambda-ddb-listener` skill
