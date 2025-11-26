# NRGkick Integration Tests

Comprehensive test suite for the NRGkick Home Assistant integration with full documentation, testing strategies, and current status.

## Table of Contents

- [Quick Start](#quick-start)
- [Testing Strategy](#testing-strategy)
- [Test Results](#test-results)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

---

## Quick Start

### Run All Tests (Recommended)

```bash
# Using the convenient script (default behavior)
./run-tests.sh

# Or explicitly
./run-tests.sh all

# Or manually
pytest tests/ -v
```

### Run Only Non-Integration Tests (Fast CI-Compatible)

```bash
# Using the convenient script
./run-tests.sh ci

# Or manually
pytest tests/ -v -m "not requires_integration"
```

### Generate Coverage Report

```bash
./run-tests.sh coverage
```

---

## Testing Strategy

### Overview

This project uses **pytest-homeassistant-custom-component** which provides a full Home Assistant test environment. All tests, including integration tests marked with `@pytest.mark.requires_integration`, now run successfully in both CI and local environments.

### Test Categories

#### 1. **Unit Tests** ✅ (Run everywhere)

These tests validate individual components in isolation using mocks:

- **API Tests** (`test_api.py`): 17 tests
  - All API client methods
  - HTTP error handling
  - Authentication flows
  - Timeout behavior

**Execution**: Run everywhere (CI and local).

#### 2. **Integration Tests** ✅ (Run everywhere)

These tests use Home Assistant's integration loader and test environment, powered by `pytest-homeassistant-custom-component`:

- **Config Flow Tests** (`test_config_flow.py`): 15 tests
  - User setup flow
  - Reauthentication
  - Options/reconfiguration
  - Zeroconf discovery
  - Error handling

- **Coordinator Tests** (`test_init.py`): 7 tests
  - Entry setup/unload/reload
  - Coordinator updates
  - Error recovery

**Execution**: These run successfully in both CI (GitHub Actions) and local environments thanks to the pytest-homeassistant-custom-component package.

**CI Strategy**: For faster CI runs, GitHub Actions currently skips integration tests using the marker filter. However, these tests work in CI if needed.

### Do Tests Connect to Real Devices?

**No!** The tests are **100% isolated** from real hardware:

```python
# Example of how mocking works:
@pytest.fixture
def mock_session():
    """Mock aiohttp session - NO real HTTP calls"""
    session = AsyncMock()
    response = AsyncMock()
    response.json = AsyncMock(return_value={"fake": "data"})
    # ... creates fake responses
    return session
```

**Benefits**:

- ✅ Tests run without NRGkick hardware
- ✅ Fast execution (no network delays)
- ✅ Predictable results
- ✅ Can simulate error conditions safely
- ✅ No risk of changing real device settings

---

## Test Results

### Current Status Summary

| Test Suite             | Count  | CI Status      | Local Status | Pass Rate |
| ---------------------- | ------ | -------------- | ------------ | --------- |
| API Tests              | 26     | ✅ PASS        | ✅ PASS      | 100%      |
| Config Flow Tests      | 21     | ⏭️ SKIP (fast) | ✅ PASS      | 100%      |
| Config Flow Additional | 8      | ⏭️ SKIP (fast) | ✅ PASS      | 100%      |
| Coordinator Tests      | 13     | ⏭️ SKIP (fast) | ✅ PASS      | 100%      |
| Naming Tests           | 2      | ⏭️ SKIP (fast) | ✅ PASS      | 100%      |
| Platform Tests         | 8      | ⏭️ SKIP (fast) | ✅ PASS      | 100%      |
| **Total**              | **78** | **26 pass**    | **78 pass**  | **100%**  |

**Note**: All 78 tests work in both environments. CI skips 52 integration tests for faster builds (runs in ~2s instead of ~5s).

### GitHub Actions (CI)

```
✅ 26 tests pass (non-integration only for speed)
⏭️ 52 tests skipped (integration tests - work but skipped for fast CI)
❌ 0 tests fail
```

### Local Development (Full Suite)

```
✅ 78 tests pass (all tests including integration)
❌ 0 tests fail
⏭️ 0 tests skipped
```

### Detailed Test Breakdown

#### API Tests (`test_api.py`) - 26/26 ✅ PASSING

| Test                            | Status | What It Tests                     |
| ------------------------------- | ------ | --------------------------------- |
| `test_api_init`                 | ✅     | API object creation               |
| `test_get_info`                 | ✅     | GET /info endpoint                |
| `test_get_info_with_sections`   | ✅     | GET /info with query params       |
| `test_get_control`              | ✅     | GET /control endpoint             |
| `test_get_values`               | ✅     | GET /values endpoint              |
| `test_get_values_with_sections` | ✅     | GET /values with query params     |
| `test_set_current`              | ✅     | POST current setting              |
| `test_set_charge_pause`         | ✅     | POST pause/resume                 |
| `test_set_energy_limit`         | ✅     | POST energy limit                 |
| `test_set_phase_count`          | ✅     | POST phase count                  |
| `test_set_phase_count_invalid`  | ✅     | Error handling for invalid phases |
| `test_api_with_auth`            | ✅     | BasicAuth authentication          |
| `test_test_connection_success`  | ✅     | Connection test success           |
| `test_test_connection_failure`  | ✅     | Connection test failure           |
| `test_api_timeout`              | ✅     | Timeout handling                  |
| `test_api_client_error`         | ✅     | Client error handling             |
| `test_api_auth_error`           | ✅     | Authentication error handling     |
| `test_api_http_error_with_json` | ✅     | HTTP error with JSON response     |
| `test_api_http_error_no_json`   | ✅     | HTTP error without JSON response  |
| `test_api_retry_on_timeout`     | ✅     | Retry logic for timeouts          |
| `test_api_retry_on_http_error`  | ✅     | Retry logic for 5xx errors        |
| `test_api_retry_exhausted`      | ✅     | Retry exhaustion handling         |
| `test_api_retry_connection`     | ✅     | Retry logic for connection errors |
| `test_api_no_retry_auth`        | ✅     | No retry for auth errors          |
| `test_api_no_retry_client`      | ✅     | No retry for 4xx errors           |
| `test_api_retry_backoff`        | ✅     | Exponential backoff timing        |

#### Config Flow Tests (`test_config_flow.py`) - 21/21 ✅ PASSING

| Test                                    | CI   | What It Tests                  |
| --------------------------------------- | ---- | ------------------------------ |
| `test_form`                             | SKIP | User setup flow                |
| `test_form_without_credentials`         | SKIP | Setup without auth             |
| `test_form_cannot_connect`              | SKIP | Connection error handling      |
| `test_form_invalid_auth`                | PASS | Authentication error handling  |
| `test_form_unknown_exception`           | SKIP | Unknown exception handling     |
| `test_form_already_configured`          | SKIP | Duplicate detection            |
| `test_reauth_flow`                      | SKIP | Reauthentication flow          |
| `test_reauth_flow_cannot_connect`       | SKIP | Reauth connection errors       |
| `test_options_flow_success`             | SKIP | Options/reconfiguration        |
| `test_options_flow_cannot_connect`      | SKIP | Options flow connection errors |
| `test_options_flow_invalid_auth`        | SKIP | Options flow auth errors       |
| `test_zeroconf_discovery`               | SKIP | Zeroconf device discovery      |
| `test_zeroconf_discovery_without_creds` | SKIP | Zeroconf setup flow            |
| `test_zeroconf_already_configured`      | SKIP | Zeroconf duplicate detection   |
| `test_zeroconf_json_api_disabled`       | SKIP | Device without JSON API        |
| `test_zeroconf_no_serial_number`        | SKIP | Device missing serial          |
| `test_zeroconf_cannot_connect`          | SKIP | Zeroconf connection errors     |
| `test_zeroconf_fallback_to_model_type`  | SKIP | Fallback naming logic          |
| `test_reconfigure_flow`                 | SKIP | Reconfiguration flow           |
| `test_reconfigure_flow_cannot_connect`  | SKIP | Reconfigure connection errors  |
| `test_reconfigure_flow_invalid_auth`    | SKIP | Reconfigure auth errors        |

#### Config Flow Additional Tests (`test_config_flow_additional.py`) - 8/8 ✅ PASSING

Tests covering edge cases and error scenarios:

| Test                                        | CI   | What It Tests                            |
| ------------------------------------------- | ---- | ---------------------------------------- |
| `test_reauth_flow_invalid_auth`             | SKIP | Reauth with wrong credentials            |
| `test_reauth_flow_unknown_exception`        | SKIP | Reauth unexpected error handling         |
| `test_options_flow_unknown_exception`       | SKIP | Options flow unexpected error handling   |
| `test_options_flow_scan_interval_only`      | SKIP | Update only scan_interval                |
| `test_options_flow_with_empty_credentials`  | SKIP | Remove credentials (set to empty)        |
| `test_zeroconf_discovery_invalid_auth`      | SKIP | Zeroconf auth error during confirmation  |
| `test_zeroconf_discovery_unknown_exception` | SKIP | Zeroconf unexpected error handling       |
| `test_zeroconf_fallback_to_default_name`    | SKIP | Fallback to "NRGkick" when names missing |

#### Integration Tests (`test_init.py`) - 13/13 ✅ PASSING

| Test                                      | CI Status | What It Tests                       |
| ----------------------------------------- | --------- | ----------------------------------- |
| `test_setup_entry`                        | SKIP      | Entry setup                         |
| `test_setup_entry_failed_connection`      | PASS      | Setup with connection failure       |
| `test_unload_entry`                       | SKIP      | Entry unload                        |
| `test_reload_entry`                       | SKIP      | Entry reload                        |
| `test_coordinator_update_success`         | SKIP      | Coordinator updates                 |
| `test_coordinator_update_failed`          | PASS      | Coordinator update failure          |
| `test_coordinator_auth_failed`            | PASS      | Coordinator auth failure            |
| `test_coordinator_async_set_current`      | SKIP      | Coordinator set current method      |
| `test_coordinator_async_set_charge_pause` | SKIP      | Coordinator set charge pause method |
| `test_coordinator_async_set_energy_limit` | SKIP      | Coordinator set energy limit method |
| `test_coordinator_async_set_phase_count`  | SKIP      | Coordinator set phase count method  |
| `test_coordinator_blocked_by_solar`       | SKIP      | Command blocked by solar logic      |
| `test_coordinator_unexpected_value`       | SKIP      | Command verification failure        |

#### Naming Tests (`test_naming.py`) - 2/2 ✅ PASSING

| Test                        | CI Status | What It Tests                                |
| --------------------------- | --------- | -------------------------------------------- |
| `test_device_name_fallback` | SKIP      | Fallback to "NRGkick" when API name is empty |
| `test_device_name_custom`   | SKIP      | Custom device name usage                     |

#### Platform Tests (Various Files) - 8/8 ✅ PASSING

| Test                          | CI Status | What It Tests                   |
| ----------------------------- | --------- | ------------------------------- |
| `test_binary_sensors`         | SKIP      | Binary sensor state mapping     |
| `test_number_entities`        | SKIP      | Number entity values & limits   |
| `test_number_set_value_error` | SKIP      | Number error handling           |
| `test_sensor_entities`        | SKIP      | Sensor value paths & attributes |
| `test_switch_entities`        | SKIP      | Switch state & toggle commands  |
| `test_switch_error`           | SKIP      | Switch turn on error handling   |
| `test_switch_turn_off_error`  | SKIP      | Switch turn off error handling  |
| `test_diagnostics`            | SKIP      | Diagnostics data generation     |

---

## Running Tests

### Prerequisites

1. **Create and activate virtual environment**:

```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

2. **Install development dependencies**:

```bash
pip install -r requirements_dev.txt
```

### Using the Test Runner Script

The `run-tests.sh` script provides convenient access to different test configurations:

```bash
# Run CI-compatible tests (same as GitHub Actions)
./run-tests.sh ci

# Run all tests (requires HA environment)
./run-tests.sh all

# Run only integration tests
./run-tests.sh integration

# Run only API tests
./run-tests.sh api

# Generate HTML coverage report
./run-tests.sh coverage

# Show help
./run-tests.sh help
```

### Manual Test Execution

#### Run Only CI-Compatible Tests

```bash
pytest tests/ -v -m "not requires_integration"
```

#### Run All Tests

```bash
pytest tests/ -v
```

#### Run Only Integration Tests

```bash
pytest tests/ -v -m "requires_integration"
```

#### Run Specific Test File

```bash
pytest tests/test_api.py -v
pytest tests/test_config_flow.py -v
pytest tests/test_init.py -v
```

#### Run Specific Test

```bash
pytest tests/test_api.py::test_get_info -v
pytest tests/test_config_flow.py::test_form -v
```

#### Run with Coverage

```bash
# CI tests with coverage
pytest tests/ -v -m "not requires_integration" \
  --cov=custom_components.nrgkick \
  --cov-report=html \
  --cov-report=term

# All tests with coverage
pytest tests/ -v \
  --cov=custom_components.nrgkick \
  --cov-report=html \
  --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### Run with Coverage in Terminal

```bash
pytest tests/ -v -m "not requires_integration" \
  --cov=custom_components.nrgkick \
  --cov-report=term-missing
```

---

## Test Structure

### Directory Layout

```
tests/
├── __init__.py                       # Test package initialization
├── conftest.py                       # Shared pytest fixtures
├── pytest.ini                        # pytest configuration (in root)
├── test_api.py                       # API client tests (17 tests)
├── test_binary_sensor.py             # Binary sensor platform tests
├── test_config_flow.py               # Config flow tests (18 tests)
├── test_config_flow_additional.py    # Config flow edge cases (8 tests)
├── test_diagnostics.py               # Diagnostics tests
├── test_init.py                      # Integration setup tests (11 tests)
├── test_naming.py                    # Device naming & fallback tests (2 tests)
├── test_number.py                    # Number platform tests
├── test_sensor.py                    # Sensor platform tests
├── test_switch.py                    # Switch platform tests
└── README.md                         # This file
```

### Fixtures (`conftest.py`)

#### `mock_setup_entry`

Mocks the integration setup entry function.

#### `mock_nrgkick_api`

Provides a fully mocked NRGkickAPI instance with:

- Successful connection test
- Device info responses
- Control data responses
- Values data responses
- All control methods (set_current, set_charge_pause, etc.)

#### `mock_config_entry`

Provides a mock ConfigEntry with realistic test data:

- Host: 192.168.1.100
- Username/Password: test credentials
- Unique ID: TEST123456

#### Mock Data Fixtures

- `mock_info_data`: Complete device information
- `mock_control_data`: Control settings
- `mock_values_data`: Real-time telemetry

---

## Writing Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>_<scenario>`
- Use descriptive names that explain what is being tested

### Async Test Pattern

All tests use `async def` and work with Home Assistant's async architecture:

```python
async def test_example(hass: HomeAssistant, mock_api) -> None:
    """Test example with clear docstring."""
    # Arrange
    mock_api.method.return_value = {"data": "value"}

    # Act
    result = await function_under_test(hass)

    # Assert
    assert result == expected_value
    mock_api.method.assert_called_once()
```

### Mocking Pattern

Use `unittest.mock.patch` for external dependencies:

```python
with patch("module.ClassName", return_value=mock_object):
    result = await function_under_test()
```

### Error Testing Pattern

Test error conditions explicitly:

```python
mock_api.method.side_effect = Exception("Error message")

with pytest.raises(ExpectedException):
    await function_under_test()
```

### Adding New Tests

1. **Identify the component to test**
2. **Determine if it needs full HA integration**:
   - NO → Add to unit tests (no marker)
   - YES → Add `@pytest.mark.requires_integration` decorator
3. **Create test function in appropriate file**
4. **Use existing fixtures or create new ones**
5. **Follow naming convention**: `test_<feature>_<scenario>`
6. **Add docstring** explaining the test
7. **Run tests** to verify: `./run-tests.sh ci`
8. **Check coverage** impact: `./run-tests.sh coverage`

### Example: Adding a New Unit Test

```python
async def test_new_api_method(mock_session, mock_info_data) -> None:
    """Test new API method functionality."""
    # Arrange
    api = NRGkickAPI("192.168.1.100", mock_session)
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "result": "success"
    }

    # Act
    result = await api.new_method()

    # Assert
    assert result == {"result": "success"}
    mock_session.get.assert_called_once_with(
        "http://192.168.1.100/api/new_method",
        timeout=10
    )
```

### Example: Adding a New Integration Test

```python
@pytest.mark.requires_integration
async def test_new_config_option(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test new configuration option."""
    # This test will only run locally, not in CI
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # ... test implementation
```

---

## Troubleshooting

### "IntegrationNotFound: Integration 'nrgkick' not found"

**Cause**: This error should not occur with current setup using `pytest-homeassistant-custom-component`.

**Solution**: If you encounter this:

1. Ensure `pytest-homeassistant-custom-component` is installed:
   ```bash
   pip install -r requirements_dev.txt
   ```
2. Verify `conftest.py` includes:
   ```python
   pytest_plugins = "pytest_homeassistant_custom_component"
   ```
3. Try running all tests: `./run-tests.sh`

### "Unknown marker: requires_integration"

**Cause**: `pytest.ini` missing marker definition.

**Solution**: Ensure `pytest.ini` contains:

```ini
markers =
    requires_integration: Tests that require Home Assistant integration loader (may fail in CI)
```

### "No tests collected"

**Cause**: All tests may be excluded by filters.

**Solution**: Try:

- Remove marker filters: `pytest tests/`
- Check test file is in `tests/` directory
- Verify test functions start with `test_`

### Import Errors

**Cause**: Virtual environment not activated or dependencies not installed.

**Solution**:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_dev.txt
```

### Async Warnings

**Cause**: `pytest-asyncio` configuration issues.

**Solution**: Ensure `pytest.ini` has:

```ini
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

### Fixture Not Found

**Cause**: `conftest.py` missing or incorrectly structured.

**Solution**: Verify `conftest.py` exists in `tests/` directory with all fixtures defined.

### Tests Running Slowly

**Cause**: May be running integration tests that attempt HA setup.

**Solution**: Run only unit tests: `pytest tests/ -m "not requires_integration"`

---

## CI/CD Integration

### GitHub Actions

Tests run automatically via `.github/workflows/test.yml` on:

- Every push to main branch
- Every pull request
- Tag creation

**CI Configuration**:

```yaml
- name: Run tests with pytest
  run: |
    pytest tests/ -v -m "not requires_integration" \
      --cov=custom_components.nrgkick \
      --cov-report=xml \
      --cov-report=term
```

This ensures:

- ✅ Only unit tests run in CI
- ✅ No false failures from integration tests
- ✅ Fast test execution
- ✅ Reliable results

### Coverage Reporting

Coverage reports are uploaded to Codecov for tracking:

- Line coverage metrics
- Branch coverage
- Historical trends

### Test Matrix

Tests run on:

- Python 3.13 (current production version)

This ensures compatibility with the latest Home Assistant versions that require Python 3.13+.

---

## Code Coverage Goals

| Component      | Target | Current | Status |
| -------------- | ------ | ------- | ------ |
| Overall        | 95%+   | 96%     | ✅ Met |
| API Client     | 93%+   | 93%     | ✅ Met |
| Config Flow    | 90%+   | 98%     | ✅ Met |
| Coordinator    | 95%+   | 96%     | ✅ Met |
| Sensors        | 95%+   | 100%    | ✅ Met |
| Binary Sensors | 95%+   | 100%    | ✅ Met |
| Switch         | 95%+   | 97%     | ✅ Met |
| Number         | 95%+   | 98%     | ✅ Met |
| Diagnostics    | 95%+   | 100%    | ✅ Met |
| Constants      | 95%+   | 100%    | ✅ Met |

**Notes:**

- **Overall**: Exceeds Silver Tier requirement (>95%) with 96% coverage
- **Platforms**: All entity platforms have 97%+ coverage including error paths
- **Diagnostics**: Full coverage for diagnostics data generation
- **Constants**: Full coverage for all constant definitions

---

## Best Practices

### For Contributors

1. **Run All Tests Locally**: Verify everything works before committing

   ```bash
   ./run-tests.sh
   ```

2. **Pre-Push Check**: Ensure CI tests will pass

   ```bash
   ./run-tests.sh ci
   ```

3. **Coverage**: Maintain or improve coverage with new tests

   ```bash
   ./run-tests.sh coverage
   ```

4. **New Tests**: Add `@pytest.mark.requires_integration` marker if test needs full HA environment
   - But remember: these tests work everywhere thanks to pytest-homeassistant-custom-component!

### For Maintainers

1. **CI Strategy**: Currently skips integration tests for speed (2s vs 3s)
   - Can run all tests in CI if needed (just remove the marker filter)
2. **Monitor Both**: Check CI results and local test runs
3. **Document Changes**: Update this README when adding new test categories
4. **Review Coverage**: Ensure new features include adequate tests

---

## Resources

### Documentation

- [pytest documentation](https://docs.pytest.org/)
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Home Assistant Testing Guide](https://developers.home-assistant.io/docs/development_testing)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)

### Related Files

- `.github/workflows/test.yml` - CI configuration
- `pytest.ini` - pytest configuration
- `requirements_dev.txt` - Development dependencies
- `CONTRIBUTING.md` - Contribution guidelines

---

## Future Improvements

Potential enhancements to the testing strategy:

1. **Run All Tests in CI**: Remove marker filter for complete CI coverage
2. **Parallel Testing**: Use pytest-xdist for faster execution
3. **E2E Tests**: Add optional end-to-end tests with real device (manual/optional)
4. **Performance Tests**: Add benchmarks for API response handling
5. **Mutation Testing**: Use mutmut to verify test quality

---

**Last Updated**: November 26, 2025
**Test Suite Version**: 3.4.0
**Python Version**: 3.13
**Maintainer**: @andijakl
**Status**: All 78 Tests Passing (96% Coverage)
