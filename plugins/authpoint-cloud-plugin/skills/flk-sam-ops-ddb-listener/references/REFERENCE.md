# SAM Ops — DDB Stream Listener Reference

Detailed reference for SAM template patterns specific to Folklore DynamoDB stream listener Lambda functions. Read when writing or reviewing `template.yaml` resources.

General SAM conventions (Globals, tags, encryption, SQS, SNS, nested stacks, Jenkinsfile) are covered by `flk-ops-template` — this reference focuses on DDB stream listener-specific patterns drawn from real templates.

---

## 1. Full Template Example

Drawn from `folklore-service/application/src/authn_context/template.yaml`.

```yaml
# --- Parameters (relevant subset) ---
Parameters:
  Flk{Feature}ListenerFnName:
    Type: String
  Flk{Feature}TableName:
    Type: String
  Flk{Feature}StreamArn:
    Type: String
  FlkDataTopicName:
    Type: String
  MainRegion:
    Type: String
  # SQS fallback (include only when needed)
  FlkEventReplayQueueName:
    Type: String
  FlkEventReplayQueueUrl:
    Type: String

# --- Resources ---

  Flk{Feature}ListenerFn:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Ref Flk{Feature}ListenerFnName
      CodeUri: {function_name}_fn
      MemorySize: 256
      Timeout: 3
      ReservedConcurrentExecutions: !FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]
      Environment:
        Variables:
          {TABLE}_TABLE_NAME: !Ref Flk{Feature}TableName
          MAIN_REGION: !Ref MainRegion
          DATA_TOPIC_ARN: !Sub 'arn:aws:sns:${MainRegion}:${AWS::AccountId}:${FlkDataTopicName}'
          # SQS fallback env var — include only when needed
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
                - Pattern: "{\"eventName\":[\"INSERT\"]}"
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

**Key rules:**
- `BatchSize: 1`, `MaximumBatchingWindowInSeconds: 1`, `MaximumRetryAttempts: 3`, `StartingPosition: LATEST` — always all four
- SNS topic ARN constructed with `!Sub` using `MainRegion` (not `AWS::Region`) — topic may be in a different region
- SQS fallback: only add `EVENT_REPLAY_QUEUE_URL` env var and `SQSSendMessagePolicy` when the code skill uses a producer

---

## 2. FilterCriteria Patterns

The `Pattern` value must be a JSON-escaped string:

| Goal | Pattern value |
|------|--------------|
| INSERT only | `"{\"eventName\":[\"INSERT\"]}"` |
| INSERT and MODIFY | `"{\"eventName\":[\"INSERT\",\"MODIFY\"]}"` |
| With string field filter | `"{\"eventName\":[\"INSERT\",\"MODIFY\"],\"dynamodb\":{\"NewImage\":{\"field\":{\"S\":[\"value\"]}}}}"` |
| With number field filter | `"{\"dynamodb\":{\"NewImage\":{\"count\":{\"N\":[\"42\"]}}}}"` |

Multiple `Filters` entries under `FilterCriteria.Filters` are OR-evaluated.

---

## 3. IAM Policy Patterns

Match whatever style is already in the target template.

**SAM policy template (DynamoDB read):**

```yaml
- DynamoDBReadPolicy:
    TableName: !Ref TableNameParam
```

**Explicit statement (required for SNS publish and cross-account):**

```yaml
- Version: 2012-10-17
  Statement:
    - Effect: Allow
      Action:
        - sns:Publish
      Resource: !Sub 'arn:aws:sns:${MainRegion}:${AWS::AccountId}:${TopicNameParam}'
```

**SQS fallback policy (include only when a fallback producer exists):**

```yaml
- SQSSendMessagePolicy:
    QueueName: !Ref FlkEventReplayQueueName
```

---

## 4. Architectural Decisions

| Decision | Rule |
|----------|------|
| `CodeUri` | Folder name only — no `./` prefix |
| `FunctionName` | Always `!Ref` to a Parameter |
| Concurrency | Always `!FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]` |
| SNS topic ARN | Use `!Sub` with `MainRegion` — never `AWS::Region` for cross-region topics |
| SQS fallback | Add env var + policy only when the listener code uses a producer |
| LogGroup | Every function needs `AWS::Logs::LogGroup` with `RetentionInDays: 14` |
| Log group logical name | Append `LogGroupSub` (stream listeners) or `LogGroup` (SQS consumers) — match sibling pattern |
