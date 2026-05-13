# Nested Stacks

Folklore services use a root `template.yaml` that orchestrates multiple sub-stacks via `AWS::Serverless::Application`. Each sub-stack owns its own resources (Lambdas, queues, topics).

---

## Root template structure

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: folklore-service-logon-app root stack

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, qa, staging, prod]
  StackModifier:
    Type: String
  MainRegion:
    Type: String
    Default: us-east-1
  # Shared parameters passed down to sub-stacks
  AuthpointLambdaLayerArn:
    Type: String
  FolkloreDomainLambdaLayerArn:
    Type: String
  WAFWebACLArn:
    Type: String

Conditions:
  ShouldDeploy: !Equals [ !Ref MainRegion, !Ref AWS::Region ]

Resources:

  DataTransactionStreamStack:
    Type: AWS::Serverless::Application
    Condition: ShouldDeploy
    Properties:
      Location: src/data/transaction_stream/template.yaml
      Parameters:
        Environment: !Ref Environment
        StackModifier: !Ref StackModifier
        AuthpointLambdaLayer: !Ref AuthpointLambdaLayerArn
        FolkloreDomainLambdaLayer: !Ref FolkloreDomainLambdaLayerArn

  TransactionStack:
    Type: AWS::Serverless::Application
    Condition: ShouldDeploy
    Properties:
      Location: src/transaction/template.yaml
      Parameters:
        Environment: !Ref Environment
        StackModifier: !Ref StackModifier
        AuthpointLambdaLayer: !Ref AuthpointLambdaLayerArn
        FolkloreDomainLambdaLayer: !Ref FolkloreDomainLambdaLayerArn
        FlkLogonAppTxTopicArn: !GetAtt DataTransactionStreamStack.Outputs.FlkLogonAppTxTopicArn

  ApiStack:
    Type: AWS::Serverless::Application
    Condition: ShouldDeploy
    Properties:
      Location: src/api/template.yaml
      Parameters:
        Environment: !Ref Environment
        StackModifier: !Ref StackModifier
        AuthpointLambdaLayer: !Ref AuthpointLambdaLayerArn
        WAFWebACLArn: !Ref WAFWebACLArn

  CacheCoreDataStack:
    Type: AWS::Serverless::Application
    Properties:
      Location: src/cache/core_data/template.yaml
      Parameters:
        Environment: !Ref Environment
        StackModifier: !Ref StackModifier
        AuthpointLambdaLayer: !Ref AuthpointLambdaLayerArn
        FolkloreDomainLambdaLayer: !Ref FolkloreDomainLambdaLayerArn
```

> Note: `CacheCoreDataStack` does not have `Condition: ShouldDeploy` — it deploys in all regions. Only stacks that must be region-scoped use the condition.

---

## Conditions

Use `ShouldDeploy` to prevent duplicate deployments in multi-region setups:

```yaml
Conditions:
  ShouldDeploy: !Equals [ !Ref MainRegion, !Ref AWS::Region ]
```

Apply to sub-stacks that own shared resources (topics, tables) that should only exist in one region:

```yaml
DataTransactionStreamStack:
  Type: AWS::Serverless::Application
  Condition: ShouldDeploy
  ...
```

---

## Cross-stack references

Use `!GetAtt <NestedStackLogicalId>.Outputs.<OutputKey>` to pass outputs from one sub-stack to another:

```yaml
# Pass SNS topic ARN from data stack to transaction stack
FlkLogonAppTxTopicArn: !GetAtt DataTransactionStreamStack.Outputs.FlkLogonAppTxTopicArn

# Pass SQS queue URL from transaction stack to cache stack
FlkLogonAppTxQueueUrl: !GetAtt TransactionStack.Outputs.FlkLogonAppTxQueueUrl
```

The referenced output must be declared in the sub-stack's `Outputs` section with an `Export.Name`.

---

## Maximum nesting depth

Sub-stacks must contain **only resources** — they must not reference further `AWS::Serverless::Application`. This means there are at most **two hops** of `AWS::Serverless::Application` from the root (root → sub-stack → resources).

**Allowed**

```text
application/template.yaml          ← root
  └── AWS::Serverless::Application
        → src/api/template.yaml    ← sub-stack (Lambdas, queues, API… only)
```

**Not allowed**

```text
application/template.yaml          ← root
  └── AWS::Serverless::Application
        → src/api/template.yaml    ← sub-stack
              └── AWS::Serverless::Application   ← ❌ sub-sub-stack
```

If you need more decomposition, flatten by merging stacks or moving shared resources to the root instead of chaining another `AWS::Serverless::Application`.

---

## Resource naming pattern

All resource names use `!Sub '${StackModifier}-resource-name'` to ensure uniqueness per environment:

```yaml
# In sub-stack template
FunctionName: !Sub '${StackModifier}-flk-logon-app-tx-consumer'
QueueName: !Sub '${StackModifier}-flk-logon-app-tx-queue'
TopicName: !Sub '${StackModifier}-flk-logon-app-tx-topic'
```

`StackModifier` is passed as a Parameter from the root template and typically has the format `<env>-<service>` (e.g. `dev-logon-app`).

---

## Parameters in sub-stack templates

Every sub-stack must declare the parameters it receives:

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, qa, staging, prod]
  StackModifier:
    Type: String
  AuthpointLambdaLayer:
    Type: String
    Description: ARN of the authpoint-lambda-layer
  FolkloreDomainLambdaLayer:
    Type: String
    Description: ARN of the folklore-lambda-layer
  # Optional: ARNs from sibling stacks
  FlkLogonAppTxTopicArn:
    Type: String
    Description: ARN of the transaction SNS topic
```

---

## Checklist

- [ ] Root `template.yaml` uses `AWS::Serverless::Application` for each sub-stack
- [ ] Sub-stacks contain only resources — no nested `AWS::Serverless::Application` inside a sub-stack
- [ ] `Conditions: ShouldDeploy` applied to region-scoped stacks
- [ ] Cross-stack references use `!GetAtt <Stack>.Outputs.<Key>`
- [ ] All resource names use `!Sub '${StackModifier}-...'`
- [ ] Layer ARNs passed as Parameters from root to sub-stacks
- [ ] Sub-stack `Outputs` export all ARNs/URLs needed by sibling stacks
- [ ] Sub-stack `Parameters` block declares all received parameters
