import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_authn.adapter.api_gateway_invoker import ZtePolicyApiInvoker
from oidc_authn.configuration import ZtePolicyApiInvokerConfig
from tests.api.oidc_authn.api_gateway_invoker_constants import (
    API_RESPONSE_WITH_SUCCESS, EXPECTED_REQUEST, EXPECTED_RESPONSE, PARSED_RESPONSE, ZTE_RESPONSE_WITH_SUCCESS,
    API_RESPONSE_WITH_ERROR, EXPECTED_REQUEST_WITH_GEOLOCATION, EXPECTED_REQUEST_WITH_PREVIOUS_LOCATION,
    EXPECTED_REQUEST_WITHOUT_ELIGIBLE_GROUPS
)
from tests.api.oidc_authn.service_constants import API_INVOKER_REQUEST_DTO_OTHERS_MFA_PUSH, \
    API_INVOKER_REQUEST_DTO_OTHERS_MFA_PUSH_WITH_GEOLOCATION, API_INVOKER_REQUEST_DTO_WITH_GEOLOCATION_MISSING_LATITUDE, \
    API_INVOKER_REQUEST_DTO_WITH_PREVIOUS_LOCATION, API_INVOKER_REQUEST_DTO_WITHOUT_ELIGIBLE_GROUPS


class TestApiGatewayInvoker:

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def config(self):
        return ZtePolicyApiInvokerConfig()

    @pytest.fixture
    def api_gateway_invoker(self, config, template_parser):
        print(config.as_dict)
        return ZtePolicyApiInvoker(config=config, template_parser=template_parser)

    @pytest.mark.parametrize('dto, api_response, expected_request, expected_response', [
        param(API_INVOKER_REQUEST_DTO_OTHERS_MFA_PUSH, API_RESPONSE_WITH_SUCCESS, EXPECTED_REQUEST, EXPECTED_RESPONSE,
              id='1'),
        param(API_INVOKER_REQUEST_DTO_OTHERS_MFA_PUSH_WITH_GEOLOCATION, API_RESPONSE_WITH_SUCCESS,
              EXPECTED_REQUEST_WITH_GEOLOCATION, EXPECTED_RESPONSE, id='2'),
        param(API_INVOKER_REQUEST_DTO_OTHERS_MFA_PUSH, API_RESPONSE_WITH_ERROR, EXPECTED_REQUEST, {}, id='3'),
        param(API_INVOKER_REQUEST_DTO_WITH_GEOLOCATION_MISSING_LATITUDE, API_RESPONSE_WITH_SUCCESS, EXPECTED_REQUEST,
              EXPECTED_RESPONSE, id='4'),
        param(API_INVOKER_REQUEST_DTO_WITH_PREVIOUS_LOCATION, API_RESPONSE_WITH_SUCCESS,
              EXPECTED_REQUEST_WITH_PREVIOUS_LOCATION, EXPECTED_RESPONSE, id='5'),
        param(API_INVOKER_REQUEST_DTO_WITHOUT_ELIGIBLE_GROUPS, API_RESPONSE_WITH_SUCCESS,
              EXPECTED_REQUEST_WITHOUT_ELIGIBLE_GROUPS, EXPECTED_RESPONSE, id='6')
    ])
    def test_retrieve_policy_with_success(self, dto: dict, api_response: dict, expected_request: dict,
                                          expected_response: dict, api_gateway_invoker, mocker):
        # Given
        api_gateway_invoker.api_invoker.execute_request = mocker.Mock(
            return_value=api_response
        )

        # When
        actual_response = api_gateway_invoker.retrieve_policy(dto=dto)

        # Then
        assert actual_response == expected_response
        api_gateway_invoker.api_invoker.execute_request.assert_called_once_with(
            config_key='evaluatePolicy',
            execute_request_kwargs=expected_request
        )

    def test_retrieve_policy_with_error(self, api_gateway_invoker, mocker):
        # Given
        api_gateway_invoker.api_invoker.execute_request = mocker.Mock(
            side_effect=Exception
        )

        # When
        actual_response = api_gateway_invoker.retrieve_policy(dto=API_INVOKER_REQUEST_DTO_OTHERS_MFA_PUSH)

        # Then
        assert actual_response == {}
        api_gateway_invoker.api_invoker.execute_request.assert_called_once_with(
            config_key='evaluatePolicy',
            execute_request_kwargs=EXPECTED_REQUEST
        )

    def test_zte_policy_api_invoker_config(self, config, template_parser):
        # When
        parsed_response = template_parser.parse_payload(
            item=ZTE_RESPONSE_WITH_SUCCESS,
            payload_map=config.as_dict['responseDataMappings']['evaluatePolicy']
        )
        # Inside the ApiGatewayInvoker adapter we are invoking the TemplateParser utility to build the response.
        # In this test we are recreating the response in the same way that ApiGatewayInvoker adapter does.
        # We want to ensure that the configuration will create the proper response.

        # Then
        assert parsed_response == PARSED_RESPONSE
