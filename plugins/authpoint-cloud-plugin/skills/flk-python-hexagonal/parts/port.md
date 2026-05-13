# Port — Abstract Interfaces

Ports define the **contracts** between the domain and infrastructure. The domain depends on ports; adapters implement them. Ports have **no implementation** — only abstract method signatures.

---

## 1. Role of Ports

| Responsibility | Description |
|----------------|-------------|
| **Contract** | Define what the domain needs from infrastructure |
| **Inversion** | Domain depends on ports, not adapters |
| **Testability** | Services can be tested with mock ports |

---

## 2. Conventions

- **Base class**: `abc.ABC`
- **Methods**: `@abstractmethod`
- **Body**: `return NotImplemented`
- **Arguments**: Keyword-only with `*` (e.g. `*, dto: dict`)
- **Class naming**: `*Port` suffix (e.g. `ClientConfigRepositoryPort`, `ResponderPort`)
- **File naming**: Simple names (`repository.py`, `responder.py`, `invoker.py`, etc.)
- **Return types**: Annotate only when returning data (`-> dict`, `-> list`, `-> str`); omit for void methods

---

## 3. Port Types

| Port Type | File | Purpose |
|-----------|------|---------|
| **Repository** | `repository.py` | Persistence (DynamoDB) |
| **Responder** | `responder.py` | HTTP response formatting |
| **Invoker** | `invoker.py` | External API calls (API Gateway, Lambda) |
| **Publisher** | `publisher.py` | SNS publish |
| **Producer** | `producer.py` | SQS produce |
| **Crypto** | `crypto.py` | Encrypt/decrypt operations |

---

## 4. Complete Examples

### Example 1: repository.py — Multiple Repository Ports

Multiple related repository interfaces in one file. Methods: `retrieve_*`, `save_*`, `update_*`.

```python
from abc import abstractmethod, ABC


class ClientConfigRepositoryPort(ABC):

    @abstractmethod
    def retrieve_client_config_by_account_id_and_resource_id(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def retrieve_client_config_by_swa_enabled_and_account_id(self, *, dto: dict) -> list:
        return NotImplemented


class UserDetailRepositoryPort(ABC):

    @abstractmethod
    def retrieve_user_detail_by_account_id_and_username(self, *, dto: dict) -> dict:
        return NotImplemented


class TransactionRepositoryPort(ABC):

    @abstractmethod
    def retrieve_transaction_by_account_id_and_transaction_id(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def update_tx_result(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def save_transaction(self, *, dto: dict):
        return NotImplemented


class AuthnContextRepositoryPort(ABC):

    @abstractmethod
    def retrieve_authn_context_by_account_id_and_authn_context_id(self, *, dto: dict) -> dict:
        return NotImplemented


class AuthnMetadataRepositoryPort(ABC):

    @abstractmethod
    def retrieve_authn_metadata_by_account_id_and_user_id(self, *, dto: dict) -> dict:
        return NotImplemented
```

---

### Example 2: repository.py — Simple (single port)

```python
from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def retrieve_transaction_by_account_id_and_transaction_id(self, *, dto: dict):
        return NotImplemented
```

---

### Example 3: responder.py — Full API Responder

```python
from abc import abstractmethod, ABC


class ResponderPort(ABC):

    @abstractmethod
    def success(self, *, encrypted_data: str, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def unauthorized(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def bad_request(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def precondition_failed(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def server_error(self, *, dto: dict) -> dict:
        return NotImplemented
```

---

### Example 4: responder.py — Minimal

```python
from abc import abstractmethod, ABC


class ResponderPort(ABC):

    @abstractmethod
    def success(self, *, encrypted_data: str, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def bad_request(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def precondition_failed(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def server_error(self, *, dto: dict) -> dict:
        return NotImplemented
```

---

### Example 5: invoker.py — API Gateway Invoker

```python
from abc import abstractmethod, ABC


class RetrievePoliciesInvokerPort(ABC):

    @abstractmethod
    def retrieve_policy(self, *, dto: dict) -> dict:
        return NotImplemented
```

---

### Example 6: invoker.py — Lambda Invoker

```python
from abc import abstractmethod, ABC


class GetTokenDataInvokerPort(ABC):

    @abstractmethod
    def get_token_data(self, *, dto: dict) -> dict:
        return NotImplemented
```

---

### Example 7: publisher.py — SNS Publisher

```python
from abc import ABC, abstractmethod


class RequestPublisherPort(ABC):

    @abstractmethod
    def push_requested(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def qrcode_requested(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def otp_requested(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def authn_code_requested(self, *, dto: dict):
        return NotImplemented
```

---

### Example 8: publisher.py — Transaction Events

```python
from abc import ABC, abstractmethod


class PublisherPort(ABC):

    @abstractmethod
    def transaction_created(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_non_mfa_done(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_authorized(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_unauthorized(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_forgot_token_enable_done(self, *, dto: dict):
        return NotImplemented
```

---

### Example 9: producer.py — SQS Producer (transaction events)

```python
from abc import ABC, abstractmethod


class ProducerPort(ABC):

    @abstractmethod
    def transaction_created(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_non_mfa_done(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_authorized(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_unauthorized(self, *, dto: dict):
        return NotImplemented

    @abstractmethod
    def transaction_forgot_token_enable_done(self, *, dto: dict):
        return NotImplemented
```

---

### Example 10: producer.py — SQS Producer (single method)

```python
from abc import ABC, abstractmethod


class ProducerPort(ABC):

    @abstractmethod
    def send_tx_timed_out(self, *, dto: dict) -> dict:
        return NotImplemented
```

---

### Example 11: crypto.py — Full (encrypt + decrypt)

```python
from abc import abstractmethod, ABC


class CommCryptoPort(ABC):

    @abstractmethod
    def decrypt_data(self, *, dto: dict) -> dict:
        return NotImplemented

    @abstractmethod
    def encrypt_data(self, *, dto: dict) -> str:
        return NotImplemented
```

---

### Example 12: crypto.py — Encrypt only

```python
from abc import abstractmethod, ABC


class CommCryptoPort(ABC):

    @abstractmethod
    def encrypt_data(self, *, dto: dict) -> str:
        return NotImplemented
```

---

## 5. File Organization

| Scenario | Approach |
|----------|----------|
| Multiple related ports (e.g. several repositories) | One file, multiple classes (`repository.py`) |
| Single port type | One file, one or few classes |
| Unrelated ports | Separate files (`repository.py`, `invoker.py`, etc.) |

---

## 6. Special Adapters

Some ports (e.g. Crypto) may have adapters that wrap external libraries or special logic. The port remains a pure interface; the adapter handles implementation details such as key management, algorithms, or integration with KMS/Secrets Manager.

---

## 7. Port Checklist

- [ ] Extends `ABC`
- [ ] All methods use `@abstractmethod`
- [ ] Methods use keyword-only args (`*, dto: dict` or specific params)
- [ ] Return type annotated only for non-void methods (`-> dict`, `-> list`, `-> str`)
- [ ] Method body: `return NotImplemented`
- [ ] Class name ends with `*Port`
- [ ] File name is simple (`repository.py`, not `repository_port.py`)
- [ ] No implementation logic — interface only
