## Backend Tests Overview

This document summarizes how backend unit tests are structured and executed.

### Goals

- Validate HTTP API behaviors (status codes, response shapes, messages)
- Validate MQTT ingestion logic (payload validation, metric mapping, DB write calls)
- Keep tests fast and deterministic by mocking external systems (DB, SMTP, MQTT broker)
- Assert structured logging for key paths (success, warnings, errors)

### Technology

- Test runner: pytest (see [`backend/pytest.ini`](../../backend/pytest.ini))
- Mocking: `pytest-mock` via the built-in `mocker` fixture
- Coverage: `pytest-cov`

### Layout

- API tests: [`backend/tests/api/`](../../backend/tests/api/)
  - Examples: [`test_device_data.py`](../../backend/tests/api/test_device_data.py), [`test_comparison.py`](../../backend/tests/api/test_comparison.py)
- MQTT tests: [`backend/tests/mqtt_client/`](../../backend/tests/mqtt_client/)
  - Examples: [`test_handler.py`](../../backend/tests/mqtt_client/test_handler.py), `test_db_writer.py`, `test_main_ingester.py`
- Shared fixtures: [`backend/tests/conftest.py`](../../backend/tests/conftest.py)

### Fixtures and Isolation

- App and client fixtures create a fresh Flask app per test and expose a test client:
  - See [`conftest.py`](../../backend/tests/conftest.py) for `app` and `client`
- DB interactions are mocked at the module boundary (e.g., `api.device_data.get_device_data_from_db`), so no real database is needed
- Logs are asserted by patching `log_event` and inspecting calls
- SMTP and other I/O are patched similarly in alert-related tests

### Typical Assertions

- HTTP: response status, JSON structure, error messages
- MQTT handler: correct coercion/validation; DB write function called/not called; log events include expected `level` and `event`
- Error mapping: domain errors map to expected HTTP codes or logged reasons

### CI

Tests are designed to run in CI (see [`docs/workflows/ci.md`](../workflows/ci.md)). Use `pytest -q` with coverage flags as needed.


