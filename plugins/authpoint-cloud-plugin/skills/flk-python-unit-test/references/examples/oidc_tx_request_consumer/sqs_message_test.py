import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.sqs_event import SqsEvent
from oidc_tx_request_consumer.configuration import SqsEventConfig
from tests.transaction.consumer.oidc_tx_request_consumer.sqs_message_constants import (
    TRANSACTION_TIMEOUT_EVENT, TRANSACTION_TIMEOUT_DTO, PASSWORD_VALIDATED_EVENT, PASSWORD_VALIDATED_UNAUTHORIZED_DTO,
    PASSWORD_VALIDATED_USER_AUTO_BLOCKED_EVENT, PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_DTO, AUTHN_REQUESTED_EVENT,
    AUTHZ_CODE_GENERATED_EVENT, AUTHN_REQUESTED_DTO, AUTHZ_CODE_GENERATED_DTO,
    PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO, PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_EVENT)


class TestSQSMessage:

    @pytest.fixture
    def sqs_event(self, mocker):
        mocker.patch('boto3.resource')
        return SqsEvent(config=SqsEventConfig().as_dict, template_parser=TemplateParser())

    @pytest.mark.parametrize('actual_event, expected_result', [
        param(AUTHN_REQUESTED_EVENT, AUTHN_REQUESTED_DTO, id='1'),
        param(AUTHZ_CODE_GENERATED_EVENT, AUTHZ_CODE_GENERATED_DTO, id='2'),
        param(TRANSACTION_TIMEOUT_EVENT, TRANSACTION_TIMEOUT_DTO, id='3'),
        param(PASSWORD_VALIDATED_EVENT, PASSWORD_VALIDATED_UNAUTHORIZED_DTO, id='4'),
        param(PASSWORD_VALIDATED_USER_AUTO_BLOCKED_EVENT,
              PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_DTO, id='5'),
        param(PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_EVENT,
              PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO, id='6')
    ])
    def test_parse_dto_with_success(self, actual_event, expected_result, sqs_event):
        # Given

        # When
        actual_result = sqs_event.as_dto(event=actual_event)

        # Then
        assert actual_result == expected_result
