# Repository Tests

File: `ddb_repository_test.py`. Tests validate DynamoDB key schemas, GSI schemas, model mappings and adapter method delegation — without ever calling DynamoDB.

---

## Class and fixtures

```python
from copy import deepcopy

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from logon_app_authn_api.adapter.db_repository import (
    ClientConfigRepository, UserDetailRepository, TransactionRepository, AuthnContextRepository
)
from logon_app_authn_api.configuration import (
    ClientConfigRepositoryConfig, UserDetailRepositoryConfig,
    TransactionRepositoryConfig, AuthnContextDdbRepositoryConfig,
    USER_DETAIL_USERNAME_GSI_NAME, USER_DETAIL_TYPE_GROUPING_MAP_KEY,
    DDB_TX_STATUS_UPDATE_ENTITY_MAP, CLIENT_CONFIG_SWA_ENABLED_GSI_NAME
)
from tests.api.logon_app_authn_api.ddb_repository_constants import (
    TX_PARTITION_KEY, TX_SORT_KEY,
    CLIENT_CONFIG_PARTITION_KEY, CLIENT_CONFIG_GSI_PARTITION_KEY, CLIENT_CONFIG_GSI_SORT_KEY,
    USER_DETAIL_USERNAME_GSI_KEY, USER_DETAIL_DB, USER_DETAIL_COLLECTION,
    HTTP_EVENT_WITH_TX_ID_DTO, HTTP_EVENT_WITH_TX_RESULT_DTO
)
from tests.api.logon_app_authn_api.http_event_constants import HTTP_EVENT_DTO, HTTP_EVENT_SWA_ENABLED_DTO


class TestDdbRepositoryConfig:

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def transaction_repository(self, template_parser):
        return TransactionRepository(config=TransactionRepositoryConfig(), parser=template_parser)

    @pytest.fixture
    def client_config_repository(self, template_parser):
        return ClientConfigRepository(config=ClientConfigRepositoryConfig(), parser=template_parser)

    @pytest.fixture
    def user_detail_repository(self, template_parser):
        return UserDetailRepository(config=UserDetailRepositoryConfig(), parser=template_parser)
```

---

## test_build_key — PK and SK schemas

Validates that `partitionKeySchema` and `sortKeySchema` in the config produce the correct DynamoDB key from a DTO. Uses `TemplateParser.parse_payload` directly — the same way the adapter does internally.

```python
    @pytest.mark.parametrize('actual_dto, key_schema_name, expected_key, repository_config', [
        param(HTTP_EVENT_WITH_TX_ID_DTO, 'partitionKeySchema', TX_PARTITION_KEY,
              TransactionRepositoryConfig(), id='1'),
        param(HTTP_EVENT_WITH_TX_ID_DTO, 'sortKeySchema', TX_SORT_KEY,
              TransactionRepositoryConfig(), id='2'),
        param(HTTP_EVENT_DTO, 'partitionKeySchema', CLIENT_CONFIG_PARTITION_KEY,
              ClientConfigRepositoryConfig(), id='3'),
    ])
    def test_build_key(self, actual_dto, key_schema_name, expected_key, template_parser, repository_config):
        # Given
        payload_map = {'key': repository_config.as_dict[key_schema_name]}

        # When
        actual_key = template_parser.parse_payload(item=deepcopy(actual_dto), payload_map=payload_map).get('key')
        # Recreates the key build as DdbRepository does internally.
        # Validates that the configuration produces the correct key.

        # Then
        assert actual_key == expected_key
```

---

## test_build_gsi_key — GSI schemas

Same pattern but navigates into `gsiSchema[gsi_name][key_schema_name]`:

```python
    @pytest.mark.parametrize('actual_dto, gsi_schema_name, key_schema_name, expected_key, repository_config', [
        param(VALID_DTO_USERNAME, USER_DETAIL_USERNAME_GSI_NAME, 'gsiPartitionKeySchema',
              USER_DETAIL_USERNAME_GSI_KEY, UserDetailRepositoryConfig(), id='1'),
        param(HTTP_EVENT_SWA_ENABLED_DTO, CLIENT_CONFIG_SWA_ENABLED_GSI_NAME, 'gsiPartitionKeySchema',
              CLIENT_CONFIG_GSI_PARTITION_KEY, ClientConfigRepositoryConfig(), id='2'),
        param(HTTP_EVENT_SWA_ENABLED_DTO, CLIENT_CONFIG_SWA_ENABLED_GSI_NAME, 'gsiSortKeySchema',
              CLIENT_CONFIG_GSI_SORT_KEY, ClientConfigRepositoryConfig(), id='3'),
    ])
    def test_build_gsi_key(self, actual_dto, gsi_schema_name, key_schema_name, expected_key,
                           repository_config, template_parser):
        # Given
        payload_map = {'key': repository_config.as_dict['gsiSchema'][gsi_schema_name][key_schema_name]}

        # When
        actual_key = template_parser.parse_payload(item=deepcopy(actual_dto), payload_map=payload_map).get('key')

        # Then
        assert actual_key == expected_key
```

