# Publisher Adapter — SNS

Implements publisher ports using the authpoint-lambda-layer `adapter.transport.sns_publisher.SnsPublisher`. File: `sns_publisher.py`. Use a private `_publish` helper to avoid duplication when multiple methods follow the same pattern. See [parts/layer-authpoint-lambda.md](../layer-authpoint-lambda.md).

---

## Layer Component

```python
from adapter.transport.sns_publisher import SnsPublisher
```

---

> **Two calling patterns:** `publish_data_as_obj(data, event_key, ...)` is the direct shortcut. The granular pattern — `build_message_payload_with_obj_data(...)` + `publish_message(...)` — is used when logging the response (`MessageId`) is needed. Both are correct; prefer the granular pattern when logging publish confirmations.

## Example 1: Request events (with _publish helper)

```python
import logging
from copy import deepcopy

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.sns_publisher import SnsPublisher
from flk_core.core_commons import SourceType, CoreRequestEventType
from logon_app_authn_api.configuration import SnsPublisherConfig, MSG_PUSH_REQUESTED, \
    MSG_QRCODE_REQUESTED, MSG_OTP_REQUESTED, MSG_AUTHN_CODE_REQUESTED
from logon_app_authn_api.port.publisher import RequestPublisherPort


class SnsMessagePublisher(RequestPublisherPort):

    def __init__(self, *, config: SnsPublisherConfig, parser: TemplateParser):
        self.publisher = SnsPublisher(config=config.as_dict, template_parser=parser)

    def push_requested(self, *, dto: dict):
        self._publish(dto=dto, event_key=MSG_PUSH_REQUESTED,
                      event_type=CoreRequestEventType.EVENT_TYPE_PUSH_REQUESTED)

    def qrcode_requested(self, *, dto: dict):
        self._publish(dto=dto, event_key=MSG_QRCODE_REQUESTED,
                      event_type=CoreRequestEventType.EVENT_TYPE_QRCODE_REQUESTED)

    def otp_requested(self, *, dto: dict):
        self._publish(dto=dto, event_key=MSG_OTP_REQUESTED,
                      event_type=CoreRequestEventType.EVENT_TYPE_OTP_REQUESTED)

    def authn_code_requested(self, *, dto: dict):
        self._publish(dto=dto, event_key=MSG_AUTHN_CODE_REQUESTED,
                      event_type=CoreRequestEventType.EVENT_TYPE_AUTHN_CODE_REQUESTED)

    def _publish(self, *, dto: dict, event_key: str, event_type: str):
        requested_dto = deepcopy(dto)
        requested_dto.update({'sourceType': SourceType.DESKTOP_LOGON})
        kwargs = self.publisher.build_message_payload_with_obj_data(data=requested_dto, event_key=event_key,
                                                                    account_id=dto['accountId'],
                                                                    entity_id=dto['userId'])
        logging.debug(f'Message built: {kwargs}')
        response = self.publisher.publish_message(message_payload_kwargs=kwargs)
        logging.info(f'{event_type} published. AccountId: {dto.get("accountId")}, '
                     f'AuthnTypes: {dto.get("authnTypes")}, UserId: {dto.get("userId")}, '
                     f'MessageId: {response.get("MessageId")}')
```

---

## Example 2: Transaction events

```python
import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.sns_publisher import SnsPublisher as SnsPublisherLayer
from logon_app_tx_listener.configuration import SnsPublishConfig, LOGON_APP_TRANSACTION_CREATED_KEY, \
    LOGON_APP_TRANSACTION_NON_MFA_POLICY_RETRIEVED_KEY, LOGON_APP_TRANSACTION_AUTHORIZED_KEY, \
    LOGON_APP_TRANSACTION_UNAUTHORIZED_KEY, LOGON_APP_TRANSACTION_FORGOT_TOKEN_ENABLE_RETRIEVED_KEY
from logon_app_tx_listener.port.publisher import Publisher


class SnsPublisher(Publisher):

    def __init__(self, *, config: SnsPublishConfig, parser: TemplateParser):
        self.sns_publisher = SnsPublisherLayer(config=config.as_dict, template_parser=parser)

    def transaction_created(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_obj_data(
            data=dto, event_key=LOGON_APP_TRANSACTION_CREATED_KEY, entity_id=dto['userId'])
        self._publish(dto=dto, event_type='TRANSACTION_CREATED', message_payload_kwargs=kwargs)

    def transaction_non_mfa_done(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_obj_data(
            data=dto, event_key=LOGON_APP_TRANSACTION_NON_MFA_POLICY_RETRIEVED_KEY, entity_id=dto['userId'])
        self._publish(dto=dto, event_type='TRANSACTION_NON_MFA_POLICY_RETRIEVED', message_payload_kwargs=kwargs)

    def transaction_authorized(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_obj_data(
            data=dto, event_key=LOGON_APP_TRANSACTION_AUTHORIZED_KEY, entity_id=dto['userId'])
        self._publish(dto=dto, event_type='TRANSACTION_AUTHORIZED', message_payload_kwargs=kwargs)

    def transaction_unauthorized(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_obj_data(
            data=dto, event_key=LOGON_APP_TRANSACTION_UNAUTHORIZED_KEY, entity_id=dto['userId'])
        self._publish(dto=dto, event_type='TRANSACTION_UNAUTHORIZED', message_payload_kwargs=kwargs)

    def transaction_forgot_token_enable_done(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_obj_data(
            data=dto, event_key=LOGON_APP_TRANSACTION_FORGOT_TOKEN_ENABLE_RETRIEVED_KEY, entity_id=dto['userId'])
        self._publish(dto=dto, event_type='TRANSACTION_FORGOT_TOKEN_ENABLE_RETRIEVED', message_payload_kwargs=kwargs)

    def _publish(self, *, dto: dict, event_type: str, message_payload_kwargs: dict):
        logging.debug(f'Message built: {message_payload_kwargs}')
        response = self.sns_publisher.publish_message(message_payload_kwargs=message_payload_kwargs)
        logging.info(f'{event_type} published. MessageId: {response.get("MessageId")}, '
                     f'AccountId: {dto["accountId"]}, UserId: {dto["userId"]}.')
```

---

## Checklist

- [ ] File: `sns_publisher.py`
- [ ] Uses `SnsPublisher` from `adapter.transport.sns_publisher`
- [ ] Passes `config.as_dict` and `template_parser=parser` to authpoint-lambda-layer
- [ ] Use `_publish` helper when multiple methods share the same pattern
