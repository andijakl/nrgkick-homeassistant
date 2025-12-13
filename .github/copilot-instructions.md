# NRGkick Home Assistant Integration

## ⚠️ CRITICAL: Pre-Commit Rules

**Most AI-generated code fails pre-commit. Follow these rules:**

1. **Line Length**: Max 88 characters. Break with parentheses.
2. **Docstrings (PEP 257)**: Blank line after last section before closing `"""`.
3. **File Endings**: Exactly ONE newline at EOF for all files.
4. **JSON**: 2-space indent, no trailing commas.

## Project Overview

- **Product**: Home Assistant integration for NRGkick Gen2 EV charger
- **API**: Local REST JSON API (no cloud), endpoints: `/info`, `/control`, `/values`
- **Architecture**: DataUpdateCoordinator polling (default 30s), 80+ sensors, 3 binary sensors, 1 switch, 3 numbers
- **Python**: 3.13+ for dev, 3.11+ runtime

## Key Files

```
custom_components/nrgkick/
├── __init__.py      # Coordinator, setup/teardown
├── api.py           # API client wrapper (delegates to nrgkick-api library)
├── config_flow.py   # UI config, discovery, reauth
├── const.py         # Constants, entity definitions
├── sensor.py        # 80+ sensors
├── binary_sensor.py # 3 binary sensors
├── switch.py        # Charge pause toggle
├── number.py        # Current, energy limit, phase count controls
└── translations/    # en.json, de.json (all UI strings go here)
```

## Code Style

- **Linter/Formatter**: Ruff (replaces Black, isort, flake8)
- **Type Checking**: mypy strict
- **Docstrings**: Google style, PEP 257 compliant

### Critical Patterns

```python
# Line breaks - use parentheses
result = await self.api_client.get_values(
    sections=["powerflow", "energy"]
)

# Docstrings - blank line after last section
def set_current(self, current: float) -> dict:
    """Set charging current.

    Args:
        current: Current in Amps (6.0-32.0).

    """
    return self._api.set_current(current)

# Long strings - implicit concatenation
raise HomeAssistantError(
    "Failed to connect to device: "
    "Connection timeout"
)
```

### HA 2025.12+ Patterns

```python
# Modern imports
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

# OptionsFlowHandler - no __init__, use self.config_entry property

# Exception chaining
raise ConfigEntryAuthFailed from err
```

## Adding Features

### New Sensor

1. Add to `SENSORS` tuple in `const.py` with `value_path`
2. Add translation to **both** `translations/en.json` AND `translations/de.json`

### New Control

1. Add to `NUMBERS` or `SWITCHES` in `const.py`
2. Implement in platform file
3. Add translations to both language files

## Testing

```bash
./run-tests.sh          # Run all tests
./run-tests.sh coverage # With coverage report
./validate.sh           # Pre-commit + tests (run before commit!)
```

## API Reference

```python
# Endpoints
GET /info    # Device info, serial, versions
GET /control # Current settings: current_set, charge_pause, energy_limit, phase_count
GET /values  # Real-time: power, energy, temperatures, status

# Control (GET with params)
GET /control?current_set=16.0
GET /control?charge_pause=1
GET /control?energy_limit=5000
GET /control?phase_count=3
```

## Exception Hierarchy

```python
NRGkickApiClientError                    # Base
├── NRGkickApiClientCommunicationError   # Timeout, connection - entities unavailable
└── NRGkickApiClientAuthenticationError  # 401/403 - triggers reauth flow
```

## Troubleshooting

| Problem                      | Solution                                      |
| ---------------------------- | --------------------------------------------- |
| Line too long                | Break with parentheses at 88 chars            |
| Missing docstring blank line | Add blank line before closing `"""`           |
| Import errors                | `pip install -r requirements_dev.txt` in venv |
| Pre-commit modifies files    | Stage changes and commit again                |

## Key Constants

```python
DOMAIN = "nrgkick"
DEFAULT_SCAN_INTERVAL = 30  # seconds (10-300 range)
MIN_CURRENT = 6.0
MAX_CURRENT_32A = 32.0
```

## Best Practices

1. Use `value_path` arrays for entity data access
2. Wait 2s after control commands before refresh
3. Run `./validate.sh` before every commit
4. Add translations to **both** en.json and de.json
5. Check ARCHITECTURE.md for detailed patterns
