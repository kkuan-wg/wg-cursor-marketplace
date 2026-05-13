# Domain — Business Logic

The domain contains business rules. The **Service** orchestrates the flow and applies validation. The domain **never** imports adapters — only ports, utils, and layer helpers. Specific exceptions are handled in the Service; the app.py handler catches generic `Exception`.

---

## 1. Role of Domain

| Responsibility | Description |
|----------------|-------------|
| **Service** | Orchestrate flow, call ports, apply business rules |
| **Validators** | Input and data validation (classes in same file) |
| **Exceptions** | Handle specific exceptions; map to responder |

---

## 2. Conventions

- **File**: `domain/service.py`
- **Class**: `Service`
- **`__init__`**: Receives ports via dependency injection (keyword-only)
- **`process`**: Main entry point with `*, dto: dict`
- **Return**: `-> dict` for HTTP APIs; void for SQS/DDB Stream consumers
- **Private methods**: Single underscore prefix (`_build_response_dto`)
- **Method order**: public → public static → private → private static

---

## 3. Imports

- **Order**: stdlib → Lambda Layer (flk_api, flk_core, utils) → local ports
- **Allowed**: Ports, utils, layer helpers (PolicyHelper, TransactionHelper, UserHelper)
- **Forbidden**: Adapters

```python
# ✅ CORRECT
from logon_app_tx.port.repository import TransactionRepositoryPort, ClientConfigRepositoryPort
from logon_app_tx.port.responder import Responder
from utils.validation_helper import DtoValidator, ValidationException

# ❌ INCORRECT
from logon_app_tx.adapter.db_repository import TransactionRepository
```

---

## 4. Layer Helpers

Layer helpers from **folklore-lambda-layer** are **allowed and recommended** in the domain. They provide shared logic and reduce duplication. See [parts/layer-folklore-lambda.md](layer-folklore-lambda.md).

```python
from flk_api.policy_helper import PolicyHelper
from flk_api.transaction_helper import TransactionHelper
from flk_api.user_helper import UserHelper
from flk_core.core_commons import CoreCredentialEntityType, CoreAuthnTypes, CorePushTransaction
from utils.validation_helper import DtoValidator, ValidationException  # authpoint-lambda-layer

class Service:
    def __init__(self, ...):
        self.policy_helper = PolicyHelper()
        self.tx_helper = TransactionHelper()
        self.user_helper = UserHelper()
```

> **Never import from `flk_utils.*`** — it is deprecated. Use `utils.*` from authpoint-lambda-layer instead.

---

## 5. Validators

Validators should be **classes in the same file** when possible. Use `DtoValidator` from `utils.validation_helper` and define `REQUIRED_FIELDS` as class constants.

```python
class Validator:
    REQUIRED_FIELDS = {
        'accountId': str,
        'transactionId': str,
        'chainId': str
    }

    def __init__(self):
        self.dto_validator = DtoValidator()

    def validate_request(self, *, dto: dict):
        self.dto_validator.validate_required_fields(dto=dto, required_fields=self.REQUIRED_FIELDS)

    @staticmethod
    def validate_transaction(*, transaction: dict):
        if not transaction:
            raise DataValidationException(param='transaction')
        if is_item_expired(item=transaction):
            raise DataValidationException(param='transactionExpirationTimeInMillis')
```

---

## 6. Exceptions

Some exceptions come from the layer (e.g. `ValidationException` from `utils.validation_helper`). When creating a **local exception**, inherit from `Exception` and include parameters needed for logging.

```python
class DataValidationException(Exception):
    def __init__(self, *, param: str):
        self.param = param

    def __str__(self):
        return f'Error param: {self.param}'
```

```python
class ServiceUnavailableException(Exception):
    def __init__(self, *, reason: str):
        self.reason = reason
```

---

## 7. DTO Updates

When updating a DTO in place, use `update()` or `dto['key'] = value`. Do **not** use the merge operator (`|`) for updates — it creates a new dict instead of an in-place update.

