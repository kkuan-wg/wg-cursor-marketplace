# Configuration — Env Vars, DTO Mapping, Error Codes

The `configuration.py` centralizes environment variables, DTO mapping, error codes, and adapter configs. Config classes extend `BaseConfig` from the authpoint-lambda-layer and expose `as_dict` for passing to layer components. See [parts/layer-authpoint-lambda.md](layer-authpoint-lambda.md).

---

## 1. Role of configuration.py

| Responsibility | Description |
|----------------|-------------|
| **Constants** | FUNCTION_NAME, table names, GSI names, entity maps |
| **API_ERROR_CODES** | HTTP error responses for APIs |
| **Event configs** | DTO mapping from event (HTTP, SQS, DDB Stream) to domain DTO |
| **Adapter configs** | Repository, Responder, Crypto, Invoker, Publisher, Producer |

---

## 2. BaseConfig and as_dict

**BaseConfig** comes from `configuration.base_config` (authpoint-lambda-layer). It provides `as_dict` — a property that converts the config instance to a dict. Adapters and event handlers pass `config.as_dict` to authpoint-lambda-layer components.

```python
from configuration.base_config import BaseConfig

class SomeConfig(BaseConfig):
    def __init__(self):
        self.table_name = getenv('TABLE_NAME')
```

```python
# In adapter: pass config.as_dict to authpoint-lambda-layer
self.repository = DdbRepository(config=config.as_dict, template_parser=parser)
```

---

## 3. getenv Without Default

Use `getenv` **without** a default value. Fail-fast is preferred: if the env var is missing, the code fails in dev and the developer fixes it immediately.

```python
# ✅ CORRECT
self.table_name = getenv('TX_TABLE_NAME')
self.topic_arn = getenv('TX_RESULT_TOPIC_ARN')

# ❌ INCORRECT — masks configuration issues
self.table_name = getenv('TX_TABLE_NAME', 'default-table')
```

---

## 4. Shared Schemas in folklore-lambda-layer

DynamoDB schemas shared across multiple services live in **folklore-lambda-layer** (`flk_api.*api_config_helper`). Use them in config classes instead of redefining PK/SK/GSI schemas locally. See [parts/layer-folklore-lambda.md](layer-folklore-lambda.md).

```python
from flk_api.logon_app.api_config_helper import LogonAppApiRepositoryConfig

class TransactionRepositoryConfig(BaseConfig):
    def __init__(self):
        self.table_name = getenv('TX_TABLE_NAME')
        self.partition_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_PK
        self.sort_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_SK
```

Each API context has its own config helper class — pick the one matching the service:
`ApiRepositoryConfig` (base) · `LogonAppApiRepositoryConfig` · `OidcApiRepositoryConfig` · `RadiusApiRepositoryConfig` · `FireboxApiRepositoryConfig`

---

## 5. Typical Structure (order)

1. **FUNCTION_NAME** — constant
2. **Constants** — UPPER_CASE (table names, GSI, entity maps, message keys)
3. **API_ERROR_CODES** — for HTTP APIs
4. **Environment** — `aws_region` from getenv
5. **Event configs** — HttpEventConfig, SqsEventConfig, DdbStreamEventConfig
6. **Adapter configs** — Repository, Responder, Crypto, Invoker, Publisher, Producer

---

## 6. API_ERROR_CODES

HTTP APIs define error codes used by the Responder. Structure: `code`, `title`, `detail`, `status`.

```python
API_ERROR_CODES = {
    'badRequest': {
        'code': f'{_PREFIX_API_CODE}001',
        'title': 'bad_request',
        'detail': 'The request body is missing the required parameters or it has an invalid value',
        'status': 400
    },
    'preconditionFailed': {
        'code': f'{_PREFIX_API_CODE}002',
        'title': 'precondition_failed',
        'detail': 'One or more conditions provided in the request were not met by the server',
        'status': 412
    },
    'unauthorized': {
        'code': f'{_PREFIX_API_CODE}201',
        'title': 'unauthorized',
        'detail': 'Unauthorized',
        'status': 401
    },
    'internalServerError': {
        'code': f'{_PREFIX_API_CODE}301',
        'title': 'server_error',
        'detail': 'The server encountered an unexpected condition that prevented it from fulfilling the request',
        'status': 500
    }
}
```

