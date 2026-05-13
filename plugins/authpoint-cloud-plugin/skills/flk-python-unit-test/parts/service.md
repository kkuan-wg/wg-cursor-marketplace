# Service Tests

File: `service_test.py`. Tests business logic in isolation — all adapter methods are mocked at the object level.

---

## Fixture chain

Build the fixture chain from bottom up: `template_parser` → individual adapters → `service`. Inject `_patch_*` fixtures into `service`, not into individual tests.

```python
from copy import deepcopy
from datetime import datetime, timezone

import pytest
from botocore.exceptions import BotoCoreError
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from logon_app_authn_api.adapter.db_repository import ClientConfigRepository, UserDetailRepository, TransactionRepository
from logon_app_authn_api.adapter.api_responder import ApiResponder
from logon_app_authn_api.adapter.sns_publisher import SnsMessagePublisher
from logon_app_authn_api.configuration import (
    ResponderConfig, ClientConfigRepositoryConfig,
    UserDetailRepositoryConfig, TransactionRepositoryConfig, SnsPublisherConfig
)
from logon_app_authn_api.domain.service import Service, Validator
from tests.api.logon_app_authn_api.service_constants import (
    EXPECTED_REQUIRED_FIELDS, CLIENT_CONFIG_DB, USER_DETAIL_DB,
    SUCCESS_RESPONSE, BAD_REQUEST_RESPONSE, HTTP_EVENT_DTO
)


class TestService:
    FAKE_TIME = datetime(2021, 9, 30, 0, 0, tzinfo=timezone.utc)

    @pytest.fixture
    def _patch_get_timestamp_now(self, mocker):
        patch_datetime = mocker.patch('utils.date_time_helper.datetime')
        patch_datetime.now.return_value = TestService.FAKE_TIME

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def client_config_repository(self, template_parser):
        return ClientConfigRepository(config=ClientConfigRepositoryConfig(), parser=template_parser)

    @pytest.fixture
    def user_detail_repository(self, template_parser):
        return UserDetailRepository(config=UserDetailRepositoryConfig(), parser=template_parser)

    @pytest.fixture
    def transaction_repository(self, template_parser):
        return TransactionRepository(config=TransactionRepositoryConfig(), parser=template_parser)

    @pytest.fixture
    def responder(self):
        return ApiResponder(config=ResponderConfig())

    @pytest.fixture
    def publisher(self, template_parser):
        return SnsMessagePublisher(config=SnsPublisherConfig(), parser=template_parser)

    @pytest.fixture
    def service(self, client_config_repository, user_detail_repository, transaction_repository,
                responder, publisher, _patch_get_timestamp_now):
        return Service(
            client_config_repository=client_config_repository,
            user_detail_repository=user_detail_repository,
            transaction_repository=transaction_repository,
            responder=responder,
            publisher=publisher
        )
```

Key points:
- `_patch_get_timestamp_now` is injected into `service` fixture — time is frozen for all tests automatically
- `FAKE_TIME` is a class-level constant on `TestService`
- `TemplateParser()` is real and shared across adapters via the `template_parser` fixture

---

## test_required_fields

Validates `Validator.REQUIRED_FIELDS` constants against expected values. No mocking needed.

```python
    @pytest.mark.parametrize('actual_fields, expected_fields', [
        param(Validator.REQUIRED_FIELDS, EXPECTED_REQUIRED_FIELDS, id='1'),
        param(Validator.REQUIRED_DECRYPTED_DATA_FIELDS, EXPECTED_REQUIRED_DECRYPTED_DATA_FIELDS, id='2')
    ])
    def test_required_fields(self, actual_fields, expected_fields):
        # Given

        # When

        # Then
        assert actual_fields == expected_fields
```

This test catches accidental changes to required field definitions. When fields change, this test forces the developer to update the expected constant.

---

## Happy path — parametrize for variants

