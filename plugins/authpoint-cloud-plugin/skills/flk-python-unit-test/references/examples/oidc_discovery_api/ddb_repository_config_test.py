import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_discovery.adapter.db_repository import ClientConfigRepository
from oidc_discovery.configuration import ClientConfigDdbRepositoryConfig, DB_OIDC_CLIENT_CONFIG_GSI_NAME
from tests.api.oidc_discovery.ddb_repository_config_constants import VALID_DTO, CLIENT_CONFIG_GSI_KEY, \
    CLIENT_CONFIG_GSI_INDEX_NAME


class TestDdbRepositoryConfig:
    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def client_config_repository(self, template_parser):
        return ClientConfigRepository(config=ClientConfigDdbRepositoryConfig(), parser=template_parser)

    @pytest.mark.parametrize('actual_dto, config, expected_key', [
        param(VALID_DTO, ClientConfigDdbRepositoryConfig(), CLIENT_CONFIG_GSI_KEY, id='1')
    ])
    def test_client_config_build_key(self, actual_dto, config, expected_key, template_parser):
        # Given
        payload_map = {'key': config.as_dict['gsiSchema'][DB_OIDC_CLIENT_CONFIG_GSI_NAME]['gsiPartitionKeySchema']}

        # When
        actual_key = template_parser.parse_payload(item=actual_dto, payload_map=payload_map).get('key')
        # Inside the DynamoRepository adapter we are invoking the TemplateParser utility to build the keys.
        # In this test we are recreating the build_key in the same way that DynamoRepository adapter do.
        # We want to ensure that the configuration will create the proper keys.

        # Then
        assert actual_key == expected_key

    def test_retrieve_oidc_client(self, client_config_repository, mocker):
        # Given
        client_config_repository.client_config_repository.query_gsi_by_partition_key = mocker.Mock()

        # When
        client_config_repository.retrieve_oidc_clients_by_account_id(dto=VALID_DTO)

        # Then
        client_config_repository.client_config_repository.query_gsi_by_partition_key.assert_called_once_with(
            dto=VALID_DTO, index_name=CLIENT_CONFIG_GSI_INDEX_NAME
        )
