# Lambda Functions

---

## Full function example (SQS consumer)

```yaml
FlkLogonAppTxConsumerFn:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: !Sub '${StackModifier}-flk-logon-app-tx-consumer'
    CodeUri: flk_logon_app_tx_consumer/
    Description: Processes logon app transaction events from SQS
    ReservedConcurrentExecutions: !FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]
    Policies:
      - DynamoDBCrudPolicy:
          TableName: !Ref FlkLogonAppTxTable
      - SQSSendMessagePolicy:
          QueueName: !GetAtt FlkLogonAppTxDLQ.QueueName
      - SNSPublishMessagePolicy:
          TopicName: !GetAtt FlkLogonAppTxTopic.TopicName
    Events:
      SQSTrigger:
        Type: SQS
        Properties:
          Queue: !GetAtt FlkLogonAppTxQueue.Arn
          BatchSize: 1
          FunctionResponseTypes:
            - ReportBatchItemFailures
    Tags:
      flk:alarm:lambda:concurrentExec: !FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]
```

---

## Full function example (DDB stream listener)

```yaml
FlkLogonAppTxListenerFn:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: !Sub '${StackModifier}-flk-logon-app-tx-listener'
    CodeUri: flk_logon_app_tx_listener/
    Description: Listens to DynamoDB stream and publishes events to SNS
    ReservedConcurrentExecutions: !FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]
    Policies:
      - DynamoDBReadPolicy:
          TableName: !Ref FlkLogonAppTxTable
      - SNSPublishMessagePolicy:
          TopicName: !GetAtt FlkLogonAppTxTopic.TopicName
    Events:
      DDBStreamTrigger:
        Type: DynamoDB
        Properties:
          Stream: !GetAtt FlkLogonAppTxTable.StreamArn
          StartingPosition: TRIM_HORIZON
          BisectBatchOnFunctionError: true
          MaximumRetryAttempts: 3
          FilterCriteria:
            Filters:
              - Pattern: '{"eventName": ["INSERT", "MODIFY"]}'
```

---

## LogGroup

Every Lambda function must have an explicit `AWS::Logs::LogGroup` resource:

```yaml
FlkLogonAppTxConsumerFnLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub '/aws/lambda/${StackModifier}-flk-logon-app-tx-consumer'
    RetentionInDays: 14
    Tags:
      - Key: wg:purpose:serviceid
        Value: folklore-service-logon-app
      - Key: wg:purpose:environment
        Value: !Ref Environment
```

> `RetentionInDays: 14` is mandatory. Never leave log groups without retention.

---

## ReservedConcurrentExecutions

Always use `!FindInMap` — never hardcode a number:

```yaml
ReservedConcurrentExecutions: !FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]
```

The mapping must be defined in the same template (see [globals.md](globals.md) for the full `Mappings` block).

---

## IAM Policy patterns

### SAM managed policies (prefer these)

```yaml
Policies:
  - DynamoDBCrudPolicy:
      TableName: !Ref MyTable
  - DynamoDBReadPolicy:
      TableName: !Ref MyTable
  - SQSSendMessagePolicy:
      QueueName: !GetAtt MyQueue.QueueName
  - SNSPublishMessagePolicy:
      TopicName: !GetAtt MyTopic.TopicName
```

### Custom inline policy — DynamoDB GSI query

```yaml
- Statement:
    - Effect: Allow
      Action:
        - dynamodb:Query
      Resource:
        - !Sub 'arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${FlkLogonAppTxTable}/index/*'
```

### Custom inline policy — Lambda invoke

```yaml
- Statement:
    - Effect: Allow
      Action:
        - lambda:InvokeFunction
      Resource:
        - !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${StackModifier}-target-function'
```

### Custom inline policy — KMS (for SNS/SQS with CMK)

```yaml
- Statement:
    - Effect: Allow
      Action:
        - kms:GenerateDataKey
        - kms:Decrypt
      Resource:
        - !Sub 'arn:aws:kms:${AWS::Region}:${AWS::AccountId}:key/*'
```

### Custom inline policy — STS AssumeRole (cross-account)

```yaml
- Statement:
    - Effect: Allow
      Action:
        - sts:AssumeRole
      Resource:
        - !Sub 'arn:aws:iam::${TargetAccountId}:role/${StackModifier}-cross-account-role'
```

---

## Event triggers

### SQS trigger

```yaml
Events:
  SQSTrigger:
    Type: SQS
    Properties:
      Queue: !GetAtt FlkLogonAppTxQueue.Arn
      BatchSize: 1
      FunctionResponseTypes:
        - ReportBatchItemFailures
```

### DynamoDB stream trigger with filter

```yaml
Events:
  DDBStreamTrigger:
    Type: DynamoDB
    Properties:
      Stream: !GetAtt FlkLogonAppTxTable.StreamArn
      StartingPosition: TRIM_HORIZON
      BisectBatchOnFunctionError: true
      MaximumRetryAttempts: 3
      FilterCriteria:
        Filters:
          - Pattern: '{"eventName": ["INSERT", "MODIFY"]}'
```

### API Gateway trigger

```yaml
Events:
  ApiTrigger:
    Type: Api
    Properties:
      RestApiId: !Ref LogonAppAuthAPI
      Path: /config
      Method: GET
```

See [api-gateway.md](api-gateway.md) for the full API resource definition.

---

## Checklist

- [ ] `FunctionName` uses `!Sub '${StackModifier}-...'` pattern
- [ ] `ReservedConcurrentExecutions: !FindInMap [...]` on every function
- [ ] Explicit `AWS::Logs::LogGroup` with `RetentionInDays: 14`
- [ ] `flk:alarm:lambda:concurrentExec` tag on function (if not in Globals)
- [ ] IAM policies use SAM managed policies where available
- [ ] Custom inline policies use specific resource ARNs (no `*` resources)
- [ ] SQS trigger uses `BatchSize: 1` and `ReportBatchItemFailures`
- [ ] DDB stream trigger has `BisectBatchOnFunctionError: true` and `FilterCriteria`
