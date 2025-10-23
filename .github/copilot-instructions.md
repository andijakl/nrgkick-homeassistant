# NRGkick Home Assistant Integration

## Project Overview

This repository contains a **Home Assistant custom integration** for the NRGkick Gen2 EV charging controller. It provides local control and monitoring through the device's REST JSON API, following Home Assistant 2025.10+ best practices.

**Key Facts:**

- **Product**: NRGkick Gen2 EV charging controller integration
- **Platform**: Home Assistant custom component
- **API**: Local REST JSON API (no cloud dependency)
- **Architecture**: DataUpdateCoordinator-based polling integration
- **Entities**: 80+ sensors, 3 binary sensors, 1 switch, 3 numbers
- **Discovery**: Automatic mDNS/Zeroconf detection
- **Python**: 3.13+ (for development/testing), 3.11+ (for runtime)

## Repository Structure

```
nrgkick-homeassistant/
├── custom_components/nrgkick/    # Integration code
│   ├── __init__.py               # Entry point, coordinator setup
│   ├── api.py                    # REST API client with custom exceptions
│   ├── binary_sensor.py          # Binary sensor platform (3 entities)
│   ├── config_flow.py            # UI configuration and discovery
│   ├── const.py                  # Constants and entity definitions
│   ├── diagnostics.py            # Diagnostics data provider
│   ├── manifest.json             # Integration metadata
│   ├── number.py                 # Number platform (3 control entities)
│   ├── sensor.py                 # Sensor platform (80+ monitoring entities)
│   ├── switch.py                 # Switch platform (1 pause toggle)
│   ├── strings.json              # English strings (not translated)
│   └── translations/             # Translated strings
│       ├── de.json               # German translation
│       └── en.json               # English translation
├── tests/                        # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py               # pytest fixtures and mocks
│   ├── test_api.py               # API client tests (17 tests)
│   ├── test_config_flow.py       # Config/options flow tests (15 tests)
│   └── test_init.py              # Coordinator tests (7 tests)
├── Documentation/                # API documentation (separate HTML file)
├── examples/                     # Lovelace cards and automation examples
├── .github/                      # GitHub workflows and templates
│   ├── workflows/                # CI/CD automation
│   └── ISSUE_TEMPLATE/           # Issue templates
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── pytest.ini                    # pytest configuration
├── requirements_dev.txt          # Development dependencies
├── run-tests.sh                  # Test runner script
├── validate.sh                   # Full validation script
├── create-release.sh             # Release packaging script
├── ARCHITECTURE.md               # Detailed architecture documentation
├── CONTRIBUTING.md               # Contribution guidelines
├── README.md                     # User documentation
├── INFO.md                       # HACS integration information
└── hacs.json                     # HACS manifest
```

## Development Architecture

### Core Design Patterns

1. **DataUpdateCoordinator Pattern**: Single coordinator polls API every 10-300s (default 30s), distributes data to all entities
2. **Value Path Mapping**: Declarative entity definitions using path arrays (e.g., `["values", "powerflow", "l1", "voltage"]`)
3. **Custom Exception Hierarchy**: Typed exceptions for proper error handling and reauth flows
4. **Platform Separation**: Entity types split across files (sensor, binary_sensor, switch, number)
5. **Config Flow UI**: Modern UI-based configuration with validation, discovery, and options management

### Custom Exception Hierarchy

```python
# custom_components/nrgkick/api.py
class NRGkickApiClientError(Exception):
    """Base exception for API errors."""

class NRGkickApiClientCommunicationError(NRGkickApiClientError):
    """Exception for communication errors (timeout, connection refused)."""

class NRGkickApiClientAuthenticationError(NRGkickApiClientError):
    """Exception for authentication errors (401, 403)."""
```

**Why This Matters:**

- `NRGkickApiClientAuthenticationError` triggers Home Assistant's reauth UI
- `NRGkickApiClientCommunicationError` makes entities unavailable without triggering reauth
- Type-specific catching enables proper error handling in config flow and coordinator

### API Client (`api.py`)

