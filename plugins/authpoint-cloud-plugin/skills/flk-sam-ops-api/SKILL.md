---
name: flk-sam-ops-api
description: Creates and updates SAM template resources for Folklore API Lambda functions (AWS::Serverless::Function, API Gateway event, IAM policies, environment variables, LogGroup). Use when writing or reviewing SAM templates for API Lambdas, or when the user mentions template.yaml, SAM, infrastructure, deploy, CloudFormation, or infra for an API Lambda. Does NOT cover Python application code — use flk-python-lambda-api for that.
---

# Folklore SAM Ops — Lambda API

Creates and updates the SAM/CloudFormation infrastructure for Folklore API Lambda functions. Covers `template.yaml` resources only — no Python application code.

`flk-ops-template` is always loaded alongside this skill — all general SAM conventions, tagging rules, encryption requirements, IAM least-privilege patterns, and the general checklist defined there apply here without repetition.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

**If a spec path was provided**, read the following files:
- `spec.md` — extract: AWS Services, env var names, DynamoDB table names, SQS/SNS resources, API path and method
- `proposal.md` — extract: the exact infra artifacts to create and scope boundaries (same folder as `spec.md`)
- `infra-tasks.md` — extract: infra tasks under **Implementation** (same folder as `spec.md`)

**If no spec was provided**, extract from the user's direct input: function name, table names, env vars, API path/method, memory, timeout.

### 2. Browse the codebase

**All browsing is scoped to the current workspace.**

Locate the nearest sibling API Lambda's SAM template **within the workspace**. Extract:
- `FunctionName` naming convention (`!Sub '${StackModifier}-flk-{domain}-{feature}-api'`)
- Existing parameter names for shared resources (layers, allowed origin, etc.)
- The `template.yaml` file path where the new resource should be added

### 3. Load flk-ops-template parts progressively

| Need | Part to read |
|------|-------------|
| Lambda resource definition | `parts/lambda.md` |
| API Gateway event / CORS | `parts/api-gateway.md` |
| Globals, tags | `parts/globals.md` |
| Template validation | `parts/template-validation.md` |
| Jenkinsfile `lambdaNames` | `parts/jenkinsfile.md` |

Read only parts relevant to the resources being added.

### 4. Ask only what you cannot find

One targeted question per gap. Never ask about things discoverable from the spec or existing templates.

---

## Phase 2: Write the Resources

### Step 1 — `AWS::Serverless::Function`

```yaml
Flk{Feature}Fn:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: ./{function_name}_fn
    FunctionName: !Sub '${StackModifier}-flk-{domain}-{feature}-api'
    MemorySize: 512
    Timeout: 10
    Handler: app.lambda_handler
    Runtime: python3.11
    Architectures: [arm64]
    ReservedConcurrentExecutions: !FindInMap [ConcurrencyMap, !Ref Environment, Flk{Feature}Fn]
    Tracing: Disabled
    Layers:
      - !Ref AuthpointLambdaLayer
      - !Ref FolkloreDomainLambdaLayer
    Environment:
      Variables:
        {TABLE}_TABLE_NAME: !Ref Flk{Table}
        WGC_ALLOWED_ORIGIN: !Ref WgcAllowedOrigin
        AWS_REGION: !Ref AWS::Region
    Events:
      ApiEvent:
        Type: Api
        Properties:
          Path: /api/v1/{path}
          Method: POST
          RestApiId: !Ref Flk{Domain}Api
    Policies:
      - DynamoDBCrudPolicy:
          TableName: !Ref Flk{Table}
    Tags:
      # WG 2.1.0 tags — see flk-ops-template parts/globals.md
      flk:alarm:lambda:error: 'true'
      flk:alarm:lambda:concurrentExec: '<concurrency>'
```

### Step 2 — `AWS::Logs::LogGroup`

Every function requires an explicit log group with 14-day retention:

```yaml
Flk{Feature}FnLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub '/aws/lambda/${Flk{Feature}Fn}'
    RetentionInDays: 14
```

### Step 3 — Jenkinsfile `lambdaNames`

Add the resolved function name to `lambdaNames` in `infra/Jenkinsfile`. See `flk-ops-template parts/jenkinsfile.md` for the exact format.

---

## Phase 3: Verify Before Finishing

The `flk-ops-template` general checklist applies in full. Additionally verify:

- [ ] `CodeUri` matches the actual `{function_name}_fn` folder in the workspace
- [ ] `FunctionName` follows `!Sub '${StackModifier}-flk-{domain}-{feature}-api'` convention
- [ ] All env vars required by `configuration.py` are present under `Environment.Variables`
- [ ] `ReservedConcurrentExecutions` uses `!FindInMap [ConcurrencyMap, ...]`
- [ ] `AWS::Logs::LogGroup` added with `RetentionInDays: 14`
- [ ] Function name added to `lambdaNames` in `Jenkinsfile`
- [ ] All WG 2.1.0 tags present (see `flk-ops-template parts/globals.md`)

## Reference

- SAM template patterns, API Gateway, tags, encryption, Jenkinsfile → `flk-ops-template` skill parts
- Lambda code (configuration, ports, adapters, service, app.py) → `flk-python-lambda-api` skill
