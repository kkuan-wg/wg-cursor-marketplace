---
name: flk-sam-ops-sqs-consumer
description: Creates and updates SAM template resources for Folklore SQS consumer Lambda functions (AWS::Serverless::Function, SQS queue + DLQ + policy + SNS subscription, IAM policies, LogGroup). Use when writing or reviewing SAM templates for SQS consumer Lambdas, or when the user mentions template.yaml, SAM, infrastructure, deploy, CloudFormation, or infra for an SQS consumer. Does NOT cover Python application code — use flk-python-lambda-sqs-consumer for that.
---

# Folklore SAM Ops — SQS Consumer

Creates and updates the SAM/CloudFormation infrastructure for Folklore SQS consumer Lambda functions. Covers `template.yaml` resources only — no Python application code.

`flk-ops-template` is always loaded alongside this skill — all general SAM conventions, tagging rules, encryption requirements, IAM least-privilege patterns, and the general checklist defined there apply here without repetition.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

**If a spec path was provided**, read the following files:
- `spec.md` — extract: env var names, DynamoDB table names, SQS queue names, SNS topic names, resource type filter values
- `proposal.md` — extract: the exact infra artifacts to create and scope boundaries (same folder as `spec.md`)
- `infra-tasks.md` — extract: infra tasks under **Implementation** (same folder as `spec.md`)

From these extract: function name, env vars, queue/topic/table names, resource type filter value.

**If no spec was provided**, extract from the user's direct input.

### 2. Browse the codebase

**All browsing is scoped to the current workspace.**

Locate the nearest sibling SQS consumer's `template.yaml` **within the workspace**. Extract:
- `FunctionName` naming convention
- Whether SAM policy templates (`DynamoDBCrudPolicy`) or explicit `Version: 2012-10-17` statements are used — match the pattern already in the target template
- The `template.yaml` file path where the new resources should be added

### 3. Load flk-ops-template parts progressively

| Need | Part to read |
|------|-------------|
| Lambda resource definition | `parts/lambda.md` |
| SQS queue + DLQ + subscription | `parts/sqs.md` |
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
Flk{Feature}Fn:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: {function_name}_fn
    FunctionName: !Ref Flk{Feature}FnName
    MemorySize: 256
    Timeout: 3
    ReservedConcurrentExecutions: !FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]
    Environment:
      Variables:
        {TABLE}_TABLE_NAME: !Ref Flk{Table}
    Events:
      {Feature}SQSEvent:
        Type: SQS
        Properties:
          Queue: !GetAtt Flk{Feature}Queue.Arn
          BatchSize: 1
    Tags:
      Name: !Ref Flk{Feature}FnName
    Policies:
      - DynamoDBCrudPolicy:
          TableName: !Ref Flk{Table}

Flk{Feature}FnLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub '/aws/lambda/${Flk{Feature}Fn}'
    RetentionInDays: 14
```

### SQS queue + DLQ + queue policy + SNS subscription

```yaml
Flk{Feature}DlQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Ref Flk{Feature}DLQName
    FifoQueue: true
    ContentBasedDeduplication: true
    SqsManagedSseEnabled: true
    MessageRetentionPeriod: 1209600
    Tags:
      - Key: Name
        Value: !Ref Flk{Feature}DLQName
      - Key: flk:alarm:sqs:dlq
        Value: 'true'
      # ... remaining WG 2.1.0 tags

Flk{Feature}Queue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Ref Flk{Feature}QueueName
    FifoQueue: true
    ContentBasedDeduplication: true
    SqsManagedSseEnabled: true
    VisibilityTimeout: 18        # 6 × Lambda Timeout (3 s)
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt Flk{Feature}DlQueue.Arn
      maxReceiveCount: 5
    Tags:
      - Key: Name
        Value: !Ref Flk{Feature}QueueName
      - Key: flk:alarm:sqs:ageOfMessage
        Value: '400'
      # ... remaining WG 2.1.0 tags

Flk{Feature}QueuePolicy:
  Type: AWS::SQS::QueuePolicy
  Properties:
    Queues:
      - !Ref Flk{Feature}Queue
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        Effect: Allow
        Principal: '*'
        Action:
          - SQS:SendMessage
        Resource: !GetAtt Flk{Feature}Queue.Arn
        Condition:
          ArnEquals:
            aws:SourceArn: !Ref Flk{Domain}CmdTopicArn

Flk{Feature}SNSSubscription:
  Type: AWS::SNS::Subscription
  Properties:
    Endpoint: !GetAtt Flk{Feature}Queue.Arn
    Protocol: sqs
    TopicArn: !Ref Flk{Domain}CmdTopicArn
    FilterPolicy:
      resourceTypes:
        - {RESOURCE_TYPE}       # e.g. SAML, OIDC
```

**`VisibilityTimeout` rule:** `6 × Lambda Timeout`. For a 3 s timeout → 18 s. For a 10 s timeout → 60 s.

### Step 3 — Jenkinsfile `lambdaNames`

Add the resolved function name to `lambdaNames` in `infra/Jenkinsfile`. See `flk-ops-template parts/jenkinsfile.md` for the exact format.

---

## Phase 3: Verify Before Finishing

The `flk-ops-template` general checklist applies in full. Additionally verify:

- [ ] `CodeUri` matches the actual `{function_name}_fn` folder in the workspace (no `./` prefix)
- [ ] `FunctionName` uses `!Ref` to a Parameter — never hardcoded
- [ ] `ReservedConcurrentExecutions` uses `!FindInMap [ReservedConcurrentExecutions, ...]`
- [ ] `VisibilityTimeout` = 6 × Lambda `Timeout`
- [ ] `maxReceiveCount: 5` and `MessageRetentionPeriod: 1209600` on DLQ
- [ ] `BatchSize: 1` on SQS event
- [ ] `FifoQueue: true` + `ContentBasedDeduplication: true` + `SqsManagedSseEnabled: true` on both queue and DLQ
- [ ] `FilterPolicy` on SNS subscription filters by `resourceTypes`
- [ ] `AWS::Logs::LogGroup` with `RetentionInDays: 14` for every function
- [ ] Function name added to `lambdaNames` in `Jenkinsfile`
- [ ] All WG 2.1.0 tags present (see `flk-ops-template parts/globals.md`)

## Reference

- SAM template patterns, SQS, SNS, tags, encryption, Jenkinsfile → `flk-ops-template` skill parts
- Full SQS consumer template example, IAM policy patterns → [references/REFERENCE.md](references/REFERENCE.md)
- Lambda code (configuration, ports, adapters, service, app.py) → `flk-python-lambda-sqs-consumer` skill
