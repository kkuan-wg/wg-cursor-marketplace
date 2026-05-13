# SAM Ops — SQS Consumer Reference

Detailed reference for SAM template patterns specific to Folklore SQS consumer Lambda functions. Read when writing or reviewing `template.yaml` resources.

General SAM conventions (Globals, tags, encryption, SQS, SNS, nested stacks, Jenkinsfile) are covered by `flk-ops-template` — this reference focuses on SQS consumer-specific patterns drawn from real templates.

---

## 1. Full Template Example

Drawn from `folklore-service/application/src/cache/user/template.yaml`.

```yaml
# --- Parameters (relevant subset) ---
Parameters:
  Flk{Feature}FnName:
    Type: String
  Flk{Feature}QueueName:
    Type: String
  Flk{Feature}DLQName:
    Type: String
  Flk{Domain}CmdTopicArn:
    Type: String
  {Table}TableName:
    Type: String
  AuthpointLambdaLayer:
    Type: String
  FolkloreDomainLambdaLayer:
    Type: String

# --- Resources ---

  Flk{Feature}DlQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Ref Flk{Feature}DLQName
      FifoQueue: true
      ContentBasedDeduplication: true
      SqsManagedSseEnabled: true
      MessageRetentionPeriod: 1209600
      Tags:
        - { Key: Name, Value: !Ref Flk{Feature}DLQName }
        - { Key: wg:info:taggingversion, Value: '2.0.0' }
        - { Key: wg:purpose:product, Value: authpoint }
        - { Key: wg:purpose:serviceid, Value: folklore-service }
        - { Key: wg:purpose:environment, Value: !Ref Environment }
        - { Key: wg:automation:expiry, Value: never }
        - { Key: wg:info:owner, Value: authpoint }
        - { Key: flk:alarm:sqs:dlq, Value: 'true' }

  Flk{Feature}Queue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Ref Flk{Feature}QueueName
      FifoQueue: true
      ContentBasedDeduplication: true
      SqsManagedSseEnabled: true
      VisibilityTimeout: 18       # 6 × Lambda Timeout (3 s)
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt Flk{Feature}DlQueue.Arn
        maxReceiveCount: 5
      Tags:
        - { Key: Name, Value: !Ref Flk{Feature}QueueName }
        - { Key: wg:info:taggingversion, Value: '2.0.0' }
        - { Key: wg:purpose:product, Value: authpoint }
        - { Key: wg:purpose:serviceid, Value: folklore-service }
        - { Key: wg:purpose:environment, Value: !Ref Environment }
        - { Key: wg:automation:expiry, Value: never }
        - { Key: wg:info:owner, Value: authpoint }
        - { Key: flk:alarm:sqs:ageOfMessage, Value: '400' }

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
          - {RESOURCE_TYPE}     # e.g. SAML, OIDC

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
          {TABLE}_TABLE_NAME: !Ref {Table}TableName
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
            TableName: !Ref {Table}TableName

  Flk{Feature}FnLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/lambda/${Flk{Feature}Fn}'
      RetentionInDays: 14
```

**Key rules:**
- `FifoQueue: true` + `ContentBasedDeduplication: true` — all user/resource command queues are FIFO
- `SqsManagedSseEnabled: true` on both queue and DLQ
- `VisibilityTimeout` = 6 × Lambda `Timeout`
- `BatchSize: 1` — process one message at a time
- `FilterPolicy` on the SNS subscription filters by `resourceTypes` — the Lambda only receives events for its domain

---

## 2. IAM Policy Patterns

Match whatever style is already in the target template.

**SAM policy templates (preferred when available):**

```yaml
- DynamoDBCrudPolicy:
    TableName: !Ref TableNameParam
- SQSPollerPolicy:
    QueueName: !GetAtt QueueName.QueueName
```

---

## 3. Architectural Decisions

| Decision | Rule |
|----------|------|
| `CodeUri` | Folder name only — no `./` prefix |
| `FunctionName` | Always `!Ref` to a Parameter |
| Concurrency | Always `!FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]` |
| `VisibilityTimeout` | `6 × Lambda Timeout` |
| FIFO queues | All user/resource command queues: `FifoQueue: true` + `ContentBasedDeduplication: true` |
| LogGroup | Every function needs `AWS::Logs::LogGroup` with `RetentionInDays: 14` |
