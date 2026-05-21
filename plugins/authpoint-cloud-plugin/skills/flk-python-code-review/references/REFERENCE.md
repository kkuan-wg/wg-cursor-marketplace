# Python Code Review Reference

Detailed reference for the Folklore Python Lambda *code-reviewer* skill.
Read this when verifying an existing implementation against Folklore patterns.

---

## 1. Scope of This Reference

This reference is intentionally reviewer-focused (not a full architecture guide). It captures:
- Hexagonal boundaries (domain vs port vs adapter)
- DTO and method signature conventions
- Logging and error-handling conventions (including SQS/DDB vs API differences)
- Configuration hygiene (env var usage and module-level key constants)
- Lambda wiring checks (`app.py`) and package integrity (`__init__.py`)

For broader architecture and folder/port/adapter rules, always read `flk-python-hexagonal` first.

---

## 2. Hexagonal Boundaries (Ports & Adapters)

### 2.1 Dependency direction
- `domain/service.py` must not import `adapter.*`.
- `domain/service.py` must not perform I/O (DDB/SQS/SNS calls, network, filesystem, AWS SDK operations).
- `Service` imports only `port.*`, `flk_core.*`, `flk_utils.*`, and stdlib (per `flk-python-hexagonal`).

### 2.2 Ports (ABCs)
- Port ABC methods must use `return NotImplemented` in abstract method bodies (not `raise NotImplementedError`).

### 2.3 Adapters
- Adapters must implement a single port type and act as thin translation layers.
- Adapters must delegate AWS operations to the appropriate layer components and pass `config.as_dict` when wiring those layer components.

---

## 3. DTO + Method Signature Conventions

### 3.1 Keyword-only parameters
- Every method parameter after `self` is keyword-only across domain/port/adapter layers: `def fn(self, *, dto: dict): ...`

### 3.2 Canonical DTO name
- The shared data bag parameter name must be exactly `dto` everywhere (service, ports, adapters).

### 3.3 DTO updates
- Prefer in-place updates: `dto.update({...})` or `dto['key'] = value`.
- Avoid using the merge operator for in-place DTO updates when the code rebinds the *same* `dto` variable (e.g., `dto = dto | {...}`), because that can break assumptions about the DTO identity being preserved.
- Allow using the merge operator when it creates a *derived* DTO, for example:
  - `derived_dto = dto | {...}` (assigned to a different variable), or
  - `return dto | {...}` (expression/return that does not imply mutating the original object).

### 3.4 Event adapter / parsing wiring
- Ensure event adapters/parsers receive config as dictionaries (`<EventConfig>().as_dict`) rather than passing config objects.

---

## 4. Logging and Error Handling

### 4.1 Logging mechanics
- Use `logging.*` only (no `print()`).
- Always include `from traceback import format_exc` in `app.py`.
- Error logs must include exception context using `format_exc()` where exceptions are caught/logged.

### 4.1.1 INFO+ payload / DTO logging (PII-safe rule)
Folklore lambdas use a safe-logging convention:
- `flk-python-hexagonal` allows `logging` of `{dto}` only when the DTO has a custom `__str__` that logs only fields defined by `dto_log_mapping` (from configuration).

For this reviewer, apply this rule:
- If you see `logging.info(...)` (or warning/error) logging raw DTO internals (e.g., `logging.info(f"... {dto.__dict__} ...")`, `json.dumps(dto)`, or direct dict dumps) without evidence of safe-logging redaction, raise a PII leakage finding.
- If you see `logging.*` logging `dto`/`{dto}` and you can find evidence in the reviewed slice/configuration that safe-logging applies (e.g., `dto_log_mapping` present/used, or DTO defines `__str__` that limits fields), mark the PII finding as `NOT_APPLICABLE` (or `LOW` when unsure) rather than assuming PII leakage.

### 4.2 Logging context lifecycle
- `set_context(dto=dto)` must be called after DTO creation/mapping.
- `reset_logging_context()` must be called in a `finally` block (never inside the `try`).

