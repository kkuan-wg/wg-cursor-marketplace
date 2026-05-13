# Lambda Layer — folklore-lambda-layer

The **folklore-lambda-layer** provides shared domain helpers, enums, constants, and repository config schemas. It is used in the **domain** (helpers, validators) and **configuration** (shared PK/SK/GSI schemas). It does not provide adapters — those come from authpoint-lambda-layer.

---

## 1. Structure

```
domain_layer/python/
├── flk_api/              # API-level helpers and configs (per context)
│   ├── api_config_helper.py          # Base repository config schemas
│   ├── policy_helper.py              # PolicyHelper
│   ├── transaction_helper.py         # TransactionHelper
│   ├── user_helper.py                # UserHelper
│   ├── transaction_builder_helper.py # TransactionBuilderBase (ABC)
│   ├── cmd_invoker_helper.py         # User/group command helpers
│   ├── logon_app/                    # logon-app context
│   ├── oidc/                         # oidc context
│   ├── radius/                       # radius context
│   └── firebox/                      # firebox context
├── flk_core/             # Core domain logic and enums
│   ├── core_commons.py               # Enums, constants, entity types
│   ├── core_validation_helper.py     # CoreAuthnDataValidator
│   ├── core_credentials_helper.py    # CoreUserHelper, is_active_token, is_software_token
│   ├── core_builder_helper.py        # CoreResultBuilder
│   └── core_settings_helper.py       # CoreSettingsHelper
├── flk_info/             # Audit and report helpers
│   ├── audit_helper.py               # AuditHelper
│   └── report_helper.py              # ReportHelper
└── flk_utils/            # ⚠️ DEPRECATED — use authpoint-lambda-layer instead
```

> **`flk_utils` is deprecated.** All functions (`DtoValidator`, `date_time_helper`, `sanitization_helper`) have been moved to authpoint-lambda-layer. Always import from `utils.*` (authpoint-lambda-layer), never from `flk_utils.*`.

---

## 2. flk_api — API helpers

### PolicyHelper

```python
from flk_api.policy_helper import PolicyHelper

helper = PolicyHelper()
helper.is_upgrade_required(session_authn_types=[...], policy_authn_type={...})
PolicyHelper.is_policy_mfa(policy=policy)          # True if otp/push/qrcode/passkey
PolicyHelper.is_policy_name_missing_or_blank(policy=policy)
PolicyHelper.get_fake_policy()                      # Returns default fake policy dict
```

### TransactionHelper

```python
from flk_api.transaction_helper import TransactionHelper

helper = TransactionHelper()
helper.is_authentication_completed(tx=tx, authn_event_dto=dto)
TransactionHelper.is_authn_event_authorized(event_dto=dto)
```

### UserHelper

```python
from flk_api.user_helper import UserHelper

helper = UserHelper()
helper.is_user_authentication_allowed(user_detail=user_detail)
helper.get_authentication_not_allowed_reason(user_detail=user_detail)
```

### TransactionBuilderBase

Abstract base class for building transaction result dicts. Each context (logon_app, oidc, radius, firebox) has its own subclass:

| Class | Import |
|-------|--------|
| `LogonAppTransactionResultBuilder` | `flk_api.logon_app.transaction_builder_helper` |
| `OidcTransactionResultBuilder` | `flk_api.oidc.transaction_builder_helper` |
| `RadiusTransactionResultBuilder` | `flk_api.radius.transaction_builder_helper` |
| `FireboxTransactionResultBuilder` | `flk_api.firebox.transaction_builder_helper` |

Key methods (all subclasses):
- `build_processing_transaction(*, tx_event_dto)` — TX_STATUS_PROCESSING
- `build_authn_done_transaction_authorized(*, authn_event_dto)` — TX_STATUS_AUTHN_DONE + AUTHORIZED
- `build_authn_done_transaction_unauthorized(*, authn_event_dto)` — TX_STATUS_AUTHN_DONE + UNAUTHORIZED
- `build_authn_done_transaction_unauthorized_server_error(tx_event_dto)` — SERVER_ERROR reason
- `build_authn_done_transaction_unauthorized_timeout(*, tx_event_dto)` — TX_TIMEOUT reason

---

## 3. flk_core — Core domain

### core_commons — enums and constants

Most-used classes:

