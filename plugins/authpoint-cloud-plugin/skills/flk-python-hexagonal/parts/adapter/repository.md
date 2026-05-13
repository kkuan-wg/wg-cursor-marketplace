# Repository Adapter — DynamoDB

Implements repository ports using the authpoint-lambda-layer `adapter.datasource.ddb_repository.DdbRepository`. File: `ddb_repository.py`. See [parts/layer-authpoint-lambda.md](../layer-authpoint-lambda.md).

---

## Layer Component

```python
from adapter.datasource.ddb_repository import DdbRepository
```

---

## Example 1: Multiple Repositories (single file)

```python
from adapter.data_processing.template_parser import TemplateParser
from adapter.datasource.ddb_repository import DdbRepository
from flk_api.logon_app.api_config_helper import UserDetailType
from logon_app_authn_api.configuration import ClientConfigRepositoryConfig, UserDetailRepositoryConfig, \
    CLIENT_CONFIG_SWA_ENABLED_GSI_NAME, USER_DETAIL_USERNAME_GSI_NAME, USER_DETAIL_TYPE_GROUPING_MAP_KEY, \
    TransactionRepositoryConfig, DDB_TX_STATUS_UPDATE_ENTITY_MAP, DDB_TX_PROCESSING_ENTITY_MAP, \
    AuthnMetadataDdbRepositoryConfig, AuthnContextDdbRepositoryConfig
from logon_app_authn_api.port.repository import ClientConfigRepositoryPort, UserDetailRepositoryPort, \
    TransactionRepositoryPort, AuthnMetadataRepositoryPort, AuthnContextRepositoryPort


class ClientConfigRepository(ClientConfigRepositoryPort):

    def __init__(self, *, config: ClientConfigRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_client_config_by_account_id_and_resource_id(self, *, dto: dict) -> dict:
        return self.repository.get_item_by_partition_key(dto=dto)

    def retrieve_client_config_by_swa_enabled_and_account_id(self, *, dto: dict) -> list:
        return self.repository.query_gsi_by_partition_and_sort_key_equals(dto=dto,
                                                                          index_name=CLIENT_CONFIG_SWA_ENABLED_GSI_NAME)


class UserDetailRepository(UserDetailRepositoryPort):

    def __init__(self, *, config: UserDetailRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_user_detail_by_account_id_and_username(self, *, dto: dict) -> dict:
        user_collection = self.repository.query_gsi_by_partition_key(dto=dto,
                                                                     index_name=USER_DETAIL_USERNAME_GSI_NAME,
                                                                     grouping_map_key=USER_DETAIL_TYPE_GROUPING_MAP_KEY)
        return user_collection.get(UserDetailType.USER, {})


class TransactionRepository(TransactionRepositoryPort):

    def __init__(self, *, config: TransactionRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_transaction_by_account_id_and_transaction_id(self, *, dto: dict) -> dict:
        return self.repository.get_item_by_partition_and_sort_key(dto=dto)

    def update_tx_result(self, *, dto: dict):
        self.repository.update_item(dto=dto, model_mappings_entity_key=DDB_TX_STATUS_UPDATE_ENTITY_MAP)

    def save_transaction(self, *, dto: dict):
        self.repository.put_item(dto=dto, model_mappings_entity_key=DDB_TX_PROCESSING_ENTITY_MAP)


class AuthnContextRepository(AuthnContextRepositoryPort):

    def __init__(self, *, config: AuthnContextDdbRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_authn_context_by_account_id_and_authn_context_id(self, *, dto: dict) -> dict:
        return self.repository.get_item_by_partition_and_sort_key(dto=dto)


class AuthnMetadataRepository(AuthnMetadataRepositoryPort):

    def __init__(self, *, config: AuthnMetadataDdbRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_authn_metadata_by_account_id_and_user_id(self, *, dto: dict) -> dict:
        return self.repository.get_item_by_partition_and_sort_key(dto=dto, include_soft_deleted=True)
```

---

## Example 2: Simple (two repositories)

```python
from adapter.data_processing.template_parser import TemplateParser
from adapter.datasource.ddb_repository import DdbRepository
from logon_app_tx.configuration import TransactionRepositoryConfig, ClientConfigRepositoryConfig
from logon_app_tx.port.repository import TransactionRepositoryPort, ClientConfigRepositoryPort


class TransactionRepository(TransactionRepositoryPort):

    def __init__(self, *, config: TransactionRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_transaction_by_account_id_and_transaction_id(self, *, dto: dict) -> dict:
        return self.repository.get_item_by_partition_and_sort_key(dto=dto, include_soft_deleted=True)


class ClientConfigRepository(ClientConfigRepositoryPort):

    def __init__(self, *, config: ClientConfigRepositoryConfig, parser: TemplateParser):
        self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

    def retrieve_client_config_by_account_id_and_resource_id(self, *, dto: dict) -> dict:
        return self.repository.get_item_by_partition_key(dto=dto)
```

---

## Example 3: Multiple DdbRepository instances

When one adapter needs to access multiple tables:

```python
from adapter.data_processing.template_parser import TemplateParser
from adapter.datasource.ddb_repository import DdbRepository
from logon_app_core_data_consumer.configuration import (
    UserDetailRepositoryConfig, UserSyncRepositoryConfig, DB_USER_TOKEN_SYNC_ENTITY
)
from logon_app_core_data_consumer.port.repository import Repository


class DynamoDbRepository(Repository):

    def __init__(self, *, user_detail_config: UserDetailRepositoryConfig,
                 user_sync_config: UserSyncRepositoryConfig,
                 parser: TemplateParser):
        self.user_detail_repository = DdbRepository(config=user_detail_config.as_dict, template_parser=parser)
        self.user_sync_repository = DdbRepository(config=user_sync_config.as_dict, template_parser=parser)

    def retrieve_user_detail_by_account_id_and_user_id(self, *, dto: dict) -> dict:
        return self.user_detail_repository.get_item_by_partition_key(dto=dto)

    def save_user_token_sync(self, *, dto: dict):
        self.user_sync_repository.soft_delete_item(dto=dto, model_mappings_entity_key=DB_USER_TOKEN_SYNC_ENTITY)
```

---

## Checklist

- [ ] File: `ddb_repository.py`
- [ ] Uses `DdbRepository` from `adapter.datasource.ddb_repository`
- [ ] Passes `config.as_dict` and `template_parser=parser` to authpoint-lambda-layer
- [ ] Extends the corresponding port(s)
