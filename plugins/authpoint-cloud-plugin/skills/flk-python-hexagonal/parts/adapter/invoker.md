# Invoker Adapter — API Gateway and Lambda

Implements invoker ports for external API calls. Two variants: **API Gateway** (`api_gateway_invoker.py`) and **Lambda** (`lambda_invoker.py`). Invokers **return `{}` on error** instead of raising — the domain validates empty responses.

---

## API Gateway Invoker

**Layer**: `adapter.transport.api_gateway_invoker.ApiGatewayInvoker`

```python
import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.api_gateway_invoker import ApiGatewayInvoker
from logon_app_authn_api.configuration import ZtePolicyApiInvokerConfig, EVALUATE_POLICY_KEY
from logon_app_authn_api.port.invoker import RetrievePoliciesInvokerPort

SUCCESS_STATUS = 200


class ZtePolicyApiInvoker(RetrievePoliciesInvokerPort):

    def __init__(self, *, config: ZtePolicyApiInvokerConfig, parser: TemplateParser):
        self.api_invoker = ApiGatewayInvoker(config=config.as_dict, template_parser=parser)

    def retrieve_policy(self, *, dto: dict) -> dict:
        try:
            request = self.api_invoker.build_request(dto=dto, config_key=EVALUATE_POLICY_KEY)
            logging.info(f"ZTE policy query. AccountId: {dto.get('accountId')}, ResourceId: {dto.get('resourceId')}.")
            logging.debug(f'ZTE evaluate request: {request}')
            response = self.api_invoker.execute_request(execute_request_kwargs=request, config_key=EVALUATE_POLICY_KEY)
            logging.debug(f'ZTE evaluate response: {response}')
            return self._handle_response(response=response)
        except Exception as ex:
            logging.error(f'Failed to retrieve policy: {ex}')
            return {}

    @staticmethod
    def _handle_response(*, response: dict) -> dict:
        if response.get('status') == SUCCESS_STATUS and response.get('body'):
            return response['body'][0]
        return {}
```

---

## Lambda Invoker

**Layer**: `adapter.transport.lambda_invoker.LambdaInvoker`

```python
import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.lambda_invoker import LambdaInvoker
from logon_app_config_api.configuration import GetTokenDataInvokerConfig
from logon_app_config_api.port.invoker import GetTokenDataInvokerPort


class GetTokenDataInvoker(GetTokenDataInvokerPort):

    def __init__(self, *, config: GetTokenDataInvokerConfig, parser: TemplateParser):
        self.invoker = LambdaInvoker(config=config.as_dict, template_parser=parser)

    def get_token_data(self, *, dto: dict) -> dict:
        try:
            return self.invoker.invoke_lambda(event_type='GET_TOKEN_DATA', entity_type='INTERNAL', data=dto)
        except Exception as ex:
            logging.error(f'Failed to get token data: {ex}')
            return {}
```

---

## Invoker Pattern

- **On success**: Return the response data
- **On error**: Log and return `{}` — do not raise
- **Domain**: Validates empty response and handles accordingly

---

## Checklist

- [ ] API Gateway: `api_gateway_invoker.py`; Lambda: `lambda_invoker.py`
- [ ] Returns `{}` on error instead of raising
- [ ] Logs errors before returning
- [ ] Passes `config.as_dict` and `template_parser=parser` to authpoint-lambda-layer
