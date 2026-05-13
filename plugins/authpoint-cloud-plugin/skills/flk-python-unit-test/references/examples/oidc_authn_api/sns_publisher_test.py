import datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_authn.adapter.msg_sender import SnsMessagePublisher
from oidc_authn.configuration import SnsPublisherConfig, SnsPwAzureAdPublisherConfig, SnsPwLdapPublisherConfig
from tests.api.oidc_authn.sns_publisher_constants import PASSWORD_REQUESTED_KWARGS, PUSH_DTO, OTP_DTO, QRCODE_DTO, \
    AUTHN_CODE_DTO, PASSWORD_ONLY_DTO, PUSH_REQUESTED_KWARGS, OTP_REQUESTED_KWARGS, QRCODE_REQUESTED_KWARGS, \
    PASSWORD_PUSH_REQUESTED_KWARGS, PASSWORD_OTP_REQUESTED_KWARGS, PASSWORD_QRCODE_REQUESTED_KWARGS, \
    PASSWORD_AUTHN_CODE_REQUESTED_KWARGS, AZURE_AD_PASSWORD_DTO, AZURE_AD_PASSWORD_REQUESTED_KWARGS, \
    AZURE_AD_PASSWORD_PUSH_DTO, AZURE_AD_PASSWORD_PUSH_REQUESTED_KWARGS, AZURE_AD_PASSWORD_OTP_DTO, \
    AZURE_AD_PASSWORD_OTP_REQUESTED_KWARGS, AZURE_AD_PASSWORD_QRCODE_DTO, AZURE_AD_PASSWORD_QRCODE_REQUESTED_KWARGS, \
    AZURE_AD_PASSWORD_AUTHN_CODE_DTO, AZURE_AD_PASSWORD_AUTHN_CODE_REQUESTED_KWARGS, AUTHN_CODE_REQUESTED_KWARGS, \
    LDAP_PASSWORD_DTO, LDAP_PASSWORD_REQUESTED_KWARGS, LDAP_PASSWORD_PUSH_DTO, LDAP_PASSWORD_PUSH_REQUESTED_KWARGS, \
    LDAP_PASSWORD_OTP_DTO, LDAP_PASSWORD_OTP_REQUESTED_KWARGS, LDAP_PASSWORD_QRCODE_DTO, \
    LDAP_PASSWORD_QRCODE_REQUESTED_KWARGS, LDAP_PASSWORD_AUTHN_CODE_DTO, LDAP_PASSWORD_AUTHN_CODE_REQUESTED_KWARGS, \
    PASSKEY_DTO, PASSKEY_REQUESTED_KWARGS


