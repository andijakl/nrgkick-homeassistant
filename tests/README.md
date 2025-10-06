# NRGkick Integration Tests

This directory contains the test suite for the NRGkick Home Assistant integration.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared pytest fixtures
├── test_config_flow.py      # Config flow tests
├── test_init.py             # Integration setup tests
└── test_api.py              # API client tests
```

## Running Tests

### Prerequisites

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate
```

2. Install development dependencies:

```bash
python -m pip install -r requirements_dev.txt
```

### Run All Tests

```bash
pytest tests/
```

**Expected Result**: 19 passing, 13 failing due to integration registration issues (see Common Issues section below).

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_config_flow.py -v
```

### Run Specific Test

```bash
pytest tests/test_config_flow.py::test_form -v
```

### Run with Coverage

```bash
pytest tests/ --cov=custom_components.nrgkick --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Run with Coverage Report in Terminal

```bash
pytest tests/ --cov=custom_components.nrgkick --cov-report=term-missing
```

## Test Coverage

**Current Status**: Significant progress has been made! **19 out of 32 tests are now passing** (59% pass rate).

### Test Results Summary

✅ **All API tests passing** (16/16) - 100%
✅ **Some integration tests passing** (3/7) - 43%
❌ **Config flow tests failing** (0/9) - 0% (due to integration registration issue)

The config flow and some integration tests fail because Home Assistant's test environment cannot find the custom integration. This requires additional test infrastructure setup to properly register custom components in the test environment.

### Do Tests Connect to Real Devices?

**No**, the tests do NOT connect to real NRGkick devices. They use:
- **Mock objects**: Python `unittest.mock` to simulate API responses
- **Fixtures**: Predefined test data that mimics real device responses
- **No network calls**: All HTTP requests are intercepted and mocked

This means:
- ✅ Tests run without a physical NRGkick device
- ✅ Tests are fast and repeatable
- ✅ No risk of changing device settings during testing
- ✅ Can test error scenarios safely

The test suite covers:

### Config Flow Tests (`test_config_flow.py`)
- ❌ User setup flow - **FAILING** (integration not found)
- ❌ Setup without credentials - **FAILING** (integration not found)
- ❌ Connection errors - **FAILING** (integration not found)
- ❌ Unknown exceptions - **FAILING** (integration not found)
- ❌ Already configured detection - **FAILING** (integration not found)
- ❌ Reauthentication flow - **FAILING** (integration not found)
- ❌ Reauth connection errors - **FAILING** (integration not found)
- ❌ Options flow - **FAILING** (integration not found)
- ❌ Options flow errors - **FAILING** (integration not found)

### Integration Tests (`test_init.py`)
- ❌ Setup entry - **FAILING** (integration not found)
- ✅ Setup with connection failure - **PASSING**
- ❌ Unload entry - **FAILING** (integration not found)
- ❌ Reload entry - **FAILING** (integration not found)
- ❌ Coordinator successful update - **FAILING** (integration not found)
- ✅ Coordinator update failure - **PASSING**
- ✅ Coordinator authentication failure (401) - **PASSING**

### API Tests (`test_api.py`)
- ✅ API initialization - **PASSING**
- ✅ Get device info - **PASSING**
- ✅ Get info with sections - **PASSING**
- ✅ Get control data - **PASSING**
- ✅ Get values - **PASSING**
- ✅ Get values with sections - **PASSING**
- ✅ Set charging current - **PASSING**
- ✅ Set charge pause/resume - **PASSING**
- ✅ Set energy limit - **PASSING**
- ✅ Set phase count - **PASSING**
- ✅ Invalid phase count handling - **PASSING**
- ✅ Authentication with BasicAuth - **PASSING**
- ✅ Test connection success - **PASSING**
- ✅ Test connection failure - **PASSING**
- ✅ Timeout handling - **PASSING**
- ✅ Client error handling - **PASSING**

## Fixtures

### `mock_setup_entry`
Mocks the integration setup entry function.

### `mock_nrgkick_api`
Provides a fully mocked NRGkickAPI instance with:
- Successful connection test
- Device info responses
- Control data responses
- Values data responses
- All control methods (set_current, set_charge_pause, etc.)

### `mock_config_entry`
Provides a mock ConfigEntry for testing.

### `mock_info_data`, `mock_control_data`, `mock_values_data`
Provide realistic mock data for API responses.

## Writing New Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>_<scenario>`

### Example Test

```python
async def test_new_feature(hass: HomeAssistant, mock_nrgkick_api) -> None:
    """Test new feature."""
    # Arrange
    mock_nrgkick_api.some_method.return_value = {"data": "value"}
    
    # Act
    result = await some_function(hass)
    
    # Assert
    assert result == expected_value
    mock_nrgkick_api.some_method.assert_called_once()
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Pushes to main branch
- Tag creation

See `.github/workflows/test.yml` for CI configuration.

## Debugging Tests

### Run with Debug Output

```bash
pytest tests/ -v -s
```

### Run with PDB on Failure

```bash
pytest tests/ --pdb
```

### Run Only Failed Tests

```bash
pytest tests/ --lf
```

## Code Coverage Goals

- **Minimum**: 80% coverage
- **Target**: 90%+ coverage
- **Focus Areas**:
  - Config flow: 100%
  - API client: 100%
  - Coordinator: 95%+
  - Entity platforms: 85%+

## Common Issues

### Tests Failing with "Integration not found"

This error occurs when Home Assistant can't find the custom integration. The tests need additional setup to work properly with Home Assistant's test environment. This is a known issue that needs to be resolved by updating the test infrastructure to properly register the integration.

**Workaround**: Tests may need to be run through Home Assistant's development environment or with additional pytest plugins configured.

### ConfigEntry Missing Arguments

If you see errors about `discovery_keys` and `options` being required, this is due to Home Assistant API changes. The `conftest.py` fixture has been updated to include these parameters.

### Async Session Mocking Issues

Some API tests may fail with coroutine-related errors. This indicates that the mocking setup for `aiohttp.ClientSession` needs improvement. The mock needs to properly implement async context managers.

### Import Errors

If you see import errors, ensure you're in an activated virtual environment and Home Assistant is installed:

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Then install dependencies
pip install homeassistant>=2023.1.0
```

### Async Warnings

Ensure `pytest-asyncio` is installed and `asyncio_mode = auto` is in `pytest.ini`.

### Fixture Not Found

Check that `conftest.py` is in the tests directory and properly structured.

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Home Assistant Testing](https://developers.home-assistant.io/docs/development_testing)
- [Home Assistant Test Fixtures](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
