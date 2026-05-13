# app.py — Entry Point and Wiring

The `app.py` is the **entry point** of the Lambda or application. Its responsibility is exclusively **wiring** (dependency injection) and **handler** (flow orchestration). **No business logic** should live in app.py.

---

## 1. Role of app.py

| Responsibility | Description |
|----------------|-------------|
| **Wiring** | Instantiate adapters, configs and Service with dependency injection |
| **Handler** | Receive event, convert to DTO, call Service, return response |
| **Logging** | Initialize log session, set context, reset at the end |
| **Error handling** | Catch unhandled exceptions and return appropriate response |

The app.py **must not** contain: validations, business rules, complex transformations or direct infrastructure access.

---

## 2. Import Order

```python
# 1. stdlib
import logging
from traceback import format_exc

# 2. authpoint-lambda-layer (adapter, configuration)
from adapter.data_processing.template_parser import TemplateParser
from adapter.event.http_event import HttpEvent
from configuration.logger import initialize_logging_session, reset_logging_context, set_context

# 3. Local module (adapter, configuration, domain)
from logon_app_authn_api.adapter.api_responder import ApiResponder
from logon_app_authn_api.configuration import FUNCTION_NAME, HttpEventConfig, ResponderConfig
from logon_app_authn_api.domain.service import Service
```

---

## 3. Initialization (top-level)

Initialization happens **once** on module load (cold start). Typical order:

1. `initialize_logging_session(service_name=FUNCTION_NAME)`
2. `TemplateParser()`
3. Event adapter (`HttpEvent`, `SqsEvent`, `DdbStreamEvent`)
4. Adapters (repositories, invokers, publishers, responder)
5. `Service(...)` with all adapters injected

### config vs config.as_dict in app.py

| Component | Receives in app.py | Reason |
|-----------|-------------------|--------|
| **Layer event adapters** (`HttpEvent`, `SqsEvent`, `DdbStreamEvent`) | `Config().as_dict` | They are layer components — expect dict directly |
| **Local adapters** (`ClientConfigRepository`, `SnsPublisher`, etc.) | `Config()` (object) | Local adapter's `__init__` calls `.as_dict` internally before passing to the layer |

```python
# ✅ Event adapter (layer component) — receives as_dict
http_event = HttpEvent(config=HttpEventConfig().as_dict, template_parser=parser)

# ✅ Local adapter — receives config object; adapter calls .as_dict internally
repository = ClientConfigRepository(config=ClientConfigRepositoryConfig(), template_parser=parser)
```

---

## 4. Standard Handler

### try/except/finally structure

```python
def lambda_handler(event: dict, _context):
    logging.debug(f'Event received: {event}')
    dto = {}
    try:
        dto = http_event.as_dto(event=event)
        set_context(dto=dto)
        return service.process(dto=dto)
    except Exception as ex:
        logging.error(f'Failed due to Exception: {ex} with Traceback: {format_exc()}')
        return responder.server_error(dto=dto)
    finally:
        reset_logging_context()
```

### Generic exception in handler

The app.py **can and should** catch generic `Exception` in the handler because:

- Specific exceptions are already handled in the **Service**
- The handler is the last point before returning to API Gateway
- Prevents unhandled errors from returning 500 without logging

---

## 5. Variations by Trigger Type

| Trigger | Event Adapter | Return on success | On error |
|---------|---------------|-------------------|----------|
| **HTTP API** | `HttpEvent` | `return service.process(dto=dto)` | `return responder.server_error(dto=dto)` |
| **SQS** | `SqsEvent` | `service.process(dto=dto)` (void) | `raise ex` |
| **DDB Stream** | `DdbStreamEvent` | `service.process(dto=dto)` (void) | `raise ex` |
| **FastAPI** | `ApiRequest` | `return build_json_response(response=...)` | `return build_json_response(response=responder.server_error(...))` |

**SQS and DDB Stream**: there is no HTTP responder; the Lambda should retry on failure, hence `raise ex`.

---

## 6. Complete Examples

### Example 1: Lambda HTTP API (full)

API with multiple repositories, invoker, publisher and responder.