```python
    @pytest.mark.parametrize(
        'decrypted_data, decrypted_dto, user_detail_dto, authn_request_dto', [
            param(DECRYPTED_DATA_PUSH_IS_RDP_TRUE, DECRYPTED_PUSH_IS_RDP_TRUE_DTO,
                  USER_DETAIL_IS_RDP_TRUE_DTO, PUSH_REQUESTED_DTO, id='1'),
            param(DECRYPTED_DATA_PUSH_IS_RDP_FALSE, DECRYPTED_PUSH_IS_RDP_FALSE_DTO,
                  USER_DETAIL_IS_RDP_FALSE_DTO, PUSH_REQUESTED_IS_RDP_FALSE_DTO, id='2'),
            param(DECRYPTED_DATA_QRCODE_IS_RDP_TRUE, DECRYPTED_QRCODE_IS_RDP_TRUE_DTO,
                  USER_DETAIL_QRCODE_IS_RDP_TRUE_DTO, QRCODE_REQUESTED_DTO, id='3'),
        ])
    def test_process_with_success(self, decrypted_data, decrypted_dto, user_detail_dto,
                                  authn_request_dto, service, mocker):
        # Given
        service.client_config_repository.retrieve_client_config_by_account_id_and_resource_id = mocker.Mock(
            return_value=CLIENT_CONFIG_DB)
        service.comm_crypto.decrypt_data = mocker.Mock(return_value=decrypted_data)
        service.user_detail_repository.retrieve_user_detail_by_account_id_and_username = mocker.Mock(
            return_value=USER_DETAIL_DB)
        service.transaction_repository.save_transaction = mocker.Mock()
        service.publisher.transaction_created = mocker.Mock()
        service.responder.success = mocker.Mock(return_value=SUCCESS_RESPONSE)

        # When
        actual_response = service.process(dto=HTTP_EVENT_DTO)

        # Then
        service.transaction_repository.save_transaction.assert_called_once_with(dto=authn_request_dto)
        service.publisher.transaction_created.assert_called_once_with(dto=authn_request_dto)
        assert actual_response == SUCCESS_RESPONSE
```

---

## Error path — single parametrize for invalid inputs

One test covers all invalid input variants. No need for a separate test per missing field.

```python
    @pytest.mark.parametrize('client_config', [
        param({}, id='1'),
        param(CLIENT_CONFIG_EXPIRED_LICENSE_DB, id='2'),
        param(CLIENT_CONFIG_NO_LICENSES_DB, id='3'),
    ])
    def test_process_request_with_invalid_client_config(self, client_config, service, mocker):
        # Given
        service.client_config_repository.retrieve_client_config_by_account_id_and_resource_id = mocker.Mock(
            return_value=client_config)
        service.responder.precondition_failed = mocker.Mock(return_value=PRECONDITION_FAILED_RESPONSE)

        # When
        actual_response = service.process(dto=HTTP_EVENT_DTO)

        # Then
        assert actual_response == PRECONDITION_FAILED_RESPONSE
```

---

## Fallback / BotoCoreError

Use `side_effect=BotoCoreError()` to simulate AWS failures and verify fallback behavior:

```python
    def test_process_tx_created_with_publish_failure(self, service, mocker):
        # Given
        service.publisher.transaction_created = mocker.Mock(side_effect=BotoCoreError())
        service.producer.transaction_created = mocker.Mock()

        # When
        service.process(dto=TX_CREATED_DTO)

        # Then
        service.publisher.transaction_created.assert_called_once_with(dto=TX_CREATED_DTO)
        service.producer.transaction_created.assert_called_once_with(dto=TX_CREATED_DTO)
```

---

## assert_not_called — verify branching

When testing a specific branch, assert that all other branches were NOT taken:

```python
    def test_process_tx_created(self, service, mocker):
        # Given
        service.publisher.transaction_created = mocker.Mock()
        service.publisher.transaction_authorized = mocker.Mock()
        service.publisher.transaction_unauthorized = mocker.Mock()

        # When
        service.process(dto=TX_CREATED_DTO)

        # Then
        service.publisher.transaction_created.assert_called_once_with(dto=TX_CREATED_DTO)
        service.publisher.transaction_authorized.assert_not_called()
        service.publisher.transaction_unauthorized.assert_not_called()
```

---

## side_effect for successive calls

When a method returns different values on successive calls:

```python
    def test_process_with_retry(self, service, mocker):
        # Given
        service.repository.retrieve_item = mocker.Mock(side_effect=[{}, USER_DETAIL_DB])

        # When
        service.process(dto=HTTP_EVENT_DTO)

        # Then
        assert service.repository.retrieve_item.call_count == 2
```

---

## CommCrypto in service fixture

When the service depends on a crypto adapter, mock `CommCrypto.initialize_crypto` at the class level in the fixture:

```python
    @pytest.fixture
    def comm_crypto(self, template_parser, mocker):
        from adapter.security.comm_crypto import CommCrypto
        CommCrypto.initialize_crypto = mocker.Mock()
        return CommunicationCrypto(payload_config=CommunicationCryptoConfig(), parser=template_parser)
```

---

## Checklist

- [ ] `_patch_get_timestamp_now` injected into `service` fixture, not individual tests
- [ ] `FAKE_TIME` defined as class-level constant
- [ ] `test_required_fields` present for every `Validator` class with `REQUIRED_FIELDS`
- [ ] Happy path uses `parametrize` for all input variants
- [ ] Error path uses a single parametrized test (not one test per missing field)
- [ ] `assert_not_called()` used on all non-triggered branches
- [ ] `BotoCoreError` used for AWS failure simulation
- [ ] `CommCrypto.initialize_crypto` mocked at class level in fixture (not per test)
