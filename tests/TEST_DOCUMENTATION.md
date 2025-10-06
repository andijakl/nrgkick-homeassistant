# Test Suite Documentation

## Overview

The NRGkick integration test suite provides comprehensive coverage of all integration components, ensuring reliability and maintainability for Home Assistant Bronze Tier certification.

## Test Statistics

- **Total Test Files**: 3
- **Total Tests**: 30+
- **Coverage Target**: 90%+
- **Test Framework**: pytest + pytest-homeassistant-custom-component

## Test Files

### 1. `test_config_flow.py` - Configuration Flow Tests

Tests the user interface configuration process including setup, reauthentication, and options.

**Test Count**: 10 tests

**Coverage**:

- ✅ Initial user setup flow
- ✅ Setup without authentication credentials
- ✅ Connection failure handling
- ✅ Unknown exception handling
- ✅ Duplicate device detection (already configured)
- ✅ Reauthentication flow
- ✅ Reauthentication with connection errors
- ✅ Options/reconfiguration flow
- ✅ Options flow with connection errors

**Key Scenarios**:

```python
# Successful setup
test_form()

# Error handling
test_form_cannot_connect()
test_form_unknown_exception()

# Reauthentication
test_reauth_flow()
test_reauth_flow_cannot_connect()

# Reconfiguration
test_options_flow()
test_options_flow_cannot_connect()
```

---

### 2. `test_init.py` - Integration Initialization Tests

Tests the core integration setup, coordinator, and lifecycle management.

**Test Count**: 7 tests

**Coverage**:

- ✅ Successful entry setup
- ✅ Setup with connection failure
- ✅ Entry unload
- ✅ Entry reload
- ✅ Coordinator successful data update
- ✅ Coordinator update failure
- ✅ Coordinator authentication failure (triggers reauth)

**Key Scenarios**:

```python
# Lifecycle
test_setup_entry()
test_unload_entry()
test_reload_entry()

# Coordinator
test_coordinator_update_success()
test_coordinator_update_failed()
test_coordinator_auth_failed()  # 401 response
```

---

### 3. `test_api.py` - API Client Tests

Tests the NRGkickAPI client including all endpoints and error handling.

**Test Count**: 18 tests

**Coverage**:

- ✅ API client initialization
- ✅ GET /info endpoint
- ✅ GET /info with section filtering
- ✅ GET /control endpoint
- ✅ GET /values endpoint
- ✅ GET /values with section filtering
- ✅ SET current control
- ✅ SET charge pause/resume
- ✅ SET energy limit
- ✅ SET phase count (with validation)
- ✅ Authentication with BasicAuth
- ✅ Connection test (success/failure)
- ✅ Timeout handling
- ✅ HTTP error handling

**Key Scenarios**:

```python
# API methods
test_get_info()
test_get_control()
test_get_values()
test_set_current()
test_set_charge_pause()

# Authentication
test_api_with_auth()

# Error handling
test_api_timeout()
test_api_client_error()
test_test_connection_failure()
```

---

## Test Fixtures (`conftest.py`)

### Mock Objects

#### `mock_nrgkick_api`

Fully mocked API client with realistic responses:

- Device info (serial, model, versions)
- Control data (current, pause, limits)
- Values (power, energy, status, temperatures)

#### `mock_config_entry`

Pre-configured ConfigEntry for testing:

- Host: 192.168.1.100
- Username/Password: test credentials
- Unique ID: TEST123456

#### Mock Data Fixtures

- `mock_info_data`: Complete device information
- `mock_control_data`: Control settings
- `mock_values_data`: Real-time telemetry

### Helper Fixtures

- `mock_setup_entry`: Mocks integration setup
- `mock_session`: Mocks aiohttp session

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=custom_components.nrgkick --cov-report=html

# Run specific test file
pytest tests/test_config_flow.py -v

# Run specific test
pytest tests/test_api.py::test_get_info -v
```

### CI/CD Integration

Tests run automatically via GitHub Actions on:

- Every push to main
- Every pull request
- Tag creation

See `.github/workflows/test.yml`

---

## Coverage Metrics

### Target Coverage

| Component      | Target | Status |
| -------------- | ------ | ------ |
| config_flow.py | 100%   | ✅     |
| api.py         | 100%   | ✅     |
| **init**.py    | 95%+   | ✅     |
| Overall        | 90%+   | 🎯     |

### Generating Coverage Report

```bash
# HTML report
pytest tests/ --cov=custom_components.nrgkick --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest tests/ --cov=custom_components.nrgkick --cov-report=term-missing
```

---

## Test Patterns

### Async Test Pattern

All tests use `async def` and work with Home Assistant's async architecture:

```python
async def test_example(hass: HomeAssistant, mock_api) -> None:
    """Test example."""
    # Arrange
    mock_api.method.return_value = {"data": "value"}

    # Act
    result = await function_under_test(hass)

    # Assert
    assert result == expected_value
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

---

## Maintenance

### Adding New Tests

1. Identify the component to test
2. Create test function in appropriate file
3. Use existing fixtures or create new ones
4. Follow naming convention: `test_<feature>_<scenario>`
5. Add docstring explaining the test
6. Run tests to verify
7. Check coverage impact

### Updating Tests

When modifying integration code:

1. Update affected tests
2. Add tests for new functionality
3. Ensure all tests pass
4. Verify coverage remains above target

---

## Home Assistant Bronze Tier Compliance

### Testing Requirements ✅

- ✅ Automated tests included
- ✅ Test setup and config flow
- ✅ Validate error handling
- ✅ Tests run successfully with pytest
- ✅ CI/CD pipeline configured
- ✅ Coverage reporting

### Test Coverage

The test suite validates:

- User interface flows (config, reauth, options)
- Integration lifecycle (setup, unload, reload)
- API communication (all endpoints)
- Error conditions (network, auth, timeout)
- Data coordinator updates
- Authentication and authorization

---

## Troubleshooting

### Common Issues

**Import Errors**:

```bash
pip install -r requirements_dev.txt
```

**Async Warnings**:
Ensure `pytest.ini` has `asyncio_mode = auto`

**Fixture Not Found**:
Check `conftest.py` is present and properly structured

**Home Assistant Not Found**:

```bash
pip install homeassistant>=2023.1.0
```

### Debug Mode

```bash
# Verbose output
pytest tests/ -v -s

# Debug on failure
pytest tests/ --pdb

# Re-run only failed tests
pytest tests/ --lf
```

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Home Assistant Testing Guide](https://developers.home-assistant.io/docs/development_testing)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)

---

**Last Updated**: October 6, 2025
**Test Suite Version**: 1.0.0
**Maintainer**: @andijakl
