# SQS Consumer Reference

Detailed reference for Folklore SQS consumer Lambda code patterns. Read when implementing configuration classes or building adapters.

---

## 1. Layer Class → Port / Adapter Mapping

| Port interface | Adapter file | AuthpointLambdaLayer class | Import path |
|---------------|-------------|--------------------------|-------------|
| `Repository` (ABC) | `ddb_repository.py` | `DdbRepository` | `adapter.datasource.ddb_repository` |

**Event adapter** (not a port — used only in `app.py`):

| Trigger | Layer class | Import path |
|---------|-------------|-------------|
| SQS queue | `SqsEvent` | `adapter.event.sqs_event` |

---

## 2. Configuration Patterns

### SqsEventConfig

```python
class SqsEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'data.accountId',
            'entityType': 'entityType',
            'eventType': 'eventType',
            'resourceTypes': 'resourceTypes',
            'lastUpdatedOn': 'data.lastUpdatedOn',
        }
        self.data_auto_mapping = False
        self.dto_log_mapping = 'AccountId: {accountId}, EntityType: {entityType}, EventType: {eventType}'
```

`SqsEvent.as_dto(event=event)` handles SQS batch records internally — `app.py` passes the whole Lambda `event` once; there is **no manual loop over `Records`** in application code.

**DTO mapping sources for SQS events** (dot-notation paths into the unwrapped SQS message body):

| Field | Typical path |
|-------|-------------|
| Top-level envelope field | `'entityType'`, `'eventType'` |
| Nested data field | `'data.accountId'`, `'data.userId'` |
| List / resource types | `'resourceTypes'` |

---

### DdbRepositoryConfig

One config class per DynamoDB table the adapter touches. Always inherits from both `Environment` and `BaseConfig`.

```python
DB_USER_ENTITY = 'user_entity'
DB_USER_GROUP_ENTITY = 'user_group_entity'

class DdbRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('MY_TABLE_NAME')
        self.partition_key_schema = {
            'type': 'join',
            'value': {
                'separator': '#',
                'keys': [{'type': 'hardcoded', 'value': 'USER'}, 'entityId']
            }
        }
        # sort_key_schema and gsi_schema are optional — include only when needed
        self.model_mappings = {
            DB_USER_ENTITY: {
                'userId': 'entityId',
                'accountId': 'accountId',
                'status': 'userStatus',
                'lastUpdatedOn': 'lastUpdatedOn',
            },
            DB_USER_GROUP_ENTITY: {
                'groups': 'groups',
            },
        }
        # TTL for soft-delete — include only when soft-delete is required
        self.ttl_attribute_name = 'softDeletedTtl'
        self.ttl_delay_in_seconds = 300
```

**`model_mappings` key format:** `{ddb_attribute_name}: {dto_field_name}`. The layer reads from the DTO and writes the mapped attribute name to DynamoDB.

**`DdbRepository` write methods — choose the right one:**

| Method | When to use |
|--------|-------------|
| `save_item(dto, model_mappings_entity_key)` | Full item create/overwrite (`PutItem`) — idempotent |
| `update_item(dto, model_mappings_entity_key)` | Partial attribute update (`UpdateItem`) — touches only mapped fields |
| `soft_delete_item(dto, model_mappings_entity_key)` | Sets `ttl_attribute_name = now + ttl_delay_in_seconds` via `UpdateItem` |

**`DdbRepository` read methods:**

| Method | When to use |
|--------|-------------|
| `get_item_by_partition_key(dto)` | Single item by PK |
| `query_gsi_by_partition_key(dto, index_name, include_soft_deleted)` | Query a GSI |

---

## 3. Real Examples

Read these when the patterns above are ambiguous. Each file is a real, working example.

| Example | What it shows |
|---------|--------------|
| [core_data_cache_consumer_fn/core_data_cache_consumer/configuration.py](examples/core_data_cache_consumer_fn/core_data_cache_consumer/configuration.py) | `FUNCTION_NAME`, `SqsEventConfig`, multiple `DdbRepositoryConfig` classes sharing the same table — `partition_key_schema`, `sort_key_schema` with hardcoded join, shared `_BASE_CORE_ENTITY` mapping, `ttl_attribute_name` |
| [core_data_cache_consumer_fn/core_data_cache_consumer/domain/service.py](examples/core_data_cache_consumer_fn/core_data_cache_consumer/domain/service.py) | `Service.process`, `entityType`/`eventType` routing, `ValidationException` discard, inner `EventValidator` with `VALID_EVENT_TYPES` + `REQUIRED_FIELDS` |
| [core_data_cache_consumer_fn/core_data_cache_consumer/adapter/ddb_repository.py](examples/core_data_cache_consumer_fn/core_data_cache_consumer/adapter/ddb_repository.py) | Multi-config `DynamoDbRepository` — three separate `DdbRepository` instances, `save_item`, `soft_delete_item` |

---

## 4. Architectural Decisions

| Decision | Rule |
|----------|------|
| `ValidationException` | Caught only in `domain/service.py`; log and return (discard the record). Never in `app.py`. |
| Other exceptions | `app.py` logs and **re-raises** (`raise ex`) so the record is retried / sent to DLQ |
| Config access | Always use `config.as_dict` when passing to layer classes |
| SQS batch iteration | **No manual `Records` loop in `app.py`** — `SqsEvent.as_dto(event=event)` handles batching internally |
| No `dto = {}` | Consumers do not return values; initializing `dto = {}` is not needed |
