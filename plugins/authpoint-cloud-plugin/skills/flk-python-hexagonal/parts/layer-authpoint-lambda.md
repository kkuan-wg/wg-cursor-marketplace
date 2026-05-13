# Lambda Layer — authpoint-lambda-layer

The **authpoint-lambda-layer** provides shared adapters and utils used by port implementations. Understanding its behavior is essential when creating or reviewing adapters.

---

## 1. Role of authpoint-lambda-layer

| Responsibility | Description |
|----------------|-------------|
| **Adapters** | DdbRepository, HttpResponder, ApiGatewayInvoker, LambdaInvoker, SnsPublisher, SqsProducer, CommCrypto |
| **Event parsing** | HttpEvent, SqsEvent, DdbStreamEvent — convert events to DTO |
| **Utils** | DtoValidator, ValidationException, date_time_helper, sanitization_helper, fallback_helper |
| **Configuration** | BaseConfig, logger |

Local adapters delegate to these components. The authpoint-lambda-layer expects **config as dict** (keys in camelCase).

---

## 2. BaseConfig and snake_case → camelCase

Local configs use snake_case; the layer expects camelCase. Use `config.as_dict`:

```python
from configuration.base_config import BaseConfig

class DdbRepositoryConfig(BaseConfig):
    def __init__(self):
        self.table_name = getenv('TABLE_NAME')
        self.partition_key_schema = {...}

# In adapter:
self.repository = DdbRepository(config=config.as_dict, template_parser=parser)
```

`as_dict` converts attributes from snake_case to camelCase (`table_name` → `tableName`, `partition_key_schema` → `partitionKeySchema`).

---

## 3. Layer structure

```
lambda_layer/python/
├── adapter/
│   ├── datasource/          # DynamoDB, S3, RDS, Secrets Manager
│   │   ├── ddb_repository.py
│   │   ├── rds_repository.py
│   │   ├── s3_bucket.py
│   │   └── secrets_manager.py
│   ├── data_processing/
│   │   └── template_parser.py
│   ├── event/               # Event → DTO
│   │   ├── http_event.py
│   │   ├── sqs_event.py
│   │   ├── ddb_stream_event.py
│   │   ├── lambda_event.py
│   │   ├── log_event.py
│   │   └── util.py         # DtoDict (custom __str__)
│   ├── security/
│   │   ├── comm_crypto.py
│   │   ├── desktop_logon_crypto.py
│   │   ├── mobile_crypto.py
│   │   └── auth_legacy_sdk.py
│   └── transport/
│       ├── http_responder.py
│       ├── http_request.py
│       ├── api_gateway_invoker.py
│       ├── api_invoker.py
│       ├── lambda_invoker.py
│       ├── sns_publisher.py
│       ├── sns_push_notification_publisher.py
│       ├── sqs_producer.py
│       └── lambda_invocation_responder.py
├── configuration/
│   ├── base_config.py
│   ├── boto_config.py
│   └── logger.py
└── utils/
    ├── validation_helper.py   # DtoValidator, ValidationException
    ├── date_time_helper.py
    ├── sanitization_helper.py
    ├── fallback_helper.py
    ├── file_helper.py
    └── jwt_helper.py
```

---

## 4. Component reference

### 4.1 DdbRepository

```python
from adapter.datasource.ddb_repository import DdbRepository
```

Config keys (camelCase): `tableName` (mandatory), `partitionKeyName`, `partitionKeySchema`, `sortKeyName`, `sortKeySchema`, `gsiSchema`, `modelMappings`, `ttlAttributeName`, `ttlDelayInSeconds`, `connectTimeout`, `readTimeout`, `maxAttempts`, `crossAccountRoleArn`.

| Method | Description |
|--------|-------------|
| `get_item_by_partition_key(*, dto, include_soft_deleted, consistent_read, partition_key)` | Get single item by PK |
| `get_item_by_partition_and_sort_key(*, dto, include_soft_deleted, consistent_read, partition_key, sort_key)` | Get single item by PK + SK |
| `query_by_partition_key(*, dto, projection_expression, consistent_read, include_soft_deleted, partition_key, grouping_map_key)` | Query by PK |
| `query_by_partition_and_sort_key_begins_with(*, dto, ...)` | Query by PK + SK begins_with |
| `query_by_partition_and_sort_key_greater_than(*, dto, sort_key, ...)` | Query by PK + SK > value |
| `query_gsi_by_partition_key(*, index_name, dto, include_soft_deleted, grouping_map_key, ...)` | Query GSI by partition key |
| `query_gsi_by_partition_and_sort_key_begins_with(*, index_name, dto, ...)` | Query GSI by PK + SK begins_with |
| `query_gsi_by_partition_and_sort_key_equals(*, index_name, dto, ...)` | Query GSI by PK + SK equals |
| `save_item(*, dto, model_mappings_entity_key, partition_key, sort_key)` | Put item (full write) |
| `update_item(*, dto, model_mappings_entity_key, partition_key, sort_key)` | Partial update |
| `soft_delete_item(*, dto, model_mappings_entity_key, partition_key, sort_key)` | Update with TTL (soft delete) |
| `delete_item(*, dto, partition_key, sort_key)` | Hard delete |
| `save_batch(*, items)` | Batch write |
| `delete_batch(*, items, key_filter, list_filter)` | Batch delete |

