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

Install development dependencies:

```bash
pip install -r requirements_dev.txt
```

### Run All Tests

```bash
pytest tests/
```

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

The test suite covers:

### Config Flow Tests (`test_config_flow.py`)
- ✅ User setup flow
- ✅ Setup without credentials
- ✅ Connection errors
- ✅ Unknown exceptions
- ✅ Already configured detection
- ✅ Reauthentication flow
- ✅ Reauth connection errors
- ✅ Options flow
- ✅ Options flow errors

### Integration Tests (`test_init.py`)
- ✅ Setup entry
- ✅ Setup with connection failure
- ✅ Unload entry
- ✅ Reload entry
- ✅ Coordinator successful update
- ✅ Coordinator update failure
- ✅ Coordinator authentication failure (401)

### API Tests (`test_api.py`)
- ✅ API initialization
- ✅ Get device info
- ✅ Get info with sections
- ✅ Get control data
- ✅ Get values
- ✅ Get values with sections
- ✅ Set charging current
- ✅ Set charge pause/resume
- ✅ Set energy limit
- ✅ Set phase count
- ✅ Invalid phase count handling
- ✅ Authentication with BasicAuth
- ✅ Test connection success
- ✅ Test connection failure
- ✅ Timeout handling
- ✅ Client error handling

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

### Import Errors

If you see import errors, ensure Home Assistant is installed:

```bash
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
