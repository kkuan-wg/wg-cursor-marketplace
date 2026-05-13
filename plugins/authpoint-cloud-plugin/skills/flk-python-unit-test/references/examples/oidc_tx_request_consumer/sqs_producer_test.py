import datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_tx_request_consumer.adapter.sqs_producer import SqsProducer
from oidc_tx_request_consumer.configuration import SqsProducerConfig, SQS_CONFIG_TIMEOUT_MESSAGE_KEY
from tests.transaction.consumer.oidc_tx_request_consumer.sqs_producer_constants import \
    TRANSACTION_TIMEOUT_KWARGS_WITH_DATA_AS_OBJ
from tests.transaction.consumer.oidc_tx_request_consumer.sqs_message_constants import AUTHN_REQUESTED_DTO


class TestSqsProducer:
    FAKE_TIME = datetime.datetime(2021, 9, 30, 0, 0, tzinfo=datetime.timezone.utc)

    @pytest.fixture
    def _patch_datetime_now(self, monkeypatch):
        class DateTime:
            @classmethod
            def utcnow(cls):
                return TestSqsProducer.FAKE_TIME

        monkeypatch.setattr(datetime, 'datetime', DateTime)

    @pytest.fixture()
    def sqs_producer_config(self):
        return SqsProducerConfig()

    @pytest.fixture()
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def producer(self, mocker, sqs_producer_config, template_parser):
        mocker.patch('boto3.resource')
        return SqsProducer(config=sqs_producer_config, template_parser=template_parser)

    @pytest.mark.parametrize('actual_dto, message_config_mapping, expected_params', [
        param(AUTHN_REQUESTED_DTO, SQS_CONFIG_TIMEOUT_MESSAGE_KEY,
              TRANSACTION_TIMEOUT_KWARGS_WITH_DATA_AS_OBJ, id='1')
    ])
    def test_publish_message(self, actual_dto, producer, expected_params, message_config_mapping, mocker,
                             _patch_datetime_now):
        # Given
        producer.sqs_producer.send_message = mocker.Mock()

        # When
        producer.send_transaction_timeout(dto=actual_dto)

        # Then
        producer.sqs_producer.send_message.assert_called_once_with(message_payload_kwargs=expected_params)