Key parameters:
- `include_soft_deleted` (bool, default `False`) — includes soft-deleted items in results
- `grouping_map_key` — groups query results by type using `modelMappings`; returns `dict` instead of `list`
- `model_mappings_entity_key` — key in `modelMappings` config used to parse the DDB item for writes

### 4.2 HttpResponder

```python
from adapter.transport.http_responder import HttpResponder
```

Config keys: `allowedOrigin` (mandatory), `exposeHeaders` (optional, default `'Request-Id'`).

| Method | Description |
|--------|-------------|
| `build_success_response(*, status_code=200, body, custom_headers, request_id)` | Standard success response |
| `build_standard_error_response(*, error, custom_headers, request_id)` | Error from `API_ERROR_CODES` map |
| `build_custom_error_response(*, error, custom_headers, request_id)` | Custom error (no standard enforced) |

`build_standard_error_response` expects `error` dict with keys: `title`, `detail`, `status`, `code` — matches the `API_ERROR_CODES` format defined in `configuration.py`.

`build_custom_error_response` only requires `statusCode` in the error dict; use only when the standard format cannot be applied.

### 4.3 Event adapters

All event adapters return a `DtoDict` — safe to log with `logging.info(f'{dto}')`.

**HttpEvent**

```python
from adapter.event.http_event import HttpEvent
```

Config keys: `dtoMapping` (mandatory), `dtoLogMapping`, `preserveRawHeaders`, `dataSanitizeEnabled`, `dataSanitizeWhitelistFields`, `dataSanitizePatterns`.

- `as_dto(*, event)` — alias for `get_event_dto`; use this in `app.py`
- `get_event_dto(*, event)` — same as `as_dto`; use when the adapter is injected and called internally

Base DTO fields always populated: `requestId`, `extendedRequestId`, `httpMethod`, `accountId` (from path param), `authorizerToken` (from authorizer context).

**SqsEvent**

```python
from adapter.event.sqs_event import SqsEvent
```

Config keys: `dtoMapping`, `dtoLogMapping`, `maxConsumeTimeout` (int, seconds).

- `as_dto(*, event)` — processes `event['Records'][0]`; returns `DtoDict`
- When `maxConsumeTimeout` is set, adds `eventExpired: bool` to the DTO based on the event timestamp

Base DTO fields always populated: `eventType`, `entityType`, `entityId`, `accountId`, `source`, `data`, `messageId`, `timestamp`.

**DdbStreamEvent**

```python
from adapter.event.ddb_stream_event import DdbStreamEvent
```

Config keys: `dtoMapping`, `dtoLogMapping`.

- `as_dto(*, event)` — processes `event['Records'][0]`; returns `DtoDict`
- Default DTO fields: `newImage`, `oldImage`, `keys`, `eventType`, `eventId`
- If `dtoMapping` is provided, the default DTO is further parsed through `TemplateParser`

### 4.4 ApiGatewayInvoker

```python
from adapter.transport.api_gateway_invoker import ApiGatewayInvoker
```

Config keys: `awsRegion` (mandatory), `apiConfigs` (mandatory), `urlMappings` (mandatory), `headersMappings`, `paramsMappings`, `requestDataMappings`, `responseDataMappings`, `connectTimeout`, `readTimeout`, `maxAttempts`, `crossAccountRoleArn`.

- `build_request(*, dto, config_key)` — builds the request dict (method, url, headers, params, data)
- Signing via SigV4 is handled internally

### 4.5 LambdaInvoker

```python
from adapter.transport.lambda_invoker import LambdaInvoker
```

Config keys: `awsRegion` (mandatory), `functionName` (mandatory), `source` (mandatory), `invocationType` (mandatory: `'RequestResponse'` or `'Event'`), `dataMapping`, `connectTimeout`, `readTimeout`, `maxAttempts`.