```python
from flk_core.core_commons import (
    CoreCredentialEntityType,   # CREDENTIAL_TYPE_USER, USER_AUTH, USER_CACHE, TOKEN_SOFTWARE, TOKEN_HARDWARE, ...
    CoreAuthnTypes,             # PASSWORD, OTP, PUSH, QRCODE, PASSKEY, AUTHN_CODE
    CoreUserCredential,         # STATUS_ACTIVE, STATUS_MANUALLY_BLOCKED, STATUS_AUTOMATICALLY_BLOCKED
    CoreToken,                  # STATUS_ACTIVE, STATUS_MANUALLY_BLOCKED, STATUS_AUTOMATICALLY_BLOCKED
    CorePushTransaction,        # STATUS_CREATED, IN_PROGRESS, TIMEOUT, DONE, FAILED
    CoreQrcodeTransaction,      # STATUS_PROCESSING, TIMEOUT, DONE
    RESULT_EVENT_AUTHN_STATUS_AUTHORIZED,
    RESULT_EVENT_AUTHN_STATUS_UNAUTHORIZED,
    TTL_TWO_DAYS                # 172800 seconds
)
```

### CoreUserHelper

```python
from flk_core.core_credentials_helper import CoreUserHelper, is_active_token, is_software_token

CoreUserHelper.increment_login_attempts(dto=dto, credentials=credentials, settings=settings)
CoreUserHelper.reset_login_attempts(dto=dto)
is_active_token(token=token)       # token['status'] == ACTIVE
is_software_token(token=token)     # token['credentialType'] == TOKEN_SOFTWARE
```

### CoreResultBuilder

Builds authn result dicts (authnStatus, authnFailureReason, authnTimestamp, etc.):

```python
from flk_core.core_builder_helper import CoreResultBuilder

builder = CoreResultBuilder(function_code='001')
builder.build_result_unauthorized_invalid_password(dto=dto)
builder.build_result_authorized(dto=dto)
```

---

## 4. Context-specific: api_commons and api_config_helper

Each API context has its own `api_commons.py` (enums, event types, entity types) and `api_config_helper.py` (shared DynamoDB schemas). Use only the ones relevant to the service being built.

| Context | api_commons import | api_config_helper import |
|---------|-------------------|--------------------------|
| **base** | — | `flk_api.api_config_helper.ApiRepositoryConfig` |
| **logon-app** | `flk_api.logon_app.api_commons` | `flk_api.logon_app.api_config_helper.LogonAppApiRepositoryConfig` |
| **oidc** | `flk_api.oidc.api_commons` | `flk_api.oidc.api_config_helper.OidcApiRepositoryConfig` |
| **radius** | `flk_api.radius.api_commons` | `flk_api.radius.api_config_helper.RadiusApiRepositoryConfig` |
| **firebox** | `flk_api.firebox.api_commons` | `flk_api.firebox.api_config_helper.FireboxApiRepositoryConfig` |

`ApiRepositoryConfig` (base) provides shared schemas like `USER_DETAIL_REPOSITORY_PK`, `USER_DETAIL_EMAIL_GSI`, `AUTHN_METADATA_REPOSITORY_PK`. Context subclasses extend it with context-specific schemas.

```python
# Example: using shared schema in configuration.py
from flk_api.logon_app.api_config_helper import LogonAppApiRepositoryConfig

class TransactionRepositoryConfig(BaseConfig):
    def __init__(self):
        self.table_name = getenv('TX_TABLE_NAME')
        self.partition_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_PK
        self.sort_key_schema = LogonAppApiRepositoryConfig.TRANSACTION_REPOSITORY_SK
```

---

## 5. flk_info — Audit and Report

```python
from flk_info.audit_helper import AuditHelper

helper = AuditHelper()
helper.validate_account_id(dto=dto)
helper.build_audit_dto(dto)
helper.build_user_status_audit_dto(dto=dto)
AuditHelper.is_auditable_event(dto=dto, supported_event_types=(...,))
```

---

## 6. Checklist

- [ ] Import helpers from `flk_api.*` or `flk_core.*` — never from `flk_utils.*` (deprecated)
- [ ] Use `CoreCredentialEntityType`, `CoreAuthnTypes`, etc. for entity type constants
- [ ] Use context-specific `api_config_helper` for shared DynamoDB schemas in `configuration.py`
- [ ] Use context-specific `api_commons` for event types, entity types, result reasons
- [ ] `TransactionBuilderBase` subclasses are context-specific — pick the right one
