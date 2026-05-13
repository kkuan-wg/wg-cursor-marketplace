import datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_tx_request_consumer.adapter.db_repository import DynamoDbRepository, AuthnMetadataRepository
from oidc_tx_request_consumer.configuration import DdbRepositoryConfig, \
    DDB_TRANSACTION_TRANSACTION_RESULT, DDB_TRANSACTION_AUTHN_TYPES_ENTITY, AuthnMetadataDdbRepositoryConfig, \
    DDB_AUTHN_METADATA_ENTITY
from tests.transaction.consumer.oidc_tx_request_consumer.db_repository_config_constants import \
    TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO, PASSWORD_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, \
    PASSWORD_VALIDATED_UNAUTHORIZED_WITH_TRANSACTION_RESULT_DTO, AUTHENTICATION_PARTITION_KEY, \
    PASSWORD_OTP_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, \
    LUFFY_TRANSACTION_SORT_KEY, TRANSACTION_PARTITION_KEY, \
    TRANSACTION_TIMEOUT_MODEL, PASSWORD_VALIDATED_AUTHORIZED_MODEL, \
    PASSWORD_VALIDATED_UNAUTHORIZED_MODEL, PASSWORD_OTP_VALIDATED_AUTHORIZED_MODEL, \
    AUTHN_REQUESTED_WITH_TRANSACTION_RESULT_DTO, \
    PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_TRANSACTION_RESULT_DTO, PASSWORD_OTP_VALIDATED_UNAUTHORIZED_MODEL, \
    TRANSACTION_AUTHN_DONE, AUTHN_METADATA_PARTITION_KEY, AUTHN_METADATA_SORT_KEY, AUTHN_METADATA_MODEL