| Method | Description |
|--------|-------------|
| `invoke_lambda(*, event_type, entity_type, data=None)` | Invokes Lambda with standard envelope |

Response:
- `RequestResponse` (sync): returns payload dict merged with `requestId`
- `Event` (async): returns `{'status': <http_status>, 'requestId': <id>}`

### 4.6 SnsPublisher

```python
from adapter.transport.sns_publisher import SnsPublisher
```

Config keys: `awsRegion` (mandatory), `topicArn` (mandatory), `source` (mandatory), `eventConfigs` (mandatory), `eventDataMappings` (mandatory), `messageAttributesMappings`, `messageGroupIdSchemas`, `connectTimeout`, `readTimeout`, `maxAttempts`.

| Method | Description |
|--------|-------------|
| `publish_data_as_message(*, data, event_key)` | Publishes parsed data directly as message body — no envelope |
| `publish_data_as_obj(*, data, event_key, account_id, entity_id)` | Publishes data inside standard AuthPoint envelope with default MessageAttributes |
| `publish_data_as_str(*, data, event_key, account_id, entity_id)` | Publishes stringified data inside standard envelope with default MessageAttributes |

Use `publish_data_as_obj` or `publish_data_as_str` for standard AuthPoint events. Use `publish_data_as_message` only when publishing raw data without an envelope.

### 4.7 SqsProducer

```python
from adapter.transport.sqs_producer import SqsProducer
```

Config keys: `awsRegion` (mandatory), `queueUrl` (mandatory), `source` (mandatory), `messageConfigs` (mandatory), `dataMappings` (mandatory), `messageGroupIdSchemas`, `sessionDuration`, `crossAccountRoleArn`.

| Method | Description |
|--------|-------------|
| `send_data_as_str(*, data, message_key, entity_id, account_id)` | Sends stringified data inside standard envelope |
| `send_data_as_obj(*, data, message_key, entity_id, account_id)` | Sends data as object inside standard envelope |

Both methods accept optional `entity_id` and `account_id` added to the message envelope.

### 4.8 CommCrypto

```python
from adapter.security.comm_crypto import CommCrypto
```

Config keys: `cryptoKeySchema`, `encryptAttributeName` (default `'data'`), `decryptAttributeName` (default `'data'`), `accountIdAttributeName` (default `'accountId'`), `agentIdAttributeName` (default `'agentId'`), `integrationKeyAttributeName` (default `'integrationKey'`).

| Method | Description |
|--------|-------------|
| `encrypt(*, dto, crypto_key, decrypted_data)` | Encrypt with explicit key |
| `encrypt_agent(*, dto, account_id, agent_id, integration_key, decrypted_data)` | Encrypt using agent key derivation |
| `decrypt(*, dto, crypto_key, encrypted_data)` | Decrypt with explicit key |
| `decrypt_agent(*, dto, account_id, agent_id, integration_key, encrypted_data)` | Decrypt using agent key derivation |

> **Note:** CommCrypto is only compatible with `x86_64` architecture. The Lambda function must specify `Architectures: [x86_64]`.

---

## 5. Config in camelCase

The layer expects keys in camelCase. Examples:

| snake_case (local) | camelCase (layer) |
|--------------------|-------------------|
| `table_name` | `tableName` |
| `partition_key_schema` | `partitionKeySchema` |
| `dto_mapping` | `dtoMapping` |
| `dto_log_mapping` | `dtoLogMapping` |
| `topic_arn` | `topicArn` |
| `event_configs` | `eventConfigs` |
| `queue_url` | `queueUrl` |
| `gsi_schema` | `gsiSchema` |
| `model_mappings` | `modelMappings` |
| `function_name` | `functionName` |
| `invocation_type` | `invocationType` |

---

## 6. DtoDict and dto_log_mapping

Event adapters return `DtoDict(source_dict=..., dto_log_mapping=...)`:

```python
from adapter.event.util import DtoDict

return DtoDict(source_dict=event_dto, dto_log_mapping=self._get_log_mapping())
```

`DtoDict` overrides `__str__` to log only the fields defined in `dto_log_mapping`. That is why `logging.info(f'{dto}')` is allowed — it does not expose sensitive data.

---

## 7. TemplateParser

Used by events, DdbRepository, SnsPublisher, SqsProducer, ApiGatewayInvoker. Parses payloads based on `payload_map` / `dto_mapping`:

| Method | Description |
|--------|-------------|
| `parse_item(*, item, payload_map)` | Parses a single item using a `type: dict` mapping |
| `parse_collection_item(*, item, payload_maps)` | Parses a collection using a list of mappings |
| `parse_payload(*, item, payload_map)` | Parses a payload dict recursively |
| `parse_list_to_grouped_items(*, items, grouping_map)` | Groups a list of items by type using a grouping map |
| `get_item_value(*, keys, item)` | Gets a value by dot-separated path (e.g. `'header.resourceId'`) |