```python
import logging
from traceback import format_exc

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.http_event import HttpEvent
from configuration.logger import initialize_logging_session, reset_logging_context, set_context
from logon_app_authn_api.adapter.api_gateway_invoker import ZtePolicyApiInvoker
from logon_app_authn_api.adapter.api_responder import ApiResponder
from logon_app_authn_api.adapter.comm_crypto import CommunicationCrypto
from logon_app_authn_api.adapter.db_repository import ClientConfigRepository, UserDetailRepository, \
    TransactionRepository, AuthnMetadataRepository, AuthnContextRepository
from logon_app_authn_api.adapter.sns_publisher import SnsMessagePublisher
from logon_app_authn_api.configuration import FUNCTION_NAME, HttpEventConfig, ZtePolicyApiInvokerConfig, \
    ClientConfigRepositoryConfig, UserDetailRepositoryConfig, TransactionRepositoryConfig, ResponderConfig, \
    CommunicationCryptoConfig, SnsPublisherConfig, AuthnMetadataDdbRepositoryConfig, AuthnContextDdbRepositoryConfig
from logon_app_authn_api.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)

parser = TemplateParser()
http_event = HttpEvent(config=HttpEventConfig().as_dict, template_parser=parser)

api_invoker = ZtePolicyApiInvoker(config=ZtePolicyApiInvokerConfig(), template_parser=parser)
client_config_repository = ClientConfigRepository(config=ClientConfigRepositoryConfig(), template_parser=parser)
user_detail_repository = UserDetailRepository(config=UserDetailRepositoryConfig(), template_parser=parser)
transaction_repository = TransactionRepository(config=TransactionRepositoryConfig(), template_parser=parser)
authn_context_repository = AuthnContextRepository(config=AuthnContextDdbRepositoryConfig(), template_parser=parser)
authn_metadata_repository = AuthnMetadataRepository(config=AuthnMetadataDdbRepositoryConfig(), template_parser=parser)
comm_crypto = CommunicationCrypto(payload_config=CommunicationCryptoConfig(), template_parser=parser)
publisher = SnsMessagePublisher(config=SnsPublisherConfig(), template_parser=parser)
responder = ApiResponder(config=ResponderConfig())

service = Service(api_invoker=api_invoker,
                  publisher=publisher,
                  client_config_repository=client_config_repository,
                  user_detail_repository=user_detail_repository,
                  transaction_repository=transaction_repository,
                  authn_context_repository=authn_context_repository,
                  authn_metadata_repository=authn_metadata_repository,
                  comm_crypto=comm_crypto,
                  responder=responder)


def lambda_handler(event: dict, _context):
    logging.debug(f'Event received: {event}')
    dto = {}
    try:
        dto = http_event.as_dto(event=event)
        set_context(dto=dto)
        return service.process(dto=dto)
    except Exception as ex:
        logging.error(f'Failed due to Exception: {ex} with Traceback: {format_exc()}')
        return responder.server_error(dto=dto)
    finally:
        reset_logging_context()
```

---

### Example 2: Lambda HTTP API (simple)

API with fewer dependencies: responder, repositories, crypto, invoker.

