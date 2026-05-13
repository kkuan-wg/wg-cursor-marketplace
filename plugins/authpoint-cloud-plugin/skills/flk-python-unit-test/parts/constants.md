# Constants Files

Constants files are pure Python modules — no classes, no functions, only module-level assignments. They follow a layered import chain where each level builds on the previous.

---

## Import hierarchy

```
http_event_constants.py          ← base: raw event + parsed DTO
        ↓
ddb_repository_constants.py      ← imports from http_event; adds DB keys + DB items
        ↓
service_constants.py             ← imports from ddb_repository + http_event; adds service-level data
```

Each file imports from its predecessor and adds what it needs. Never import in reverse order.

---

## http_event_constants.py

Defines the raw Lambda event and the expected parsed DTO. Always the base of the chain.

```python
from copy import deepcopy

HTTP_EVENT = {
    'resource': 'abc',
    'httpMethod': 'POST',
    'headers': {
        'Request-Id': '12345',
        'source-ip': '194.168.1.222',
        'Cloudfront-Viewer-City': 'Santa Rita do Sapucaí',
        'Cloudfront-Viewer-Country-Name': 'Brazil',
        'Cloudfront-Viewer-Country': 'BR',
        'Cloudfront-Viewer-Country-Region-Name': 'Minas Gerais',
        'Cloudfront-Viewer-Longitude': '-45.0',
        'Cloudfront-Viewer-Latitude': '-22.0'
    },
    'requestContext': {'extendedRequestId': '12345'},
    'pathParameters': {'accountId': 'WGC-0', 'resourceId': '123'},
    'body': {
        'data': '<encrypted>',
        'clientVersion': '1.3.3',
        'chainId': '00cf2b3f-2d69-4ee9-ac9b-87271837bbe2'
    }
}

HTTP_EVENT_SWA_ENABLED = deepcopy(HTTP_EVENT)
HTTP_EVENT_SWA_ENABLED['headers']['wgc-swa-enabled'] = 'true'

HTTP_EVENT_DTO = {
    'accountId': 'WGC-0',
    'resourceId': '123',
    'encryptedData': '<encrypted>',
    'pathParamAccountId': 'WGC-0',
    'chainId': '00cf2b3f-2d69-4ee9-ac9b-87271837bbe2',
    'clientVersion': '1.3.3',
    'httpMethod': 'POST',
    'extendedRequestId': '12345',
    'requestId': '12345',
    'resourceEndpoint': 'abc',
    'sourceIp': '194.168.1.222',
    'city': 'Santa Rita do Sapucaí',
    'country': 'BR',
    'countryName': 'Brazil',
    'regionName': 'Minas Gerais',
    'latitude': '-22.0',
    'longitude': '-45.0',
}

HTTP_EVENT_SWA_ENABLED_DTO = deepcopy(HTTP_EVENT_DTO) | {'swaEnabled': 'true'}
```

---

## ddb_repository_constants.py

Imports the base DTO and adds DynamoDB key constants and DB item fixtures.

```python
from decimal import Decimal
from tests.api.my_fn.http_event_constants import HTTP_EVENT_DTO

TX_PARTITION_KEY = 'WGC-0'
TX_SORT_KEY = 'LOGON_APP_TX#245c29a6-4e6e-4333-8437-04b9faa6383f'

CLIENT_CONFIG_PARTITION_KEY = 'WGC-0#LOGON_APP_CONFIG#123'
CLIENT_CONFIG_GSI_PARTITION_KEY = 'true'
CLIENT_CONFIG_GSI_SORT_KEY = 'WGC-0'

HTTP_EVENT_WITH_TX_ID_DTO = HTTP_EVENT_DTO | {'transactionId': '245c29a6-4e6e-4333-8437-04b9faa6383f'}
HTTP_EVENT_WITH_USER_ID_DTO = HTTP_EVENT_DTO | {'userId': 12}

USER_DETAIL_DB = {
    'partitionKey': 'USER#12',
    'accountId': 'WGC-0',
    'username': 'luffy',
    'userId': 12,
    'status': 'ACTIVE',
    'isMfa': True,
    'groups': [
        {'name': 'main', 'id': Decimal('71'), 'type': 'AUTH_POINT', 'quarantine': False}
    ],
    'userDetailType': 'USER'
}

USER_DETAIL_COLLECTION = {'USER': USER_DETAIL_DB}
```

---

## service_constants.py

Imports from both previous levels and adds service-specific data. May shadow an imported constant with an enriched version.

```python
from copy import deepcopy
from tests.api.my_fn.ddb_repository_constants import USER_DETAIL_DB
from tests.api.my_fn.http_event_constants import HTTP_EVENT_DTO

# Enrich the base DTO with service-level fields
HTTP_EVENT_DTO = deepcopy(HTTP_EVENT_DTO) | {'swaEnabled': False}

CLIENT_CONFIG_DB = {
    'accountId': 'WGC-0',
    'resourceId': '123',
    'licenses': [{'type': 'AUTH_POINT', 'count': 10}],
    'authnTypes': ['push', 'qrcode']
}

CLIENT_CONFIG_EXPIRED_LICENSE_DB = deepcopy(CLIENT_CONFIG_DB) | {
    'licenses': [{'type': 'AUTH_POINT', 'count': 0}]
}

EXPECTED_REQUIRED_FIELDS = {'accountId': str, 'resourceId': str, 'encryptedData': str}

SUCCESS_RESPONSE = {'statusCode': 200, 'body': '{"data": "<encrypted>"}', 'headers': {...}}
BAD_REQUEST_RESPONSE = {'statusCode': 400, 'body': '{"title": "bad_request", ...}', 'headers': {...}}
```

---

## Variant pattern — `_BASE_*` + deepcopy

Use a private `_BASE_*` dict to define shared fields, then compose variants:

```python
_BASE_DECRYPT_DATA = {
    'accountId': 'WGC-0',
    'userId': 12,
    'computer': 'DESKTOP-ABC123',
    'authnTypes': ['push']
}

DECRYPTED_DATA_PUSH_IS_RDP_TRUE = deepcopy(_BASE_DECRYPT_DATA) | {'isRdp': True}
DECRYPTED_DATA_PUSH_IS_RDP_FALSE = deepcopy(_BASE_DECRYPT_DATA) | {'isRdp': False, 'authnTypes': ['push']}
DECRYPTED_DATA_QRCODE = deepcopy(_BASE_DECRYPT_DATA) | {'authnTypes': ['qrcode'], 'qrcodeResponse': '123456'}
```

---

## Rules

- Constants files are **pure modules** — no classes, no functions
- Use `deepcopy(base) | {overrides}` for variants — never mutate the base
- `_BASE_*` prefix for private base dicts used only within the file
- Import from the hierarchy — never import `service_constants` into `ddb_repository_constants`
- `service_constants.py` may re-export an enriched version of `HTTP_EVENT_DTO` (shadowing the import)