---

## 7. Environment Class

Common base for configs that need AWS region:

```python
class Environment:
    def __init__(self):
        self.aws_region = getenv('AWS_REGION')


class SomeRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('TABLE_NAME')
```

---

## 8. Event Configs

### HttpEventConfig

For HTTP APIs. Maps request path/body/headers to DTO.

```python
class HttpEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'pathParameters.accountId',
            'resourceId': 'pathParameters.resourceId',
            'encryptedData': 'body.data',
            'chainId': 'body.chainId',
            'clientVersion': 'body.clientVersion',
            'swaEnabled': 'headers.wgc-swa-enabled'
        }
        self.data_sanitize_whitelist_fields = ['encryptedData']
        self.data_auto_mapping = False
        self.dto_log_mapping = ('AccountId: {accountId}, ResourceId: {resourceId}, ClientVersion: {clientVersion}, '
                                'ChainId: {chainId}')
```

- **dto_mapping**: event path → DTO field (dot notation)
- **dto_log_mapping**: fields included when logging DTO (no sensitive data)
- **data_sanitize_whitelist_fields**: fields allowed in sanitization
- **data_auto_mapping**: usually `False`

### SqsEventConfig

For SQS consumers:

```python
class SqsEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'data.accountId',
            'chainId': {
                'type': 'first_not_none',
                'values': ['data.chainId', 'data.header.chainId']
            },
            'userId': 'data.userId',
            'transactionId': 'data.transactionId',
            'header': 'data.header',
            'user': 'data.user',
            'authnResult': 'data.authnResult',
            'authnApiResult': 'data.authnApiResult'
        }
        self.data_auto_mapping = False
        self.dto_log_mapping = 'AccountId: {accountId}, TransactionId: {transactionId}, EventType: {eventType}, ' \
                               'EntityType: {entityType}'
```

### DdbStreamEventConfig

For DynamoDB Streams:

```python
class DdbStreamEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'newImage.accountId',
            'transactionId': 'newImage.transactionId',
            'header': 'newImage.header',
            'chainId': 'newImage.header.chainId',
            'user': 'newImage.user',
            'userId': 'newImage.user.userId',
            'transactionResult': 'newImage.transactionResult',
            'policy': 'newImage.policy',
            'isReplayEvent': {'type': 'hardcoded', 'value': False}
        }
        self.dto_log_mapping = 'AccountId: {accountId}, TransactionId: {transactionId}'
```

---

## 9. Repository Configs

Extend `Environment` and `BaseConfig`. Use `partition_key_schema`, `sort_key_schema`, `gsi_schema`, `model_mappings` from the layer when available.

```python
class ClientConfigRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('CLIENT_CONFIG_TABLE_NAME')
        self.partition_key_schema = LogonAppApiRepositoryConfig.CLIENT_CONFIG_REPOSITORY_PK


class TransactionRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('TX_TABLE_NAME')
        self.partition_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_PK
        self.sort_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_SK
        self.gsi_schema = {
            DDB_TX_GSI_1_NAME: LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_GSI_1_PK
        }
        self.model_mappings = {
            DDB_TX_TRANSACTION_RESULT: {'transactionResult': 'transactionResult'},
            DDB_TX_FORGOT_TOKEN_ENABLE_DONE: LogonAppApiRepositoryConfig.TRANSACTION_FORGOT_TOKEN_ENABLE_DONE_ENTITY_MAP
        }
```

---

## 10. Responder Config

```python
class ResponderConfig(BaseConfig):
    def __init__(self):
        self.allowed_origin = getenv('WGC_ALLOWED_ORIGIN')
```

---

## 11. Crypto Config

```python
class CommunicationCryptoConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.decrypt_attribute_name = 'encryptedData'
        self.encrypt_attribute_name = 'responsePayload'
```

---

## 12. Invoker Config

