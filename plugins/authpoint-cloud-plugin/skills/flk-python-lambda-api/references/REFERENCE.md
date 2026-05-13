# Lambda API Reference

Detailed reference for Folklore API Lambda patterns. Read when implementing configuration classes, choosing the right layer class, or building adapters.

---

## 1. Layer Class → Port / Adapter Mapping

| Port interface | Adapter file | AuthpointLambdaLayer class | Import path |
|---------------|-------------|--------------------------|-------------|
| `Repository` (ABC) | `ddb_repository.py` | `DdbRepository` | `adapter.datasource.ddb_repository` |
| `Responder` (ABC) | `api_responder.py` | `HttpResponder` | `adapter.transport.http_responder` |
| `Invoker` (ABC) — API | `api_gateway_invoker.py` | `ApiGatewayInvoker` | `adapter.transport.api_gateway_invoker` |
| `Invoker` (ABC) — Lambda | `lambda_invoker.py` | `LambdaInvoker` | `adapter.transport.lambda_invoker` |
| `Publisher` (ABC) — SNS | `msg_sender.py` | `SnsPublisher` | `adapter.transport.sns_publisher` |
| `Producer` (ABC) — SQS | `sqs_producer.py` | `SqsProducer` | `adapter.transport.sqs_producer` |
| `Crypto` (ABC) | `comm_crypto.py` | `CommCrypto` | `adapter.transport.comm_crypto` |

**Event adapter** (not a port — used only in `app.py`):

| Trigger type | Layer class | Import path |
|-------------|-------------|-------------|
| JSON body (REST) | `HttpEvent` | `adapter.event.http_event` |

---

## 2. Configuration Class Templates

### HttpEventConfig (JSON body)

```python
from flk_api.api_config_helper import ApiEventConfig

class HttpEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = ApiEventConfig.API_EVENT_LOCATION_MAPPING | {
            'accountId': 'body.accountId',
            'login': 'body.username',
            'clientId': 'pathParameters.clientId',
            'state': 'queryStringParameters.state',
            'cookieHeader': 'headers.cookie',
        }
        self.data_auto_mapping = False
        self.dto_log_mapping = 'AccountId: {accountId}, Login: {login}'
```

**DTO location prefixes:**

| Prefix | Source |
|--------|--------|
| `body.field` | JSON request body |
| `pathParameters.field` | URL path parameter |
| `queryStringParameters.field` | Query string |
| `headers.field` | Request header |
| `requestContext.identity.sourceIp` | Source IP |

### ResponderConfig

```python
class ResponderConfig(BaseConfig):
    def __init__(self):
        self.allowed_origin = getenv('WGC_ALLOWED_ORIGIN')
```

### Repository Config

```python
class Environment:
    def __init__(self):
        self.aws_region = getenv('AWS_REGION')

class {Feature}RepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('{TABLE}_TABLE_NAME')
        self.partition_key_schema = ApiRepositoryConfig.{FEATURE}_REPOSITORY_PK
        self.sort_key_schema = ApiRepositoryConfig.{FEATURE}_REPOSITORY_SK   # optional
```

### SnsPublisherConfig

Used when the API Lambda publishes an event to an SNS topic (e.g. after a successful write).

```python
SOME_EVENT_KEY = 'someEvent'

class SnsPublisherConfig(BaseConfig):
    def __init__(self):
        self.topic_arn = getenv('DATA_TOPIC_ARN')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('MAIN_REGION')
        self.event_data_mappings = {
            SOME_EVENT_KEY: {
                'accountId': 'accountId',
                'entityId': 'entityId',
            }
        }
        self.message_group_id_schemas = {
            SOME_EVENT_KEY: {
                'type': 'join',
                'value': {'separator': '#', 'keys': ['accountId', 'entityId']}
            }
        }
        self.event_configs = {
            SOME_EVENT_KEY: {
                'eventType': SomeEventType.SOME_EVENT,
                'entityType': SomeEntityType.SOME_ENTITY,
                'dataMappingKey': SOME_EVENT_KEY,
                'messageGroupIdSchemaKey': SOME_EVENT_KEY,
            }
        }
```

### API Error Codes

```python
API_ERROR_CODES = {
    'paramName': {
        'code': '601003001',   # 6 (OIDC) + 01 (service) + 003 (API) + 001 (seq)
        'title': 'invalid_request',
        'detail': 'The request is missing paramName or it has an invalid value',
        'status': 400,
    },
    'internalServerError': {
        'code': '601003301',
        'title': 'server_error',
        'detail': 'Internal server error. Please contact support',
        'status': 500,
    },
}
```

---

## 3. Adapter Implementation Patterns

### DdbRepository adapter

```python
from adapter.datasource.ddb_repository import DdbRepository

class {Feature}Repository({Feature}RepositoryPort):
    def __init__(self, *, config: {Feature}RepositoryConfig, template_parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=template_parser)

    def get(self, *, dto: dict) -> dict:
        return self.repository.get_item(dto=dto)
```

### ApiResponder adapter

```python
from adapter.transport.http_responder import HttpResponder

class ApiResponder(ResponderPort):
    def __init__(self, *, config: ResponderConfig):
        self.responder = HttpResponder(config=config.as_dict)

    def success(self, *, dto: dict) -> dict:
        return self.responder.ok(dto=dto)

    def server_error(self, *, dto: dict) -> dict:
        return self.responder.internal_server_error(dto=dto)

    def invalid_request(self, *, param: str, dto: dict) -> dict:
        return self.responder.bad_request(param=param, dto=dto)
```

### LambdaInvoker adapter

```python
from adapter.transport.lambda_invoker import LambdaInvoker

class {Feature}Invoker({Feature}InvokerPort):
    def __init__(self, *, config: {Feature}InvokerConfig):
        self.invoker = LambdaInvoker(config=config.as_dict)

    def invoke(self, *, dto: dict) -> dict:
        result = self.invoker.invoke(dto=dto)
        return result if result else {}
```

**Invokers must return `{}` on error — never raise.**

---

## 4. Real Examples

Read these when the patterns above are ambiguous. Each file is a real, working example.

| Example | What it shows |
|---------|--------------|
| [oidc_discovery_api/oidc_discovery/domain/service.py](examples/oidc_discovery_api/oidc_discovery/domain/service.py) | `Service.process`, inline `EventValidator` with `REQUIRED_FIELDS`, `ValidationException` → `responder.invalid_request(param=ex.param, dto=dto)` |
| [oidc_discovery_api/oidc_discovery/adapter/db_repository.py](examples/oidc_discovery_api/oidc_discovery/adapter/db_repository.py) | Single-table `DdbRepository` adapter — `query_gsi_by_partition_key` |

---

## 5. Architectural Decisions

| Decision | Rule |
|----------|------|
| Domain exceptions | `ValidationException`, `ApiRequestHelperException` caught only in Service — never in `app.py` |
| Unexpected exceptions | Caught in `lambda_handler` → `responder.server_error(dto=dto)` |
| `dto = {}` | Always declared before `try` so error responses include `requestId` even when parsing fails |
| Config access | Always use `config.as_dict` when passing to layer classes — never pass the config object itself |
| Invoker errors | Return `{}` on error — never raise from an invoker |
