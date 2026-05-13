---
name: flk-python-lambda-api
description: Creates Folklore API Lambda Python code (configuration, ports, adapters, domain service, app.py) for HTTP Lambdas following hexagonal architecture. Use when creating or modifying API Lambda code, HTTP handlers, REST endpoints, or when the user mentions API Lambda, api_fn, HttpEvent, or API Gateway. Does NOT cover SAM templates or infrastructure — use flk-sam-ops-api for that.
---

# Folklore Python Lambda API

Creates the Python application code for API Lambda functions that handle HTTP requests from API Gateway. Covers `configuration.py`, ports, adapters, `domain/service.py`, and `app.py` only — no SAM templates or infrastructure.

`flk-python-hexagonal` is always loaded alongside this skill — all general architecture rules, quality standards, and the general checklist defined there apply here without repetition.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

**If a spec path was provided**, read the following files before doing anything else:
- `spec.md` — extract: AWS Services, REQ descriptions, port method names, endpoint paths, DynamoDB table names, error codes
- `proposal.md` — found in the same folder as the spec; extract: the exact files to create (listed under **Artifacts**) and scope boundaries
- `code-tasks.md` — found in the same folder as `proposal.md`; extract: the ordered implementation tasks under **Implementation**; treat these as the work checklist

From these files extract: `function_name`, `module_name`, adapters needed, port method names, env var names.

**If no spec was provided**, extract from the user's direct input.

### 2. Browse the codebase

**All browsing is scoped to the current workspace.** Never navigate into sibling repositories to locate reference lambdas or to place output files — the workspace root is both the reference boundary and the output destination.

Find the nearest sibling lambda **within the workspace** and read its `app.py` and `configuration.py`. Extract:
- `FUNCTION_NAME` format (`flk-{domain}-{feature}-api`) — match the convention
- The subfolder path where the sibling lives — use this as the basis for placing the new lambda's folder

If updating an existing lambda, read all its files first.

### 3. Load flk-python-hexagonal parts progressively

| Need | Part to read |
|------|-------------|
| `app.py` wiring | `parts/app-py.md` |
| Port / adapter / domain patterns | `parts/port.md`, `parts/adapter.md`, `parts/domain.md` |
| Config / DTO mapping / error codes | `parts/configuration.md` |
| Layer class catalogue | `parts/layer-authpoint-lambda.md` |
| flk_api, flk_core imports | `parts/layer-folklore-lambda.md` |

Read only parts relevant to the adapters you are implementing.

### 4. Ask only what you cannot find

One targeted question per gap. Never ask about things discoverable from the spec or codebase.

---

## Phase 2: Write the Files

Write files in this strict order. Implement every task listed under **Implementation** in `code-tasks.md`.

### Step 1 — `{module_name}/configuration.py`

- `FUNCTION_NAME = 'flk-{domain}-{feature}-api'`
- `HttpEventConfig(BaseConfig)` — `dto_mapping` merging `ApiEventConfig.API_EVENT_LOCATION_MAPPING` with custom fields; `dto_log_mapping`
- `ResponderConfig(BaseConfig)` — `allowed_origin` from `getenv`
- One config class per adapter
- `API_ERROR_CODES`

See [references/REFERENCE.md](references/REFERENCE.md) for config class examples.

### Step 2 — `{module_name}/port/*.py`

One file per adapter type. Method names come from `spec.md` REQ definitions or `proposal.md` Artifacts.

### Step 3 — `{module_name}/adapter/*.py`

One file per adapter. Delegate all AWS operations to the authpoint-lambda-layer class.

### Step 4 — `{module_name}/domain/service.py`

- `Service.__init__` keyword-only arguments for each port
- `process(self, *, dto: dict)` is the single public entry point
- Inner `EventValidator` with `REQUIRED_FIELDS` dicts and `validate_required_fields(dto)`
- Catches `ValidationException` → `responder.invalid_request(param=ex.param, dto=dto)`

### Step 5 — `__init__.py` files

Create an empty `__init__.py` in every directory of the module tree:
- `{function_name}_fn/__init__.py`
- `{function_name}_fn/{module_name}/__init__.py`
- `{function_name}_fn/{module_name}/port/__init__.py`
- `{function_name}_fn/{module_name}/adapter/__init__.py`
- `{function_name}_fn/{module_name}/domain/__init__.py`

### Step 6 — `app.py`

```python
import logging
from traceback import format_exc

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.http_event import HttpEvent
from configuration.logger import initialize_logging_session, reset_logging_context, set_context
from {module_name}.adapter.api_responder import ApiResponder
from {module_name}.adapter.{adapter_1} import {Adapter1Class}
# from {module_name}.adapter.{adapter_2} import {Adapter2Class}  # add one import per adapter
from {module_name}.configuration import FUNCTION_NAME, HttpEventConfig, ResponderConfig, {Adapter1Config}
from {module_name}.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)

parser = TemplateParser()
http_event = HttpEvent(config=HttpEventConfig().as_dict, template_parser=parser)
{adapter_1} = {Adapter1Class}(config={Adapter1Config}(), template_parser=parser)
# {adapter_2} = {Adapter2Class}(config={Adapter2Config}(), template_parser=parser)
responder = ApiResponder(config=ResponderConfig())
service = Service({adapter_1}={adapter_1}, responder=responder)
# service = Service({adapter_1}={adapter_1}, {adapter_2}={adapter_2}, responder=responder)


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

**API-specific rules (override / extend the general hexagonal rules):**
- `dto = {}` declared before the `try` block — so `responder.server_error(dto=dto)` can include `requestId` even when parsing fails
- Catch-all `except Exception` → `return responder.server_error(dto=dto)` — **never re-raise**
- `HttpEvent` receives `config=HttpEventConfig().as_dict` (not the config object itself)
- `ApiResponder` takes only `config=ResponderConfig()` — no `template_parser`
- Adapters that wrap a layer datasource/transport class take `template_parser=parser`; `ApiResponder` does not

---

## Phase 3: Verify Before Finishing

The `flk-python-hexagonal` general checklist applies in full. Additionally verify:

- [ ] All files listed in `proposal.md` Artifacts exist
- [ ] All tasks under **Implementation** in `code-tasks.md` are addressed
- [ ] `dto = {}` is declared before the `try` block in `app.py`
- [ ] `except Exception` returns `responder.server_error(dto=dto)` — no re-raise
- [ ] `HttpEvent` receives `.as_dict` in `app.py`
- [ ] `configuration.py` contains `API_ERROR_CODES`

## Reference

- Layer class catalogue, config patterns, adapter patterns, DTO mapping examples → [references/REFERENCE.md](references/REFERENCE.md)
- SAM template / infrastructure → `flk-sam-ops-api` skill
