# SAML User Cache Consumer — Infrastructure

> **Spec ID:** aaas-30040  
> **Type:** Infra  
> **AWS Services:** Lambda, SQS, DynamoDB, SNS

## References

- Database model: `get_database_model(domain='saml', model_name='flk-saml-user-detail')` (`../../database-model/flk-saml-user-detail.json`) — GSIs: `emailGSI` (`accountId#email`), `usernameGSI` (`accountId#username`); TTL fields: `ttl`, `softDeletedTtl`; DynamoDB Streams: enabled, `NEW_AND_OLD_IMAGES`

## Requirements

### REQ-1: SQS queue and dead-letter queue

The deployment MUST provision:

- SQS FIFO queue: `flk-saml-user-cmd-queue.fifo` — subscribes to `flk-user-cmd-topic.fifo` in the `authpointsec` account; `VisibilityTimeout: 18s`.
- SQS DLQ: `flk-saml-user-cmd-dlqueue.fifo` — `MessageRetentionPeriod: 14 days`, `maxReceiveCount: 5`, `ContentBasedDeduplication: true`.

### REQ-2: Lambda function

The deployment MUST provision a Lambda function `flk-saml-user-cmd-invoker` with:

- Trigger: `flk-saml-user-cmd-queue.fifo`; `BatchSize: 1`.
- `MemorySize: 256 MB`, `Timeout: 3s`, runtime `python3.11`, arch `arm64`.
- Layers: `AuthpointLambdaLayer`, `FolkloreDomainLambdaLayer`.
- `ReservedConcurrentExecutions`: 5 (dev/qa/staging), 30 (prod).

### REQ-3: DynamoDB global table

The deployment MUST provision a DynamoDB global table `flk-saml-user-detail` with:

- Partition key: `USER#<userId>`.
- DynamoDB Streams enabled (`NEW_AND_OLD_IMAGES`).
- GSIs: `emailGSI` (pk `accountId#email`), `usernameGSI` (pk `accountId#username`).
- TTL attribute: `ttl` — cache TTL; DynamoDB TTL enabled on this attribute.
- TTL attribute: `softDeletedTtl` — soft-delete marker; DynamoDB TTL enabled on this attribute.
