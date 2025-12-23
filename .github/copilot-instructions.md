# NRGkick Home Assistant Integration

## ⚠️ CRITICAL: Pre-Commit Rules (Most AI Code Fails Here)

1. **Line Length**: Max 88 chars. Break with parentheses, not backslashes.
2. **Docstrings**: Google style with blank line before closing `"""`.
3. **File Endings**: Exactly ONE newline at EOF.
4. **JSON**: 2-space indent, no trailing commas.
5. **Always run `./validate.sh` before committing.**

## Architecture Overview

**Two-layer design**: `nrgkick-api` library (PyPI) handles HTTP/auth → HA wrapper adds coordinator pattern.

```
custom_components/nrgkick/
├── __init__.py      # Entry point, setup/teardown
├── coordinator.py   # NRGkickDataUpdateCoordinator
├── entity.py        # NRGkickEntity base class
├── api.py           # Thin wrapper translating library exceptions to HA types
├── sensor.py        # 80+ sensors using value_path pattern
├── number.py        # Controls: current_set, energy_limit, phase_count
├── switch.py        # Charge pause toggle
└── translations/    # en.json AND de.json (both required!)
```

**Data Flow**: Coordinator polls `/info`, `/control`, `/values` → merges into `coordinator.data` dict → entities extract via `value_path`.

## Entity Pattern (Critical)

All entities use `value_path` arrays to navigate `coordinator.data`:

```python
# In sensor.py - define entity with path to data
NRGkickSensor(
    coordinator,
    key="active_power",  # Translation key + unique_id suffix
    value_path=["values", "powerflow", "power", "total"],
    # ... other params
)

# In entity's native_value property
data = self.coordinator.data
for key in self._value_path:
    data = data.get(key)  # Navigates: data["values"]["powerflow"]["power"]["total"]
```

## Adding New Features

### New Sensor

1. Add `NRGkickSensor(...)` instance to list in [sensor.py](custom_components/nrgkick/sensor.py)
2. Add translation key to **both** `translations/en.json` AND `translations/de.json`

### New Control (Number/Switch)

1. Add entity to [number.py](custom_components/nrgkick/number.py) or [switch.py](custom_components/nrgkick/switch.py)
2. Add coordinator method in `coordinator.py` using
   `_async_execute_command_with_verification`
3. Add translations to both language files

## Code Style Examples

```python
# Long lines - use parentheses
result = await self.coordinator.async_set_current(
    value=16.0
)

# Docstring format (blank line before closing)
def set_current(self, current: float) -> dict:
    """Set charging current.

    Args:
        current: Current in Amps (6.0-32.0).

    """
    return self._api.set_current(current)

# Exception chaining (HA 2025.12+)
raise ConfigEntryAuthFailed from err
```

## Testing & Validation

When executing scripts, ensure your virtual environment is activated.
Activate it with: ./venv/bin/activate

```bash
./validate.sh           # Full validation (pre-commit + tests) - RUN BEFORE COMMIT
./run-tests.sh          # Tests only
./run-tests.sh coverage # Tests with HTML coverage report
```

Tests use `pytest-homeassistant-custom-component`. See [tests/conftest.py](tests/conftest.py) for mock fixtures.

## Exception Handling

```python
# In api.py - translate library exceptions
NRGkickApiClientError       # → Base exception for NRGkick API client errors
NRGkickApiClientAuthenticationError  # → Exception for NRGkick API client authentication errors
NRGkickApiClientCommunicationError   # → Exception for NRGkick API client communication errors
```

## Key Constants

- `DOMAIN = "nrgkick"`
- `DEFAULT_SCAN_INTERVAL = 30` (range: 10-300 seconds)
- API endpoints: `/info`, `/control`, `/values`

## Common Mistakes

| Issue                | Fix                                            |
| -------------------- | ---------------------------------------------- |
| Missing translation  | Add to **both** en.json and de.json            |
| Line too long        | Break at 88 chars with parentheses             |
| Docstring format     | Add blank line before closing `"""`            |
| Control not updating | Use `_async_execute_command_with_verification` |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design and data flow diagrams.
