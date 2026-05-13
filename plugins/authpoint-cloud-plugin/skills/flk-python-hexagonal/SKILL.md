---
name: flk-python-hexagonal
description: Guide for writing and reviewing Python code following hexagonal architecture (Ports & Adapters), PEP 8 and quality standards. Use when writing or reviewing Python code with hexagonal architecture.
---

# Folklore Python Hexagonal Architecture

Guide for writing and reviewing Python code following hexagonal architecture (Ports & Adapters), PEP 8 and Folklore project quality standards.

## When to Use

- Writing or reviewing Python code with hexagonal architecture
- Creating or modifying `app.py`, Services, Ports or Adapters
- Validating layer separation (domain/port/adapter)
- Verifying compliance with Folklore patterns

---

## Parts Index

| Part | File | Content |
|------|------|---------|
| **app.py** | [parts/app-py.md](parts/app-py.md) | Entry point, wiring, handler, examples by trigger type (HTTP, SQS, DDB Stream, FastAPI) |
| **port** | [parts/port.md](parts/port.md) | Abstract interfaces (ABC), Repository, Responder, Invoker, Publisher, Producer, Crypto |
| **adapter** | [parts/adapter.md](parts/adapter.md) | Implementations (Repository, Responder, Invoker, Publisher, Producer, Crypto) |
| **configuration** | [parts/configuration.md](parts/configuration.md) | Configs, BaseConfig, dto_mapping, API_ERROR_CODES, getenv, shared schemas |
| **domain** | [parts/domain.md](parts/domain.md) | Service, Validators, layer helpers, exceptions, process(*, dto: dict) |
| **layer (authpoint)** | [parts/layer-authpoint-lambda.md](parts/layer-authpoint-lambda.md) | authpoint-lambda-layer: adapters, utils, BaseConfig.as_dict, DtoDict, TemplateParser |
| **layer (folklore)** | [parts/layer-folklore-lambda.md](parts/layer-folklore-lambda.md) | folklore-lambda-layer: domain helpers, enums, shared DDB schemas (flk_api, flk_core, flk_info) |

---

## Lambda Folder Structure

```
<fn_name>/
├── __init__.py               # empty — required for Python package resolution
├── app.py                    # Lambda handler, wiring, entry point
└── <module_name>/
    ├── __init__.py           # empty — required
    ├── configuration.py      # Configs (env, DTO mapping, error codes)
    ├── domain/
    │   ├── __init__.py       # empty — required
    │   └── service.py        # Business rules
    ├── port/
    │   ├── __init__.py       # empty — required
    │   ├── repository.py     # Persistence interface
    │   ├── responder.py      # Response interface
    │   ├── invoker.py        # Invocation interface (API/Lambda)
    │   ├── publisher.py      # Publish interface (SNS)
    │   ├── producer.py       # Produce interface (SQS)
    │   └── crypto.py         # Encrypt/decrypt interface
    └── adapter/
        ├── __init__.py       # empty — required
        ├── ddb_repository.py     # DynamoDB implementation
        ├── api_responder.py      # HTTP implementation
        ├── api_gateway_invoker.py # API Gateway implementation
        ├── lambda_invoker.py     # Lambda invocation implementation
        ├── sns_publisher.py       # SNS implementation
        ├── sqs_producer.py       # SQS implementation
        └── comm_crypto.py        # Crypto implementation
```

**Every directory in the module tree must contain an empty `__init__.py`** — including `<fn_name>/`, `<module_name>/`, `port/`, `adapter/`, and `domain/`. Without them Python cannot resolve the package imports and the Lambda fails with `ImportError` at runtime.

---

## Hexagonal Architecture — Principles

- **domain/**: Business logic only; imports ports and layer helpers; Validators as classes; no adapter imports
- **port/**: Abstract interfaces (ABC with `@abstractmethod`)
- **adapter/**: Concrete implementations; delegate to authpoint-lambda-layer; use `config.as_dict`
- **configuration.py**: Extends BaseConfig; dto_mapping, API_ERROR_CODES; use config.as_dict for authpoint-lambda-layer

```python
# ✅ CORRECT — domain imports port
from ..port.repository import CredentialsRepository

# ❌ INCORRECT — domain importing adapter
from ..adapter.db_repository import DdbCredentialsRepository
```

---

## Quality and Review

### Conventions (PEP 8 / pylint)

- **Naming**: `snake_case` (variables/functions), `PascalCase` (classes), `UPPER_CASE` (constants)
- **Line length**: max 120 characters
- **Indentation**: 4 spaces
- **Complexity**: max 50 statements per function, max 5 nesting levels, max 10 arguments

### Method Order

In all files, order methods as:

1. Public methods
2. Public static methods
3. Private methods
4. Private static methods

### Logging

- **DEBUG**: Allowed to log full payloads, events, requests
- **INFO or higher**: Do not log raw payloads
- **Exception**: Logging `{dto}` is allowed — DTOs have custom `__str__` that only logs fields defined in `dto_log_mapping` (configuration)

### DTO Updates

When updating a DTO in place, use `update()` or `dto['key'] = value`. Do **not** use the merge operator (`|`) for updates — it creates a new dict, not an in-place update.

```python
# ✅ CORRECT
dto['resourceId'] = transaction.get('header', {}).get('resourceId')
dto.update({'key': 'value'})

# ❌ INCORRECT — merge creates new dict
dto = dto | {'key': 'value'}
```

See [parts/domain.md](parts/domain.md) for details.

### Exception in app.py

The handler **can and should** catch generic `Exception` — specific exceptions are handled in the Service. See [parts/app-py.md](parts/app-py.md).

### General Checklist

- [ ] Domain does not import adapters
- [ ] Adapters pass `config.as_dict` to authpoint-lambda-layer components
- [ ] Event adapters (`HttpEvent`, `SqsEvent`, `DdbStreamEvent`) receive `config.as_dict` in `app.py`
- [ ] Invokers return `{}` on error instead of raising
- [ ] Services use `*, dto: dict` in public methods
- [ ] Ports use ABC with `@abstractmethod`
- [ ] Imports: stdlib → authpoint-lambda-layer / folklore-lambda-layer → local module
- [ ] `configuration.py` contains `dto_mapping` and `API_ERROR_CODES` (for HTTP APIs)
- [ ] Config classes extend BaseConfig; use `getenv` without default
- [ ] Method order: public → public static → private → private static
- [ ] DTO updates: use `update()` or `dto['key']=value`, not `|`
- [ ] `reset_logging_context()` called in `finally` block
- [ ] Never import from `flk_utils.*` — use `utils.*` from authpoint-lambda-layer
