# SAML User Cache Consumer — Infrastructure Provisioning

**Ticket:** AAAS-30040

## Goal

- Provision `flk-saml-user-cmd-queue.fifo` SQS FIFO queue with SNS subscription filter (`ResourceTypes: SAML`) and `flk-saml-user-cmd-dlqueue.fifo` dead-letter queue (`ContentBasedDeduplication: true`, `maxReceiveCount: 5`, retention 14 days).
- Provision `flk-saml-user-cmd-invoker` Lambda (`BatchSize: 1`, `MemorySize: 256 MB`, `Timeout: 3 s`, `python3.11`, `arm64`) with `AuthpointLambdaLayer` and `FolkloreDomainLambdaLayer`; `ReservedConcurrentExecutions` 5 (dev/qa/staging) / 30 (prod).
- Provision `flk-saml-user-detail` DynamoDB global table (PK `USER#<userId>`, GSIs `emailGSI`/`usernameGSI`, streams `NEW_AND_OLD_IMAGES`, TTL on `ttl` and `softDeletedTtl`).

## Scope

- SAM template (`template.yaml`) declaring all AWS resources: SQS FIFO queue, DLQ, SNS subscription with filter policy, DynamoDB global table, Lambda function with event source mapping.
- Minimal Lambda scaffold (`app.py` stub) sufficient for the SAM deployment to succeed.
- IAM permissions required for the Lambda to read from SQS and write to DynamoDB.

**Out of scope**

- Business logic, event routing, handlers, or any application-layer code — covered by the companion Code spec.
- Changes to the Folklore Cache producer or `flk-user-cmd-topic.fifo`.
- Schema changes to the shared Folklore Cache event envelope.

## Spec

[./spec.md](./spec.md) — satisfies:

- **Requirement: SQS queue and dead-letter queue**
- **Requirement: Lambda function**
- **Requirement: DynamoDB global table**

## Artifacts

Artifacts are listed in `./spec.md#references`; verify all expected paths exist before starting implementation.

New files this change will create:

- `template.yaml` — SAM IaC: SQS FIFO queue + DLQ, SNS subscription with filter policy, `flk-saml-user-detail` DynamoDB global table, `flk-saml-user-cmd-invoker` Lambda with event source mapping and layer references
- `saml_user_cmd_invoker_fn/app.py` — minimal Lambda stub; wired by SAM; business logic added by Code implementation

## Risks / Open questions

- SNS topic ARN (`flk-user-cmd-topic.fifo`) is cross-account (`authpointsec`); confirm the SNS subscription and resource-based policy are correctly scoped before deploying.
