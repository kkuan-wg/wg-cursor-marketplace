# Adapter — Infrastructure Implementations

Adapters implement ports and encapsulate infrastructure. They delegate to authpoint-lambda-layer components (`adapter.datasource`, `adapter.transport`, `adapter.security`). The domain never imports adapters.

---

## 1. Role of Adapters

| Responsibility | Description |
|----------------|-------------|
| **Implementation** | Implement port interfaces |
| **Delegation** | Use authpoint-lambda-layer components for actual work |
| **Encapsulation** | Hide infrastructure details from domain |

---

## 2. Conventions

- **Inheritance**: Class extends the corresponding port
- **`__init__`**: Receives `config` and `parser` (when needed)
- **Arguments**: Keyword-only (`*, dto: dict`) matching the port
- **File naming**: Simple names (`ddb_repository.py`, `api_responder.py`, etc.)
- **Class naming**: No `*Adapter` suffix (e.g. `ClientConfigRepository`, `ApiResponder`)
- **Import order**: stdlib → authpoint-lambda-layer → configuration → port

---

## 3. Config and Parser

### Config as dict

Configuration classes are defined in `configuration.py` for maintainability, but the authpoint-lambda-layer always expects a **dict**. Pass `config.as_dict` when calling layer components. See [parts/layer-authpoint-lambda.md](layer-authpoint-lambda.md).

```python
# ✅ CORRECT
self.repository = DdbRepository(config=config.as_dict, template_parser=parser)

# ❌ INCORRECT
self.repository = DdbRepository(config=config, template_parser=parser)
```

### Parser parameter

Standardize on `parser` as the parameter name. The layer may expect `template_parser` — pass it accordingly:

```python
def __init__(self, *, config: SomeConfig, parser: TemplateParser):
    self.repository = DdbRepository(config=config.as_dict, template_parser=parser)
```

---

## 4. File Naming

- **Repository**: `ddb_repository.py` (standardized)
- **Responder**: `api_responder.py`
- **Invoker**: `api_gateway_invoker.py` or `lambda_invoker.py`
- **Publisher**: `sns_publisher.py`
- **Producer**: `sqs_producer.py`
- **Crypto**: `comm_crypto.py`

---

## 5. Invoker Pattern

Invokers **return `{}` on error** instead of raising exceptions. The domain validates empty responses and handles them appropriately.

```python
def retrieve_policy(self, *, dto: dict) -> dict:
    try:
        # ... call layer
        return response
    except Exception as ex:
        logging.error(f'Failed to retrieve policy: {ex}')
        return {}
```

---

## 6. Parts Index

| Adapter Type | File | Content |
|--------------|------|---------|
| **Repository** | [adapter/repository.md](adapter/repository.md) | DynamoDB, DdbRepository layer |
| **Responder** | [adapter/responder.md](adapter/responder.md) | HTTP response, API_ERROR_CODES |
| **Invoker** | [adapter/invoker.md](adapter/invoker.md) | API Gateway, Lambda |
| **Publisher** | [adapter/publisher.md](adapter/publisher.md) | SNS |
| **Producer** | [adapter/producer.md](adapter/producer.md) | SQS |
| **Crypto** | [adapter/crypto.md](adapter/crypto.md) | Encrypt/decrypt |

---

## 7. Checklist

- [ ] Extends the correct port
- [ ] `__init__` receives `config` (and `parser` when needed)
- [ ] Passes `config.as_dict` to authpoint-lambda-layer components
- [ ] Uses `parser` as parameter name
- [ ] Methods use keyword-only args (`*, dto: dict`)
- [ ] Invokers return `{}` on error instead of raising
- [ ] Domain does not import adapters