class TestSnsPublisher:
    FAKE_TIME = datetime.datetime(2021, 9, 30, 0, 0, tzinfo=datetime.timezone.utc)

    @pytest.fixture
    def _patch_datetime_now(self, monkeypatch):
        class DateTime:
            @classmethod
            def utcnow(cls):
                return TestSnsPublisher.FAKE_TIME

        monkeypatch.setattr(datetime, 'datetime', DateTime)

    @pytest.fixture
    def parser(self):
        return TemplateParser()

    @pytest.fixture
    def publisher(self, parser):
        return SnsMessagePublisher(config=SnsPublisherConfig(), azure_ad_config=SnsPwAzureAdPublisherConfig(),
                                   ldap_config=SnsPwLdapPublisherConfig(), parser=parser)

    @pytest.mark.parametrize('dto,method_called,expected_kwargs', [
        param(PASSWORD_ONLY_DTO, 'password_requested', PASSWORD_REQUESTED_KWARGS, id='1'),
        param(PUSH_DTO, 'push_requested', PUSH_REQUESTED_KWARGS, id='2'),
        param(OTP_DTO, 'otp_requested', OTP_REQUESTED_KWARGS, id='3'),
        param(QRCODE_DTO, 'qrcode_requested', QRCODE_REQUESTED_KWARGS, id='4'),
        param(PUSH_DTO, 'password_push_requested', PASSWORD_PUSH_REQUESTED_KWARGS, id='5'),
        param(OTP_DTO, 'password_otp_requested', PASSWORD_OTP_REQUESTED_KWARGS, id='6'),
        param(QRCODE_DTO, 'password_qrcode_requested', PASSWORD_QRCODE_REQUESTED_KWARGS, id='7'),
        param(AUTHN_CODE_DTO, 'password_authn_code_requested', PASSWORD_AUTHN_CODE_REQUESTED_KWARGS, id='8'),
        param(AUTHN_CODE_DTO, 'authn_code_requested', AUTHN_CODE_REQUESTED_KWARGS, id='9'),
        param(PASSKEY_DTO, 'passkey_requested', PASSKEY_REQUESTED_KWARGS, id='10'),
    ])
    def test_publish_request(self, publisher, dto, method_called: str, expected_kwargs, mocker,
                             _patch_datetime_now):
        # Given
        publisher.publisher.publish_message = mocker.Mock()

        # When
        getattr(publisher, method_called)(dto=dto)

        # Then
        publisher.publisher.publish_message.assert_called_once_with(message_payload_kwargs=expected_kwargs)

    @pytest.mark.parametrize('dto,method_called,expected_kwargs', [
        param(AZURE_AD_PASSWORD_DTO, 'password_requested', AZURE_AD_PASSWORD_REQUESTED_KWARGS, id='1'),
        param(AZURE_AD_PASSWORD_PUSH_DTO, 'password_push_requested',
              AZURE_AD_PASSWORD_PUSH_REQUESTED_KWARGS, id='2'),
        param(AZURE_AD_PASSWORD_OTP_DTO, 'password_otp_requested',
              AZURE_AD_PASSWORD_OTP_REQUESTED_KWARGS, id='3'),
        param(AZURE_AD_PASSWORD_QRCODE_DTO, 'password_qrcode_requested',
              AZURE_AD_PASSWORD_QRCODE_REQUESTED_KWARGS, id='4'),
        param(AZURE_AD_PASSWORD_AUTHN_CODE_DTO, 'password_authn_code_requested',
              AZURE_AD_PASSWORD_AUTHN_CODE_REQUESTED_KWARGS, id='5')
    ])
    def test_publish_azure_ad_request(self, publisher, dto, method_called: str, expected_kwargs, mocker,
                                      _patch_datetime_now):
        # Given
        publisher.azure_ad_publisher.publish_message = mocker.Mock()

        # When
        getattr(publisher, method_called)(dto=dto)

        # Then
        publisher.azure_ad_publisher.publish_message.assert_called_once_with(message_payload_kwargs=expected_kwargs)

    @pytest.mark.parametrize('dto,method_called,expected_kwargs', [
        param(LDAP_PASSWORD_DTO, 'password_requested', LDAP_PASSWORD_REQUESTED_KWARGS, id='1'),
        param(LDAP_PASSWORD_PUSH_DTO, 'password_push_requested',
              LDAP_PASSWORD_PUSH_REQUESTED_KWARGS, id='2'),
        param(LDAP_PASSWORD_OTP_DTO, 'password_otp_requested',
              LDAP_PASSWORD_OTP_REQUESTED_KWARGS, id='3'),
        param(LDAP_PASSWORD_QRCODE_DTO, 'password_qrcode_requested',
              LDAP_PASSWORD_QRCODE_REQUESTED_KWARGS, id='4'),
        param(LDAP_PASSWORD_AUTHN_CODE_DTO, 'password_authn_code_requested',
              LDAP_PASSWORD_AUTHN_CODE_REQUESTED_KWARGS, id='5')
    ])
    def test_publish_ldap_request(self, publisher, dto, method_called: str, expected_kwargs, mocker,
                                  _patch_datetime_now):
        # Given
        publisher.ldap_publisher.publish_message = mocker.Mock()

        # When
        getattr(publisher, method_called)(dto=dto)

        # Then
        publisher.ldap_publisher.publish_message.assert_called_once_with(message_payload_kwargs=expected_kwargs)
