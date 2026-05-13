# Crypto Adapter — Encrypt/Decrypt

Implements crypto ports using the authpoint-lambda-layer `adapter.security.comm_crypto.CommCrypto`. File: `comm_crypto.py`. Some use cases require `parser` (e.g. payload crypto with template parsing); others only need `config`. See [parts/layer-authpoint-lambda.md](../layer-authpoint-lambda.md).

---

## Layer Component

```python
from adapter.security.comm_crypto import CommCrypto
```

---

## Example 1: Encrypt and decrypt (with parser)

```python
from json import loads

from adapter.data_processing.template_parser import TemplateParser
from adapter.security.comm_crypto import CommCrypto
from logon_app_authn_api.configuration import CommunicationCryptoConfig
from logon_app_authn_api.port.crypto import CommCryptoPort


class CommunicationCrypto(CommCryptoPort):

    def __init__(self, *, payload_config: CommunicationCryptoConfig, parser: TemplateParser):
        self.payload_crypto = CommCrypto(config=payload_config.as_dict, template_parser=parser)

    def decrypt_data(self, *, dto: dict) -> dict:
        return loads(self.payload_crypto.decrypt_agent(dto=dto))

    def encrypt_data(self, *, dto: dict) -> str:
        return self.payload_crypto.encrypt_agent(dto=dto)
```

---

## Example 2: Encrypt only (config only)

```python
from adapter.security.comm_crypto import CommCrypto
from logon_app_tx.configuration import CommunicationCryptoConfig
from logon_app_tx.port.crypto import CommCryptoPort


class CommunicationCrypto(CommCryptoPort):

    def __init__(self, *, config: CommunicationCryptoConfig):
        self.crypto = CommCrypto(config=config.as_dict)

    def encrypt_data(self, *, dto: dict) -> str:
        return self.crypto.encrypt_agent(dto=dto)
```

---

## Checklist

- [ ] File: `comm_crypto.py`
- [ ] Uses `CommCrypto` from `adapter.security.comm_crypto`
- [ ] Passes `config.as_dict` to authpoint-lambda-layer
- [ ] Add `parser` when the layer requires `template_parser`
