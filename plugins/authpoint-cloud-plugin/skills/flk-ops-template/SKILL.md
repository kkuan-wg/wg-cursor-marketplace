---
name: flk-ops-template
description: Ops template for Folklore SAM/CloudFormation and deployment. Use when creating or reviewing SAM templates, Jenkinsfile, or deployment configurations.
---

# Folklore Ops Template

Guide for writing and reviewing SAM templates, CloudFormation resources, and Jenkinsfile **Lambda registration lists** (`lambdaNames`) in Folklore projects.

## When to Use

- Creating or reviewing `template.yaml` (SAM/CloudFormation)
- Adding Lambda functions, SQS queues, SNS topics or API Gateway
- Defining or reviewing `lambdaNames` in a `Jenkinsfile`
- Validating tags, encryption, concurrency, LogGroups or IAM policies

---

## Parts Index

| Part | File | Content |
|------|------|---------|
| **globals** | [parts/globals.md](parts/globals.md) | Globals block, WG tags 2.0 vs 2.1, architecture, alarm tags, compliance values |
| **lambda** | [parts/lambda.md](parts/lambda.md) | Lambda definition, concurrency mapping, LogGroup, IAM policies, triggers |
| **api-gateway** | [parts/api-gateway.md](parts/api-gateway.md) | AWS::Serverless::Api, CORS, WAF, Swagger, API trigger on Lambda |
| **sqs** | [parts/sqs.md](parts/sqs.md) | SQS queue pair (queue + DLQ), VisibilityTimeout (consumer vs validator), SSE, SNS subscription |
| **sns** | [parts/sns.md](parts/sns.md) | SNS topic, KMS encryption, FIFO, cross-account TopicPolicy |
| **nested-stacks** | [parts/nested-stacks.md](parts/nested-stacks.md) | Root template, AWS::Serverless::Application, max depth, Conditions, cross-stack refs |
| **encryption-at-rest** | [parts/encryption-at-rest.md](parts/encryption-at-rest.md) | Secrets Manager, S3, DynamoDB, EFS, RDS (beyond SQS/SNS) |
| **template-validation** | [parts/template-validation.md](parts/template-validation.md) | Parameters, Swagger, !Ref/!GetAtt, X-Ray, sam validate / cfn-lint, review shape |
| **jenkinsfile** | [parts/jenkinsfile.md](parts/jenkinsfile.md) | Pipeline stages, checkout layers, lambdaNames, SAM deployment |

---

## Template Structure

```
application/
├── template.yaml                         # Root orchestrator (nested stacks)
└── src/
    ├── api/
    │   └── template.yaml                 # API Gateway + Lambda functions
    ├── transaction/
    │   └── template.yaml                 # SQS-triggered Lambdas
    ├── data/transaction_stream/
    │   └── template.yaml                 # DDB stream + SNS topic
    └── cache/
        ├── core_data/template.yaml
        ├── resource/template.yaml
        └── user/template.yaml
infra/
└── Jenkinsfile
```

Each sub-stack template has: `Globals` → `Mappings` → `Parameters` → `Resources` → `Outputs`.

---

## General Checklist

### Tags
- [ ] All resources use WG 2.1.0 tags (9 tags including `wg:compliance:*`)
- [ ] `flk:alarm:lambda:error: true` on all Lambda functions (in Globals or per function)
- [ ] `flk:alarm:lambda:concurrentExec` set to concurrency value on each Lambda
- [ ] `flk:alarm:sqs:dlq: "true"` on all DLQ resources
- [ ] `flk:alarm:sqs:ageOfMessage` on main SQS queues

### Encryption
- [ ] `SqsManagedSseEnabled: true` on all SQS queues
- [ ] `KmsMasterKeyId: alias/aws/sns` on all SNS topics
- [ ] Other data stores (Secrets Manager, S3, DynamoDB, EFS, RDS when present) follow [parts/encryption-at-rest.md](parts/encryption-at-rest.md)

### Lambda
- [ ] `Tracing: Disabled` in Globals (no `AWS::XRay::*` resources unless explicitly excepted)
- [ ] `ReservedConcurrentExecutions` set via `!FindInMap` on every function
- [ ] Explicit `AWS::Logs::LogGroup` with `RetentionInDays: 14` for every function
- [ ] IAM policies follow least privilege (specific actions + specific resource ARNs)

### SQS
- [ ] Every SQS queue has a paired DLQ
- [ ] `VisibilityTimeout` matches **consumer** (`6×` Lambda timeout) or **validator** (`~timeout×1.3`) per [parts/sqs.md](parts/sqs.md)
- [ ] `maxReceiveCount: 5` in `RedrivePolicy`
- [ ] `MessageRetentionPeriod: 1209600` (14 days) on DLQs

### API Gateway
- [ ] `TracingEnabled: False` on `AWS::Serverless::Api`
- [ ] `DataTraceEnabled: false` in `MethodSettings`
- [ ] WAF `AWS::WAFv2::WebACLAssociation` attached
- [ ] `AWS::IAM::Role` + `AWS::ApiGateway::Account` for CloudWatch logs

### Nested stacks
- [ ] Sub-stacks contain only resources — no `AWS::Serverless::Application` inside a sub-stack (see [parts/nested-stacks.md](parts/nested-stacks.md))

### Template hygiene
- [ ] No unused `Parameters`; references in co-located Swagger checked when API uses `AWS::Include`
- [ ] All `!Ref` / `!GetAtt` resolve to real parameters or resources ([parts/template-validation.md](parts/template-validation.md))
- [ ] `sam validate` / `cfn-lint` run on changed templates when available

### Jenkinsfile (`lambdaNames`)
- [ ] All deployed Lambda `FunctionName` values listed in `lambdaNames` (every `AWS::Serverless::Function` in every sub-stack)
- [ ] Names match SAM `!Sub '${StackModifier}-...'` after resolving `StackModifier` for the target environment
