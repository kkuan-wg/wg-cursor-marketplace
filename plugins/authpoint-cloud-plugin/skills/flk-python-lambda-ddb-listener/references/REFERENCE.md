# DDB Stream Listener Reference

Detailed reference for Folklore DynamoDB stream listener Lambda code patterns. Read when implementing configuration classes, choosing SNS publishing style, or building adapters.

---

## 1. Layer Class → Port / Adapter Mapping

| Port interface | Adapter file | AuthpointLambdaLayer class | Import path |
|---------------|-------------|--------------------------|-------------|
| `Publisher` (ABC) | `sns_publisher.py` | `SnsPublisher` | `adapter.transport.sns_publisher` |
| `Producer` (ABC) | `sqs_producer.py` | `SqsProducer` | `adapter.transport.sqs_producer` |

**Event adapter** (not a port — used only in `app.py`):

| Trigger | Layer class | Import path |
|---------|-------------|-------------|
| DynamoDB stream | `DdbStreamEvent` | `adapter.event.ddb_stream_event` |

**Fallback helper:**

| Utility | Import path |
|---------|-------------|
| `execute_with_fallback` | `utils.fallback_helper` |

---

## 2. Configuration Patterns

### DdbStreamEventConfig

```python
class DdbStreamEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': {'type': 'first_not_none', 'values': ['newImage.accountId', 'oldImage.accountId']},
            'credentialType': 'newImage.credentialType',
            'userId': {'type': 'int', 'value': 'newImage.userId'},
            'isActive': {'type': 'hardcoded', 'value': False},
            'score': {'type': 'expression', 'value': 'newImage.score', 'expression': 'int(value) if value else None'},
        }
        self.dto_log_mapping = 'AccountId: {accountId}, CredentialType: {credentialType}'
```

**DTO mapping types:**

| Type | When to use | Example |
|------|-------------|---------|
| Direct string | Simple field from stream image | `'newImage.fieldName'` |
| `first_not_none` | Field exists in new or old image | `{'type': 'first_not_none', 'values': ['newImage.x', 'oldImage.x']}` |
| `hardcoded` | Constant value regardless of stream | `{'type': 'hardcoded', 'value': False}` |
| `int` | Cast string field to int | `{'type': 'int', 'value': 'newImage.count'}` |
| `expression` | Custom transform | `{'type': 'expression', 'value': 'newImage.x', 'expression': 'int(value) if value else None'}` |

`DdbStreamEvent` automatically adds `eventType` from the stream `eventName` (INSERT → `INSERT`, MODIFY → `MODIFY`, REMOVE → `REMOVE`).

---

### SnsPublishConfig — Credential-style

Use when the publish method receives an explicit `event_type` argument. Each entry in `event_configs` defines only `entityType`, `dataMappingKey`, and `messageGroupIdSchemaKey`.

```python
CORE_USER_STATUS_UPDATED_KEY = 'coreUserStatusUpdated'

class SnsPublishConfig(BaseConfig):
    def __init__(self):
        self.topic_arn = getenv('DATA_TOPIC_ARN')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('MAIN_REGION')
        self.event_data_mappings = {
            CORE_USER_STATUS_UPDATED_KEY: {
                'accountId': 'accountId',
                'userId': 'userId',
                'credentialType': 'credentialType',
            }
        }
        self.message_group_id_schemas = {
            CREDENTIALS_ENTITY_KEY: CoreEventConfig.CREDENTIALS_MESSAGE_GROUP_ID_SCHEMA,
        }
        self.event_configs = {
            CORE_USER_STATUS_UPDATED_KEY: {
                'entityType': CoreCredentialEntityType.CREDENTIAL,
                'dataMappingKey': CORE_USER_STATUS_UPDATED_KEY,
                'messageGroupIdSchemaKey': CREDENTIALS_ENTITY_KEY,
            }
        }
```

**Adapter call (credential-style):**

```python
payload = self.sns_publisher.build_message_payload_with_str_data(
    dto=dto,
    event_key=CORE_USER_STATUS_UPDATED_KEY,
    event_type=CoreCredentialDataEventType.CORE_USER_STATUS_UPDATED,
)
self._publish(dto=dto, message_payload_kwargs=payload)
```

---

### SnsPublishConfig — Transaction-style

Use when `event_configs` already contains `eventType`. The adapter passes only `event_key`.

```python
PUSH_TX_DONE_KEY = 'pushTxDone'

class SnsPublishConfig(BaseConfig):
    def __init__(self):
        self.topic_arn = getenv('DATA_TOPIC_ARN')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('MAIN_REGION')
        self.event_data_mappings = {
            PUSH_TX_DONE_KEY: {
                'accountId': 'accountId',
                'transactionId': 'transactionId',
            }
        }
        self.message_group_id_schemas = {
            TX_ENTITY_KEY: CoreEventConfig.TX_MESSAGE_GROUP_ID_SCHEMA,
        }
        self.event_configs = {
            PUSH_TX_DONE_KEY: {
                'eventType': CoreRequestEventType.PUSH_TX_DONE,
                'entityType': CoreTxEntityType.PUSH_TX,
                'dataMappingKey': PUSH_TX_DONE_KEY,
                'messageGroupIdSchemaKey': TX_ENTITY_KEY,
            }
        }
```

**Adapter call (transaction-style):**

```python
payload = self.sns_publisher.build_message_payload_with_str_data(dto=dto, event_key=PUSH_TX_DONE_KEY)
self._publish(dto=dto, message_payload_kwargs=payload)
```

---

### SqsProducerConfig (fallback only)

