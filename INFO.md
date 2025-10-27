# NRGkick Integration - Technical Reference

Quick reference for NRGkick Home Assistant integration internals. For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md). For user documentation, see [README.md](README.md).

## File Structure

```
custom_components/nrgkick/
├── __init__.py           # Coordinator, setup/teardown
├── api.py                # REST client, custom exceptions
├── binary_sensor.py      # 3 binary sensors
├── config_flow.py        # UI flows (user, zeroconf, reauth, options)
├── const.py              # Constants, STATUS_MAP, entity definitions
├── diagnostics.py        # Diagnostics provider
├── manifest.json         # Integration metadata
├── number.py             # 3 number controls
├── sensor.py             # 80+ sensors
├── switch.py             # 1 switch
└── translations/         # en.json, de.json
```

## Core Classes

**`NRGkickDataUpdateCoordinator`** (`__init__.py`)

- Polls device every 10-300s (default: 30s)
- Fetches `/info`, `/control`, `/values`
- Distributes data to 80+ entities
- Handles `ConfigEntryAuthFailed` for reauth flow

**`NRGkickAPI`** (`api.py`)

- aiohttp client with 10s timeout
- Optional BasicAuth
- Custom exceptions: `NRGkickApiClientAuthenticationError`, `NRGkickApiClientCommunicationError`, `NRGkickApiClientError`
- Methods: `get_info()`, `get_control()`, `get_values()`, `set_current()`, `set_charge_pause()`, `set_energy_limit()`, `set_phase_count()`, `test_connection()`

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

All entities use value_path arrays for data extraction and include 2-second sync delays after control commands.

## API Endpoints

### Read Operations

- **GET /info**: Device metadata (general, connector, grid, network, versions)
- **GET /control**: Current control parameters
- **GET /values**: Real-time telemetry

### Write Operations (GET with params)

- **GET /control?current=16.0**: Set charging current (6.0-32.0A)
- **GET /control?pause=1**: Pause (1) or resume (0) charging
- **GET /control?energy=5000**: Set energy limit (Wh, 0=unlimited)
- **GET /control?phases=3**: Set phase count (1-3, if supported)

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

### 2-Second Sync Delay

All control entities (switch, number) use this pattern:

```python
await self.coordinator.api.set_current(value)
await asyncio.sleep(2)  # Device state sync
await self.coordinator.async_request_refresh()
```

### Exception Hierarchy

- **`NRGkickApiClientError`**: Base exception
- **`NRGkickApiClientCommunicationError`**: Network/timeout → entities unavailable
- **`NRGkickApiClientAuthenticationError`**: 401/403 → triggers reauth flow

## Key Implementation Details

- **Session reuse**: Uses `async_get_clientsession(hass)` for connection pooling
- **First refresh**: `async_config_entry_first_refresh()` validates device before entity creation
- **Update listener**: `entry.add_update_listener(async_reload_entry)` triggers reload on config changes
- **Unique ID**: Device serial number prevents duplicates
- **Discovery tracking**: `_abort_if_unique_id_configured(updates={CONF_HOST: ...})` updates IP on rediscovery

## Testing

Run tests: `./run-tests.sh`
Run validation: `./validate.sh` (pre-commit + pytest)

**Test suite**: 50 tests with 89% coverage

- API tests: 17 (97% coverage)
- Config flow tests: 26 (90% coverage)
- Coordinator tests: 7 (98% coverage)

## Performance Characteristics

- **Memory**: ~5MB per device
- **Network**: 3 HTTP requests per scan interval
- **CPU**: Negligible (async I/O only)
- **Entity count**: 87 total (80+ sensors + 3 binary + 1 switch + 3 numbers)