class TestDdbRepositoryConfig:
    FAKE_TIME = datetime.datetime(2021, 9, 30, 0, 0, tzinfo=datetime.timezone.utc)

    @pytest.fixture
    def _patch_datetime_now(self, monkeypatch):
        class DateTime:
            @classmethod
            def utcnow(cls):
                return TestDdbRepositoryConfig.FAKE_TIME

        monkeypatch.setattr(datetime, 'datetime', DateTime)

    @pytest.fixture()
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def repository(self, template_parser):
        return DynamoDbRepository(config=DdbRepositoryConfig(), template_parser=template_parser)

    @pytest.fixture
    def authn_metadata_repository(self, template_parser):
        return AuthnMetadataRepository(config=AuthnMetadataDdbRepositoryConfig(), template_parser=template_parser)

    @pytest.mark.parametrize('actual_dto, key_schema_name, repository_config, expected_key', [
        param(AUTHN_REQUESTED_WITH_TRANSACTION_RESULT_DTO, 'partitionKeySchema',
              DdbRepositoryConfig(), TRANSACTION_PARTITION_KEY, id='1'),
        param(AUTHN_REQUESTED_WITH_TRANSACTION_RESULT_DTO, 'sortKeySchema',
              DdbRepositoryConfig(), LUFFY_TRANSACTION_SORT_KEY, id='2'),
        param(TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO, 'partitionKeySchema',
              DdbRepositoryConfig(), TRANSACTION_PARTITION_KEY, id='3'),
        param(TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO, 'sortKeySchema',
              DdbRepositoryConfig(), LUFFY_TRANSACTION_SORT_KEY, id='4'),
        param(PASSWORD_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, 'partitionKeySchema',
              DdbRepositoryConfig(), AUTHENTICATION_PARTITION_KEY, id='7'),
        param(PASSWORD_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, 'sortKeySchema',
              DdbRepositoryConfig(), LUFFY_TRANSACTION_SORT_KEY, id='8'),
        param(TRANSACTION_AUTHN_DONE, 'partitionKeySchema',
              AuthnMetadataDdbRepositoryConfig(), AUTHN_METADATA_PARTITION_KEY, id='9'),
        param(TRANSACTION_AUTHN_DONE, 'sortKeySchema',
              AuthnMetadataDdbRepositoryConfig(), AUTHN_METADATA_SORT_KEY, id='10')
    ])
    def test_build_key(self, actual_dto, key_schema_name, repository_config, expected_key, template_parser):
        # Given
        payload_map = {'key': repository_config.as_dict[key_schema_name]}

        # When
        actual_key = template_parser.parse_payload(item=actual_dto, payload_map=payload_map).get('key')
        # Inside the DynamoRepository adapter we are invoking the TemplateParser utility to build the keys.
        # In this test we are recreating the build_key in the same way that DynamoRepository adapter do.
        # We want to ensure that the configuration will create the proper keys.

        # Then
        assert actual_key == expected_key

    @pytest.mark.parametrize('actual_dto, model_mapping_key, repository_config, expected_model', [
        param(TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO, DDB_TRANSACTION_TRANSACTION_RESULT,
              DdbRepositoryConfig(), TRANSACTION_TIMEOUT_MODEL, id='1'),
        param(PASSWORD_VALIDATED_UNAUTHORIZED_WITH_TRANSACTION_RESULT_DTO, DDB_TRANSACTION_TRANSACTION_RESULT,
              DdbRepositoryConfig(), PASSWORD_VALIDATED_UNAUTHORIZED_MODEL, id='2'),
        param(PASSWORD_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, DDB_TRANSACTION_AUTHN_TYPES_ENTITY,
              DdbRepositoryConfig(), PASSWORD_VALIDATED_AUTHORIZED_MODEL, id='3'),
        param(PASSWORD_OTP_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, DDB_TRANSACTION_AUTHN_TYPES_ENTITY,
              DdbRepositoryConfig(), PASSWORD_OTP_VALIDATED_AUTHORIZED_MODEL, id='4'),
        param(PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_TRANSACTION_RESULT_DTO,
              DDB_TRANSACTION_TRANSACTION_RESULT, DdbRepositoryConfig(),
              PASSWORD_OTP_VALIDATED_UNAUTHORIZED_MODEL, id='5'),
        param(TRANSACTION_AUTHN_DONE, DDB_AUTHN_METADATA_ENTITY, AuthnMetadataDdbRepositoryConfig(),
              AUTHN_METADATA_MODEL, id='6')
    ])
    def test_map_payload(self, actual_dto, model_mapping_key, expected_model, template_parser, repository_config,
                         _patch_datetime_now):
        # Given
        model_map = repository_config.as_dict['modelMappings'][model_mapping_key]

        # When
        actual_model = template_parser.parse_payload(item=actual_dto, payload_map=model_map)
        # Inside the DynamoRepository adapter we are invoking the TemplateParser utility to build the db model.
        # In this test we are recreating the parse of the model in the same way that DynamoRepository adapter do.
        # We want to ensure that the configuration will create the proper model.

        # Then
        assert actual_model == expected_model

    @pytest.mark.parametrize('actual_dto', [
        param(TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO, id='1')
    ])
    def test_update_transaction_result(self, actual_dto: dict, repository, mocker):
        # Given
        repository.tx_repository.update_item = mocker.Mock()

        # When
        repository.update_transaction_result(dto=actual_dto)

        # Then
        repository.tx_repository.update_item.assert_called_once_with(
            dto=actual_dto,
            model_mappings_entity_key=DDB_TRANSACTION_TRANSACTION_RESULT
        )

    @pytest.mark.parametrize('actual_dto', [
        param(PASSWORD_OTP_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, id='1')
    ])
    def test_update_transaction_result_authn_type(self, actual_dto: dict, repository, mocker):
        # Given
        repository.tx_repository.update_item = mocker.Mock()

        # When
        repository.update_transaction_result_authn_type(dto=actual_dto)

        # Then
        repository.tx_repository.update_item.assert_called_once_with(
            dto=actual_dto,
            model_mappings_entity_key=DDB_TRANSACTION_AUTHN_TYPES_ENTITY
        )

    @pytest.mark.parametrize('actual_dto', [
        param(PASSWORD_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO, id='1')
    ])
    def test_retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted(self, actual_dto: dict, repository,
                                                                                 mocker):
        # Given
        repository.tx_repository.get_item_by_partition_and_sort_key = mocker.Mock()

        # When
        repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted(dto=actual_dto)

        # Then
        repository.tx_repository.get_item_by_partition_and_sort_key.assert_called_once_with(
            dto=actual_dto,
            include_soft_deleted=True
        )

    def test_save_authn_metadata(self, authn_metadata_repository, mocker):
        # Given
        authn_metadata_repository.tx_repository.save_item = mocker.Mock()

        # When
        authn_metadata_repository.save_authn_metadata(dto=TRANSACTION_AUTHN_DONE)

        # Then
        authn_metadata_repository.tx_repository.save_item.assert_called_once_with(
            dto=TRANSACTION_AUTHN_DONE,
            model_mappings_entity_key=DDB_AUTHN_METADATA_ENTITY
        )
