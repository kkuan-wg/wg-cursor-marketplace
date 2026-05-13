from copy import deepcopy
from datetime import timezone, datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_tx_request_consumer.adapter.db_repository import DynamoDbRepository, AuthnMetadataRepository
from oidc_tx_request_consumer.adapter.sqs_producer import SqsProducer
from oidc_tx_request_consumer.configuration import DdbRepositoryConfig, AuthnMetadataDdbRepositoryConfig, \
    SqsProducerConfig
from oidc_tx_request_consumer.domain.service import Service, EventValidator
from tests.transaction.consumer.oidc_tx_request_consumer.service_constants import (
    EVENT_REQUIRED_FIELDS, INVALID_ENTITY_TYPE_DTO, INVALID_EVENT_TYPE_DTO, MISSING_ACCOUNT_ID_DTO,
    MISSING_TRANSACTION_ID_DTO, DB_TRANSACTION_PW_PROCESSING,
    TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO, DB_TRANSACTION_DONE_WITHOUT_VALID_GEOLOCATION,
    PASSWORD_VALIDATED_MISSING_AUTHN_RESULT_FIELD_DTO, PASSWORD_VALIDATED_INVALID_AUTHN_TYPES_FIELD_DTO,
    PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO, PASSWORD_OTP_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DTO,
    DB_TRANSACTION_PW_OTP_PROCESSING, PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_PROCESSING_DTO,
    PASSWORD_VALIDATED_UNAUTHORIZED_TRANSACTION_RESULT_DTO, PASSWORD_VALIDATED_INVALID_EVENT_TYPE_FIELD_DTO,
    PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_TRANSACTION_RESULT_DTO,
    AUTHZ_CODE_GENERATED_UPDATE_TRANSACTION_RESULT_DTO, ID_TOKEN_GENERATED_UPDATE_TRANSACTION_RESULT_DTO,
    PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_TRANSACTION_RESULT_DTO, DB_TRANSACTION_DONE,
    DB_TRANSACTION_PW_PROCESSING_WITHOUT_VALID_GEOLOCATION, DB_TRANSACTION_PASSKEY_PROCESSING,
    PASSKEY_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO, PASSKEY_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_PROCESSING_DTO,
    PASSKEY_VALIDATED_UNAUTHORIZED_TRANSACTION_RESULT_DTO)
from tests.transaction.consumer.oidc_tx_request_consumer.sqs_message_constants import (
    TRANSACTION_TIMEOUT_DTO, PASSWORD_VALIDATED_AUTHORIZED_DTO,
    PASSWORD_OTP_VALIDATED_AUTHORIZED_DTO, PASSWORD_VALIDATED_UNAUTHORIZED_DTO,
    PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_DTO, AUTHN_REQUESTED_DTO, AUTHZ_CODE_GENERATED_DTO,
    ID_TOKEN_GENERATED_DTO, PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO,
    PASSKEY_VALIDATED_AUTHORIZED_DTO, PASSKEY_VALIDATED_UNAUTHORIZED_DTO)

FAKE_NOW = datetime(2023, 7, 31, 0, 0, 0, 0, tzinfo=timezone.utc)


