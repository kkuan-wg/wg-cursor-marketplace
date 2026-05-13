# Event Adapter Tests

Tests for `HttpEvent`, `SqsEvent` and `DdbStreamEvent`. Each validates that the event adapter correctly parses the raw Lambda event into the expected DTO.

---

## HttpEvent

File: `http_event_test.py`

```python
import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.http_event import HttpEvent
from logon_app_authn_api.configuration import HttpEventConfig
from tests.api.logon_app_authn_api.http_event_constants import (
    HTTP_EVENT, HTTP_EVENT_DTO,
    HTTP_EVENT_SWA_ENABLED, HTTP_EVENT_SWA_ENABLED_DTO
)


class TestHttpEvent:

    @pytest.fixture
    def http_event(self):
        return HttpEvent(config=HttpEventConfig().as_dict, template_parser=TemplateParser())

    @pytest.mark.parametrize('actual_event, expected_result', [
        param(HTTP_EVENT, HTTP_EVENT_DTO, id='1'),
        param(HTTP_EVENT_SWA_ENABLED, HTTP_EVENT_SWA_ENABLED_DTO, id='2')
    ])
    def test_parse_dto_with_success(self, actual_event: dict, expected_result, http_event):
        # Given

        # When
        actual_result = http_event.as_dto(event=actual_event)

        # Then
        assert actual_result == expected_result
```

Key points:
- Fixture instantiates `HttpEvent` with `Config().as_dict` — event adapters always receive a dict
- `TemplateParser()` is real, never mocked
- Parametrize covers all event variants (standard, SWA-enabled, etc.)
- Given section is empty when no setup is needed — keep the comment

---

## SqsEvent

File: `sqs_message_test.py`

```python
import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.sqs_event import SqsEvent
from logon_app_tx_consumer.configuration import SqsEventConfig
from tests.transaction.logon_app_tx_consumer.sqs_message_constants import (
    SQS_EVENT, SQS_EVENT_DTO,
    SQS_EVENT_EXPIRED, SQS_EVENT_EXPIRED_DTO
)


class TestSqsMessage:

    @pytest.fixture
    def sqs_event(self):
        return SqsEvent(config=SqsEventConfig().as_dict, template_parser=TemplateParser())

    @pytest.mark.parametrize('actual_event, expected_result', [
        param(SQS_EVENT, SQS_EVENT_DTO, id='1'),
        param(SQS_EVENT_EXPIRED, SQS_EVENT_EXPIRED_DTO, id='2'),
    ])
    def test_parse_dto_with_success(self, actual_event: dict, expected_result: dict, sqs_event):
        # Given

        # When
        actual_result = sqs_event.as_dto(event=actual_event)

        # Then
        assert actual_result == expected_result
```

When `maxConsumeTimeout` is configured, the expired variant should have `eventExpired: True` in the expected DTO.

---

## DdbStreamEvent

File: `ddb_stream_test.py`

```python
import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.ddb_stream_event import DdbStreamEvent
from logon_app_tx_listener.configuration import DdbStreamEventConfig
from tests.data.transaction_stream.logon_app_tx_listener.ddb_stream_constants import (
    TX_CREATED_EVENT, TX_CREATED_DTO,
    TX_AUTHORIZED_EVENT, TX_AUTHORIZED_DTO,
    TX_UNAUTHORIZED_EVENT, TX_UNAUTHORIZED_DTO
)


class TestDdbStreamEvent:

    @pytest.fixture
    def ddb_stream_event(self):
        return DdbStreamEvent(config=DdbStreamEventConfig().as_dict, template_parser=TemplateParser())

    @pytest.mark.parametrize('actual_event, expected_result', [
        param(TX_CREATED_EVENT, TX_CREATED_DTO, id='1'),
        param(TX_AUTHORIZED_EVENT, TX_AUTHORIZED_DTO, id='2'),
        param(TX_UNAUTHORIZED_EVENT, TX_UNAUTHORIZED_DTO, id='3'),
    ])
    def test_parse_dto_with_success(self, actual_event: dict, expected_result: dict, ddb_stream_event):
        # Given

        # When
        actual_result = ddb_stream_event.as_dto(event=actual_event)

        # Then
        assert actual_result == expected_result
```

DDB stream constants files tend to be large (raw DynamoDB typed-attribute events + parsed DTOs). Keep raw events and DTOs in the same `ddb_stream_constants.py` file.

---

## Constants pattern for event tests

```python
# http_event_constants.py
from copy import deepcopy

HTTP_EVENT = {
    'resource': 'abc',
    'httpMethod': 'POST',
    'headers': {
        'Request-Id': '12345',
        'source-ip': '194.168.1.222',
        'Cloudfront-Viewer-Country': 'BR',
    },
    'requestContext': {'extendedRequestId': '12345'},
    'pathParameters': {'accountId': 'WGC-0', 'resourceId': '123'},
    'body': {'data': '<encrypted>', 'chainId': '00cf2b3f-2d69-4ee9-ac9b-87271837bbe2'}
}

HTTP_EVENT_SWA_ENABLED = deepcopy(HTTP_EVENT)
HTTP_EVENT_SWA_ENABLED['headers']['wgc-swa-enabled'] = 'true'

HTTP_EVENT_DTO = {
    'accountId': 'WGC-0',
    'resourceId': '123',
    'encryptedData': '<encrypted>',
    'requestId': '12345',
    'country': 'BR',
    ...
}

HTTP_EVENT_SWA_ENABLED_DTO = deepcopy(HTTP_EVENT_DTO) | {'swaEnabled': 'true'}
```

---

## Checklist

- [ ] Fixture uses `Config().as_dict` (not `Config()`) — event adapters receive a dict
- [ ] `TemplateParser()` is a real instance, never mocked
- [ ] All event variants covered via `parametrize`
- [ ] Raw event and expected DTO defined in `*_constants.py`
- [ ] `SqsEvent` expired variant included when `maxConsumeTimeout` is configured