### 4.3 Two-tier exception strategy (universal)
- Tier 1: business/validation failures are handled at the service layer (e.g., discard message on SQS/DDB, map to HTTP error on API) and are not re-raised.
- Tier 2: infrastructure/unexpected failures are handled in `app.py` and must either:
  - SQS/DDB: re-raise to trigger retry/DLQ
  - API: return 500 via `responder.server_error(dto=dto)` (do not re-raise from `app.py`)

### 4.4 Retry/discard behavior reminders
- For SQS/DDB Lambdas: do not re-raise validation/discard exceptions (messages should be consumed/removed from retry flow).
- For SQS/DDB Lambdas: re-raise unhandled exceptions to ensure retries and DLQ.

### 4.5 Event schema validation depth (schema vs required-field checks)
Do not require a full JSON schema validator unless the spec explicitly requires it.
In this codebase, “validation depth” is typically satisfied by:
- `DtoValidator.validate_required_fields(dto=..., required_fields=...)` (required-field checks), plus
- additional explicit domain validations (e.g., enum checks, presence checks, etc.).

Apply this rule:
- If the reviewed code calls `validate_required_fields` (or an equivalent required-field validator) before any persistence/DynamoDB writes, downgrade “missing schema validation” findings to `NOT_APPLICABLE` or `LOW` and explain which validation exists.
- Only raise “schema validation not met” when you find evidence of writes/persistence occurring without even the required-field validation path.

### 4.6 SQS event batch size (“Records” size 1)
Consider that for Lambdas that process SQS queue events, Folklore convention enforces an SQS event source mapping batch size of `1`.
- Do not require per-`Records` iteration; treat `event["Records"]` as a single-element list.

### 4.8 PATCH semantics (merge vs replace)
Only treat merge-vs-replace as a finding when the provided spec explicitly defines patch/merge semantics.
When the spec does not specify merge behavior, downgrade merge/patch findings to `LOW` and mark as `NEEDS_DISCUSSION` in the Questions section.

---

## 5. Configuration Hygiene

### 5.1 Env var usage
- `os.getenv` / `os.environ.get` calls must be confined to configuration modules (e.g., `configuration.py`), not in `app.py` handler logic, `domain/service.py`, `port`, or `adapter` implementations.
- In `configuration.py`, simple module-level `getenv(...)` assignments used to define constants (e.g., `TABLE_NAME = getenv(...)`, including building derived constant strings from that value) are allowed.
- If env var lookups occur outside configuration modules, treat that as a configuration-hygiene finding.

### 5.2 Key strings and mapping constants
- Do not inline map keys, message keys, or DDB schema keys in domain/adapter logic.
- Define all such string constants at module level in `configuration.py`.

### 5.3 `config.as_dict` contract
- When passing config into layer utilities/classes, use `**config.as_dict` or `config=config.as_dict` (never pass config objects directly).

---

## 6. Lambda Wiring (`app.py`) Checks

Verify at least:
- `dto` is initialized to `{}` before the `try` block (so error paths can safely reference it).
- The handler maps raw events into `dto` via the correct event adapter/parsers.
- `set_context(dto=dto)` is called after DTO mapping.
- `reset_logging_context()` is called in `finally`.
- SQS/DDB handler re-raises unexpected exceptions; API handler returns `responder.server_error(dto=dto)` on uncaught exceptions.

---

## 7. Python Package Integrity

- Every directory in the lambda module tree must contain an empty `__init__.py` so runtime imports work.

---

## 8. Reviewer Severity Guidance (for findings)

Use these severities consistently:
- `CRITICAL`: functional bug or architectural contract violation that likely breaks correctness at runtime.
- `HIGH`: strong systemic pattern violation that will likely cause incorrect behavior or future repeated defects.
- `MEDIUM`: quality/maintainability issue that increases risk over time.
- `LOW`: stylistic/consistency issue.