- **Endpoints**: `/info`, `/control`, `/values`
- **Methods**: `get_info()`, `get_control()`, `get_values()`, `set_current()`, `set_charge_pause()`, `set_energy_limit()`, `set_phase_count()`
- **Authentication**: Optional BasicAuth
- **Error Handling**: Detects 401/403 before `raise_for_status()` to throw proper auth exceptions
- **Session Management**: Uses `aiohttp.ClientSession` with configurable timeouts

### Coordinator (`__init__.py`)

```python
class NRGkickDataUpdateCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        # Fetch all three endpoints
        info = await self.api_client.get_info()
        control = await self.api_client.get_control()
        values = await self.api_client.get_values()
        return {**info, **control, **values}
```

- **Polling Interval**: Configurable 10-300s via options flow
- **Error Handling**: Catches `NRGkickApiClientAuthenticationError` → raises `ConfigEntryAuthFailed`
- **Update Flow**: After control commands, waits 2 seconds then triggers manual refresh

### Entity Definitions (`const.py`)

Entities are defined declaratively using dataclasses:

```python
@dataclass
class NRGkickSensorEntityDescription(SensorEntityDescription):
    value_path: list[str] | None = None
    value_fn: Callable[[Any], Any] | None = None

SENSORS: tuple[NRGkickSensorEntityDescription, ...] = (
    NRGkickSensorEntityDescription(
        key="total_active_power",
        translation_key="total_active_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_path=["values", "powerflow", "total_active_power"],
    ),
    # ... 80+ more definitions
)
```

## Code Style Guidelines

### Python Style

- **Formatter**: Black (line length 88)
- **Import Sorting**: isort with Black profile
- **Linter**: flake8 + pylint (disabled: C0111, C0103, W0212, R0913, R0902, R0914, R0801)
- **Type Checking**: mypy with strict settings
- **Docstrings**: Required for public methods (Google style preferred)
- **Async/Await**: All I/O operations must be async

### Naming Conventions

- **Classes**: PascalCase (`NRGkickDataUpdateCoordinator`)
- **Functions**: snake_case (`async_setup_entry`, `_async_update_data`)
- **Constants**: UPPER_SNAKE_CASE (`CONF_SCAN_INTERVAL`, `DEFAULT_SCAN_INTERVAL`)
- **Private Methods**: Prefix with `_` (`_get_device_info`)
- **Entity Keys**: snake_case matching translation keys

### Home Assistant Patterns

1. **Import Order**:

   ```python
   # Standard library
   from typing import Any
   import logging

   # Home Assistant core
   from homeassistant.core import HomeAssistant
   from homeassistant.config_entries import ConfigEntry

   # Home Assistant helpers
   from homeassistant.helpers.entity import Entity
   from homeassistant.helpers.update_coordinator import CoordinatorEntity

   # Local imports
   from .const import DOMAIN, CONF_SCAN_INTERVAL
   from .api import NRGkickApiClient
   ```

2. **Modern Import Paths** (HA 2025.10+):

   - ✅ `from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo`
   - ❌ `from homeassistant.components.zeroconf import ZeroconfServiceInfo` (deprecated in HA 2026.2)

3. **Options Flow** (HA 2025.12+):

   - ✅ No explicit `__init__` in `OptionsFlowHandler` - base class provides `self.config_entry` property
   - ❌ `def __init__(self, config_entry): self.config_entry = config_entry` (deprecated, removed in HA 2025.12)

4. **Exception Handling**:

   - Use custom exceptions, not generic `Exception`
   - Chain exceptions with `raise ... from err`
   - Catch specific exception types in config flow

5. **Entity Registration**:
   - Use `CoordinatorEntity` base class for automatic update subscription
   - Define entities in `const.py` using dataclasses
   - Use `translation_key` for localization

## Testing Requirements

### Test Coverage Targets

- **Overall**: ≥89% (current: 89%)
- **API Client**: ≥97% (current: 97%)
- **Config Flow**: ≥90% (current: 90%)
- **Coordinator**: ≥98% (current: 98%)

### Test Structure

