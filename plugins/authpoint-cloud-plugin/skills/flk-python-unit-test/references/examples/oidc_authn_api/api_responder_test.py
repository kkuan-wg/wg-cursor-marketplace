import pytest
from pytest import param

from oidc_authn.adapter.api_responder import ApiResponder
from oidc_authn.configuration import ResponderConfig
from tests.api.oidc_authn.api_responder_constants import (
    VALID_DTO, ACCEPTED_DTO, SUCCESS_ACCEPTED_RESPONSE,
    INVALID_ACCOUNT_ID_RESPONSE, INVALID_LOGIN_RESPONSE, INVALID_PASSWORD_RESPONSE,
    INVALID_OTP_RESPONSE, INVALID_QRCODE_RESPONSE_RESPONSE, INVALID_QRCODE_TRANSACTION_ID_RESPONSE,
    INVALID_FORGOT_TOKEN_AUTHN_CODE_RESPONSE, INVALID_COOKIE_RESPONSE, AUTHN_CONTEXT_EXPIRED_RESPONSE,
    INVALID_REQUEST_RESPONSE, INVALID_ACCURACY_RESPONSE, INVALID_LATITUDE_RESPONSE,
    INVALID_LONGITUDE_RESPONSE, INVALID_APPLICATION_TYPE_RESPONSE, INVALID_AUTHN_TYPES_RESPONSE,
    INTERNAL_SERVER_ERROR_RESPONSE
)


class TestResponder:

    @pytest.fixture
    def responder_config(self):
        return ResponderConfig()

    @pytest.fixture
    def responder(self, responder_config):
        return ApiResponder(config=responder_config)

    def test_accepted_response(self, responder):
        # Given

        # When
        actual_response = responder.accepted(dto=ACCEPTED_DTO)

        # Then
        assert actual_response == SUCCESS_ACCEPTED_RESPONSE

    def test_accepted_response_with_custom_status_code(self, responder):
        # Given
        expected_response = {
            **SUCCESS_ACCEPTED_RESPONSE,
            'statusCode': 201
        }

        # When
        actual_response = responder.accepted(status_code=201, dto=ACCEPTED_DTO)

        # Then
        assert actual_response == expected_response

    @pytest.mark.parametrize('parameter, expected_response', [
        param('accountId', INVALID_ACCOUNT_ID_RESPONSE, id='1'),
        param('login', INVALID_LOGIN_RESPONSE, id='2'),
        param('password', INVALID_PASSWORD_RESPONSE, id='3'),
        param('otp', INVALID_OTP_RESPONSE, id='4'),
        param('qrcodeResponse', INVALID_QRCODE_RESPONSE_RESPONSE, id='5'),
        param('qrcodeTransactionId', INVALID_QRCODE_TRANSACTION_ID_RESPONSE, id='6'),
        param('forgotTokenAuthnCode', INVALID_FORGOT_TOKEN_AUTHN_CODE_RESPONSE, id='7'),
        param('invalidRequest', INVALID_REQUEST_RESPONSE, id='8'),
        param('accuracy', INVALID_ACCURACY_RESPONSE, id='9'),
        param('latitude', INVALID_LATITUDE_RESPONSE, id='10'),
        param('longitude', INVALID_LONGITUDE_RESPONSE, id='11'),
        param('applicationType', INVALID_APPLICATION_TYPE_RESPONSE, id='12'),
        param('authnTypes', INVALID_AUTHN_TYPES_RESPONSE, id='13')
    ])
    def test_invalid_request_response(self, parameter, expected_response, responder):
        # Given

        # When
        actual_response = responder.invalid_request(param=parameter, dto=VALID_DTO)

        # Then
        assert actual_response == expected_response

    def test_invalid_cookie_response(self, responder):
        # Given

        # When
        actual_response = responder.invalid_cookie(dto=VALID_DTO)

        # Then
        assert actual_response == INVALID_COOKIE_RESPONSE

    def test_authn_context_expired_error_response(self, responder):
        # Given

        # When
        actual_response = responder.authn_context_expired_error(dto=VALID_DTO)

        # Then
        assert actual_response == AUTHN_CONTEXT_EXPIRED_RESPONSE

    def test_internal_server_error_response(self, responder):
        # Given

        # When
        actual_response = responder.internal_server_error(dto=VALID_DTO)

        # Then
        assert actual_response == INTERNAL_SERVER_ERROR_RESPONSE
