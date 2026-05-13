# Globals Block

The `Globals` section applies defaults to all Lambda functions in the template. Define it at the top of every sub-stack template.

---

## API sub-stack (x86_64, WG 2.1.0)

Used when the sub-stack contains functions that use `CommCrypto` (requires x86_64) or API Gateway functions:

```yaml
Globals:
  Api:
    OpenApiVersion: "3.0.3"
    AlwaysDeploy: True
    MethodSettings:
      - HttpMethod: "*"
        ResourcePath: "/*"
        LoggingLevel: !Ref ApiGatewayLoggingLevel  # INFO or ERROR
        DataTraceEnabled: false                    # Never log request/response body
  Function:
    Handler: app.lambda_handler
    Runtime: python3.11
    Architectures:
      - x86_64
    Tracing: Disabled
    MemorySize: 256
    Timeout: 29
    Layers:
      - !Ref AuthpointLambdaLayer
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        LOGGING_LEVEL: !Ref LoggingLevel
        WGC_ALLOWED_ORIGIN: !Ref WGCAllowedOrigin
    Tags:
      Region: !Ref AWS::Region
      wg:info:taggingversion: 2.1.0
      wg:purpose:product: authpoint
      wg:purpose:serviceid: folklore-service-logon-app
      wg:purpose:environment: !Ref Environment
      wg:purpose:region: !Ref AWS::Region
      wg:automation:expiry: never
      wg:compliance:program: pci
      wg:compliance:dataclassification: business-only
      wg:compliance:specialdata: customerorigin
      wg:info:owner: authpoint
      flk:alarm:lambda:concurrentExec: !FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]
      flk:alarm:lambda:error: true
```

---

## Non-API sub-stack (arm64, WG 2.0.0 — legacy)

Used for SQS consumers, DDB stream listeners, cache functions — no CommCrypto. This pattern uses WG 2.0.0 (6 tags, no `wg:compliance:*`); **new** sub-stacks of this type should migrate to 2.1.0 and add the 3 compliance tags:

```yaml
Globals:
  Function:
    Handler: app.lambda_handler
    Runtime: python3.11
    Architectures:
      - arm64
    Tracing: Disabled
    Layers:
      - !Ref AuthpointLambdaLayer
      - !Ref FolkloreDomainLambdaLayer
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        LOGGING_LEVEL: !Ref LoggingLevel
    Tags:
      Region: !Ref AWS::Region
      wg:info:taggingversion: 2.0.0
      wg:purpose:product: authpoint
      wg:purpose:serviceid: folklore-service-logon-app
      wg:purpose:environment: !Ref Environment
      wg:purpose:region: !Ref AWS::Region
      wg:automation:expiry: never
      wg:info:owner: authpoint
      flk:alarm:lambda:error: true
```

---

## WG Tags — 2.0.0 vs 2.1.0

| Tag | 2.0.0 | 2.1.0 |
|-----|-------|-------|
| `wg:info:taggingversion` | `2.0.0` | `2.1.0` |
| `wg:purpose:product` | ✅ | ✅ |
| `wg:purpose:serviceid` | ✅ | ✅ |
| `wg:purpose:environment` | ✅ | ✅ |
| `wg:purpose:region` | ✅ | ✅ |
| `wg:automation:expiry` | ✅ | ✅ |
| `wg:info:owner` | ✅ | ✅ |
| `wg:compliance:program` | ❌ | ✅ (e.g. `pci`) |
| `wg:compliance:dataclassification` | ❌ | ✅ (e.g. `business-only`) |
| `wg:compliance:specialdata` | ❌ | ✅ (e.g. `customerorigin`) |

Use **2.1.0** for all new templates. 2.0.0 is present in legacy sub-stacks only.

**WatchGuard tagging reference (internal):** [Resource Tagging](https://watchguard.atlassian.net/wiki/spaces/WC/pages/31211700/Resource+Tagging)

---

## Adapting WG values to the service

Examples in this skill use placeholders such as `folklore-service-logon-app` and `authpoint`. **Do not copy blindly:** set `wg:purpose:serviceid`, `wg:purpose:product`, and compliance tags from the **current** repository’s existing templates or from the service’s documented standards.

To discover what the repo already uses:

```bash
grep -r "wg:purpose:serviceid" application/
grep -r "wg:purpose:product" application/
grep -r "wg:compliance:program" application/
```

If values are unknown, align with the team or product owner before changing tags.

### Allowed values — `wg:compliance:*` (2.1.0)

| Tag | Allowed values |
|-----|----------------|
| `wg:compliance:program` | `pci`, `iso27001`, `iso27001-pci` |
| `wg:compliance:dataclassification` | `public`, `business-only`, `confidential`, `mission-critical` |
| `wg:compliance:specialdata` | `pii`, `customerorigin`, `customerorigin-pii`, `trade-secrets`, `security-risk` |

Pick the **strictest** program and classification that match real data processed by the stack. `specialdata` can combine concepts (e.g. `customerorigin-pii`) where policy allows.

---

## Architecture rule

| Architecture | When to use |
|---|---|
| `x86_64` | Functions using `CommCrypto` (crypto adapter requires native `.so` compiled for x86_64) |
| `arm64` | All other functions (lower cost, better performance for Python workloads) |

---

## Alarm tags

| Tag | Where | Value |
|-----|-------|-------|
| `flk:alarm:lambda:error` | Globals or per function | `true` |
| `flk:alarm:lambda:concurrentExec` | Globals or per function | `!FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]` |
| `flk:alarm:sqs:dlq` | DLQ resource | `"true"` |
| `flk:alarm:sqs:ageOfMessage` | Main SQS queue | e.g. `"180"` (seconds) |

---

## Concurrency Mappings

Define a `Mappings` block in every sub-stack to control `ReservedConcurrentExecutions` per environment:

```yaml
Mappings:
  ReservedConcurrentExecutions:
    dev:
      concurrency: 5
    qa:
      concurrency: 5
    staging:
      concurrency: 5
    prod:
      concurrency: 30
```

For sub-stacks with multiple functions at different concurrency levels, add separate keys:

```yaml
Mappings:
  ReservedConcurrentExecutions:
    dev:
      concurrency: 5
      timeoutConcurrency: 5
    prod:
      concurrency: 30
      timeoutConcurrency: 15
```

---

## Checklist

- [ ] `Tracing: Disabled` in Globals (never `Active`)
- [ ] `Runtime: python3.11`
- [ ] Architecture: `x86_64` for CommCrypto, `arm64` for all others
- [ ] `wg:purpose:serviceid`, `wg:purpose:product`, and `wg:compliance:*` match **this** service (not copied blindly from examples in this skill)
- [ ] WG 2.1.0 tags in Globals (9 tags including `wg:compliance:*`) — legacy 2.0.0 sub-stacks are exempt but must migrate when touched
- [ ] `flk:alarm:lambda:error: true` in Globals
- [ ] `flk:alarm:lambda:concurrentExec` in Globals using `!FindInMap`
- [ ] `Mappings.ReservedConcurrentExecutions` defined for all environments
- [ ] `AuthpointLambdaLayer` always in Globals layers; `FolkloreDomainLambdaLayer` added where needed
