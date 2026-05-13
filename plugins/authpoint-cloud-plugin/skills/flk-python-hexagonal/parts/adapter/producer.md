# Producer Adapter — SQS

Implements producer ports using the authpoint-lambda-layer `adapter.transport.sqs_producer.SqsProducer`. File: `sqs_producer.py`. Use a private `_send` helper when multiple methods share the same pattern. See [parts/layer-authpoint-lambda.md](../layer-authpoint-lambda.md).

---

## Layer Component

```python
from adapter.transport.sqs_producer import SqsProducer
```

---

> **Two calling patterns:** `send_data_as_obj(data, message_key, ...)` is the direct shortcut. The granular pattern — `build_message_payload_with_obj_data(...)` + `send_message(...)` — is used when logging the response (`MessageId`) is needed. Both are correct; prefer the granular pattern when logging send confirmations.

## Example 1: Multiple methods (with _send helper)

```python
import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.sqs_producer import SqsProducer as SqsProducerLayer
from logon_app_tx_listener.configuration import SqsProducerConfig, LOGON_APP_TRANSACTION_CREATED_KEY, \
    LOGON_APP_TRANSACTION_NON_MFA_POLICY_RETRIEVED_KEY, LOGON_APP_TRANSACTION_AUTHORIZED_KEY, \
    LOGON_APP_TRANSACTION_UNAUTHORIZED_KEY, LOGON_APP_TRANSACTION_FORGOT_TOKEN_ENABLE_RETRIEVED_KEY
from logon_app_tx_listener.port.producer import ProducerPort


class SqsProducer(ProducerPort):

    def __init__(self, *, config: SqsProducerConfig, parser: TemplateParser):
        self.sqs_producer = SqsProducerLayer(config=config.as_dict, template_parser=parser)

    def transaction_created(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=LOGON_APP_TRANSACTION_CREATED_KEY, entity_id=dto['userId'])
        self._send(dto=dto, event_type='TRANSACTION_CREATED', message_payload_kwargs=kwargs)

    def transaction_non_mfa_done(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=LOGON_APP_TRANSACTION_NON_MFA_POLICY_RETRIEVED_KEY, entity_id=dto['userId'])
        self._send(dto=dto, event_type='TRANSACTION_NON_MFA_POLICY_RETRIEVED', message_payload_kwargs=kwargs)

    def transaction_authorized(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=LOGON_APP_TRANSACTION_AUTHORIZED_KEY, entity_id=dto['userId'])
        self._send(dto=dto, event_type='TRANSACTION_AUTHORIZED', message_payload_kwargs=kwargs)

    def transaction_unauthorized(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=LOGON_APP_TRANSACTION_UNAUTHORIZED_KEY, entity_id=dto['userId'])
        self._send(dto=dto, event_type='TRANSACTION_UNAUTHORIZED', message_payload_kwargs=kwargs)

    def transaction_forgot_token_enable_done(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=LOGON_APP_TRANSACTION_FORGOT_TOKEN_ENABLE_RETRIEVED_KEY, entity_id=dto['userId'])
        self._send(dto=dto, event_type='TRANSACTION_FORGOT_TOKEN_ENABLE_RETRIEVED', message_payload_kwargs=kwargs)

    def _send(self, *, dto: dict, event_type: str, message_payload_kwargs: dict):
        logging.debug(f'Message built: {message_payload_kwargs}')
        response = self.sqs_producer.send_message(message_payload_kwargs=message_payload_kwargs)
        logging.info(f'Fallback {event_type} sent. MessageId: {response.get("MessageId")}, '
                     f'AccountId: {dto["accountId"]}, UserId: {dto["userId"]}.')
```

---

## Example 2: Single method

```python
import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.sqs_producer import SqsProducer as SqsProducerLayer
from logon_app_tx_timeout_publisher.configuration import SqsProducerConfig, MSG_LOGON_APP_TX_TIMEOUT
from logon_app_tx_timeout_publisher.port.producer import ProducerPort


class SqsProducer(ProducerPort):

    def __init__(self, *, config: SqsProducerConfig, parser: TemplateParser):
        self.sqs_producer = SqsProducerLayer(config=config.as_dict, template_parser=parser)

    def send_tx_timed_out(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(data=dto, message_key=MSG_LOGON_APP_TX_TIMEOUT)
        logging.debug(f'Message built: {kwargs}')
        response = self.sqs_producer.send_message(message_payload_kwargs=kwargs)
        logging.info(f'Transaction timeout sent. MessageId: {response.get("MessageId")} {dto}')
```

---

## Checklist

- [ ] File: `sqs_producer.py`
- [ ] Uses `SqsProducer` from `adapter.transport.sqs_producer`
- [ ] Passes `config.as_dict` and `template_parser=parser` to authpoint-lambda-layer
- [ ] Use `_send` helper when multiple methods share the same pattern
