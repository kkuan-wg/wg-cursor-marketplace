---
name: flk-python-lambda-ddb-listener
description: Creates Folklore Lambda Python code (configuration, ports, adapters, domain service, app.py) for DynamoDB stream listener functions following hexagonal architecture. Use when creating or modifying a DDB stream listener Lambda, or when the user mentions DynamoDB stream listener, DdbStreamEvent, DdbStreamEventConfig, stream Lambda, or authn context listener. Does NOT cover SAM templates or infrastructure — use flk-sam-ops-ddb-listener for that.
---

# Folklore Python Lambda DynamoDB Stream Listener

Creates the Python application code for Lambda functions that listen to DynamoDB stream events and publish to SNS FIFO topics (with optional SQS fallback). Covers `configuration.py`, ports, adapters, `domain/service.py`, and `app.py` only — no SAM templates or infrastructure.

`flk-python-hexagonal` is always loaded alongside this skill — all general architecture rules, quality standards, and the general checklist defined there apply here without repetition.

## Phase 1: Investigate Before Acting

**Complete all steps before writing any file.**

### 1. Parse the input

**If a spec path was provided**, read the following files before doing anything else:
- `spec.md` — extract: AWS Services, REQ descriptions, port method names, entity types, event types, DynamoDB table names
- `proposal.md` — found in the same folder as the spec; extract: the exact files to create (listed under **Artifacts**) and scope boundaries
- `code-tasks.md` — found in the same folder as `proposal.md`; extract: the ordered implementation tasks under **Implementation**; treat these as the work checklist

From these files extract: `function_name`, `module_name`, entity types, event types, port method names, env var names, whether SQS fallback is needed.

**If no spec was provided**, extract from the user's direct input.

### 2. Browse the codebase

**All browsing is scoped to the current workspace.** Never navigate into sibling repositories to locate reference lambdas or to place output files — the workspace root is both the reference boundary and the output destination.

Find the nearest sibling DDB stream listener **within the workspace** and read its `app.py` and `configuration.py`. Extract:
- `FUNCTION_NAME` format (`flk-{domain}-{feature}-listener`) — match the convention
- Whether credential-style or transaction-style SNS publishing is used (see [references/REFERENCE.md](references/REFERENCE.md))
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

- `FUNCTION_NAME = 'flk-{domain}-{feature}-listener'`
- Event key constants
- `DdbStreamEventConfig(BaseConfig)` — `dto_mapping` and `dto_log_mapping`
- `SnsPublishConfig(BaseConfig)` — `topic_arn`, `source`, `aws_region`, `event_data_mappings`, `message_group_id_schemas`, `event_configs`
- `SqsProducerConfig(BaseConfig)` — only when SQS fallback is needed
- `DdbRepositoryConfig(Environment, BaseConfig)` — only when the listener also writes to DynamoDB
- One config class per adapter

See [references/REFERENCE.md](references/REFERENCE.md) for all config patterns.

### Step 2 — `{module_name}/port/*.py`

One file per adapter type. Method names come from `spec.md` REQ definitions or `proposal.md` Artifacts.

### Step 3 — `{module_name}/adapter/*.py`

One file per adapter. Delegate all AWS operations to the authpoint-lambda-layer class.

**SNS adapter publishing styles:**
- **Credential-style:** passes `event_type` explicitly per publish call
- **Transaction-style:** passes `event_key` only; `event_configs` in `SnsPublishConfig` define `eventType`

See [references/REFERENCE.md §4](references/REFERENCE.md#4-adapter-class-bodies) for the canonical adapter class bodies.

### Step 4 — `{module_name}/domain/service.py`

- `Service.__init__` keyword-only arguments matching the ports needed
- Inner `EventValidator` (or validator class named in spec) with `REQUIRED_FIELDS` dicts per entity/event type
- `process(self, *, dto: dict)` routes by `entityType` then `eventType`; private `_process_*` per combination
- Catches `ValidationException` → log and **return** (discard the record — do not re-raise)
- When producer exists: use `execute_with_fallback(dto=dto, primary=publisher.method, fallback=producer.method)`
- Implement every handler defined in `code-tasks.md` under Implementation

### Step 5 — `__init__.py` files

Create an empty `__init__.py` in every directory of the module tree:
- `{function_name}_fn/__init__.py`
- `{function_name}_fn/{module_name}/__init__.py`
- `{function_name}_fn/{module_name}/port/__init__.py`
- `{function_name}_fn/{module_name}/adapter/__init__.py`
- `{function_name}_fn/{module_name}/domain/__init__.py`

### Step 6 — `app.py`

**Without SQS fallback:**

```python
import logging
from traceback import format_exc

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.ddb_stream_event import DdbStreamEvent
from configuration.logger import initialize_logging_session, set_context, reset_logging_context
from {module_name}.adapter.sns_publisher import SnsPublisher
from {module_name}.configuration import FUNCTION_NAME, DdbStreamEventConfig, SnsPublishConfig
from {module_name}.domain.service import Service

initialize_logging_session(service_name=FUNCTION_NAME)

parser = TemplateParser()
ddb_stream_event = DdbStreamEvent(config=DdbStreamEventConfig().as_dict, template_parser=parser)
publisher = SnsPublisher(config=SnsPublishConfig(), template_parser=parser)
service = Service(publisher=publisher)


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

**With SQS fallback:** also import `SqsProducer` and `SqsProducerConfig`, add `producer = SqsProducer(...)`, pass `producer=producer` to `Service`.

**DDB stream listener-specific rules:**
- **No** `dto = {}` before `try` — no response value to return
- `except Exception` logs and **`raise ex`** — always re-raise so AWS retries or routes to DLQ
- **Never** catch `ValidationException` in `app.py` — domain service handles it and discards silently
- SQS fallback adapter uses `message_key` (not `event_key`) in `build_message_payload_with_str_data`

---

## Phase 3: Verify Before Finishing

The `flk-python-hexagonal` general checklist applies in full. Additionally verify:

- [ ] All files listed in `proposal.md` Artifacts exist
- [ ] All tasks under **Implementation** in `code-tasks.md` are addressed
- [ ] No `dto = {}` before `try` in `app.py`
- [ ] `except Exception` re-raises (`raise ex`) — no swallowing
- [ ] `ValidationException` caught only in `domain/service.py` → log and return
- [ ] `execute_with_fallback` used when a SQS fallback producer exists
- [ ] SQS fallback adapter uses `message_key` (not `event_key`)

## Reference

- `DdbStreamEventConfig` with DTO mapping types, `SnsPublishConfig` (both styles), `SqsProducerConfig`, SNS/SQS adapter bodies, fallback pattern → [references/REFERENCE.md](references/REFERENCE.md)
- Real examples (DDB stream listener with SNS + SQS fallback) → [references/REFERENCE.md §5](references/REFERENCE.md#5-real-examples)
- SAM template / infrastructure → `flk-sam-ops-ddb-listener` skill
