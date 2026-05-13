import pytest
from oidc_user_detail_listener.adapter.db_repository import DynamoDbRepository
from oidc_user_detail_listener.configuration import DdbRepositoryConfig, DB_SESSION_ENTITY
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from tests.cache.oidc_user_detail_listener.db_repository_config_constants import SESSION, PARTITION_KEY, SORT_KEY, \
    GSI_KEY, AUTHN_CONTEXT_GSI_NAME, UPDATE_EXPIRATION_TIME_SESSION_MODEL, SESSION_EXPIRED
from tests.cache.oidc_user_detail_listener.ddb_stream_constants import USER_BLOCKED_DTO


class TestSessionRepositoryConfig:

    @pytest.fixture()
    def repository_config(self):
        return DdbRepositoryConfig().as_dict

    @pytest.fixture()
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def repository(self, template_parser):
        return DynamoDbRepository(authn_context_config=DdbRepositoryConfig(), template_parser=template_parser)

    @pytest.mark.parametrize('actual_dto, expected_gsi_key', [
        param(USER_BLOCKED_DTO, GSI_KEY, id='1')
    ])
    def test_user_detail_build_gsi_key(self, actual_dto, expected_gsi_key, template_parser,
                                       repository_config):
        # Given
        payload_map = {'key': repository_config['gsiSchema'][AUTHN_CONTEXT_GSI_NAME]['gsiPartitionKeySchema']}

        # When
        actual_key = template_parser.parse_payload(item=actual_dto, payload_map=payload_map).get('key')
        # Inside the DynamoRepository adapter we are invoking the TemplateParser utility to build the keys.
        # In this test we are recreating the build_key in the same way that DynamoRepository adapter do.
        # We want to ensure that the configuration will create the proper keys.

        # Then
        assert actual_key == expected_gsi_key

    @pytest.mark.parametrize('actual_dto, key_schema_name, expected_key', [
        param(SESSION, 'partitionKeySchema', PARTITION_KEY, id='1'),
        param(SESSION, 'sortKeySchema', SORT_KEY, id='2')
    ])
    def test_build_key(self, actual_dto, key_schema_name, expected_key, template_parser, repository_config):
        # Given
        payload_map = {'key': repository_config[key_schema_name]}

        # When
        actual_key = template_parser.parse_payload(item=actual_dto, payload_map=payload_map).get('key')
        # Inside the DynamoRepository adapter we are invoking the TemplateParser utility to build the keys.
        # In this test we are recreating the build_key in the same way that DynamoRepository adapter do.
        # We want to ensure that the configuration will create the proper keys.

        # Then
        assert actual_key == expected_key

    @pytest.mark.parametrize('actual_dto, model_mapping_key, expected_model', [
        param(SESSION_EXPIRED, DB_SESSION_ENTITY, UPDATE_EXPIRATION_TIME_SESSION_MODEL, id='2')
    ])
    def test_map_payload(self, actual_dto, model_mapping_key, expected_model, template_parser, repository_config):
        # Given
        model_map = repository_config['modelMappings'][model_mapping_key]

        # When
        actual_model = template_parser.parse_payload(item=actual_dto, payload_map=model_map)
        # Inside the DynamoRepository adapter we are invoking the TemplateParser utility to build the db model.
        # In this test we are recreating the parse of the model in the same way that DynamoRepository adapter do.
        # We want to ensure that the configuration will create the proper model.

        # Then
        assert actual_model == expected_model

    @pytest.mark.parametrize('actual_dto', [
        param(USER_BLOCKED_DTO, id='1')
    ])
    def test_retrieve_sessions_by_account_id_and_user_id_including_soft_deleted(self, actual_dto: dict, repository,
                                                                                mocker):
        # Given
        repository.authn_context_repository.query_gsi_by_partition_key = mocker.Mock()

        # When
        repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted(dto=actual_dto)

        # Then
        repository.authn_context_repository.query_gsi_by_partition_key.assert_called_once_with(
            dto=actual_dto,
            include_soft_deleted=True,
            index_name=AUTHN_CONTEXT_GSI_NAME
        )

    @pytest.mark.parametrize('actual_dto', [
        param(SESSION, id='1')
    ])
    def test_update_session(self, actual_dto: dict, repository, mocker):
        # Given
        repository.authn_context_repository.update_item = mocker.Mock()

        # When
        repository.update_session(dto=actual_dto)

        # Then
        repository.authn_context_repository.update_item.assert_called_once_with(
            dto=actual_dto,
            model_mappings_entity_key=DB_SESSION_ENTITY
        )
