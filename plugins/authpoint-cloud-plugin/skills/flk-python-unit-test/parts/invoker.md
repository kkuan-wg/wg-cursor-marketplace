# Invoker and Crypto Tests

Tests for `ApiGatewayInvoker`, `LambdaInvoker` and `CommCrypto` adapters.

---

## ApiGatewayInvoker

File: `api_gateway_invoker_test.py`

```python
import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from logon_app_authn_api.adapter.api_gateway_invoker import ZtePolicyApiInvoker
from logon_app_authn_api.configuration import ZtePolicyApiInvokerConfig
from tests.api.logon_app_authn_api.api_gateway_invoker_constants import (
    API_INVOKER_REQUEST_DTO, API_INVOKER_REQUEST_DTO_WITH_GEOLOCATION,
    API_RESPONSE_WITH_SUCCESS, API_RESPONSE_WITH_ERROR,
    EXPECTED_REQUEST, EXPECTED_REQUEST_WITH_GEOLOCATION,
    EXPECTED_RESPONSE, PARSED_RESPONSE, ZTE_RESPONSE_WITH_SUCCESS
)


class TestApiGatewayInvoker:

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def config(self):
        return ZtePolicyApiInvokerConfig()

    @pytest.fixture
    def api_gateway_invoker(self, config, template_parser):
        return ZtePolicyApiInvoker(config=config, template_parser=template_parser)

    @pytest.mark.parametrize('dto, api_response, expected_request, expected_response', [
        param(API_INVOKER_REQUEST_DTO, API_RESPONSE_WITH_SUCCESS,
              EXPECTED_REQUEST, EXPECTED_RESPONSE, id='1'),
        param(API_INVOKER_REQUEST_DTO_WITH_GEOLOCATION, API_RESPONSE_WITH_SUCCESS,
              EXPECTED_REQUEST_WITH_GEOLOCATION, EXPECTED_RESPONSE, id='2'),
        param(API_INVOKER_REQUEST_DTO, API_RESPONSE_WITH_ERROR,
              EXPECTED_REQUEST, {}, id='3'),
    ])
    def test_retrieve_policy_with_success(self, dto, api_response, expected_request,
                                          expected_response, api_gateway_invoker, mocker):
        # Given
        api_gateway_invoker.api_invoker.execute_request = mocker.Mock(return_value=api_response)

        # When
        actual_response = api_gateway_invoker.retrieve_policy(dto=dto)

        # Then
        assert actual_response == expected_response
        api_gateway_invoker.api_invoker.execute_request.assert_called_once_with(
            config_key='evaluatePolicy',
            execute_request_kwargs=expected_request
        )

    def test_retrieve_policy_with_error(self, api_gateway_invoker, mocker):
        # Given
        api_gateway_invoker.api_invoker.execute_request = mocker.Mock(side_effect=Exception)

        # When
        actual_response = api_gateway_invoker.retrieve_policy(dto=API_INVOKER_REQUEST_DTO)

        # Then
        assert actual_response == {}
        api_gateway_invoker.api_invoker.execute_request.assert_called_once_with(
            config_key='evaluatePolicy',
            execute_request_kwargs=EXPECTED_REQUEST
        )

    def test_invoker_response_mapping(self, config, template_parser):
        # When
        parsed_response = template_parser.parse_payload(
            item=ZTE_RESPONSE_WITH_SUCCESS,
            payload_map=config.as_dict['responseDataMappings']['evaluatePolicy']
        )
        # Recreates the response parsing as ApiGatewayInvoker does internally.
        # Validates that the configuration produces the correct response mapping.

        # Then
        assert parsed_response == PARSED_RESPONSE
```

Key points:
- Parametrize covers: success with different DTOs, error response (returns `{}`)
- `test_retrieve_policy_with_error` verifies invokers return `{}` on exception — never raise
- `test_invoker_response_mapping` validates `responseDataMappings` config using `TemplateParser` directly

---

## api_gateway_invoker_constants.py

```python
from copy import deepcopy

_BASE_API_REQUEST = {
    'accountId': 'WGC-0',
    'clientIp': '1.0.0.1',
    'userId': 121,
    'groups': [{'id': '71'}],
    'resources': [{'id': '123'}]
}

API_INVOKER_REQUEST_DTO = _BASE_API_REQUEST

API_INVOKER_REQUEST_DTO_WITH_GEOLOCATION = {
    **_BASE_API_REQUEST,
    'accuracy': 11.71,
    'latitude': -22.4451083,
    'longitude': -45.4551853
}

API_RESPONSE_WITH_SUCCESS = {
    'status': 200,
    'body': [{'allowAuth': True, 'policy': {'otp': False, 'push': True}, 'name': 'Main Policy'}]
}

API_RESPONSE_WITH_ERROR = {'status': 500, 'body': {'error': 'validation error'}}

EXPECTED_REQUEST = {
    'headers': {'content-type': 'application/json'},
    'method': 'POST',
    'params': {},
    'url': 'zte-policy-evaluator/v1/WGC-0/evaluate',
    'data': b'{"user_id": "121", "namespace": "AUTHPOINT", "ip_address": "1.0.0.1", ...}'
}

EXPECTED_RESPONSE = {
    'allowAuth': True,
    'policy': {'otp': False, 'push': True},
    'name': 'Main Policy'
}

PARSED_RESPONSE = {'status': 200, 'body': [EXPECTED_RESPONSE]}
```

