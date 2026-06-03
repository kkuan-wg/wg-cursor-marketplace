# Guardrail Checklist

Apply before creating or modifying each class.

| Origin | Document | Role |
|--------|----------|------|
| Target repo `.cursor/rules/` | `java-package-map.mdc` | **where** |
| Target repo `.cursor/rules/` | `java-design-patterns.mdc` | **how** |
| **authpoint-cloud-plugin** `rules/` | [`java-spring-properties-injection.mdc`](../../../rules/java-spring-properties-injection.mdc) | **properties triad** |

## Before any implementation (authpt-java-code-impl Phase 2)

**Stop** if Phase 2 is incomplete — read entirely, then apply on every artifact:

- [ ] `.cursor/rules/java-package-map.mdc` (where)
- [ ] `.cursor/rules/java-design-patterns.mdc` (how)
- [ ] Plugin [`java-spring-properties-injection.mdc`](../../../rules/java-spring-properties-injection.mdc) (property triad)
- [ ] Skim `java-properties-registry.md` when present in the target repo

## Per artifact type

| Artifact | Allowed package | Suffix | Must do | Must not |
|----------|-----------------|--------|---------|----------|
| REST endpoint | `api/{dominio}/controller` | `*Controller` | Delegate to service; use `ApiConstants` for paths | Business logic; RBAC in controller |
| API service | `api/{dominio}/service` | `*Service` | Orchestrate validation, persistence, publisher, audit | Direct HTTP concerns |
| Request validator | `api/{dominio}/service` | `*RequestValidator` | Spring `Validator` + `@InitBinder` | Persistence calls |
| Data validator | `api/{dominio}/service` | `*DataValidator` | Post-mapping business rules | HTTP binding |
| DTO builder | `api/{dominio}/service` | `*Builder` | Request ↔ DTO ↔ Entity ↔ Response | Side effects |
| API DTO | `api/{dominio}/model` | `*Request`, `*Response`, `*Dto` | Lombok POJOs | JPA annotations |
| API exception | `api/{dominio}/exception` | `*ApiException`, `*ApiError` | Typed errors | Generic RuntimeException |
| Exception handler | `api/{dominio}/exception` | `*ExceptionHandler` | Extend `BaseExceptionHandler` | Catch-all without domain scope |
| SQS listener | `cache/{dominio}/` | `*Listener`, `*CacheListener` | `@SqsListener`, MDC, route by event | Business logic (delegate to handler) |
| SQS parser (inbound) | `cache/{dominio}/` | `*Parser`, `*CacheParser` | JSON → object | Persistence writes |
| Cache builder | `cache/{dominio}/` | `*Builder`, `*CacheBuilder` | Payload → DTO → entity | Repository calls |
| Cache handler | `cache/{dominio}/` | `*Handler`, `*CacheHandler` | CRUD via repository; optimistic locking | HTTP or SNS publish orchestration |
| JPA entity | `persistence/aurora/{dominio}/model` | entity name | `@Entity`, domain methods | Import from `api` or `cache` |
| JPA repository | `persistence/aurora/{dominio}/repository` | `*Repository` | `extends JpaRepository` | Import from `api` or `cache` |
| Dynamo entity | `persistence/dynamo/{dominio}/model` | entity name | `@DynamoDBTable` | Import from `api` or `cache` |
| Dynamo repository | `persistence/dynamo/{dominio}/repository` | `*Repository`, `*RepositoryImpl` | Interface + `@Service` impl | Import from `api` or `cache` |
| SNS publisher | `publisher/{dominio}/` | `*Publisher` | Build + serialize + publish with retry | Business orchestration |
| Publisher builder | `publisher/{dominio}/` | `*Builder`, `*PayloadBuilder` | Entity → messaging payload | Repository queries |
| Publisher parser | `publisher/{dominio}/` | `*Parser`, `*PublisherParse` | Object → JSON (outbound) | Inbound deserialization |
| SQS sender | `sender/{dominio}/` | `*Sender` | `SqsClient.sendMessage` | Business logic |
| Spring config | `configuration/cloud` or `local/` | `*Config` | `@Bean` factory, `@Profile`, `@Value` keys declared in `application.properties` and `run.sh` when deploy overrides | Business logic; hardcoded ARNs/queue names |
| Audit helper | `audit/` | `{Domain}AuditHelper` | Extend `BaseAudit` | Direct controller calls |
| Shared helper | `helper/{dominio}/` | `{Domain}Helper` | Cross-domain orchestration | HTTP adapters |
| Transaction listener | `transaction/` | `TransactionListener` | Dispatch by subType | Domain-specific API logic |
| Transaction handler | `transaction/handler/` | `*TransactionHandler` | Extend `TransactionHandlerBase` | REST endpoints |

## Dependency guardrails

| From | May import | Must not import |
|------|------------|-----------------|
| `api.*` | `persistence`, `publisher`, `helper`, `audit` | — |
| `cache.*` | `persistence`, `publisher`, `transaction`, `audit` | `api.*` |
| `persistence.*` | `helper.*` (limited) | `api.*`, `cache.*`, `publisher.*` |
| `publisher.*` | persistence models, api DTOs, SNS config | `cache.*`, service logic |
| `configuration.*` | Spring/AWS SDK | business packages |

## Parser direction

| Direction | Packages | Parser role |
|-----------|----------|-------------|
| Inbound | `cache/`, `transaction/`, `timeout/` | Deserialize SQS message JSON → object |
| Outbound | `publisher/`, `sender/` | Serialize object → JSON for SNS/SQS |

## Properties triad

Source: **authpoint-cloud-plugin** [`rules/java-spring-properties-injection.mdc`](../../../rules/java-spring-properties-injection.mdc) — load in Phase 2 (mandatory gate); apply the checklist below when the task touches external config.

- [ ] Key declared in `src/main/resources/application.properties` (cloud + `local.*` mirror if applicable)
- [ ] `scripts/run.sh` passes `--key=$ENV` on deploy branch when value comes from container
- [ ] Same literal key in `@Value` or `@SqsListener("${...}")` / queue constant placeholder
- [ ] Config class in `configuration/{cloud|local|test}/` with matching `@Profile`
- [ ] Consumers use beans or property placeholders — not literal queue/topic/endpoint strings

## Per-task mini-checklist

Before marking a `code-tasks.md` item done:

- [ ] Class name suffix matches design patterns rule
- [ ] Package path matches package map rule
- [ ] No forbidden imports (see dependency table)
- [ ] Sibling reference pattern followed
- [ ] Requirement/scenario from spec is satisfied
- [ ] Properties triad satisfied when task adds/changes AWS or datasource keys