class TestService:

    @pytest.fixture
    def _patch_get_timestamp_now(self, mocker):
        patch_datetime = mocker.patch('flk_utils.date_time_helper.datetime')
        patch_datetime.now.return_value = FAKE_NOW

    @pytest.fixture
    def sqs_producer_config(self):
        return SqsProducerConfig()

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def producer(self, mocker, sqs_producer_config, template_parser):
        mocker.patch('boto3.resource')
        return SqsProducer(config=sqs_producer_config, template_parser=template_parser)

    @pytest.fixture
    def repository(self, mocker, template_parser):
        mocker.patch('boto3.resource')
        return DynamoDbRepository(config=DdbRepositoryConfig(), template_parser=template_parser)

    @pytest.fixture
    def authn_metadata_repository(self, mocker, template_parser):
        mocker.patch('boto3.resource')
        return AuthnMetadataRepository(config=AuthnMetadataDdbRepositoryConfig(), template_parser=template_parser)

    @pytest.fixture
    def service(self, repository, authn_metadata_repository, producer):
        return Service(repository=repository, authn_metadata_repository=authn_metadata_repository, producer=producer)

    def test_consume_message_authn_requested(self, service, mocker, _patch_get_timestamp_now):
        # Given
        dto = deepcopy(AUTHN_REQUESTED_DTO)
        service.producer.send_transaction_timeout = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.producer.send_transaction_timeout.assert_called_once_with(dto=dto)

    @pytest.mark.parametrize('actual_dto, expected_dto', [
        param(AUTHZ_CODE_GENERATED_DTO, AUTHZ_CODE_GENERATED_UPDATE_TRANSACTION_RESULT_DTO, id='1'),
        param(ID_TOKEN_GENERATED_DTO, ID_TOKEN_GENERATED_UPDATE_TRANSACTION_RESULT_DTO, id='2')
    ])
    def test_consume_message_authorized_with_authn_done_transaction(self, actual_dto, expected_dto, service,
                                                                    mocker, _patch_get_timestamp_now):
        # Given
        dto = deepcopy(actual_dto)
        tx_db = deepcopy(DB_TRANSACTION_DONE)
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted = mocker.Mock(
            return_value=tx_db)
        service.repository.update_transaction_result = mocker.Mock()
        service.authn_metadata_repository.save_authn_metadata = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted(dto=actual_dto)
        service.repository.update_transaction_result.assert_called_once_with(dto=expected_dto)
        service.authn_metadata_repository.save_authn_metadata.assert_called_once_with(dto=tx_db)

    @pytest.mark.parametrize('actual_dto, expected_dto', [
        param(AUTHZ_CODE_GENERATED_DTO, AUTHZ_CODE_GENERATED_UPDATE_TRANSACTION_RESULT_DTO, id='1'),
        param(ID_TOKEN_GENERATED_DTO, ID_TOKEN_GENERATED_UPDATE_TRANSACTION_RESULT_DTO, id='2')
    ])
    def test_consume_message_authorized_with_authn_done_tx_without_geolocation(self, actual_dto, expected_dto, service,
                                                                               mocker, _patch_get_timestamp_now):
        # Given
        dto = deepcopy(actual_dto)
        tx_db = deepcopy(DB_TRANSACTION_DONE_WITHOUT_VALID_GEOLOCATION)
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted = mocker.Mock(
            return_value=tx_db)
        service.repository.update_transaction_result = mocker.Mock()
        service.authn_metadata_repository.save_authn_metadata = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted(dto=actual_dto)
        service.repository.update_transaction_result.assert_called_once_with(dto=expected_dto)
        service.authn_metadata_repository.save_authn_metadata.assert_not_called()

    @pytest.mark.parametrize('actual_dto', [
        param(AUTHZ_CODE_GENERATED_DTO, id='1'),
        param(ID_TOKEN_GENERATED_DTO, id='2')
    ])
    def test_consume_message_authorized_without_authn_done_transaction(self, actual_dto, service, mocker,
                                                                       caplog, _patch_get_timestamp_now):
        # Given
        dto = deepcopy(actual_dto)
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted = mocker.Mock(
            return_value={})
        service.repository.update_transaction_result = mocker.Mock()
        service.authn_metadata_repository.save_authn_metadata = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted(dto=actual_dto)
        service.repository.update_transaction_result.assert_not_called()
        service.authn_metadata_repository.save_authn_metadata.assert_not_called()
        assert 'Message discarded:' in caplog.text

    @pytest.mark.parametrize('actual_dto, expected_dto, ddb_item', [
        param(TRANSACTION_TIMEOUT_DTO, TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO,
              DB_TRANSACTION_PW_PROCESSING, id='1')
    ])
    def test_consume_tx_timeout_with_ddb_item_processing(self, actual_dto, expected_dto, ddb_item, service, mocker,
                                                         caplog, _patch_get_timestamp_now):
        # Given
        dto = deepcopy(actual_dto)
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted = mocker.Mock(
            return_value=ddb_item
        )
        service.repository.update_transaction_result = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted. \
            assert_called_once_with(dto=dto)
        service.repository.update_transaction_result.assert_called_once_with(dto=expected_dto)
        assert 'Transaction timeout' in caplog.text

    @pytest.mark.parametrize('actual_dto, ddb_item', [
        param(TRANSACTION_TIMEOUT_DTO, DB_TRANSACTION_DONE_WITHOUT_VALID_GEOLOCATION, id='1')
    ])
    def test_consume_tx_timeout_with_ddb_item_done(self, actual_dto, ddb_item, service, mocker):
        # Given
        dto = deepcopy(actual_dto)
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted = mocker.Mock(
            return_value=ddb_item
        )
        service.repository.update_transaction_result = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_account_id_and_tx_id_including_soft_deleted. \
            assert_called_once_with(dto=dto)
        service.repository.update_transaction_result.assert_not_called()

    @pytest.mark.parametrize('actual_dto, expected_error_message', [
        param(INVALID_ENTITY_TYPE_DTO, 'Invalid entityType.', id='1'),
        param(INVALID_EVENT_TYPE_DTO, 'Invalid eventType', id='2'),
        param(MISSING_ACCOUNT_ID_DTO, 'Exception: Invalid accountId', id='3'),
        param(MISSING_TRANSACTION_ID_DTO, 'Exception: Invalid transactionId', id='4'),
        param(PASSWORD_VALIDATED_MISSING_AUTHN_RESULT_FIELD_DTO, 'Exception: Invalid authnStatus', id='5'),
        param(PASSWORD_VALIDATED_INVALID_AUTHN_TYPES_FIELD_DTO, 'Exception: Invalid authnTypes', id='6'),
        param(PASSWORD_VALIDATED_INVALID_EVENT_TYPE_FIELD_DTO, 'Exception: Invalid eventType', id='7')
    ])
    def test_consume_message_with_failure(self, actual_dto, expected_error_message, service, caplog):
        # Given
        dto = deepcopy(actual_dto)

        # When
        service.process(dto=dto)

        # Then
        assert expected_error_message in caplog.text
        assert 'Message discarded:' in caplog.text

    def test_required_fields(self):
        # Given

        # When

        # Then
        assert EventValidator.EVENT_REQUIRED_FIELDS == EVENT_REQUIRED_FIELDS

    @pytest.mark.parametrize('actual_dto, ddb_item, transaction_result_dto', [
        param(PASSWORD_VALIDATED_AUTHORIZED_DTO, DB_TRANSACTION_PW_PROCESSING,
              PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO, id='password_done'),
        param(PASSWORD_VALIDATED_AUTHORIZED_DTO, DB_TRANSACTION_PW_OTP_PROCESSING,
              PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_PROCESSING_DTO, id='password_processing'),
        param(PASSWORD_OTP_VALIDATED_AUTHORIZED_DTO, DB_TRANSACTION_PW_OTP_PROCESSING,
              PASSWORD_OTP_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DTO, id='password_otp_done'),
        param(PASSKEY_VALIDATED_AUTHORIZED_DTO, DB_TRANSACTION_PASSKEY_PROCESSING,
              PASSKEY_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO, id='passkey_done'),
        param(PASSKEY_VALIDATED_AUTHORIZED_DTO, DB_TRANSACTION_PW_OTP_PROCESSING,
              PASSKEY_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_PROCESSING_DTO, id='passkey_processing')
    ])
    def test_consume_authn_event(self, actual_dto, ddb_item, transaction_result_dto, service, mocker,
                                 _patch_get_timestamp_now):
        # Given
        dto = deepcopy(actual_dto)
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted = mocker.Mock(
            return_value=deepcopy(ddb_item)
        )
        service.repository.update_transaction_result_authn_type = mocker.Mock()
        service.authn_metadata_repository.save_authn_metadata = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted. \
            assert_called_once_with(dto=dto)
        service.repository.update_transaction_result_authn_type.assert_called_once_with(dto=transaction_result_dto)
        if transaction_result_dto['transactionResult']['transactionStatus'] == 'AUTHN_DONE':
            service.authn_metadata_repository.save_authn_metadata.assert_called_once_with(
                dto=ddb_item | {'accountId': actual_dto['accountId'], 'userId': actual_dto['userId']})
        else:
            service.authn_metadata_repository.save_authn_metadata.assert_not_called()

    def test_consume_authn_event_with_tx_without_geolocation(self, service, mocker, _patch_get_timestamp_now):
        # Given
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted = mocker.Mock(
            return_value=deepcopy(DB_TRANSACTION_PW_PROCESSING_WITHOUT_VALID_GEOLOCATION)
        )
        service.repository.update_transaction_result_authn_type = mocker.Mock()
        service.authn_metadata_repository.save_authn_metadata = mocker.Mock()

        # When
        service.process(dto=PASSWORD_VALIDATED_AUTHORIZED_DTO)

        # Then
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted. \
            assert_called_once_with(dto=PASSWORD_VALIDATED_AUTHORIZED_DTO)
        service.repository.update_transaction_result_authn_type.assert_called_once_with(
            dto=PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO)
        service.authn_metadata_repository.save_authn_metadata.assert_not_called()

    @pytest.mark.parametrize('actual_dto, ddb_item, expected_dto', [
        param(PASSWORD_VALIDATED_UNAUTHORIZED_DTO, DB_TRANSACTION_PW_PROCESSING,
              PASSWORD_VALIDATED_UNAUTHORIZED_TRANSACTION_RESULT_DTO, id='password_unauthorized'),
        param(PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_DTO, DB_TRANSACTION_PW_PROCESSING,
              PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_TRANSACTION_RESULT_DTO, id='password_user_blocked'),
        param(PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO, DB_TRANSACTION_PW_OTP_PROCESSING,
              PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_TRANSACTION_RESULT_DTO, id='password_otp_token_blocked'),
        param(PASSKEY_VALIDATED_UNAUTHORIZED_DTO, DB_TRANSACTION_PASSKEY_PROCESSING,
              PASSKEY_VALIDATED_UNAUTHORIZED_TRANSACTION_RESULT_DTO, id='passkey_unauthorized')
    ])
    def test_consume_tx_unauthorized(self, actual_dto, expected_dto, ddb_item, service, mocker,
                                     _patch_get_timestamp_now):
        # Given
        dto = deepcopy(actual_dto)
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted = mocker.Mock(
            return_value=ddb_item
        )
        service.repository.update_transaction_result = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted. \
            assert_called_once_with(dto=dto)
        service.repository.update_transaction_result.assert_called_once_with(dto=expected_dto)

    @pytest.mark.parametrize('actual_dto, ddb_item', [
        param(PASSWORD_VALIDATED_AUTHORIZED_DTO, {}, id='1'),
        param(PASSWORD_VALIDATED_AUTHORIZED_DTO, {
            'header': {'accountId': 'WGC-123-abc'}, 'transactionResult': {'transactionStatus': 'AUTHN_DONE'}}, id='2')
    ])
    def test_consume_authn_validated_without_valid_transaction(self, actual_dto, ddb_item, mocker,
                                                               service, caplog):
        # Given
        dto = deepcopy(actual_dto)
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted = mocker.Mock(
            return_value=ddb_item
        )
        service.repository.update_transaction_result_authn_type = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_transaction_by_transaction_id_including_soft_deleted. \
            assert_called_once_with(dto=dto)
        service.repository.update_transaction_result_authn_type.assert_not_called()
        assert 'Authn event discarded. Transaction does not exist or already ended.' in caplog.text