```python
# ✅ CORRECT
dto['resourceId'] = transaction.get('header', {}).get('resourceId')
dto['swaEnabled'] = normalize_string_to_bool(value=dto.get('swaEnabled'))
dto.update({'key': 'value'})

# ❌ INCORRECT — merge creates new dict, not in-place update
dto = dto | {'key': 'value'}
```

Note: Using `dto | client_config` to pass a **combined** dict to another method is fine — that is creating a new dict for the call, not updating the original dto.

---

## 8. Invoker Empty Response

Invokers return `{}` on error. The domain must validate empty responses before using them.

```python
policy_data = self.api_invoker.retrieve_policy(dto=dto)
if not policy_data:
    # handle empty response
    return self.responder.precondition_failed(dto=dto)
```

---

## 9. Typical Flow

1. Validate input (Validator)
2. Call ports (repository, invoker, crypto)
3. Validate responses (empty invoker, missing data)
4. Apply business rules
5. Call responder (APIs) or publisher/producer (consumers)
6. Catch specific exceptions and map to responder

---

## 10. Example — HTTP API (tx_mw)

```python
import logging
from copy import deepcopy
from json import dumps

from logon_app_tx.port.crypto import CommCryptoPort
from logon_app_tx.port.repository import TransactionRepositoryPort, ClientConfigRepositoryPort
from logon_app_tx.port.responder import Responder
from utils.date_time_helper import is_item_expired
from utils.validation_helper import DtoValidator, ValidationException


class Service:

    def __init__(self, *, transaction_repository: TransactionRepositoryPort,
                 client_config_repository: ClientConfigRepositoryPort,
                 comm_crypto: CommCryptoPort,
                 responder: Responder):
        self.transaction_repository = transaction_repository
        self.client_config_repository = client_config_repository
        self.comm_crypto = comm_crypto
        self.responder = responder
        self.validator = Validator()

    def process(self, *, dto: dict) -> dict:
        logging.info(f'Processing Request. {dto}')
        try:
            self.validator.validate_request(dto=dto)

            transaction = self.transaction_repository.retrieve_transaction_by_account_id_and_transaction_id(dto=dto)
            self.validator.validate_transaction(transaction=transaction)

            dto['resourceId'] = transaction.get('header', {}).get('resourceId')
            client_config = self.client_config_repository.retrieve_client_config_by_account_id_and_resource_id(dto=dto)
            self.validator.validate_client_config(client_config=client_config)

            response_dto = self._build_response_dto(dto=dto, transaction=transaction)
            encrypted_data = self.comm_crypto.encrypt_data(dto=response_dto | client_config)
            logging.info(f'Request successfully processed. {dto}')
            return self.responder.success(encrypted_data=encrypted_data, dto=response_dto)

        except ValidationException as ex:
            logging.error(f'Bad request. {ex}. {dto}.')
            return self.responder.bad_request(dto=dto)
        except DataValidationException as ex:
            logging.error(f'Precondition failed. {ex}. {dto}.')
            return self.responder.precondition_failed(dto=dto)

    def _build_response_dto(self, *, dto: dict, transaction: dict) -> dict:
        response_dto = deepcopy(dto)
        response = self._build_response(transaction=transaction)
        response_dto['responsePayload'] = dumps(response, default=int, ensure_ascii=False, separators=(',', ':'))
        return response_dto

    @staticmethod
    def _build_response(*, transaction: dict) -> dict:
        return {
            'transactionId': transaction.get('transactionId'),
            'transactionStatus': transaction.get('transactionResult', {}).get('transactionStatus'),
            'authnStatus': transaction.get('transactionResult', {}).get('authnStatus'),
            'authnFailureReason': transaction.get('transactionResult', {}).get('authnFailureReason')
        }


class Validator:
    REQUIRED_FIELDS = {
        'accountId': str,
        'transactionId': str,
        'chainId': str
    }

    def __init__(self):
        self.dto_validator = DtoValidator()

    def validate_request(self, *, dto: dict):
        self.dto_validator.validate_required_fields(dto=dto, required_fields=self.REQUIRED_FIELDS)

    @staticmethod
    def validate_transaction(*, transaction: dict):
        if not transaction:
            raise DataValidationException(param='transaction')
        if is_item_expired(item=transaction):
            raise DataValidationException(param='transactionExpirationTimeInMillis')

    @staticmethod
    def validate_client_config(*, client_config: dict):
        if not client_config:
            raise DataValidationException(param='clientConfig')


class DataValidationException(Exception):
    def __init__(self, *, param: str):
        self.param = param

    def __str__(self):
        return f'Error param: {self.param}'
```

