---
name: flk-python-lambda-sqs-consumer
description: Creates Folklore Lambda Python code (configuration, ports, adapters, domain service, app.py) for SQS consumer functions following hexagonal architecture. Use when creating or modifying an SQS consumer Lambda, or when the user mentions SQS consumer, SqsEvent, SqsEventConfig, cmd invoker, or cache consumer. Does NOT cover SAM templates or infrastructure — use flk-sam-ops-sqs-consumer for that.
---

# Folklore Python Lambda SQS Consumer

Creates the Python application code for Lambda functions that consume SQS messages. Covers `configuration.py`, ports, adapters, `domain/service.py`, and `app.py` only — no SAM templates or infrastructure.

`flk-python-hexagonal` is always loaded alongside this skill — all general architecture rules, quality standards, and the general checklist defined there apply here without repetition.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

**If a spec path was provided**, read the following files before doing anything else:
- `spec.md` — extract: AWS Services, REQ descriptions, port method names, entity types, event types, DynamoDB table names
- `proposal.md` — found in the same folder as the spec; extract: the exact files to create (listed under **Artifacts**) and scope boundaries
- `code-tasks.md` — found in the same folder as `proposal.md`; extract: the ordered implementation tasks under **Implementation**; treat these as the work checklist

From these files extract: `function_name`, `module_name`, entity types, event types, port method names, env var names.

**If no spec was provided**, extract from the user's direct input.

### 2. Browse the codebase

**All browsing is scoped to the current workspace.** Never navigate into sibling repositories to locate reference lambdas or to place output files — the workspace root is both the reference boundary and the output destination.

Find the nearest sibling SQS consumer **within the workspace** and read its `app.py` and `configuration.py`. Extract:
- `FUNCTION_NAME` format (`flk-{domain}-{feature}-consumer`) — match the convention
- The subfolder path where the sibling lives — use this as the basis for placing the new lambda's folder

If updating an existing lambda, read all its files first.

### 3. Load flk-python-hexagonal parts progressively

| Need | Part to read |
|------|-------------|
| `app.py` wiring | `parts/app-py.md` |
| Port / adapter / domain patterns | `parts/port.md`, `parts/adapter.md`, `parts/domain.md` |
| Config / DTO mapping | `parts/configuration.md` |
| Layer class catalogue | `parts/layer-authpoint-lambda.md` |
| flk_core, flk_utils imports | `parts/layer-folklore-lambda.md` |

Read only parts relevant to the adapters you are implementing.

### 4. Ask only what you cannot find

One targeted question per gap. Never ask about things discoverable from the spec or codebase.

---

## Phase 2: Write the Files

Write files in this strict order. Implement every task listed under **Implementation** in `code-tasks.md`.

### Step 1 — `{module_name}/configuration.py`

- `FUNCTION_NAME = 'flk-{domain}-{feature}-consumer'`
- `SqsEventConfig(BaseConfig)` — `dto_mapping` and `dto_log_mapping`
- `DdbRepositoryConfig(Environment, BaseConfig)` — `table_name`, `partition_key_schema`, `model_mappings`; add `ttl_attribute_name` / `ttl_delay_in_seconds` only when soft-delete is required
- One config class per adapter

See [references/REFERENCE.md](references/REFERENCE.md) for `SqsEventConfig` and `DdbRepositoryConfig` patterns.

### Step 2 — `{module_name}/port/*.py`

One file per adapter type. Method names come from `spec.md` REQ definitions or `proposal.md` Artifacts.

### Step 3 — `{module_name}/adapter/*.py`

One file per adapter. Delegate all AWS operations to the authpoint-lambda-layer class.

### Step 4 — `{module_name}/domain/service.py`

- `Service.__init__` keyword-only arguments matching the ports needed
- Inner `EventValidator` (or validator class named in spec) with `REQUIRED_FIELDS` dicts per entity/event type
- `process(self, *, dto: dict)` routes by `entityType` then `eventType`; private `_process_*` per combination
- Catches `ValidationException` → log and **return** (discard the record — do not re-raise)
- Implement every handler defined in `code-tasks.md` under Implementation

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
from adapter.event.sqs_event import SqsEvent
from configuration.logger import initialize_logging_session, set_context, reset_logging_context
from {module_name}.adapter.{adapter_1} import {Adapter1Class}
# from {module_name}.adapter.{adapter_2} import {Adapter2Class}  # add one import per adapter
from {module_name}.configuration import FUNCTION_NAME, SqsEventConfig, {Adapter1Config}
from {module_name}.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)

parser = TemplateParser()
sqs_event = SqsEvent(config=SqsEventConfig().as_dict, template_parser=parser)
{adapter_1} = {Adapter1Class}(config={Adapter1Config}(), template_parser=parser)
# {adapter_2} = {Adapter2Class}(config={Adapter2Config}(), template_parser=parser)
service = Service({adapter_1}={adapter_1})
# service = Service({adapter_1}={adapter_1}, {adapter_2}={adapter_2})


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

**SQS consumer-specific rules:**
- **No** `dto = {}` before `try` — no response value to return
- `except Exception` logs and **`raise ex`** — always re-raise so AWS retries or routes to DLQ
- **Never** catch `ValidationException` in `app.py` — domain service handles it and discards silently
- `SqsEvent.as_dto(event=event)` handles batch records internally — **no manual loop over `Records`**
- Adapters wrapping a layer datasource/transport class (e.g. `DdbRepository`, `SnsPublisher`, `SqsProducer`) take `template_parser=parser`; pass it explicitly in `app.py`

---

## Phase 3: Verify Before Finishing

The `flk-python-hexagonal` general checklist applies in full. Additionally verify:

- [ ] All files listed in `proposal.md` Artifacts exist
- [ ] All tasks under **Implementation** in `code-tasks.md` are addressed
- [ ] No `dto = {}` before `try` in `app.py`
- [ ] `except Exception` re-raises (`raise ex`) — no swallowing
- [ ] `ValidationException` caught only in `domain/service.py` → log and return

## Reference

- `SqsEventConfig`, `DdbRepositoryConfig` with `model_mappings`, `DdbRepository` method table → [references/REFERENCE.md](references/REFERENCE.md)
- SAM template / infrastructure → `flk-sam-ops-sqs-consumer` skill
