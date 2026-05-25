# Tasks — SAML User Cache Consumer Infrastructure Provisioning

> Spec: [./spec.md](./spec.md)

## Spec & Alignment

- [ ] Confirm `./database-model/flk-saml-user-detail.json` exists and verify PK format (`USER#<userId>`), GSI names (`emailGSI`, `usernameGSI`), TTL attribute names (`ttl`, `softDeletedTtl`), and streams config (`NEW_AND_OLD_IMAGES`) (Requirement: DynamoDB global table)
- [ ] Confirm SNS topic ARN for `flk-user-cmd-topic.fifo` in the `authpointsec` account and verify cross-account SNS subscription policy is in place (Requirement: SQS queue and dead-letter queue)
- [ ] Confirm `ReservedConcurrentExecutions` values per environment (dev/qa/staging: 5, prod: 30) with the team before writing the SAM template (Requirement: Lambda function)

## Infrastructure

- [ ] Define `flk-saml-user-cmd-dlqueue.fifo` SQS FIFO DLQ in `template.yaml`: `ContentBasedDeduplication: true`, `MessageRetentionPeriod: 14 days`, `maxReceiveCount: 5` (Requirement: SQS queue and dead-letter queue)
- [ ] Define `flk-saml-user-cmd-queue.fifo` SQS FIFO main queue in `template.yaml`: `VisibilityTimeout: 18s`, redrive policy pointing to DLQ (Requirement: SQS queue and dead-letter queue)
- [ ] Add SNS subscription from `flk-user-cmd-topic.fifo` to `flk-saml-user-cmd-queue.fifo` in `template.yaml` with filter policy `resourceTypes: SAML` (Requirement: SQS queue and dead-letter queue)
- [ ] Define `flk-saml-user-detail` DynamoDB global table in `template.yaml`: PK `USER#<userId>`, GSIs `emailGSI` / `usernameGSI`, streams `NEW_AND_OLD_IMAGES`, TTL enabled on `ttl` and `softDeletedTtl` (Requirement: DynamoDB global table)
- [ ] Define `flk-saml-user-cmd-invoker` Lambda in `template.yaml`: runtime `python3.11`, arch `arm64`, `MemorySize: 256 MB`, `Timeout: 3s`, layers `AuthpointLambdaLayer` + `FolkloreDomainLambdaLayer`, SQS event source mapping with `BatchSize: 1` (Requirement: Lambda function)
- [ ] Set `ReservedConcurrentExecutions` per environment mapping in `template.yaml`: 5 for dev/qa/staging, 30 for prod (Requirement: Lambda function)
- [ ] Add IAM policy to `flk-saml-user-cmd-invoker` in `template.yaml`: `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `flk-saml-user-cmd-queue.fifo`; `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:UpdateItem`, `dynamodb:DeleteItem` on `flk-saml-user-detail` (Requirement: Lambda function)
- [ ] Create minimal `saml_user_cmd_invoker_fn/app.py` stub sufficient for SAM deployment; full handler added by the Code implementation change (Requirement: Lambda function)
