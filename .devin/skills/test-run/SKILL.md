# Test Runner

Run tests for the Superset project with appropriate configurations.

## Usage

```
/test-run [test_path]
```

## Examples

- Run all tests: `/test-run`
- Run specific test file: `/test-run tests/unit_tests/charts/test_chart_data_api.py`
- Run specific test directory: `/test-run tests/unit_tests/charts/`

## What it does

- Activates the Python virtual environment if needed
- Runs pytest with appropriate flags
- Handles both unit tests and integration tests
- Reports test results and failures

## Context

Superset uses pytest for Python testing. Unit tests are in `tests/unit_tests/` and integration tests are in `tests/integration_tests/`. Always run tests from the project root.