```python
class GetTokenDataInvokerConfig(BaseConfig, Environment):
    def __init__(self):
        super().__init__()
        self.function_name = getenv('CORE_USER_MGMT_GET_TOKEN_DATA_API_ARN')
        self.source = FUNCTION_NAME
        self.invocation_type = 'RequestResponse'
        self.data_mapping = {
            'accountId': 'accountId',
            'userIds': 'userIds'
        }
```

---

## 13. Publisher and Producer Configs

```python
class SnsPublishConfig(BaseConfig):
    def __init__(self):
        self.topic_arn = getenv('TX_RESULT_TOPIC_ARN')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('AWS_REGION')
        self.event_data_mappings = { ... }
        self.message_group_id_schemas = { ... }
        self.event_configs = { ... }


class SqsProducerConfig(BaseConfig):
    def __init__(self):
        self.queue_url = getenv('TX_EVENT_REPLAY_QUEUE_URL')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('AWS_REGION')
        self.data_mappings = { ... }
        self.message_configs = { ... }
```

---

## 14. Complete Example — Simple API (config_api)

```python
from os import getenv

from configuration.base_config import BaseConfig
from flk_api.logon_app.api_commons import API_CODE_LOGON_APP, LOGON_APP_FUNCTION_CODE_CONFIG_API
from flk_api.logon_app.api_config_helper import LogonAppApiRepositoryConfig

FUNCTION_NAME = 'flk-logon-app-config-api'
CLIENT_CONFIG_TABLE_NAME = getenv('CLIENT_CONFIG_TABLE_NAME')
CLIENT_CONFIG_SWA_ENABLED_GSI_NAME = f'{CLIENT_CONFIG_TABLE_NAME}-swa-enabled-gsi'
USER_DETAIL_TABLE_NAME = getenv('USER_DETAIL_TABLE_NAME')
USER_DETAIL_USERNAME_GSI_NAME = f'{USER_DETAIL_TABLE_NAME}-username-gsi'
USER_DETAIL_TYPE_GROUPING_MAP_KEY = 'userConfigTypeGroupingMapKey'
_PREFIX_API_CODE = f'{API_CODE_LOGON_APP}{LOGON_APP_FUNCTION_CODE_CONFIG_API}'

API_ERROR_CODES = {
    'badRequest': {
        'code': f'{_PREFIX_API_CODE}001',
        'title': 'bad_request',
        'detail': 'The request body is missing the required parameters or it has an invalid value',
        'status': 400
    },
    'preconditionFailed': {
        'code': f'{_PREFIX_API_CODE}002',
        'title': 'precondition_failed',
        'detail': 'One or more conditions provided in the request were not met by the server',
        'status': 412
    },
    'internalServerError': {
        'code': f'{_PREFIX_API_CODE}301',
        'title': 'server_error',
        'detail': 'The server encountered an unexpected condition that prevented it from fulfilling the request',
        'status': 500
    }
}


class HttpEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'pathParameters.accountId',
            'resourceId': 'pathParameters.resourceId',
            'encryptedData': 'body.data',
            'chainId': 'body.chainId',
            'clientVersion': 'body.clientVersion',
            'swaEnabled': 'headers.wgc-swa-enabled'
        }
        self.data_sanitize_whitelist_fields = ['encryptedData']
        self.data_auto_mapping = False
        self.dto_log_mapping = ('AccountId: {accountId}, ResourceId: {resourceId}, ClientVersion: {clientVersion}, '
                                'ChainId: {chainId}')


class Environment:
    def __init__(self):
        self.aws_region = getenv('AWS_REGION')


class ClientConfigRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = CLIENT_CONFIG_TABLE_NAME
        self.partition_key_schema = LogonAppApiRepositoryConfig.CLIENT_CONFIG_REPOSITORY_PK
        self.gsi_schema = {
            CLIENT_CONFIG_SWA_ENABLED_GSI_NAME: LogonAppApiRepositoryConfig.CLIENT_CONFIG_SWA_ENABLED_GSI
        }


class UserDetailRepositoryConfig(BaseConfig, Environment):
    def __init__(self):
        super().__init__()
        self.table_name = USER_DETAIL_TABLE_NAME
        self.gsi_schema = {
            USER_DETAIL_USERNAME_GSI_NAME: LogonAppApiRepositoryConfig.USER_DETAIL_USERNAME_GSI
        }
        self.model_mappings = {
            USER_DETAIL_TYPE_GROUPING_MAP_KEY: LogonAppApiRepositoryConfig.USER_DETAIL_TYPE_GROUPING_MAP
        }


class GetTokenDataInvokerConfig(BaseConfig, Environment):
    def __init__(self):
        super().__init__()
        self.function_name = getenv('CORE_USER_MGMT_GET_TOKEN_DATA_API_ARN')
        self.source = FUNCTION_NAME
        self.invocation_type = 'RequestResponse'
        self.data_mapping = {
            'accountId': 'accountId',
            'userIds': 'userIds'
        }


class ResponderConfig(BaseConfig):
    def __init__(self):
        self.allowed_origin = getenv('WGC_ALLOWED_ORIGIN')


class CommunicationCryptoConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.decrypt_attribute_name = 'encryptedData'
        self.encrypt_attribute_name = 'responsePayload'
```