---

## CommCrypto

File: `comm_crypto_test.py`. Mock `CommCrypto.initialize_crypto` at the class level in the fixture — this prevents the real crypto initialization from running.

```python
import pytest

from adapter.data_processing.template_parser import TemplateParser
from adapter.security.comm_crypto import CommCrypto
from logon_app_authn_api.adapter.comm_crypto import CommunicationCrypto
from logon_app_authn_api.configuration import CommunicationCryptoConfig
from tests.api.logon_app_authn_api.http_event_constants import HTTP_EVENT_DTO


class TestCommCrypto:

    @pytest.fixture
    def comm_crypto(self, mocker):
        CommCrypto.initialize_crypto = mocker.Mock()
        return CommunicationCrypto(payload_config=CommunicationCryptoConfig(), parser=TemplateParser())

    def test_decrypt_payload(self, comm_crypto, mocker):
        # Given
        comm_crypto.payload_crypto.decrypt_agent = mocker.Mock(return_value='{"key": "value"}')

        # When
        decrypted_data = comm_crypto.decrypt_data(dto=HTTP_EVENT_DTO)

        # Then
        comm_crypto.payload_crypto.decrypt_agent.assert_called_once_with(dto=HTTP_EVENT_DTO)
        assert decrypted_data == {'key': 'value'}

    def test_encrypt_payload(self, comm_crypto, mocker):
        # Given
        comm_crypto.payload_crypto.encrypt_agent = mocker.Mock(return_value='<encrypted>')

        # When
        encrypted_data = comm_crypto.encrypt_data(dto=HTTP_EVENT_DTO)

        # Then
        comm_crypto.payload_crypto.encrypt_agent.assert_called_once_with(dto=HTTP_EVENT_DTO)
        assert encrypted_data == '<encrypted>'
```

Key points:
- `CommCrypto.initialize_crypto = mocker.Mock()` — class-level mock in the fixture, before instantiation
- Mock target is `comm_crypto.payload_crypto.decrypt_agent` / `encrypt_agent` (the layer method)
- `decrypt_agent` returns a JSON string — the adapter parses it; assert the parsed dict

---

## LambdaInvoker

File: `lambda_invoker_test.py`

```python
import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from logon_app_qrcode_api.adapter.lambda_invoker import QrcodeTransactionInvoker
from logon_app_qrcode_api.configuration import LambdaInvokerConfig
from tests.api.logon_app_qrcode_api.lambda_invoker_constants import (
    HTTP_EVENT_DTO, LAMBDA_RESPONSE, EXPECTED_RESPONSE
)


class TestLambdaInvoker:

    @pytest.fixture
    def template_parser(self):
        return TemplateParser()

    @pytest.fixture
    def lambda_invoker(self, template_parser):
        return QrcodeTransactionInvoker(config=LambdaInvokerConfig(), template_parser=template_parser)

    def test_invoke_with_success(self, lambda_invoker, mocker):
        # Given
        lambda_invoker.lambda_invoker.invoke_lambda = mocker.Mock(return_value=LAMBDA_RESPONSE)

        # When
        actual_response = lambda_invoker.create_transaction(dto=HTTP_EVENT_DTO)

        # Then
        lambda_invoker.lambda_invoker.invoke_lambda.assert_called_once_with(
            event_type='LOGON_APP_TX_CREATED',
            entity_type='LOGON_APP_TRANSACTION',
            data=HTTP_EVENT_DTO
        )
        assert actual_response == EXPECTED_RESPONSE

    def test_invoke_with_error(self, lambda_invoker, mocker):
        # Given
        lambda_invoker.lambda_invoker.invoke_lambda = mocker.Mock(side_effect=Exception)

        # When
        actual_response = lambda_invoker.create_transaction(dto=HTTP_EVENT_DTO)

        # Then
        assert actual_response == {}
```

---

## Checklist

### ApiGatewayInvoker
- [ ] Parametrize covers success variants + error response (returns `{}`)
- [ ] `test_retrieve_policy_with_error` verifies `{}` returned on exception
- [ ] `test_invoker_response_mapping` validates `responseDataMappings` config via `TemplateParser`
- [ ] Mock target is `api_gateway_invoker.api_invoker.execute_request`

### CommCrypto
- [ ] `CommCrypto.initialize_crypto = mocker.Mock()` in fixture before instantiation
- [ ] Mock target is `payload_crypto.decrypt_agent` / `encrypt_agent`
- [ ] `decrypt_agent` return value is a JSON string — assert parsed dict result

### LambdaInvoker
- [ ] `test_invoke_with_error` verifies `{}` returned on exception
- [ ] `invoke_lambda` called with correct `event_type`, `entity_type`, `data`
