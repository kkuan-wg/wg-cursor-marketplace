# Responder Adapter — HTTP

Implements responder ports using the authpoint-lambda-layer `adapter.transport.http_responder.HttpResponder`. File: `api_responder.py`. Uses `API_ERROR_CODES` from configuration for error responses. See [parts/layer-authpoint-lambda.md](../layer-authpoint-lambda.md).

---

## Layer Component

```python
from adapter.transport.http_responder import HttpResponder
```

---

## Example

```python
from adapter.transport.http_responder import HttpResponder

from logon_app_authn_api.configuration import ResponderConfig, API_ERROR_CODES
from logon_app_authn_api.port.responder import Responder


class ApiResponder(Responder):

    def __init__(self, *, config: ResponderConfig):
        self.responder = HttpResponder(config=config.as_dict)

    def success(self, *, encrypted_data: str, dto: dict) -> dict:
        return self.responder.build_success_response(body={'data': encrypted_data},
                                                     request_id=dto.get('requestId'))

    def unauthorized(self, *, dto: dict) -> dict:
        return self.responder.build_standard_error_response(error=API_ERROR_CODES['unauthorized'],
                                                            request_id=dto.get('requestId'))

    def bad_request(self, *, dto: dict) -> dict:
        return self.responder.build_standard_error_response(error=API_ERROR_CODES['badRequest'],
                                                            request_id=dto.get('requestId'))

    def precondition_failed(self, *, dto: dict) -> dict:
        return self.responder.build_standard_error_response(error=API_ERROR_CODES['preconditionFailed'],
                                                            request_id=dto.get('requestId'))

    def server_error(self, *, dto: dict) -> dict:
        return self.responder.build_standard_error_response(error=API_ERROR_CODES['internalServerError'],
                                                            request_id=dto.get('requestId'))
```

---

## Checklist

- [ ] File: `api_responder.py`
- [ ] Uses `HttpResponder` from `adapter.transport.http_responder`
- [ ] Passes `config.as_dict` to authpoint-lambda-layer
- [ ] Uses `API_ERROR_CODES` from configuration for error responses