---

## 15. Complete Example — SQS Consumer (tx_consumer)

```python
from os import getenv

from configuration.base_config import BaseConfig
from flk_api.logon_app.api_config_helper import LogonAppApiRepositoryConfig

FUNCTION_NAME = 'flk-logon-app-tx-consumer'

DDB_TX_TRANSACTION_RESULT = 'db_tx_update_transaction_result'
DDB_TX_FORGOT_TOKEN_ENABLE_DONE = 'db_tx_update_transaction_forgot_token_enable_done'
DDB_AUTHN_METADATA_ENTITY = 'db_authn_metadata'
TX_TABLE_NAME = getenv('TX_TABLE_NAME')
DDB_TX_GSI_1_NAME = f'{TX_TABLE_NAME}-gsi-1'


class Environment:
    def __init__(self):
        self.aws_region = getenv('AWS_REGION')


class SqsEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'data.accountId',
            'chainId': {
                'type': 'first_not_none',
                'values': ['data.chainId', 'data.header.chainId']
            },
            'userId': 'data.userId',
            'transactionId': 'data.transactionId',
            'header': 'data.header',
            'user': 'data.user',
            'authnResult': 'data.authnResult',
            'authnApiResult': 'data.authnApiResult'
        }
        self.data_auto_mapping = False
        self.dto_log_mapping = 'AccountId: {accountId}, TransactionId: {transactionId}, EventType: {eventType}, ' \
                               'EntityType: {entityType}'


class DdbRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = TX_TABLE_NAME
        self.partition_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_PK
        self.sort_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_SK
        self.gsi_schema = {
            DDB_TX_GSI_1_NAME: LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_GSI_1_PK
        }
        self.model_mappings = {
            DDB_TX_TRANSACTION_RESULT: {
                'transactionResult': 'transactionResult'
            },
            DDB_TX_FORGOT_TOKEN_ENABLE_DONE: LogonAppApiRepositoryConfig.TRANSACTION_FORGOT_TOKEN_ENABLE_DONE_ENTITY_MAP
        }


class AuthnMetadataDdbRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('AUTHN_METADATA_TABLE_NAME')
        self.partition_key_schema = LogonAppApiRepositoryConfig.AUTHN_METADATA_REPOSITORY_PK
        self.sort_key_schema = LogonAppApiRepositoryConfig.AUTHN_METADATA_REPOSITORY_SK
        self.model_mappings = {
            DDB_AUTHN_METADATA_ENTITY: LogonAppApiRepositoryConfig.AUTHN_METADATA_MODEL
        }
```

---

## 16. Checklist

- [ ] Extends `BaseConfig` (and `Environment` when needed)
- [ ] `FUNCTION_NAME` at top
- [ ] `API_ERROR_CODES` for HTTP APIs
- [ ] `getenv` without default
- [ ] `dto_mapping` and `dto_log_mapping` in event configs
- [ ] Shared schemas from folklore-lambda-layer (e.g. `LogonAppApiRepositoryConfig`)
- [ ] Config classes pass to authpoint-lambda-layer via `config.as_dict`