---

## 8. Logger

```python
from configuration.logger import initialize_logging_session, set_context, reset_logging_context
```

| Function | When to call | Description |
|----------|-------------|-------------|
| `initialize_logging_session(service_name)` | `app.py`, once at cold start | Sets up log formatter, level, and suppresses noisy loggers |
| `set_context(*, dto, custom_fields)` | After parsing the event DTO | Adds `requestId` or `messageId` (and optionally `accountId`, `chainId`, custom fields) to all subsequent log lines |
| `reset_logging_context()` | After processing, in `finally` block | Clears all context fields |

`set_context` requires the DTO to contain `requestId`, `messageId`, or `eventId` — raises `ValueError` otherwise.

```python
# app.py pattern
initialize_logging_session(service_name='my-service')

dto = event_adapter.as_dto(event=event)
set_context(dto=dto, custom_fields={'transaction_id': dto.get('transactionId')})
try:
    result = service.process(dto=dto)
finally:
    reset_logging_context()
```

---

## 9. Utils

### DtoValidator

```python
from utils.validation_helper import DtoValidator, ValidationException
```

```python
validator = DtoValidator()
validator.validate_required_fields(dto=dto, required_fields={
    'accountId': str,
    'clientId': {'type': str, 'minLength': 5, 'maxLength': 100},
    'wifId': int,
    'resourceId': {'type': int, 'minValue': 1},
    'otp': {'type': str, 'pattern': VALIDATION_OTP_PATTERN}
})
```

Raises `ValidationException(param=<field_name>)` on the first invalid field. `ValidationException.__str__` returns `'Invalid <param>'`.

Constructor parameters: `string_min_length` (default 1), `string_max_length` (default 255), `int_min_value` (default 0), `int_max_value` (default inf).

### date_time_helper

```python
from utils.date_time_helper import (
    get_current_utc_timestamp_in_millis,
    get_current_utc_timestamp_in_seconds,
    is_item_expired,
    is_request_expired
)
```

| Function | Description |
|----------|-------------|
| `get_current_utc_timestamp_in_millis()` | Current UTC timestamp in milliseconds |
| `get_current_utc_timestamp_in_seconds()` | Current UTC timestamp in seconds |
| `is_item_expired(*, item, custom_key='expirationTimeInMillis')` | True if `item[custom_key] < now_millis` |
| `is_request_expired(*, item, duration_in_millis, custom_key='timestampInMillis')` | True if `item[custom_key] + duration < now_millis` |

### fallback_helper

```python
from utils.fallback_helper import execute_with_fallback
```

Executes `primary(**kwargs)`. If primary fails (AWS or non-AWS error), logs the error and executes `fallback(**kwargs)`. If fallback also fails, the fallback exception is propagated.

```python
result = execute_with_fallback(
    primary=self.primary_publisher.publish_data_as_obj,
    fallback=self.fallback_producer.send_data_as_obj,
    account_id=dto.get('accountId'),
    data=dto,
    event_key='USER_CREATED'
)
```

Parameters: `primary` (callable), `fallback` (callable), `account_id` (optional, for log context), `user_id` (optional, for log context), `**kwargs` (passed to both functions).

---

## 10. Checklist

- [ ] Use `config.as_dict` when passing config to the layer
- [ ] Local configs in snake_case; layer receives camelCase via `as_dict`
- [ ] Inject `TemplateParser` where the layer requires it (`template_parser=parser`)
- [ ] DTOs returned by event adapters are `DtoDict` — `logging.info(f'{dto}')` is safe
- [ ] Use `build_standard_error_response` with `API_ERROR_CODES`; `build_custom_error_response` only as exception
- [ ] `SnsPublisher`: use `publish_data_as_obj` or `publish_data_as_str` for standard AuthPoint events
- [ ] `SqsProducer`: choose `send_data_as_str` vs `send_data_as_obj` based on consumer expectation
- [ ] `LambdaInvoker`: set `invocationType` to `RequestResponse` (sync) or `Event` (async)
- [ ] `CommCrypto`: Lambda must use `Architectures: [x86_64]`
- [ ] `set_context` requires `requestId`, `messageId`, or `eventId` in the DTO
- [ ] Call `reset_logging_context()` in `finally` block after processing
- [ ] Utils (DtoValidator, date_time_helper, etc.) come from authpoint-lambda-layer