---

## test_grouping_map — grouped query results

Validates that `parse_list_to_grouped_items` produces the expected grouped dict:

```python
    @pytest.mark.parametrize('db_items, expected_response', [
        param([USER_DETAIL_DB], USER_DETAIL_COLLECTION, id='1'),
        param([], {}, id='2'),
    ])
    def test_user_detail_grouping_map(self, db_items, expected_response, user_detail_repository):
        # Given

        # When
        actual_model = user_detail_repository.repository.ddb_parser.parse_list_to_grouped_items(
            items=db_items,
            grouping_map_key=USER_DETAIL_TYPE_GROUPING_MAP_KEY
        )

        # Then
        assert actual_model == expected_response
```

---

## Method coverage tests

Verify that each adapter method calls the correct underlying layer method with the correct arguments. Mock the layer method directly on the instantiated repository.

```python
    def test_retrieve_client_config(self, client_config_repository, mocker):
        # Given
        client_config_repository.repository.get_item_by_partition_key = mocker.Mock()

        # When
        client_config_repository.retrieve_client_config_by_account_id_and_resource_id(dto=HTTP_EVENT_DTO)

        # Then
        client_config_repository.repository.get_item_by_partition_key.assert_called_once_with(dto=HTTP_EVENT_DTO)

    def test_retrieve_client_config_swa_enabled(self, client_config_repository, mocker):
        # Given
        client_config_repository.repository.query_gsi_by_partition_and_sort_key_equals = mocker.Mock()

        # When
        client_config_repository.retrieve_client_config_by_swa_enabled_and_account_id(dto=HTTP_EVENT_SWA_ENABLED_DTO)

        # Then
        client_config_repository.repository.query_gsi_by_partition_and_sort_key_equals.assert_called_once_with(
            dto=HTTP_EVENT_SWA_ENABLED_DTO,
            index_name=CLIENT_CONFIG_SWA_ENABLED_GSI_NAME
        )

    def test_update_transaction_result(self, transaction_repository, mocker):
        # Given
        transaction_repository.repository.update_item = mocker.Mock()

        # When
        transaction_repository.update_tx_result(dto=HTTP_EVENT_WITH_TX_RESULT_DTO)

        # Then
        transaction_repository.repository.update_item.assert_called_once_with(
            dto=HTTP_EVENT_WITH_TX_RESULT_DTO,
            model_mappings_entity_key=DDB_TX_STATUS_UPDATE_ENTITY_MAP
        )

    def test_retrieve_authn_metadata_by_account_id_and_user_id(self, authn_metadata_repository, mocker):
        # Given
        authn_metadata_repository.repository.get_item_by_partition_and_sort_key = mocker.Mock()

        # When
        authn_metadata_repository.retrieve_authn_metadata_by_account_id_and_user_id(
            dto=HTTP_EVENT_WITH_USER_ID_DTO)

        # Then
        authn_metadata_repository.repository.get_item_by_partition_and_sort_key.assert_called_once_with(
            dto=HTTP_EVENT_WITH_USER_ID_DTO,
            include_soft_deleted=True
        )
```

When a method returns a value, also assert the return value:

```python
    @pytest.mark.parametrize('db_response, expected_response', [
        param(USER_DETAIL_COLLECTION, USER_DETAIL_DB, id='1'),
        param({}, {}, id='2'),
    ])
    def test_retrieve_user_detail_by_account_id_and_username(self, db_response, expected_response,
                                                             user_detail_repository, mocker):
        # Given
        user_detail_repository.repository.query_gsi_by_partition_key = mocker.Mock(return_value=db_response)

        # When
        response = user_detail_repository.retrieve_user_detail_by_account_id_and_username(dto=HTTP_EVENT_DTO)

        # Then
        user_detail_repository.repository.query_gsi_by_partition_key.assert_called_once_with(
            dto=HTTP_EVENT_DTO,
            index_name=USER_DETAIL_USERNAME_GSI_NAME,
            grouping_map_key=USER_DETAIL_TYPE_GROUPING_MAP_KEY,
        )
        assert response == expected_response
```

---

## Checklist

- [ ] `TemplateParser()` is real, never mocked
- [ ] `test_build_key` covers PK and SK for every config class
- [ ] `test_build_gsi_key` covers all GSI schemas
- [ ] `test_grouping_map` included when `grouping_map_key` is used
- [ ] One method coverage test per adapter method
- [ ] `model_mappings_entity_key` constant verified in `update_item` / `save_item` calls
- [ ] `include_soft_deleted=True` verified when applicable
- [ ] Return value asserted when the method returns data