All tests use `pytest` with `pytest-homeassistant-custom-component`:

```python
# tests/test_api.py - API client tests
async def test_get_info(nrgkick_api_client, aresponses):
    aresponses.add(...)
    result = await nrgkick_api_client.get_info()
    assert result["general"]["serial_number"] == "..."

# tests/test_config_flow.py - Config flow tests
async def test_form(hass):
    result = await hass.config_entries.flow.async_init(...)
    assert result["type"] == "form"

# tests/test_init.py - Coordinator tests
async def test_setup_entry(hass, mock_config_entry):
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state == ConfigEntryState.LOADED
```

### Running Tests

```bash
# Run all tests (default)
./run-tests.sh

# Run specific test file
./run-tests.sh tests/test_api.py

# Run with coverage
./run-tests.sh coverage

# Run only fast tests (for CI)
./run-tests.sh ci
```

### Validation Before Commit

```bash
./validate.sh
# Runs: pre-commit checks + all tests
# Must pass before committing!
```

## Common Development Tasks

### Adding a New Sensor

1. **Define in `const.py`**:

   ```python
   NRGkickSensorEntityDescription(
       key="new_sensor",
       translation_key="new_sensor",
       native_unit_of_measurement=UnitOfPower.WATT,
       device_class=SensorDeviceClass.POWER,
       state_class=SensorStateClass.MEASUREMENT,
       value_path=["values", "section", "field"],
   ),
   ```

2. **Add translation in `strings.json`**:

   ```json
   "new_sensor": {
     "name": "New Sensor"
   }
   ```

3. **Add test** in `test_init.py` (verify entity exists and has correct state)

### Adding a New Control (Number/Switch)

1. **Define in `const.py`** (in `NUMBERS` or `SWITCHES` tuple)
2. **Implement service call** in platform file (e.g., `number.py`)
3. **Add test** in appropriate test file
4. **Test with real device** to verify control works

### Updating API Client

1. **Modify `api.py`** - add/modify methods
2. **Update tests** in `test_api.py` with mock responses
3. **Run validation**: `./validate.sh`
4. **Test with real device** to verify API changes

### Fixing a Bug

1. **Write failing test** that reproduces the bug
2. **Fix the bug** in source code
3. **Verify test passes**: `./run-tests.sh`
4. **Run full validation**: `./validate.sh`
5. **Update documentation** if behavior changed

## Pre-Commit Hooks

The repository uses pre-commit hooks to enforce code quality:

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml/json**: Validate YAML/JSON files
- **black**: Auto-format Python code
- **isort**: Sort imports
- **flake8**: Lint for common issues
- **mypy**: Type checking
- **pylint**: Advanced linting
- **prettier**: Format JSON/YAML/Markdown

**Installation**:

```bash
pip install pre-commit
pre-commit install
```

**Manual Run**:

```bash
pre-commit run --all-files
```

## Configuration Storage

Home Assistant stores integration configuration in two places:

1. **`entry.data`** - Connection settings (host, username, password)
   - Updated via config/options flow
   - Triggers reload when changed
2. **`entry.options`** - User preferences (scan_interval)
   - Updated via options flow
   - Triggers reload when changed

**Retrieval Pattern** (with fallbacks):

```python
scan_interval = entry.options.get(
    CONF_SCAN_INTERVAL,
    entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
)
```

## API Endpoints and Data Structure

### GET /info

Returns device information:

```json
{
  "general": {"serial_number": "...", "model_type": "..."},
  "connector": {"rated_current": 32, ...},
  "grid": {"voltage": 400, "frequency": 50},
  "network": {"ip_address": "...", "mac_address": "..."},
  "versions": {"smartmodule": "...", "powermodule": "..."}
}
```

### GET /control

Returns control parameters:

```json
{
  "control": {
    "current_set": 16.0,
    "charge_pause": 0,
    "energy_limit": 0,
    "phase_count": 3
  }
}
```

### GET /values

Returns real-time telemetry (most frequently accessed):