```python
import logging
from traceback import format_exc

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.http_event import HttpEvent
from configuration.logger import initialize_logging_session, reset_logging_context, set_context
from logon_app_config_api.adapter.api_responder import ApiResponder
from logon_app_config_api.adapter.comm_crypto import CommunicationCrypto
from logon_app_config_api.adapter.db_repository import ClientConfigRepository, UserDetailRepository
from logon_app_config_api.adapter.lambda_invoker import GetTokenDataInvoker
from logon_app_config_api.configuration import FUNCTION_NAME, HttpEventConfig, ResponderConfig, BlobCryptoConfig, \
    CommunicationCryptoConfig, GetTokenDataInvokerConfig, ClientConfigRepositoryConfig, UserDetailRepositoryConfig
from logon_app_config_api.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)
parser = TemplateParser()
http_event = HttpEvent(config=HttpEventConfig().as_dict,
                       template_parser=parser)
responder = ApiResponder(config=ResponderConfig())
user_detail_repository = UserDetailRepository(config=UserDetailRepositoryConfig(),
                                              template_parser=parser)
client_config_repository = ClientConfigRepository(config=ClientConfigRepositoryConfig(),
                                                  template_parser=parser)
comm_crypto = CommunicationCrypto(blob_config=BlobCryptoConfig(),
                                  payload_config=CommunicationCryptoConfig(),
                                  template_parser=parser)
invoker = GetTokenDataInvoker(config=GetTokenDataInvokerConfig(),
                              template_parser=parser)
service = Service(comm_crypto=comm_crypto,
                  client_config_repository=client_config_repository,
                  invoker=invoker,
                  user_detail_repository=user_detail_repository,
                  responder=responder)


def lambda_handler(event: dict, _context):
    logging.debug(f'Event received: {event}')
    dto = {}
    try:
        dto = http_event.as_dto(event=event)
        set_context(dto=dto)
        return service.process(dto=dto)
    except Exception as ex:
        logging.error(f'Failed due to Exception: {ex} with Traceback: {format_exc()}')
        return responder.server_error(dto=dto)
    finally:
        reset_logging_context()
```

---

### Example 3: Lambda SQS Consumer

Consumer that processes SQS messages. On error, raises to allow retry.

```python
import logging
from traceback import format_exc

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.sqs_event import SqsEvent
from configuration.logger import initialize_logging_session, set_context, reset_logging_context
from logon_app_tx_consumer.adapter.db_repository import DynamoDbRepository, AuthnMetadataRepository
from logon_app_tx_consumer.configuration import FUNCTION_NAME, DdbRepositoryConfig, SqsEventConfig, \
    AuthnMetadataDdbRepositoryConfig
from logon_app_tx_consumer.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)

parser = TemplateParser()

repository = DynamoDbRepository(config=DdbRepositoryConfig(), template_parser=parser)
authn_metadata_repository = AuthnMetadataRepository(config=AuthnMetadataDdbRepositoryConfig(), template_parser=parser)
sqs_event = SqsEvent(config=SqsEventConfig().as_dict, template_parser=parser)
service = Service(repository=repository, authn_metadata_repository=authn_metadata_repository)


def lambda_handler(event: dict, _context):
    logging.debug(f'Event received: {event}')
    try:
        dto = sqs_event.as_dto(event=event)
        set_context(dto=dto)
        service.process(dto=dto)
        logging.info(f'Successfully executed {FUNCTION_NAME} function.')
    except Exception as ex:
        logging.error(f'Failed due to Exception: {ex} with Traceback: {format_exc()}')
        raise ex
    finally:
        reset_logging_context()
```

---

### Example 4: Lambda DDB Stream Listener

DynamoDB Streams listener. Publishes to SNS and produces to SQS.

```python
import logging
from traceback import format_exc

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.ddb_stream_event import DdbStreamEvent
from configuration.logger import initialize_logging_session, set_context, reset_logging_context
from logon_app_tx_listener.adapter.sns_publisher import SnsPublisher
from logon_app_tx_listener.adapter.sqs_producer import SqsProducer
from logon_app_tx_listener.configuration import FUNCTION_NAME, DdbStreamEventConfig, SnsPublishConfig, SqsProducerConfig
from logon_app_tx_listener.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)

parser = TemplateParser()

ddb_stream_event = DdbStreamEvent(config=DdbStreamEventConfig().as_dict, template_parser=parser)
publisher = SnsPublisher(config=SnsPublishConfig(), template_parser=parser)
producer = SqsProducer(config=SqsProducerConfig(), template_parser=parser)
service = Service(publisher=publisher, producer=producer)


def lambda_handler(event: dict, _context):
    logging.debug(f'Event received: {event}')
    try:
        dto = ddb_stream_event.as_dto(event=event)
        set_context(dto=dto)
        service.process(dto=dto)
        logging.info(f'Successfully executed {FUNCTION_NAME} function.')
    except Exception as ex:
        logging.error(f'Failed due to Exception: {ex} with Traceback: {format_exc()}')
        raise ex
    finally:
        reset_logging_context()
```

