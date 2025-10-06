# Developer Documentation

## Architecture

### Overview

```
Home Assistant
    ↓
NRGkickDataUpdateCoordinator (polls every 30s)
    ↓
NRGkickAPI (aiohttp HTTP client)
    ↓
NRGkick Device (REST JSON API: /info, /control, /values)
```

### Component Structure

```
custom_components/nrgkick/
├── __init__.py           # Integration entry point, coordinator
├── api.py                # API client (NRGkickAPI)
├── binary_sensor.py      # Binary sensors (3 entities)
├── config_flow.py        # UI configuration flow
├── const.py              # Constants (STATUS_MAP, DOMAIN, endpoints)
├── manifest.json         # Metadata (domain, version, dependencies)
├── number.py             # Number controls (3 entities)
├── sensor.py             # Sensors (80+ entities)
├── switch.py             # Switches (1 entity)
└── translations/         # i18n (en, de)
```

## Key Classes

### NRGkickDataUpdateCoordinator

**File**: `__init__.py`

**Purpose**: Manages data fetching and distribution to entities

**Features**:

- Polls device every 30 seconds
- Fetches `/info`, `/control`, `/values` endpoints
- Caches data for all entities
- Handles errors and retries

### NRGkickAPI

**File**: `api.py`

**Purpose**: HTTP client for NRGkick REST API

**Methods**:

- `get_info(sections)` - Device info
- `get_control()` - Control parameters
- `get_values(sections)` - Real-time values
- `set_current(float)` - Set charging current
- `set_charge_pause(bool)` - Pause/resume
- `set_energy_limit(int)` - Set energy limit (Wh)
- `set_phase_count(int)` - Set phase count (1-3)
- `test_connection()` - Connectivity check

**Features**:

- Optional BasicAuth support
- 10-second timeout
- Error handling

### ConfigFlow

**File**: `config_flow.py`

**Purpose**: UI-based configuration

**Features**:

- Host (IP/hostname) input
- Optional username/password
- Connection validation
- Unique ID from serial number
- Duplicate prevention

## Entity Types

### Sensors (80+)

**Categories**:

- Power & Energy (8 sensors)
- Per-phase metrics (18 sensors: L1/L2/L3)
- Temperatures (6 sensors)
- Network info (4 sensors)
- Device info (10+ sensors)
- Status (10+ sensors)

**Features**:

- Display precision hints
- Suggested unit conversions (Wh → kWh)
- Disabled by default (version sensors)
- Translation keys

### Binary Sensors (3)

- `charging` - Active charging status
- `charge_permitted` - Charge allowed
- `charge_pause` - Pause state

### Switch (1)

- `charge_pause` - Pause/resume control
- 2-second delay after turn_off for state sync

### Number Entities (3)

- `charging_current` - 6-32A (slider)
- `energy_limit` - 0-100,000 Wh (box)
- `phase_count` - 1-3 (slider)
- 2-second delay after changes for state sync

## API Endpoints

### GET /info

Device information:

```json
{
  "general": {
    "serial_number": "ABC123",
    "device_name": "NRGkick",
    "model_type": "NRGkick Gen2",
    "rated_current": 32
  },
  "connector": { ... },
  "grid": { ... },
  "network": { ... },
  "versions": { ... }
}
```

### GET /control

Control parameters:

```json
{
  "current_set": 16.0,
  "charge_pause": 0,
  "energy_limit": 0,
  "phase_count": 3
}
```

### GET /values

Real-time telemetry:

```json
{
  "general": {
    "status": 3,
    "charging_rate": 95,
    "vehicle_connect_time": 1234,
    "vehicle_charging_time": 890
  },
  "energy": {
    "total_charged_energy": 150000,
    "charged_energy": 5000
  },
  "powerflow": {
    "total_active_power": 11000,
    "charging_voltage": 230,
    "charging_current": 16.0,
    "l1": { ... },
    "l2": { ... },
    "l3": { ... }
  },
  "temperatures": { ... }
}
```

### Control Commands

**Set current**: `GET /control?current=16.0`
**Pause charging**: `GET /control?pause=1`
**Resume charging**: `GET /control?pause=0`
**Set energy limit**: `GET /control?energy=10000`
**Set phases**: `GET /control?phases=3`

## Status Codes

```python
STATUS_MAP = {
    0: "Standby",
    1: "Connected",
    2: "Permitted",
    3: "Charging",
    4: "Error",
    5: "Wakeup",
    6: "Booting",
    7: "Reserved",
}
```

## Configuration

### manifest.json

```json
{
  "domain": "nrgkick",
  "name": "NRGkick",
  "version": "0.1.0",
  "config_flow": true,
  "documentation": "https://github.com/andijakl/nrgkick-homeassistant",
  "issue_tracker": "https://github.com/andijakl/nrgkick-homeassistant/issues",
  "requirements": ["aiohttp", "async-timeout"],
  "codeowners": ["@andijakl"],
  "iot_class": "local_polling"
}
```

### hacs.json

```json
{
  "name": "NRGkick",
  "render_readme": true,
  "domains": ["sensor", "binary_sensor", "switch", "number"]
}
```

## Development Workflow

### Setup

1. Clone repository
2. Copy `custom_components/nrgkick` to HA config
3. Restart Home Assistant
4. Configure via UI

### Testing

1. Enable debug logging:

   ```yaml
   logger:
     default: info
     logs:
       custom_components.nrgkick: debug
   ```

2. Check logs: Settings → System → Logs

3. Monitor coordinator updates (every 30s)

### Debugging

**Common issues**:

- Import errors: Expected in dev environment (no HA core)
- Connection timeouts: Check device IP, network
- Authentication errors: Verify BasicAuth settings
- State sync: Uses 2-second delays after control commands

## Code Patterns

### Entity Initialization

All entities include:

- Translation key for i18n
- Device info (serial, model, manufacturer)
- Unique ID: `{serial}_{entity_key}`

### Data Access

Entities access coordinator data via value paths:

```python
["values", "powerflow", "total_active_power"]  # → data["values"]["powerflow"]["total_active_power"]
```

### Control Commands

Pattern for control entities:

1. Call API method
2. Sleep 2 seconds (device state sync)
3. Request coordinator refresh

## Testing Checklist

- [ ] UI configuration with valid IP
- [ ] UI configuration with invalid IP (error handling)
- [ ] BasicAuth with credentials
- [ ] BasicAuth without credentials (should fail if enabled)
- [ ] All sensors show data
- [ ] Switch toggle works
- [ ] Number entities update device
- [ ] Coordinator polls every 30s
- [ ] Device disconnection handling
- [ ] Device reconnection recovery
- [ ] Multiple device support

## Performance

**Resource Usage**:

- Memory: ~5MB per device
- CPU: Negligible (async I/O)
- Network: 3 HTTP requests every 30s

**Optimization**:

- Single coordinator per device
- Shared data across entities
- Async/await throughout
- Connection pooling (aiohttp session reuse)

## Future Enhancements

- Energy dashboard integration
- Charging session statistics
- Cost calculation
- Advanced scheduling
- OCPP support (if available)

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [Entity Platform](https://developers.home-assistant.io/docs/core/entity)
