# Publisher and Producer Tests

Tests for `SnsPublisher` and `SqsProducer` adapters. Both follow the same pattern: mock the underlying layer's `publish_message` / `send_message`, call the adapter method, and assert the exact kwargs passed.

---

## SnsPublisher

File: `sns_publisher_test.py`

```python
import datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from logon_app_tx_listener.adapter.sns_publisher import SnsPublisher
from logon_app_tx_listener.configuration import SnsPublishConfig
from tests.data.transaction_stream.logon_app_tx_listener.ddb_stream_constants import (
    TX_CREATED_DTO, TX_AUTHORIZED_DTO, TX_UNAUTHORIZED_DTO,
    TX_NON_MFA_DONE_DTO, TX_FORGOT_TOKEN_ENABLE_DONE_DTO
)
from tests.data.transaction_stream.logon_app_tx_listener.sns_publisher_constants import (
    TX_CREATED_KWARGS, TX_AUTHORIZED_KWARGS, TX_UNAUTHORIZED_KWARGS,
    TX_NON_MFA_DONE_KWARGS, TX_FORGOT_TOKEN_ENABLE_DONE_KWARGS
)


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
        return SnsPublisher(config=SnsPublishConfig(), template_parser=parser)

    @pytest.mark.parametrize('actual_dto, method_called, expected_kwargs', [
        param(TX_CREATED_DTO, 'transaction_created', TX_CREATED_KWARGS, id='1'),
        param(TX_AUTHORIZED_DTO, 'transaction_authorized', TX_AUTHORIZED_KWARGS, id='2'),
        param(TX_UNAUTHORIZED_DTO, 'transaction_unauthorized', TX_UNAUTHORIZED_KWARGS, id='3'),
        param(TX_NON_MFA_DONE_DTO, 'transaction_non_mfa_done', TX_NON_MFA_DONE_KWARGS, id='4'),
        param(TX_FORGOT_TOKEN_ENABLE_DONE_DTO, 'transaction_forgot_token_enable_done',
              TX_FORGOT_TOKEN_ENABLE_DONE_KWARGS, id='5'),
    ])
    def test_publish_message(self, publisher, actual_dto, method_called: str, expected_kwargs,
                             mocker, _patch_datetime_now):
        # Given
        publisher.sns_publisher.publish_message = mocker.Mock()

        # When
        getattr(publisher, method_called)(dto=actual_dto)

        # Then
        publisher.sns_publisher.publish_message.assert_called_once_with(
            message_payload_kwargs=expected_kwargs)
```

Key points:
- `_patch_datetime_now` uses `monkeypatch.setattr` to freeze `datetime.datetime.utcnow` — used when the message payload includes a timestamp
- `getattr(publisher, method_called)(dto=actual_dto)` — single parametrized test covers all event types
- Mock target is `publisher.sns_publisher.publish_message` (the layer method), not the adapter method itself

---

## sns_publisher_constants.py — kwargs structure

Each constant is the exact dict passed to `publish_message(message_payload_kwargs=...)`. The `Message` field is a JSON string.

```python
TX_CREATED_KWARGS = {
    'Message': '{"type": "LOGON_APP_TRANSACTION_CREATED", "entityType": "LOGON_APP_TRANSACTION", '
               '"source": "flk-logon-app-tx-listener", "timestamp": 1632960000000, '
               '"data": {"accountId": "WGC-1-1dd9eb0da71842ada3f5", '
               '"transactionId": "fb19dc73-e38c-4c1b-a8bb-a92d5f837b2b", '
               '"userId": 1000608, ...}, "entityId": 1000608}',
    'MessageAttributes': {
        'entityType': {'DataType': 'String', 'StringValue': 'LOGON_APP_TRANSACTION'},
        'eventType': {'DataType': 'String', 'StringValue': 'LOGON_APP_TRANSACTION_CREATED'}
    },
    'MessageGroupId': 'WGC-1-1dd9eb0da71842ada3f5#USER#1000608',
    'TopicArn': 'flk-logon-app-tx-result-topic.fifo'
}

TX_AUTHORIZED_KWARGS = {
    'Message': '{"type": "LOGON_APP_TRANSACTION_AUTHORIZED", ...}',
    'MessageAttributes': {
        'entityType': {'DataType': 'String', 'StringValue': 'LOGON_APP_TRANSACTION'},
        'eventType': {'DataType': 'String', 'StringValue': 'LOGON_APP_TRANSACTION_AUTHORIZED'}
    },
    'MessageGroupId': 'WGC-1-1dd9eb0da71842ada3f5#USER#1000608',
    'TopicArn': 'flk-logon-app-tx-result-topic.fifo'
}
```