```json
{
  "energy": {"session": 15234, "total": 1523456},
  "powerflow": {
    "total_active_power": 11000,
    "l1": {"voltage": 230.5, "current": 16.2, "active_power": 3686},
    "l2": {...},
    "l3": {...}
  },
  "status": {"charging": 3, "rate": 11},
  "temperatures": {"housing": 34.79, "connector_l1": 21.09}
}
```

### Control Endpoints (GET with parameters)

- **Set Current**: `GET /control?current_set=16.0` (6.0-32.0A)
- **Pause/Resume**: `GET /control?charge_pause=1` (0=resume, 1=pause)
- **Energy Limit**: `GET /control?energy_limit=5000` (0=unlimited, Wh)
- **Phase Count**: `GET /control?phase_count=3` (1-3, if supported)

**Important**: After control commands, integration waits 2 seconds then triggers coordinator refresh.

## Important Constants

```python
# Domains and platforms
DOMAIN = "nrgkick"
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BINARY_SENSOR]

# Configuration
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

# Control limits
MIN_CURRENT = 6.0
DEFAULT_CURRENT = 16.0
MAX_CURRENT_16A = 16.0
MAX_CURRENT_32A = 32.0

# Zeroconf
ZEROCONF_TYPE = "_nrgkick._tcp.local."
```

## Troubleshooting Development Issues

### Import Errors in Pylint

**Problem**: `E0401: Unable to import 'homeassistant.helpers.service_info.zeroconf'`

**Solution**: Ensure pre-commit uses Python 3.13+ and Home Assistant 2025.10.0+

- Check `.pre-commit-config.yaml`: `default_language_version: python: python3.13`
- Check pylint dependencies: `homeassistant>=2025.10.0`
- Clean cache: `pre-commit clean`

### Tests Fail with Import Errors

**Problem**: `ModuleNotFoundError: No module named 'homeassistant'`

**Solution**: Install development dependencies in virtual environment

```bash
source venv/bin/activate
pip install -r requirements_dev.txt
```

### Device Not Discovered

**Problem**: NRGkick device not appearing in Home Assistant

**Solution**:

1. Verify JSON API is enabled in NRGkick App
2. Check mDNS works: `avahi-browse -r _nrgkick._tcp`
3. Manually add integration with IP address

### Entities Showing "Unavailable"

**Problem**: All entities show as unavailable

**Solution**:

1. Check Home Assistant logs for authentication or connection errors
2. Verify device is reachable: `curl http://<device-ip>/info`
3. Check credentials if authentication is enabled
4. Increase scan interval if device is slow to respond

## Release Process

For maintainers only:

```bash
./create-release.sh
# Creates versioned zip in releases/ directory
# Automatically updates manifest.json version
# Ready to upload to GitHub releases
```

## External Documentation

- **ARCHITECTURE.md**: Detailed technical architecture and design patterns
- **CONTRIBUTING.md**: Full contribution guidelines and development setup
- **README.md**: User-facing documentation for installation and usage
- **tests/README.md**: Test suite documentation and test status
- **Documentation/**: Interactive API documentation (HTML file for device API, not integration)

## Key Differences from Generic HA Integrations

1. **Value Path System**: Unique declarative entity definition pattern using path arrays
2. **Control Command Delays**: 2-second wait + refresh after control changes (device needs time)
3. **Custom Exception Hierarchy**: Three-tier exception system for proper error handling
4. **Full Reconfiguration in Options**: Options flow allows changing host/credentials, not just preferences
5. **No Cloud Dependency**: 100% local API, no internet required
6. **Discovery Tracking**: Updates config entry when device IP changes after discovery

## Best Practices for This Codebase

1. **Never hardcode API paths** - use constants from `const.py`
2. **Always use value paths** - don't manually traverse coordinator data in entities
3. **Test with real device** - mocks don't catch all API quirks
4. **Wait after control commands** - device needs time to process changes
5. **Check ARCHITECTURE.md first** - comprehensive technical documentation
6. **Run validation before PR** - `./validate.sh` must pass
7. **Update both strings.json and translations/** - keep localization in sync
8. **Follow HA 2025.10+ patterns** - use modern import paths and patterns
