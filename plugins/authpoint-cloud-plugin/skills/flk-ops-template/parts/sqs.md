# SQS Queues

Every SQS queue must be paired with a Dead Letter Queue (DLQ). Both require SSE enabled.

---

## Standard queue pair (DLQ + main queue)

```yaml
FlkLogonAppTxDLQ:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Sub '${StackModifier}-flk-logon-app-tx-dlq'
    SqsManagedSseEnabled: true
    MessageRetentionPeriod: 1209600   # 14 days
    Tags:
      - Key: wg:info:taggingversion
        Value: 2.0.0
      - Key: wg:purpose:product
        Value: authpoint
      - Key: wg:purpose:serviceid
        Value: folklore-service-logon-app
      - Key: wg:purpose:environment
        Value: !Ref Environment
      - Key: wg:purpose:region
        Value: !Ref AWS::Region
      - Key: wg:automation:expiry
        Value: never
      - Key: wg:info:owner
        Value: authpoint
      - Key: flk:alarm:sqs:dlq
        Value: "true"

FlkLogonAppTxQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Sub '${StackModifier}-flk-logon-app-tx-queue'
    SqsManagedSseEnabled: true
    VisibilityTimeout: 18             # 6× Lambda timeout (3s × 6 = 18s)
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt FlkLogonAppTxDLQ.Arn
      maxReceiveCount: 5
    Tags:
      - Key: wg:info:taggingversion
        Value: 2.0.0
      # ... same WG tags as DLQ ...
      - Key: flk:alarm:sqs:ageOfMessage
        Value: "180"
```

---

## VisibilityTimeout

Pick the formula that matches how the queue is used:

| Pattern | Queue role | Formula | Example (Lambda timeout 3s) |
|---------|------------|---------|----------------------------|
| **Consumer** | Async worker; message may be retried until processing finishes | `6 × Lambda TimeoutSeconds` | `18` |
| **Validator** | Short synchronous-style handling; adjust per team convention | `ceil(Lambda TimeoutSeconds × 1.3)` (minimum 1) | `4` |

**Default Folklore consumer** (timeout 3s): `VisibilityTimeout: 18`.

**Long API Lambdas** (e.g. timeout 29s): consumer VT = `6 × 29` → **`174`**.

Document in YAML with a one-line comment which pattern applies so reviewers do not “fix” a validator queue to consumer VT by mistake.

---

## FIFO queue pair

Use FIFO when message ordering or exactly-once processing is required:

```yaml
FlkLogonAppTxFifoDLQ:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Sub '${StackModifier}-flk-logon-app-tx-fifo-dlq.fifo'
    FifoQueue: True
    SqsManagedSseEnabled: true
    MessageRetentionPeriod: 1209600
    Tags:
      - Key: flk:alarm:sqs:dlq
        Value: "true"

FlkLogonAppTxFifoQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Sub '${StackModifier}-flk-logon-app-tx-fifo-queue.fifo'
    FifoQueue: True
    ContentBasedDeduplication: True
    SqsManagedSseEnabled: true
    VisibilityTimeout: 18
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt FlkLogonAppTxFifoDLQ.Arn
      maxReceiveCount: 5
```

> FIFO queue names must end with `.fifo`.

---

## Delayed queue (optional)

For use cases requiring delayed processing (e.g. retry after a timeout):

```yaml
FlkLogonAppTxDelayedQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Sub '${StackModifier}-flk-logon-app-tx-delayed-queue'
    SqsManagedSseEnabled: true
    DelaySeconds: 900               # 15 minutes
    VisibilityTimeout: 18
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt FlkLogonAppTxDLQ.Arn
      maxReceiveCount: 5
```

---

## SQS Queue Policy (allow SNS to send)

Required when an SNS topic from another account or stack needs to send to this queue:

```yaml
FlkLogonAppTxQueuePolicy:
  Type: AWS::SQS::QueuePolicy
  Properties:
    Queues:
      - !Ref FlkLogonAppTxQueue
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Service: sns.amazonaws.com
          Action: sqs:SendMessage
          Resource: !GetAtt FlkLogonAppTxQueue.Arn
          Condition:
            ArnEquals:
              aws:SourceArn: !Ref FlkLogonAppTxTopicArn   # Parameter from root template
```

---

## SNS Subscription

Subscribe the SQS queue to an SNS topic with a filter policy:

```yaml
FlkLogonAppTxSubscription:
  Type: AWS::SNS::Subscription
  Properties:
    TopicArn: !Ref FlkLogonAppTxTopicArn
    Protocol: sqs
    Endpoint: !GetAtt FlkLogonAppTxQueue.Arn
    FilterPolicy:
      event_type:
        - "LOGON_APP_TX_CREATED"
        - "LOGON_APP_TX_UPDATED"
```

---

## Outputs

Export queue ARNs and URLs for cross-stack use:

```yaml
Outputs:
  FlkLogonAppTxQueueArn:
    Value: !GetAtt FlkLogonAppTxQueue.Arn
    Export:
      Name: !Sub '${StackModifier}-flk-logon-app-tx-queue-arn'

  FlkLogonAppTxQueueUrl:
    Value: !Ref FlkLogonAppTxQueue
    Export:
      Name: !Sub '${StackModifier}-flk-logon-app-tx-queue-url'
```

---

## Checklist

- [ ] Every queue has a paired DLQ
- [ ] `SqsManagedSseEnabled: true` on all queues (including DLQs)
- [ ] `VisibilityTimeout` matches **consumer** (`6×` Lambda timeout) or **validator** (`~timeout×1.3`) as documented for that queue
- [ ] `maxReceiveCount: 5` in `RedrivePolicy`
- [ ] `MessageRetentionPeriod: 1209600` (14 days) on DLQs
- [ ] `flk:alarm:sqs:dlq: "true"` tag on DLQ
- [ ] `flk:alarm:sqs:ageOfMessage` tag on main queue
- [ ] `AWS::SQS::QueuePolicy` added when SNS cross-account/cross-stack sends to queue
- [ ] FIFO queue names end with `.fifo`