---

## 11. Example — DDB Stream Listener (tx_listener)

```python
import logging

from flk_api.logon_app.api_commons import LogonAppTransactionStatus
from flk_api.transaction_helper import TX_AUTHN_STATUS_AUTHORIZED, TX_AUTHN_STATUS_UNAUTHORIZED
from logon_app_tx_listener.port.producer import ProducerPort
from logon_app_tx_listener.port.publisher import Publisher
from utils.fallback_helper import execute_with_fallback


class Service:

    def __init__(self, *, publisher: Publisher, producer: ProducerPort):
        self.publisher = publisher
        self.producer = producer

    def process(self, *, dto: dict):
        logging.info(f'Processing DTO {dto}')
        if dto['eventType'] == 'INSERT':
            self._handle_insert_transaction(dto=dto)
        elif dto['eventType'] == 'MODIFY':
            self._handle_modify_transaction(dto=dto)
        else:
            logging.debug(f'Stream discarded, invalid eventType. {dto}')

    def _handle_insert_transaction(self, dto: dict):
        transaction_result = dto.get('transactionResult', {})
        transaction_status = transaction_result.get('transactionStatus')

        if transaction_status == LogonAppTransactionStatus.TX_STATUS_CREATED:
            execute_with_fallback(dto=dto, primary=self.publisher.transaction_created,
                                  fallback=self.producer.transaction_created)
        elif transaction_status == LogonAppTransactionStatus.TX_STATUS_NON_MFA_POLICY_DONE:
            execute_with_fallback(dto=dto, primary=self.publisher.transaction_non_mfa_done,
                                  fallback=self.producer.transaction_non_mfa_done)
        else:
            logging.error(f'Stream discarded, invalid transactionStatus {dto}')

    def _handle_modify_transaction(self, dto: dict):
        transaction_result = dto.get('transactionResult', {})
        transaction_status = transaction_result.get('transactionStatus')
        authn_status = transaction_result.get('authnStatus')

        if transaction_status == LogonAppTransactionStatus.TX_STATUS_AUTHN_DONE:
            if authn_status == TX_AUTHN_STATUS_AUTHORIZED:
                execute_with_fallback(dto=dto, primary=self.publisher.transaction_authorized,
                                      fallback=self.producer.transaction_authorized)
            elif authn_status == TX_AUTHN_STATUS_UNAUTHORIZED:
                execute_with_fallback(dto=dto, primary=self.publisher.transaction_unauthorized,
                                      fallback=self.producer.transaction_unauthorized)
            else:
                logging.error(f'Stream discarded, invalid authnStatus {dto}')
        elif transaction_status == LogonAppTransactionStatus.TX_STATUS_FORGOT_TOKEN_ENABLE_DONE:
            execute_with_fallback(dto=dto, primary=self.publisher.transaction_forgot_token_enable_done,
                                  fallback=self.producer.transaction_forgot_token_enable_done)
        else:
            logging.error(f'Stream discarded, invalid transactionStatus {dto}')
```

---

## 12. Example — SQS Consumer (core_data_consumer)

