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

### Run All Tests

```bash
# Using the convenient script
./run-tests.sh

# Or manually
pytest tests/ -v
```

### Generate Coverage Report

```bash
./run-tests.sh coverage
```

---

## Testing Strategy

### Overview

This project uses **pytest-homeassistant-custom-component** which provides a full Home Assistant test environment. All tests, including integration tests marked with `@pytest.mark.requires_integration`, run successfully in both CI and local environments.

### Architecture

The integration uses a **two-layer architecture**:

1. **nrgkick-api** - Standalone PyPI library for device communication
   - Has its own test suite in a separate repository
   - Tests HTTP communication, retries, authentication
   - See: https://github.com/andijakl/nrgkick-api

2. **Home Assistant Integration** - This repository
   - Tests the HA wrapper, config flows, coordinator, entities
   - Uses mocked library responses (doesn't test actual HTTP calls)

### Test Categories

#### 1. **Unit Tests** ✅ (Run everywhere)

These tests validate individual components in isolation using mocks:

- **API Wrapper Tests** (`test_api.py`): 19 tests
  - Wrapper initialization and delegation to library
  - Exception translation (library → Home Assistant)
  - All wrapper methods pass-through correctly

**Execution**: Run everywhere (CI and local).

#### 2. **Integration Tests** ✅ (Run everywhere)

These tests use Home Assistant's integration loader and test environment, powered by `pytest-homeassistant-custom-component`:

- **Config Flow Tests** (`test_config_flow.py`): 19 tests
  - User setup flow
  - Reauthentication and reconfiguration
  - Zeroconf discovery
  - Error handling

- **Coordinator Tests** (`test_init.py`): 13 tests
  - Entry setup/unload/reload
  - Coordinator updates
  - Error recovery

**Execution**: These run successfully in both CI (GitHub Actions) and local environments thanks to the pytest-homeassistant-custom-component package.

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

| Test Suite             | Count  | Status  | Pass Rate |
| ---------------------- | ------ | ------- | --------- |
| API Wrapper Tests      | 19     | ✅ PASS | 100%      |
| Config Flow Tests      | 19     | ✅ PASS | 100%      |
| Config Flow Additional | 5      | ✅ PASS | 100%      |
| Coordinator Tests      | 13     | ✅ PASS | 100%      |
| Naming Tests           | 2      | ✅ PASS | 100%      |
| Platform Tests         | 8      | ✅ PASS | 100%      |
| **Total**              | **66** | ✅ PASS | **100%**  |

**Note**: All 66 tests run in both CI and local environments. The `nrgkick-api` library has its own separate test suite.

### Expected Results (CI & Local)

```
✅ 66 tests pass
❌ 0 tests fail
⏭️ 0 tests skipped
```

### Detailed Test Breakdown

#### API Wrapper Tests (`test_api.py`) - 19/19 ✅ PASSING

These tests verify the Home Assistant wrapper around the `nrgkick-api` library:

| Test                                     | Status | What It Tests                           |
| ---------------------------------------- | ------ | --------------------------------------- |
| `test_api_init`                          | ✅     | Wrapper initialization                  |
| `test_wrapper_converts_auth_error`       | ✅     | Library auth error → HA exception       |
| `test_wrapper_converts_connection_error` | ✅     | Library connection error → HA exception |
| `test_get_info_passes_through`           | ✅     | get_info delegates to library           |
| `test_get_info_with_sections`            | ✅     | get_info with sections parameter        |
| `test_get_control`                       | ✅     | get_control delegates to library        |
| `test_get_values`                        | ✅     | get_values delegates to library         |
| `test_set_current`                       | ✅     | set_current delegates to library        |
| `test_set_charge_pause`                  | ✅     | set_charge_pause delegates to library   |
| `test_set_energy_limit`                  | ✅     | set_energy_limit delegates to library   |
| `test_set_phase_count`                   | ✅     | set_phase_count delegates to library    |
| `test_set_phase_count_invalid`           | ✅     | Invalid phase count error handling      |
| `test_api_with_auth`                     | ✅     | Wrapper passes auth to library          |
| `test_test_connection_success`           | ✅     | test_connection success path            |
| `test_test_connection_failure`           | ✅     | test_connection failure path            |
| `test_api_timeout`                       | ✅     | Timeout converted to HA exception       |
| `test_api_auth_error`                    | ✅     | Auth error converted to HA exception    |
| `test_exception_inheritance`             | ✅     | Exception class hierarchy correct       |
| `test_exception_translation_keys`        | ✅     | Exceptions have translation keys        |

**Note**: HTTP-level tests (retries, backoff, actual requests) are covered by the `nrgkick-api` library's test suite.

#### Config Flow Tests (`test_config_flow.py`) - 19/19 ✅ PASSING

| Test                                    | What It Tests                 |
| --------------------------------------- | ----------------------------- |
| `test_form`                             | User setup flow               |
| `test_form_without_credentials`         | Setup without auth            |
| `test_form_cannot_connect`              | Connection error handling     |
| `test_form_invalid_auth`                | Authentication error handling |
| `test_form_unknown_exception`           | Unknown exception handling    |
| `test_form_already_configured`          | Duplicate detection           |
| `test_reauth_flow`                      | Reauthentication flow         |
| `test_reauth_flow_cannot_connect`       | Reauth connection errors      |
| `test_options_flow_success`             | Options flow success          |
| `test_reconfigure_flow`                 | Reconfiguration flow          |
| `test_reconfigure_flow_cannot_connect`  | Reconfigure connection errors |
| `test_reconfigure_flow_invalid_auth`    | Reconfigure auth errors       |
| `test_zeroconf_discovery`               | Zeroconf device discovery     |
| `test_zeroconf_discovery_without_creds` | Zeroconf setup flow           |
| `test_zeroconf_already_configured`      | Zeroconf duplicate detection  |
| `test_zeroconf_json_api_disabled`       | Device without JSON API       |
| `test_zeroconf_no_serial_number`        | Device missing serial         |
| `test_zeroconf_cannot_connect`          | Zeroconf connection errors    |
| `test_zeroconf_fallback_to_model_type`  | Fallback naming logic         |

#### Config Flow Additional Tests (`test_config_flow_additional.py`) - 5/5 ✅ PASSING

Tests covering edge cases and error scenarios:

| Test                                        | What It Tests                            |
| ------------------------------------------- | ---------------------------------------- |
| `test_reauth_flow_invalid_auth`             | Reauth with wrong credentials            |
| `test_reauth_flow_unknown_exception`        | Reauth unexpected error handling         |
| `test_zeroconf_discovery_invalid_auth`      | Zeroconf auth error during confirmation  |
| `test_zeroconf_discovery_unknown_exception` | Zeroconf unexpected error handling       |
| `test_zeroconf_fallback_to_default_name`    | Fallback to "NRGkick" when names missing |

#### Coordinator Tests (`test_init.py`) - 13/13 ✅ PASSING

| Test                                        | What It Tests                       |
| ------------------------------------------- | ----------------------------------- |
| `test_setup_entry`                          | Entry setup                         |
| `test_setup_entry_failed_connection`        | Setup with connection failure       |
| `test_unload_entry`                         | Entry unload                        |
| `test_reload_entry`                         | Entry reload                        |
| `test_coordinator_update_success`           | Coordinator updates                 |
| `test_coordinator_update_failed`            | Coordinator update failure          |
| `test_coordinator_auth_failed`              | Coordinator auth failure            |
| `test_coordinator_async_set_current`        | Coordinator set current method      |
| `test_coordinator_async_set_charge_pause`   | Coordinator set charge pause method |
| `test_coordinator_async_set_energy_limit`   | Coordinator set energy limit method |
| `test_coordinator_async_set_phase_count`    | Coordinator set phase count method  |
| `test_coordinator_command_blocked_by_solar` | Command blocked by solar logic      |
| `test_coordinator_command_unexpected_value` | Command verification failure        |

#### Naming Tests (`test_naming.py`) - 2/2 ✅ PASSING

| Test                        | What It Tests                                |
| --------------------------- | -------------------------------------------- |
| `test_device_name_fallback` | Fallback to "NRGkick" when API name is empty |
| `test_device_name_custom`   | Custom device name usage                     |

#### Platform Tests (Various Files) - 8/8 ✅ PASSING

| Test                          | What It Tests                   |
| ----------------------------- | ------------------------------- |
| `test_binary_sensors`         | Binary sensor state mapping     |
| `test_number_entities`        | Number entity values & limits   |
| `test_number_set_value_error` | Number error handling           |
| `test_sensor_entities`        | Sensor value paths & attributes |
| `test_switch_entities`        | Switch state & toggle commands  |
| `test_switch_error`           | Switch turn on error handling   |
| `test_switch_turn_off_error`  | Switch turn off error handling  |
| `test_diagnostics`            | Diagnostics data generation     |

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
# Run all tests
./run-tests.sh

# Run only API tests
./run-tests.sh api

# Generate HTML coverage report
./run-tests.sh coverage

# Show help
./run-tests.sh help
```

### Manual Test Execution

#### Run All Tests

```bash
pytest tests/ -v
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
pytest tests/ -v \
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
├── test_api.py                       # API wrapper tests (19 tests)
├── test_binary_sensor.py             # Binary sensor platform tests
├── test_config_flow.py               # Config flow tests (19 tests)
├── test_config_flow_additional.py    # Config flow edge cases (5 tests)
├── test_diagnostics.py               # Diagnostics tests
├── test_init.py                      # Integration setup tests (13 tests)
├── test_naming.py                    # Device naming & fallback tests (2 tests)
├── test_number.py                    # Number platform tests
├── test_sensor.py                    # Sensor platform tests
├── test_switch.py                    # Switch platform tests
└── README.md                         # This file
```

**Note**: The `nrgkick-api` library has its own test suite at https://github.com/andijakl/nrgkick-api

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
    pytest tests/ -v \
      --cov=custom_components.nrgkick \
      --cov-report=xml \
      --cov-report=term
```

This ensures:

- ✅ All 66 tests run in CI
- ✅ Full test coverage
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

- **Overall**: Achieves 96% coverage (exceeds 95% goal)
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

2. **Coverage**: Maintain or improve coverage with new tests

   ```bash
   ./run-tests.sh coverage
   ```

3. **New Tests**: Add `@pytest.mark.requires_integration` marker if test needs full HA environment
   - All tests run everywhere thanks to pytest-homeassistant-custom-component

### For Maintainers

1. **All Tests in CI**: All 66 tests run in GitHub Actions
2. **Document Changes**: Update this README when adding new test categories
3. **Review Coverage**: Ensure new features include adequate tests

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

1. **Parallel Testing**: Use pytest-xdist for faster execution
2. **E2E Tests**: Add optional end-to-end tests with real device (manual/optional)
3. **Performance Tests**: Add benchmarks for API response handling
4. **Mutation Testing**: Use mutmut to verify test quality

---

**Test Suite Version**: 4.0.0
**Python Version**: 3.13+
**Maintainer**: @andijakl
**Status**: All 66 Tests Passing (see `nrgkick-api` library for additional API-level tests)