---

### Example 5: FastAPI (logon_app_tx_mw)

FastAPI application with `@lru_cache` for lazy loading and lifespan.

```python
import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from os import getenv
from traceback import format_exc

import newrelic.agent
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from adapter.data_processing.template_parser import TemplateParser
from configuration.logger import initialize_logging_session, set_context, reset_logging_context
from logon_app_tx.adapter.api_request import ApiRequest
from logon_app_tx.adapter.api_responder import ApiResponder
from logon_app_tx.adapter.comm_crypto import CommunicationCrypto
from logon_app_tx.adapter.db_repository import TransactionRepository, ClientConfigRepository
from logon_app_tx.configuration import FUNCTION_NAME, ApiRequestConfig, TransactionRepositoryConfig, \
    ClientConfigRepositoryConfig, CommunicationCryptoConfig, ResponderConfig
from logon_app_tx.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)


@lru_cache
def get_template_parser() -> TemplateParser:
    return TemplateParser()


@lru_cache
def get_api_request() -> ApiRequest:
    return ApiRequest(config=ApiRequestConfig(), template_parser=get_template_parser())


@lru_cache
def get_api_responder() -> ApiResponder:
    return ApiResponder(config=ResponderConfig())


@lru_cache
def get_service() -> Service:
    parser = get_template_parser()
    transaction_repository = TransactionRepository(config=TransactionRepositoryConfig(), template_parser=parser)
    client_config_repository = ClientConfigRepository(config=ClientConfigRepositoryConfig(), template_parser=parser)
    comm_crypto = CommunicationCrypto(config=CommunicationCryptoConfig())
    responder = get_api_responder()
    return Service(
        transaction_repository=transaction_repository,
        client_config_repository=client_config_repository,
        comm_crypto=comm_crypto,
        responder=responder
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan handler"""
    # Startup
    newrelic.agent.initialize()
    logging.info("Application startup completed with New Relic request tracing")
    yield


app = FastAPI(title=FUNCTION_NAME, lifespan=lifespan)


def build_json_response(*, response: dict) -> JSONResponse:
    return JSONResponse(
        status_code=response['statusCode'],
        content=response.get('body', {}),
        headers=response['headers']
    )


@app.get('/account/{accountId}/transaction/{transactionId}')
@newrelic.agent.function_trace()
async def get_tx_result(request: Request):
    dto = {}
    try:
        api_request = get_api_request()
        service = get_service()

        dto = api_request.as_dto(request=request)
        set_context(dto=dto)
        response = service.process(dto=dto)
        return build_json_response(response=response)
    except Exception as ex:
        logging.error(f'Failed due to Exception: {ex} with Traceback: {format_exc()}')
        responder = get_api_responder()
        return build_json_response(response=responder.server_error(dto=dto))
    finally:
        reset_logging_context()


@app.get('/health')
async def health():
    return {'message': 'healthy'}


if __name__ == '__main__':
    num_workers = int(getenv('WORKER_THREADS', '1'))
    config = uvicorn.Config(
        'app:app',
        host='0.0.0.0',
        port=5000,
        workers=num_workers,
        access_log=False
    )
    server = uvicorn.Server(config)
    server.run()
```

---

## 7. app.py Checklist

- [ ] `initialize_logging_session(service_name=FUNCTION_NAME)` at the beginning
- [ ] `set_context(dto=dto)` inside try, before calling the Service
- [ ] `reset_logging_context()` in `finally`
- [ ] `logging.debug(f'Event received: {event}')` at the start of the handler
- [ ] `dto = {}` initialized before try (for APIs with responder)
- [ ] HTTP API: `return responder.server_error(dto=dto)` in except
- [ ] SQS/DDB Stream: `raise ex` in except
- [ ] Event adapters (`HttpEvent`, `SqsEvent`, `DdbStreamEvent`) receive `Config().as_dict`
- [ ] Local adapters receive `Config()` object (adapter calls `.as_dict` internally)
- [ ] Import order: stdlib → authpoint-lambda-layer → local module
- [ ] No business logic in app.py