```python
import logging
from copy import deepcopy

from flk_core.core_commons import CoreCredentialEntityType, CoreCredentialDataEventType
from utils.validation_helper import DtoValidator, ValidationException
from logon_app_core_data_consumer.port.repository import Repository

_SUPPORTED_EVENT_TYPES = (
    CoreCredentialDataEventType.CORE_HW_TOKEN_ADDED,
    CoreCredentialDataEventType.CORE_HW_TOKEN_BLOB_UPDATED,
    CoreCredentialDataEventType.CORE_SW_TOKEN_ADDED,
    CoreCredentialDataEventType.CORE_SW_TOKEN_BLOB_UPDATED
)


class Service:

    def __init__(self, *, repository: Repository):
        self.repository = repository
        self.event_validator = EventValidator()

    def process(self, *, dto: dict):
        logging.info(f'Processing DTO {dto}')

        try:
            self.event_validator.validate_required_fields(dto=dto)
            if dto.get('eventType') in _SUPPORTED_EVENT_TYPES:
                user_detail = self.repository.retrieve_user_detail_by_account_id_and_user_id(dto=dto)
                if user_detail.get('email') and user_detail.get('username'):
                    sync_dto = deepcopy(dto)
                    sync_dto['email'] = user_detail['email']
                    sync_dto['username'] = user_detail['username']
                    self.repository.save_user_token_sync(dto=sync_dto)
                else:
                    logging.info(f'Message discarded. User not provisioned. {dto}.')
            else:
                logging.error(f'Message discarded. Invalid eventType. {dto}.')
        except ValidationException as ex:
            logging.error(f'Message discarded. Exception: {ex}. {dto}.')


class EventValidator:
    REQUIRED_FIELDS = {
        'accountId': str,
        'userId': int
    }

    def __init__(self):
        self.dto_validator = DtoValidator()

    def validate_required_fields(self, *, dto: dict):
        self._validate_event_data(dto=dto)
        self._validate_entity_type(dto=dto)

    def _validate_event_data(self, *, dto: dict):
        self.dto_validator.validate_required_fields(dto=dto, required_fields=self.REQUIRED_FIELDS)

    @staticmethod
    def _validate_entity_type(*, dto: dict):
        if dto.get('entityType') not in (CoreCredentialEntityType.CREDENTIAL_TYPE_TOKEN_SOFTWARE,
                                         CoreCredentialEntityType.CREDENTIAL_TYPE_TOKEN_HARDWARE):
            raise ValidationException(param='entityType')
```

---

## 13. Example — Simple SQS Consumer (tx_timeout_publisher)

```python
import logging

from flk_api.logon_app.api_commons import LOGON_APP_TX_EVENT_TYPE_TRANSACTION_CREATED, LogonAppTransactionStatus
from logon_app_tx_timeout_publisher.port.producer import ProducerPort
from logon_app_tx_timeout_publisher.port.repository import Repository


class Service:

    def __init__(self, *, producer: ProducerPort, repository: Repository):
        self.producer = producer
        self.repository = repository

    def process(self, *, dto: dict):
        logging.info(f'Processing message. {dto}')
        if dto['eventType'] == LOGON_APP_TX_EVENT_TYPE_TRANSACTION_CREATED:
            transaction = self.repository.retrieve_transaction_by_account_id_and_transaction_id(dto=dto)
            if transaction and transaction['transactionResult']['transactionStatus'] in (
                    LogonAppTransactionStatus.TX_STATUS_CREATED, LogonAppTransactionStatus.TX_STATUS_PROCESSING):
                self.producer.send_tx_timed_out(dto=dto)
            else:
                logging.info(f'Message discarded. {dto}')
        else:
            logging.warning(f'Message discarded. {dto}')
```

---

## 14. Checklist

- [ ] No adapter imports — only ports, utils, layer helpers
- [ ] `process(self, *, dto: dict)` with keyword-only args
- [ ] Validators as classes in same file when possible
- [ ] Layer helpers used for generic logic
- [ ] Local exceptions inherit from Exception with params for logging
- [ ] Empty invoker responses validated before use
- [ ] Specific exceptions caught and mapped to responder
- [ ] DTO updates use `update()` or `dto['key'] = value`, not `|`
- [ ] Method order: public → public static → private → private static
