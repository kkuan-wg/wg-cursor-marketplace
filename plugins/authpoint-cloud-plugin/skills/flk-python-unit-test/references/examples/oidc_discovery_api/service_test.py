import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_discovery.adapter.api_responder import ApiResponder
from oidc_discovery.adapter.db_repository import ClientConfigRepository
from oidc_discovery.configuration import ClientConfigDdbRepositoryConfig, ResponderConfig
from oidc_discovery.domain.service import Service, EventValidator
from tests.api.oidc_discovery.service_constants import VALID_DTO, CLIENT_DDB_ITEM_ID_TOKEN, SUCCESS_RESPONSE_ID_TOKEN, \
    CLIENT_DDB_ITEM_CODE, SUCCESS_RESPONSE_CODE, SUCCESS_RESPONSE_CODE_ID_TOKEN, NO_OIDC_CLIENTS_ERR_RESP, \
    INVALID_DTO, INVALID_ACCOUNT_ID_ERR_RESP, REQUIRED_FIELDS


class TestService:

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def client_config_repository(self, template_parser):
        return ClientConfigRepository(config=ClientConfigDdbRepositoryConfig(), parser=template_parser)

    @pytest.fixture
    def responder_config(self):
        return ResponderConfig()

    @pytest.fixture
    def responder(self, responder_config):
        return ApiResponder(config=responder_config)

    @pytest.fixture
    def service(self, client_config_repository, responder):
        return Service(client_config_repository=client_config_repository, responder=responder)

    @pytest.mark.parametrize('event_dto, db_item, expected_response', [
        param(VALID_DTO, [CLIENT_DDB_ITEM_ID_TOKEN], SUCCESS_RESPONSE_ID_TOKEN, id='1'),
        param(VALID_DTO, [CLIENT_DDB_ITEM_CODE], SUCCESS_RESPONSE_CODE, id='2'),
        param(VALID_DTO, [CLIENT_DDB_ITEM_ID_TOKEN, CLIENT_DDB_ITEM_CODE], SUCCESS_RESPONSE_CODE_ID_TOKEN,
              id='3'),
        param(VALID_DTO, [CLIENT_DDB_ITEM_ID_TOKEN, CLIENT_DDB_ITEM_CODE, CLIENT_DDB_ITEM_CODE],
              SUCCESS_RESPONSE_CODE_ID_TOKEN, id='4'),
        param(VALID_DTO, [CLIENT_DDB_ITEM_ID_TOKEN, CLIENT_DDB_ITEM_ID_TOKEN, CLIENT_DDB_ITEM_CODE],
              SUCCESS_RESPONSE_CODE_ID_TOKEN, id='5'),
        param(VALID_DTO, [], NO_OIDC_CLIENTS_ERR_RESP, id='6')
    ])
    def test_process_with_success(self, event_dto, db_item, expected_response, service, mocker):
        # Given
        service.client_config_repository.retrieve_oidc_clients_by_account_id = mocker.Mock(return_value=db_item)

        # When
        actual_response = service.process(dto=event_dto)

        # Then
        service.client_config_repository.retrieve_oidc_clients_by_account_id.assert_called_once_with(dto=event_dto)
        assert actual_response == expected_response

    @pytest.mark.parametrize('event_dto, db_item, expected_response', [
        param(INVALID_DTO, [], INVALID_ACCOUNT_ID_ERR_RESP, id='1')
    ])
    def test_process_with_error(self, event_dto, db_item, expected_response, service, mocker):
        # Given
        service.client_config_repository.retrieve_oidc_clients_by_account_id = mocker.Mock(return_value=db_item)

        # When
        actual_response = service.process(dto=event_dto)

        # Then
        service.client_config_repository.retrieve_oidc_clients_by_account_id.assert_not_called()
        assert actual_response == expected_response

    @pytest.mark.parametrize('actual_fields, expected_fields', [
        param(EventValidator.REQUIRED_FIELDS, REQUIRED_FIELDS, id='1'),
    ])
    def test_required_fields(self, actual_fields, expected_fields):
        # Given

        # When

        # Then
        assert actual_fields == expected_fields
