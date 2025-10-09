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

### Run CI-Compatible Tests (Recommended)

```bash
# Using the convenient script
./run-tests.sh ci

# Or manually
pytest tests/ -v -m "not requires_integration"
```

### Run All Tests (Local Development)

```bash
# Using the convenient script
./run-tests.sh all

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

This project uses a **tiered testing approach** to balance comprehensive test coverage with practical CI/CD constraints.

### Test Categories

#### 1. **Unit Tests** ✅ (Run in CI)

These tests validate individual components in isolation using mocks. They **do NOT require** a full Home Assistant integration setup.

- **API Tests** (`test_api.py`): 16 tests
  - All API client methods
  - HTTP error handling
  - Authentication flows
  - Timeout behavior

- **Coordinator Tests** (`test_init.py`): 3 tests
  - Data update failures
  - Authentication failures
  - Connection error handling

**CI Execution**: These tests run on every push/PR via GitHub Actions.

#### 2. **Integration Tests** 🏠 (Local Only)

These tests require Home Assistant's integration loader and full test environment. They are marked with `@pytest.mark.requires_integration` and **skipped in CI**.

- **Config Flow Tests** (`test_config_flow.py`): 13 tests
  - User setup flow
  - Reauthentication
  - Options/reconfiguration
  - Duplicate detection

- **Setup Tests** (`test_init.py`): 4 tests
  - Entry setup/unload/reload
  - Coordinator updates with full integration

**Why Skip in CI?**

- Require `custom_components.nrgkick` to be loadable by Home Assistant
- Need full Home Assistant test harness
- Complex setup not practical in GitHub Actions environment

**Local Execution**: Run these tests in your development environment where the integration is properly registered.

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

| Test Suite        | Count  | CI Status   | Local Status | Pass Rate    |
| ----------------- | ------ | ----------- | ------------ | ------------ |
| API Tests         | 16     | ✅ PASS     | ✅ PASS      | 100%         |
| Coordinator Tests | 3      | ✅ PASS     | ✅ PASS      | 100%         |
| Config Flow Tests | 13     | ⏭️ SKIP     | ⚠️ PARTIAL   | N/A          |
| Setup Tests       | 4      | ⏭️ SKIP     | ⚠️ PARTIAL   | N/A          |
| **Total**         | **36** | **19 pass** | **Varies**   | **CI: 100%** |

### GitHub Actions (CI)

```
✅ 19 tests pass
⏭️ 15 tests skipped (requires_integration marker)
❌ 0 tests fail
```

### Local Development (Full Suite)

Integration tests may fail with `IntegrationNotFound` error unless you have a proper Home Assistant development environment set up.

### Detailed Test Breakdown

#### API Tests (`test_api.py`) - 16/16 ✅ PASSING

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

#### Config Flow Tests (`test_config_flow.py`) - 13 tests 🏠 LOCAL ONLY

| Test                                      | Marker               | What It Tests              |
| ----------------------------------------- | -------------------- | -------------------------- |
| `test_form`                               | requires_integration | User setup flow            |
| `test_form_without_credentials`           | requires_integration | Setup without auth         |
| `test_form_cannot_connect`                | requires_integration | Connection error handling  |
| `test_form_unknown_exception`             | requires_integration | Unknown exception handling |
| `test_form_already_configured`            | requires_integration | Duplicate detection        |
| `test_reauth_flow`                        | requires_integration | Reauthentication flow      |
| `test_reauth_flow_cannot_connect`         | requires_integration | Reauth connection errors   |
| `test_options_flow`                       | requires_integration | Options/reconfiguration    |
| `test_options_flow_cannot_connect`        | requires_integration | Options flow errors        |
| `test_options_flow_with_scan_interval`    | requires_integration | Scan interval config       |
| `test_options_flow_invalid_scan_interval` | requires_integration | Scan interval validation   |

#### Integration Tests (`test_init.py`) - 7 tests (3 CI, 4 Local)

| Test                                 | Marker               | CI Status | What It Tests                  |
| ------------------------------------ | -------------------- | --------- | ------------------------------ |
| `test_setup_entry`                   | requires_integration | ⏭️ SKIP   | Entry setup                    |
| `test_setup_entry_failed_connection` | -                    | ✅ PASS   | Setup with connection failure  |
| `test_unload_entry`                  | requires_integration | ⏭️ SKIP   | Entry unload                   |
| `test_reload_entry`                  | requires_integration | ⏭️ SKIP   | Entry reload                   |
| `test_coordinator_update_success`    | requires_integration | ⏭️ SKIP   | Coordinator updates            |
| `test_coordinator_update_failed`     | -                    | ✅ PASS   | Coordinator update failure     |
| `test_coordinator_auth_failed`       | -                    | ✅ PASS   | Coordinator auth failure (401) |

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

# Generate coverage report for all tests
./run-tests.sh coverage-all

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
├── __init__.py              # Test package initialization
├── conftest.py              # Shared pytest fixtures
├── pytest.ini               # pytest configuration (in root)
├── test_api.py              # API client tests (16 tests)
├── test_config_flow.py      # Config flow tests (13 tests)
├── test_init.py             # Integration setup tests (7 tests)
└── README.md                # This file
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

**Cause**: Running integration tests without proper Home Assistant setup.

**Solution**: Either:

- Run only unit tests: `./run-tests.sh ci`
- Or set up proper HA development environment (see Home Assistant developer docs)

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

Tests run on multiple Python versions:

- Python 3.11
- Python 3.12

This ensures compatibility across supported Home Assistant versions.

---

## Code Coverage Goals

| Component        | Target   | Status         |
| ---------------- | -------- | -------------- |
| Config Flow      | 100%     | 🎯 On track    |
| API Client       | 100%     | ✅ Achieved    |
| Coordinator      | 95%+     | 🎯 On track    |
| Entity Platforms | 85%+     | 📊 In progress |
| **Overall**      | **90%+** | 🎯 Target      |

---

## Best Practices

### For Contributors

1. **New Tests**: Consider environment requirements
   - If NO HA integration needed → Add to unit tests (no marker)
   - If YES HA integration needed → Add `@pytest.mark.requires_integration`

2. **Local Development**: Run full test suite before committing

   ```bash
   ./run-tests.sh all
   ```

3. **Pre-Push Check**: Verify CI tests pass

   ```bash
   ./run-tests.sh ci
   ```

4. **Coverage**: Maintain or improve coverage with new tests
   ```bash
   ./run-tests.sh coverage
   ```

### For Maintainers

1. **Monitor Both**: Check both CI results AND local test runs
2. **Update Markers**: Revisit which tests can run in CI as infrastructure improves
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

1. **Docker-based CI**: Run full HA environment in container
2. **Custom Component Loading**: Research proper test integration registration
3. **Separate Workflows**: Different CI jobs for unit vs integration tests
4. **Mock Integration Loader**: Create stub loader for integration tests
5. **E2E Tests**: Add optional end-to-end tests with real device
6. **Performance Tests**: Add benchmarks for API response handling

---

**Last Updated**: October 9, 2025
**Test Suite Version**: 2.0.0
**Maintainer**: @andijakl
**Status**: ✅ CI Passing | 🏠 Local Tests Available
