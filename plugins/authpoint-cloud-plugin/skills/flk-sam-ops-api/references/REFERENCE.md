# SAM Ops — Lambda API Reference

Detailed reference for SAM template patterns specific to Folklore API Lambda functions. Read when writing or reviewing `template.yaml` resources for API Lambdas.

General SAM conventions (Globals, tags, encryption, SQS, SNS, nested stacks, Jenkinsfile) are covered by `flk-ops-template` — this reference focuses only on the API Lambda-specific patterns.

---

## 1. Function Resource

The minimal shape for an API Lambda function. Properties shared across all functions in the stack (runtime, architecture, tracing, layers, base tags) belong in `Globals.Function` — only overrides go on the individual resource.

```yaml
Flk{Feature}ApiFn:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: {function_name}_fn          # must match the actual folder name exactly
    FunctionName: !Ref Flk{Feature}ApiFnName
    ReservedConcurrentExecutions: !FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]
    Environment:
      Variables:
        {TABLE}_TABLE_NAME: !Ref Flk{Table}
        WGC_ALLOWED_ORIGIN: !Ref WgcAllowedOrigin
        AWS_REGION: !Ref AWS::Region
    Tags:
      Name: !Ref Flk{Feature}ApiFnName
    Policies:
      - Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - dynamodb:Query
              - dynamodb:PutItem
            Resource: !Sub "arn:${AWS::Partition}:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${Flk{Table}}"
    Events:
      {Feature}Edge:
        Type: Api
        Properties:
          RestApiId: !Ref Flk{Domain}Api
          Path: /api/v1/{path}
          Method: POST

Flk{Feature}ApiFnLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub '/aws/lambda/${Flk{Feature}ApiFn}'
    RetentionInDays: 14
```

**Rules:**
- `CodeUri` must be a relative path matching the actual folder — no leading `./` in real templates (e.g. `oidc_authn_fn`, not `./oidc_authn_fn`)
- `FunctionName` always uses `!Ref` to a Parameter — never hardcoded
- `ReservedConcurrentExecutions` always uses `!FindInMap` — never a literal number
- Every function must have a paired `AWS::Logs::LogGroup` with `RetentionInDays: 14`

---

## 2. IAM Policy Patterns

Inline `Version: 2012-10-17` statements are used for all policies — **not** SAM policy templates (`DynamoDBCrudPolicy` etc.) unless already used in the surrounding stack. Match whatever pattern is already in the target template.

**DynamoDB read + write:**

```yaml
- Version: 2012-10-17
  Statement:
    - Effect: Allow
      Action:
        - dynamodb:Query
        - dynamodb:PutItem
      Resource: !Sub "arn:${AWS::Partition}:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${TableNameParam}"
```

**DynamoDB with GSI:**

```yaml
- Version: 2012-10-17
  Statement:
    - Effect: Allow
      Action:
        - dynamodb:Query
      Resource:
        - !Sub "arn:${AWS::Partition}:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${TableNameParam}"
        - !Sub "arn:${AWS::Partition}:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${TableNameParam}/index/*"
```

**SNS publish:**

```yaml
- Version: 2012-10-17
  Statement:
    - Effect: Allow
      Action:
        - sns:Publish
      Resource: !Ref TopicArnParam
```

**Lambda invoke:**

```yaml
- LambdaInvokePolicy:
    FunctionName: !Ref Flk{Feature}FnName
```

**STS assume role (cross-account):**

```yaml
- Version: 2012-10-17
  Statement:
    - Effect: Allow
      Action:
        - sts:AssumeRole
      Resource: !Ref CrossAccountRoleArnParam
```

---

## 3. Parameter Conventions

Each function's `FunctionName` is always a separate `Parameters` entry passed from the root stack:

```yaml
Parameters:
  Flk{Feature}ApiFnName:
    Type: String
  {Table}TableName:
    Type: String
  WgcAllowedOrigin:
    Type: String
  AuthpointLambdaLayer:
    Type: String
  FolkloreDomainLambdaLayer:
    Type: String
```

Shared parameters (layers, table names, allowed origin) are passed down from the root template via `AWS::Serverless::Application` properties — never duplicated or hardcoded.

---

## 4. Globals Block (API sub-stack)

```yaml
Globals:
  Api:
    OpenApiVersion: "3.0.3"
    MethodSettings:
      - HttpMethod: "*"
        ResourcePath: "/*"
        LoggingLevel: !Ref ApiGatewayLoggingLevel
        DataTraceEnabled: false
  Function:
    Handler: app.lambda_handler
    Runtime: python3.11
    Architectures:
      - arm64
    Tracing: Disabled
    MemorySize: 256
    Timeout: 29
    Layers:
      - !Ref AuthpointLambdaLayer
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        LOGGING_LEVEL: !Ref LoggingLevel
    Tags:
      wg:info:taggingversion: 2.0.0
      wg:purpose:product: authpoint
      wg:purpose:serviceid: folklore-service
      wg:purpose:environment: !Ref Environment
      wg:purpose:region: !Ref AWS::Region
      wg:automation:expiry: never
      wg:info:owner: authpoint
      flk:alarm:lambda:concurrentExec: !FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]
      flk:alarm:lambda:error: true
```

`FolkloreDomainLambdaLayer` is **not** in Globals — it is added per-function under `Layers` because not every function in the stack uses it.

---

## 5. Architectural Decisions

| Decision | Rule |
|----------|------|
| `CodeUri` | Relative folder name only — no `./` prefix (matches real templates) |
| `FunctionName` | Always `!Ref` to a Parameter — never `!Sub` with a hardcoded string |
| Concurrency | Always `!FindInMap [ReservedConcurrentExecutions, !Ref Environment, concurrency]` |
| LogGroup | Every function needs a paired `AWS::Logs::LogGroup` with `RetentionInDays: 14` |
| IAM policies | Explicit `Version: 2012-10-17` statements with least-privilege actions and specific resource ARNs |
| `FolkloreDomainLambdaLayer` | Added per-function under `Layers`, not in Globals |
| `DataTraceEnabled` | Always `false` — never enable request/response logging |
| `Tracing` | Always `Disabled` in Globals |
