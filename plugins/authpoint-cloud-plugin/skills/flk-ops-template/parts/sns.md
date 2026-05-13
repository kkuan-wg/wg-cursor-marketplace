# SNS Topics

---

## Standard SNS topic

```yaml
FlkLogonAppTxTopic:
  Type: AWS::SNS::Topic
  Properties:
    TopicName: !Sub '${StackModifier}-flk-logon-app-tx-topic'
    KmsMasterKeyId: alias/aws/sns
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
```

> `KmsMasterKeyId: alias/aws/sns` is mandatory on all SNS topics — uses the AWS-managed SNS key.

---

## FIFO SNS topic

Use FIFO when consumers require ordered, exactly-once delivery:

```yaml
FlkLogonAppTxFifoTopic:
  Type: AWS::SNS::Topic
  Properties:
    TopicName: !Sub '${StackModifier}-flk-logon-app-tx-topic.fifo'
    FifoTopic: True
    ContentBasedDeduplication: True
    KmsMasterKeyId: alias/aws/sns
    Tags:
      - Key: wg:info:taggingversion
        Value: 2.0.0
      # ... same WG tags ...
```

> FIFO topic names must end with `.fifo`.

---

## Cross-account TopicPolicy

Allow SQS queues in other accounts to subscribe to this topic. The account ID map is defined in `Mappings`:

```yaml
Mappings:
  AccountIds:
    dev:
      accountId: "111111111111"
    qa:
      accountId: "222222222222"
    staging:
      accountId: "333333333333"
    prod:
      accountId: "444444444444"
```

```yaml
FlkLogonAppTxTopicPolicy:
  Type: AWS::SNS::TopicPolicy
  Properties:
    Topics:
      - !Ref FlkLogonAppTxTopic
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Sid: AllowSameAccountPublish
          Effect: Allow
          Principal:
            AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
          Action: sns:Publish
          Resource: !Ref FlkLogonAppTxTopic

        - Sid: AllowCrossAccountSubscribe
          Effect: Allow
          Principal:
            AWS: !Sub
              - 'arn:aws:iam::${TargetAccountId}:root'
              - TargetAccountId: !FindInMap [ AccountIds, !Ref Environment, accountId ]
          Action:
            - sns:Subscribe
            - sns:Receive
          Resource: !Ref FlkLogonAppTxTopic
```

---

## Outputs

Export the topic ARN for cross-stack references (e.g. SQS subscriptions in other sub-stacks):

```yaml
Outputs:
  FlkLogonAppTxTopicArn:
    Value: !Ref FlkLogonAppTxTopic
    Export:
      Name: !Sub '${StackModifier}-flk-logon-app-tx-topic-arn'

  FlkLogonAppTxTopicName:
    Value: !GetAtt FlkLogonAppTxTopic.TopicName
    Export:
      Name: !Sub '${StackModifier}-flk-logon-app-tx-topic-name'
```

---

## Checklist

- [ ] `KmsMasterKeyId: alias/aws/sns` on all SNS topics
- [ ] FIFO topic names end with `.fifo`
- [ ] `AWS::SNS::TopicPolicy` added for cross-account subscribe permissions
- [ ] Cross-account account IDs sourced from `Mappings` (not hardcoded)
- [ ] Topic ARN exported in `Outputs` for use by SQS subscriptions in other sub-stacks
