# NRGkick Integration - Technical Reference

Quick reference for NRGkick Home Assistant integration internals. For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md). For user documentation, see [README.md](README.md).

## Architecture Overview

The integration uses a **two-layer architecture**:

1. **nrgkick-api** - Standalone Python library on [PyPI](https://pypi.org/project/nrgkick-api/) for device communication ([separate repository](https://github.com/andijakl/nrgkick-api))
2. **Home Assistant Integration** - This repository: thin wrapper with HA-specific patterns

This separation enables potential Home Assistant core integration and allows the API library to be used independently.

## File Structure

```
custom_components/nrgkick/
├── __init__.py           # Coordinator, setup/teardown
├── api.py                # Wrapper around nrgkick-api library
├── binary_sensor.py      # 3 binary sensors
├── config_flow.py        # UI flows (user, zeroconf, reauth, reconfigure, options)
├── const.py              # Constants, STATUS_MAP, entity definitions
├── diagnostics.py        # Diagnostics provider
├── icons.json            # Default icon mapping
├── manifest.json         # Integration metadata (requires nrgkick-api)
├── number.py             # 3 number controls
├── sensor.py             # 80+ sensors
├── switch.py             # 1 switch
└── translations/         # en.json, de.json
```

**External Dependency**: [nrgkick-api](https://github.com/andijakl/nrgkick-api) library on PyPI handles device communication.

## Core Classes

**`NRGkickDataUpdateCoordinator`** (`__init__.py`)

- Polls device every 10-300s (default: 30s)
- Fetches `/info`, `/control`, `/values`
- Distributes data to 80+ entities
- Handles `ConfigEntryAuthFailed` for reauth flow
- Public methods: `async_set_current()`, `async_set_charge_pause()`, `async_set_energy_limit()`, `async_set_phase_count()`

**`NRGkickEntity`** (`__init__.py`)

- Base class for all entity types
- Provides common device info setup
- Sets `_attr_has_entity_name = True` for modern naming
- Type annotation: `coordinator: NRGkickDataUpdateCoordinator`

**`NRGkickAPI`** ([nrgkick-api](https://github.com/andijakl/nrgkick-api) library - external)

- Standalone Python package on PyPI (no Home Assistant dependencies)
- aiohttp client with 10s timeout
- Optional BasicAuth
- Automatic retry with exponential backoff (3 attempts, 1.5s base)
- Retries: Timeouts, HTTP 500-504, connection errors
- No retry: Authentication errors (401/403), client errors (4xx)
- Library exceptions: `NRGkickError`, `NRGkickConnectionError`, `NRGkickAuthenticationError`
- Methods: `get_info()`, `get_control()`, `get_values()`, `set_current()`, `set_charge_pause()`, `set_energy_limit()`, `set_phase_count()`, `test_connection()`

**`NRGkickApiClient`** (`api.py` - integration wrapper)

- Thin wrapper around `NRGkickAPI` from `nrgkick-api` library
- Converts library exceptions to HA-specific exceptions with translation support
- Custom exceptions: `NRGkickApiClientAuthenticationError`, `NRGkickApiClientCommunicationError`
- Uses `async_get_clientsession(hass)` for HA session management

**`ConfigFlow`** (`config_flow.py`)

- Discovery via mDNS `_nrgkick._tcp.local.`
- Unique ID from device serial number
- Full reconfiguration support (host, credentials, scan_interval)
- Reauth flow using `async_update_reload_and_abort()`

## Entity Distribution

- **Sensors**: 80+ (power, energy, voltage, current, temperatures, status, network, versions)
- **Binary Sensors**: 3 (charging, charge_permitted, charge_pause)
- **Switch**: 1 (charge_pause toggle)
- **Numbers**: 3 (charging_current 6-32A, energy_limit 0-100kWh, phase_count 1-3)

All entities use value_path arrays for data extraction. Control commands verify responses immediately.

## API Endpoints

### Read Operations

- **GET /info**: Device metadata (general, connector, grid, network, versions)
- **GET /control**: Current control parameters
- **GET /values**: Real-time telemetry

### Write Operations (GET with params)

- **GET /control?current_set=16.0**: Set charging current (6.0-32.0A)
- **GET /control?charge_pause=1**: Pause (1) or resume (0) charging
- **GET /control?energy_limit=5000**: Set energy limit (Wh, 0=unlimited)
- **GET /control?phase_count=3**: Set phase count (1-3, if supported)

Responses:

- **Success**: Returns confirmed value (e.g., `{"current_set": 16.0}`)
- **Error**: Returns error message (e.g., `{"Response": "blocked by solar-charging"}`)

## Configuration Storage

**`entry.data`** (connection settings):

```python
{"host": "192.168.1.100", "username": "admin", "password": "secret"}
```

**`entry.options`** (user preferences):

```python
{"scan_interval": 30}
```

**Retrieval pattern** (with fallbacks):

```python
entry.options.get(CONF_SCAN_INTERVAL,
    entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
```

## Constants (`const.py`)

```python
DOMAIN = "nrgkick"
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BINARY_SENSOR]

# Scan interval
DEFAULT_SCAN_INTERVAL = 30  # seconds
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

# Status codes
STATUS_MAP = {
    0: "Unknown", 1: "Standby", 2: "Connected",
    3: "Charging", 6: "Error", 7: "Wakeup"
}
```

## Value Path System

Entities use declarative path arrays to extract data from coordinator:

```python
value_path = ["values", "powerflow", "l1", "voltage"]
# Resolves to: coordinator.data["values"]["powerflow"]["l1"]["voltage"]
```

Optional transformation via `value_fn`:

```python
value_fn = lambda x: STATUS_MAP.get(x, "Unknown")  # Convert 3 → "Charging"
```

## Control Flow Patterns

### Coordinator Control Methods

Entities call coordinator methods for control operations:

```python
await self.coordinator.async_set_current(value)
# Coordinator handles: API call → parse response → verify → update state
```

Control responses from device:

- **Success**: `{"current_set": 6.7}` - Contains confirmed value
- **Error**: `{"Response": "Charging pause is blocked by solar-charging"}` - Contains error message

### Exception Hierarchy

**Library exceptions** (`nrgkick-api`):

- **`NRGkickError`**: Base exception
- **`NRGkickConnectionError`**: Network/timeout errors
- **`NRGkickAuthenticationError`**: 401/403 errors

**Integration exceptions** (`api.py` wrapper):

- **`NRGkickApiClientError`**: Base exception (wraps `NRGkickError`)
- **`NRGkickApiClientCommunicationError`**: Network/timeout → entities unavailable
- **`NRGkickApiClientAuthenticationError`**: 401/403 → triggers reauth flow

The wrapper translates library exceptions to HA exceptions with translation support for user-friendly error messages.

## Key Implementation Details

- **Session reuse**: Uses `async_get_clientsession(hass)` for connection pooling
- **First refresh**: `async_config_entry_first_refresh()` validates device before entity creation
- **Update listener**: `entry.add_update_listener(async_reload_entry)` triggers reload on config changes
- **Unique ID**: Device serial number prevents duplicates
- **Discovery tracking**: `_abort_if_unique_id_configured(updates={CONF_HOST: ...})` updates IP on rediscovery

## Testing

Run tests: `./run-tests.sh`
Run validation: `./validate.sh` (pre-commit + pytest)

**Test suite**: 73 tests with 96% coverage

- API tests: 26 (94% coverage)
- Config flow tests: 24 (95% coverage)
- Coordinator tests: 13 (95% coverage)
- Platform tests: 7 (97-100% coverage)
- Naming tests: 2 (100% coverage)
- Diagnostics tests: 1 (100% coverage)

## Performance Characteristics

- **Memory**: ~5MB per device
- **Network**: 3 HTTP requests per scan interval
- **CPU**: Negligible (async I/O only)
- **Entity count**: 87 total (80+ sensors + 3 binary + 1 switch + 3 numbers)
