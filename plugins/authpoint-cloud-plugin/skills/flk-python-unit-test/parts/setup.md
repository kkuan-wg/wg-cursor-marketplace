# Test Project Setup

Configuration files required for every Folklore Python test project.

---

## pytest.ini

Located at `application/pytest.ini`. All env vars and pythonpath entries go here — never in test files.

```ini
[pytest]
python_files = *_test.py
pythonpath =
    src/cache/core_data/logon_app_core_data_consumer_fn
    src/cache/resource/logon_app_resource_cmd_invoker_fn
    src/cache/user/logon_app_user_cmd_invoker_fn
    src/transaction/logon_app_tx_consumer_fn
    src/transaction/logon_app_tx_timeout_publisher_fn
    src/data/transaction_stream/logon_app_tx_listener_fn
    src/data/transaction_stream/logon_app_tx_event_replay_fn
    src/api/logon_app_authn_api_fn
    src/api/logon_app_config_api_fn
    src/api/logon_app_online_policy_api_fn
    src/api/logon_app_qrcode_api_fn
    src/api/logon_app_tx_mw
    ../../../layers/authpoint-lambda-layer/application/lambda_layer/python
    ../../folklore-lambda-layer/application/domain_layer/python

addopts = --maxfail=2 -s -rf --cov=src --cov-report term-missing --cov-report xml tests/

flake8-ignore = * E402 \
                * E731 \
                * W503 \
                * E501

filterwarnings =
    ignore : :DeprecationWarning

env =
    AWS_REGION = us-west-2
    MAIN_REGION = us-west-2
    ENVIRONMENT = dev
    TX_TABLE_NAME = flk-logon-app-tx
    CLIENT_CONFIG_TABLE_NAME = dev-amer-flk-logon-app-client-config
    USER_DETAIL_TABLE_NAME = dev-amer-flk-logon-app-user-detail
    AUTHN_METADATA_TABLE_NAME = dev-amer-flk-authn-metadata
    TX_RESULT_TOPIC_ARN = flk-logon-app-tx-result-topic.fifo
    TX_QUEUE_URL = flk-logon-app-tx-queue.fifo
    TX_EVENT_REPLAY_QUEUE_URL = flk-logon-app-tx-event-replay-queue
    ZTE_POLICY_QUERY_API_BASE_URL = zte-query/v1
    ZTE_POLICY_EVALUATOR_API_BASE_URL = zte-policy-evaluator/v1
    AUTHENTICATION_CORE_REQUEST_TOPIC_ARN = flk-authn-core-request-topic.fifo
```

**Rules:**
- `pythonpath` must include **all** lambda `src/` dirs and both Lambda Layers
- `env` must include **all** env vars read by any function under test (`getenv(...)` calls)
- `--cov=src` covers only `src/`, not tests or layers
- `--maxfail=2` stops after 2 failures

---

## .coveragerc

Located at `application/.coveragerc`:

```ini
[run]
omit =
    */port/*
    */app.py
    tests/*
branch = True
```

- `*/port/*` — Ports are abstract interfaces; no tests needed
- `*/app.py` — Lambda entry points are wiring only; no tests needed
- `branch = True` — Branch coverage enabled

---

## sonar-project.properties

Located at `application/sonar-project.properties`:

```properties
sonar.coverage.exclusions=**/port/**,**/app.py,**/configure_newrelic.py
sonar.cpd.exclusions=**/port/**,**/adapter/**,**/configuration.py,**/app.py,**/domain/service.py
sonar.sources=src
sonar.tests=tests
sonar.verbose=true
sonar.python.xunit.reportPath=results.xml
sonar.python.coverage.reportPaths=coverage.xml
```

---

## tests/requirements.txt

Located at `application/tests/requirements.txt`. Include every library used by any function under test:

```
pytest==8.3.3
coverage==7.6.1
pytest-cov==5.0.0
pytest-env==1.1.4
pytest-mock==3.14.0
flake8==5.0.4
pytest-flake8==1.2.2
boto3==1.35.18
fastapi==0.116.1
uvicorn==0.35.0
```

**Rule:** Any library imported by a Lambda function must be declared here — even if it comes from a Lambda Layer in production.

---

## Jenkins execution commands

Run from `application/` directory:

```bash
# Tests with coverage
python -m pytest --cov-report xml --junitxml results.xml

# PEP-8 validation
python -m pytest --flake8 --junitxml pep8.out
```

---

## Checklist

- [ ] `pythonpath` includes all lambda `src/` dirs
- [ ] `pythonpath` includes both `authpoint-lambda-layer` and `folklore-lambda-layer`
- [ ] `env` includes all env vars used by functions under test
- [ ] `.coveragerc` omits `*/port/*`, `*/app.py`, `tests/*`
- [ ] `tests/requirements.txt` includes all libs (including layer dependencies)