```python
class SqsProducerConfig(BaseConfig):
    def __init__(self):
        self.queue_url = getenv('EVENT_REPLAY_QUEUE_URL')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('MAIN_REGION')
        self.data_mappings = {
            CORE_USER_STATUS_UPDATED_KEY: {
                'accountId': 'accountId',
                'credentialType': 'credentialType',
            }
        }
        self.message_configs = {
            CORE_USER_STATUS_UPDATED_KEY: {
                'entityType': CoreCredentialEntityType.CREDENTIAL,
                'dataMappingKey': CORE_USER_STATUS_UPDATED_KEY,
            }
        }
```

**Adapter call (SQS uses `message_key`, not `event_key`):**

```python
payload = self.sqs_producer.build_message_payload_with_str_data(
    dto=dto,
    message_key=CORE_USER_STATUS_UPDATED_KEY,
)
self._send(dto=dto, message_payload_kwargs=payload)
```

---

## 3. Fallback Pattern

```python
from utils.fallback_helper import execute_with_fallback

# In domain/service.py
execute_with_fallback(
    dto=dto,
    primary=self.publisher.publish_user_status_updated,
    fallback=self.producer.send_user_status_updated,
)
```

`execute_with_fallback` calls `primary`; if it raises, calls `fallback`. Both must accept `*, dto: dict`.

---

## 4. Adapter Class Bodies

The patterns below show how a port method calls the layer. These are the only two shapes that exist — pick the one that matches the payload style.

### SNS publisher adapter (`build_message_payload_with_str_data`)

Use when the data payload must be serialised to a JSON string (most publish cases).

```python
from adapter.transport.sns_publisher import SnsPublisher as SnsPublisherLayer
from {module_name}.port.publisher import Publisher

class SnsPublisher(Publisher):

    def __init__(self, *, config: SnsPublishConfig, template_parser: TemplateParser):
        self.sns_publisher = SnsPublisherLayer(config=config.as_dict, template_parser=template_parser)

    def publish_something(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_str_data(
            data=dto,
            event_key=SOMETHING_KEY,
            entity_id=dto['entityId'],   # used for deduplication / message group id
        )
        self._publish(dto=dto, message_payload_kwargs=kwargs)

    def _publish(self, *, dto: dict, message_payload_kwargs: dict):
        logging.debug(f'Message built: {message_payload_kwargs}')
        response = self.sns_publisher.publish_message(message_payload_kwargs=message_payload_kwargs)
        logging.info(f'Message published. MessageId: {response.get("MessageId")}, AccountId: {dto["accountId"]}.')
```

### SQS producer adapter (`build_message_payload_with_obj_data`)

Use for the SQS fallback — data is sent as a structured object (not serialised to string).

```python
from adapter.transport.sqs_producer import SqsProducer as SqsProducerLayer
from {module_name}.port.producer import Producer

class SqsProducer(Producer):

    def __init__(self, *, config: SqsProducerConfig, template_parser: TemplateParser):
        self.sqs_producer = SqsProducerLayer(config=config.as_dict, template_parser=template_parser)

    def send_something(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto,
            message_key=SOMETHING_KEY,
        )
        self._send(dto=dto, message_payload_kwargs=kwargs)

    def _send(self, *, dto: dict, message_payload_kwargs: dict):
        logging.debug(f'Message built: {message_payload_kwargs}')
        response = self.sqs_producer.send_message(message_payload_kwargs=message_payload_kwargs)
        logging.info(f'Message sent. MessageId: {response.get("MessageId")}, AccountId: {dto.get("accountId")}.')
```

> `build_message_payload_with_str_data` → SNS (serialises data to JSON string)  
> `build_message_payload_with_obj_data` → SQS (sends data as object)

---

## 5. Real Examples

Read these when the patterns above are ambiguous. Each file is a real, working example.

| Example | What it shows |
|---------|--------------|
| [examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/configuration.py](examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/configuration.py) | DDB stream listener — `DdbStreamEventConfig`, `DdbRepositoryConfig` with `model_mappings`, `SqsProducerConfig` with `message_group_id_schemas` and multiple `message_configs`, `SnsPublishConfig` (transaction-style) |
| [examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/domain/service.py](examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/domain/service.py) | `Service.process` routing on `INSERT`/`MODIFY`/`REMOVE` stream `eventType`; soft-delete detection via `softDeletedTtl` |
| [examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/adapter/sns_publisher.py](examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/adapter/sns_publisher.py) | SNS publisher adapter — `build_message_payload_with_str_data`, `_publish` pattern |
| [examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/adapter/sqs_producer.py](examples/oidc_authn_context_listener_fn/oidc_authn_context_listener/adapter/sqs_producer.py) | SQS producer adapter — `build_message_payload_with_obj_data`, `_send` pattern, multiple send methods |

---

## 6. Architectural Decisions

| Decision | Rule |
|----------|------|
| `ValidationException` | Caught only in `domain/service.py`; log and return (discard the record). Never in `app.py`. |
| Other exceptions | `app.py` logs and **re-raises** (`raise ex`) so the record is retried / routed to DLQ |
| Config access | Always use `config.as_dict` when passing to layer classes |
| SNS vs SQS key | SNS uses `event_key`; SQS uses `message_key` in `build_message_payload_with_str_data` |
| Credential-style SNS | Pass `event_type` explicitly; `event_configs` define `entityType` only |
| Transaction-style SNS | Pass `event_key` only; `event_configs` define `eventType` + `entityType` |
| Fallback | Use `execute_with_fallback` — never duplicate publish logic in the service |
| No `dto = {}` | Listeners do not return values; initializing `dto = {}` is not needed |