The `timestamp` in `Message` must match `FAKE_TIME` converted to milliseconds.

---

## SqsProducer

File: `sqs_producer_test.py`. Identical pattern — mock `producer.sqs_producer.send_message` instead.

```python
import datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from logon_app_tx_listener.adapter.sqs_producer import SqsProducer
from logon_app_tx_listener.configuration import SqsProducerConfig
from tests.data.transaction_stream.logon_app_tx_listener.ddb_stream_constants import (
    TX_CREATED_DTO, TX_AUTHORIZED_DTO
)
from tests.data.transaction_stream.logon_app_tx_listener.sqs_producer_constants import (
    TX_CREATED_KWARGS, TX_AUTHORIZED_KWARGS
)


class TestSqsProducer:
    FAKE_TIME = datetime.datetime(2021, 9, 30, 0, 0, tzinfo=datetime.timezone.utc)

    @pytest.fixture
    def _patch_datetime_now(self, monkeypatch):
        class DateTime:
            @classmethod
            def utcnow(cls):
                return TestSqsProducer.FAKE_TIME

        monkeypatch.setattr(datetime, 'datetime', DateTime)

    @pytest.fixture
    def parser(self):
        return TemplateParser()

    @pytest.fixture
    def producer(self, parser):
        return SqsProducer(config=SqsProducerConfig(), template_parser=parser)

    @pytest.mark.parametrize('actual_dto, method_called, expected_kwargs', [
        param(TX_CREATED_DTO, 'transaction_created', TX_CREATED_KWARGS, id='1'),
        param(TX_AUTHORIZED_DTO, 'transaction_authorized', TX_AUTHORIZED_KWARGS, id='2'),
    ])
    def test_send_message(self, producer, actual_dto, method_called: str, expected_kwargs,
                          mocker, _patch_datetime_now):
        # Given
        producer.sqs_producer.send_message = mocker.Mock()

        # When
        getattr(producer, method_called)(dto=actual_dto)

        # Then
        producer.sqs_producer.send_message.assert_called_once_with(
            message_payload_kwargs=expected_kwargs)
```

---

## Responder tests

File: `api_responder_test.py`. Tests each response method and validates `API_ERROR_CODES` constant.

```python
import pytest

from logon_app_authn_api.adapter.api_responder import ApiResponder
from logon_app_authn_api.configuration import ResponderConfig, API_ERROR_CODES
from tests.api.logon_app_authn_api.http_event_constants import HTTP_EVENT_DTO
from tests.api.logon_app_authn_api.api_responder_constants import (
    SUCCESS_RESPONSE, UNAUTHORIZED_RESPONSE, BAD_REQUEST_RESPONSE,
    PRECONDITION_FAILED_RESPONSE, SERVER_ERROR_RESPONSE, EXPECTED_API_ERROR_CODES
)


class TestResponder:

    @pytest.fixture
    def responder(self):
        return ApiResponder(config=ResponderConfig())

    def test_responder_success_response(self, responder):
        # Given

        # When
        actual_response = responder.success(dto=HTTP_EVENT_DTO, encrypted_data='<encrypted>')

        # Then
        assert actual_response == SUCCESS_RESPONSE

    def test_responder_unauthorized_response(self, responder):
        # Given

        # When
        actual_response = responder.unauthorized(dto=HTTP_EVENT_DTO)

        # Then
        assert actual_response == UNAUTHORIZED_RESPONSE

    def test_api_error_codes(self):
        # Given

        # When

        # Then
        assert API_ERROR_CODES == EXPECTED_API_ERROR_CODES
```

`test_api_error_codes` validates the `API_ERROR_CODES` constant in `configuration.py` against the expected values. This catches accidental changes to error codes.

---

## Checklist

### SnsPublisher / SqsProducer
- [ ] `_patch_datetime_now` fixture freezes time via `monkeypatch.setattr`
- [ ] `FAKE_TIME` defined as class-level constant
- [ ] Single parametrized `test_publish_message` / `test_send_message` covers all event types
- [ ] Mock target is the layer method (`publisher.sns_publisher.publish_message`)
- [ ] `expected_kwargs` constants include full `Message` JSON string with frozen timestamp
- [ ] `getattr(publisher, method_called)` pattern used for dynamic method dispatch

### Responder
- [ ] One test per response method
- [ ] `test_api_error_codes` validates `API_ERROR_CODES` constant
- [ ] `EXPECTED_API_ERROR_CODES` defined in `api_responder_constants.py`
