# NRGkick Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/andijakl/nrgkick-homeassistant.svg)](https://github.com/andijakl/nrgkick-homeassistant/releases)
[![License](https://img.shields.io/github/license/andijakl/nrgkick-homeassistant.svg)](LICENSE)

Home Assistant integration for the NRGkick Gen2 EV charging controller using the local REST JSON API.

## Features

### Automatic Discovery

Supports automatic network discovery via mDNS/Zeroconf. Devices are automatically detected on your local network and tracked even if the IP address changes.

### Monitoring (80+ Sensors)

- **Power & Energy**: Active/reactive/apparent power, power factor, session/total energy, per-phase monitoring
- **Electrical**: Voltage, current, frequency (total and per-phase), neutral current
- **Status**: Charging status, rate, relay state, charge count, error/warning codes
- **Temperature**: Housing, per-phase connector, domestic plug
- **Network**: IP/MAC address, WiFi SSID/RSSI
- **Device Info**: Connector details, grid info, firmware versions
- **Session**: Connect time, charging time

### Controls

- **Charging Current**: 6-32A (range based on device rating)
- **Charge Pause**: Pause/resume charging
- **Energy Limit**: 0-100,000 Wh (0 = unlimited)
- **Phase Count**: 1-3 phases (if supported)

### Binary Sensors

- Charging active
- Charge permitted
- Charge pause status

## Requirements

- Home Assistant 2023.1 or newer
- NRGkick Gen2 device with firmware >= SmartModule 4.0.0.0
- Local network access to your NRGkick device
- JSON API enabled in the NRGkick App (Settings → API Settings)

## Installation

### Via HACS Custom Repository (Before Official Release)

1. Open **HACS** → **Integrations**
2. Click **⋮** (three dots) → **Custom repositories**
3. Add repository:
   - **URL**: `https://github.com/andijakl/nrgkick-homeassistant`
   - **Category**: Integration
4. Click **Add**
5. Search for **NRGkick** and click **Download**
6. Restart Home Assistant
7. Add integration via UI

### Via HACS (not yet available)

Once this integration is available in HACS:

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click **Explore & Download Repositories**
4. Search for **NRGkick**
5. Click **Download**
6. Restart Home Assistant
7. Go to **Settings** → **Devices & Services** → **Add Integration** → **NRGkick**

### Manual Installation

1. Download the latest release from GitHub
2. Extract and copy the `custom_components/nrgkick` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Add integration via UI

**Directory structure after installation:**

```
config/
└── custom_components/
    └── nrgkick/
        ├── __init__.py
        ├── api.py
        ├── binary_sensor.py
        ├── config_flow.py
        ├── const.py
        ├── manifest.json
        ├── number.py
        ├── sensor.py
        ├── switch.py
        └── translations/
            ├── en.json           # English translations
            └── de.json           # German translations
```

## Configuration

### Prerequisites

Enable JSON API on your NRGkick device:

1. Open NRGkick mobile app → **Extended** → **Local API**
2. Enable **JSON API** under **API Variants**
3. (Optional & recommended) Enable **Authentication (JSON)** and set credentials

### Setup

**Automatic Discovery (Recommended)**

Home Assistant will automatically discover NRGkick devices on your network. Click the notification or go to **Settings** → **Devices & Services** → **Configure** the discovered device. Enter credentials if BasicAuth is enabled.

**Manual Configuration**

1. **Settings** → **Devices & Services** → **Add Integration** → **NRGkick**
2. Enter host (IP address or `nrgkick.local`) and credentials (if using BasicAuth)
3. Click **Submit**

**Multiple Devices**: Repeat setup for each device. Each is identified by its unique serial number.

**Reconfiguration**: To update the IP address, credentials, or scan interval, go to **Settings** → **Devices & Services**, find the NRGkick integration, and click **Configure**. The integration will validate the new settings and reload automatically.

**Scan Interval**: Default 30s, adjustable 10-300s via configuration options. Lower values provide fresher data but increase network traffic.

## Usage

### Entity Naming

All entities follow the pattern: `{domain}.nrgkick_{entity_name}`

**Key Entities:**

- `sensor.nrgkick_total_active_power` - Current power (W)
- `sensor.nrgkick_current_session_energy` - Session energy (Wh)
- `sensor.nrgkick_charging_status` - Status text
- `binary_sensor.nrgkick_charging` - Charging on/off
- `switch.nrgkick_charge_pause` - Pause/resume
- `number.nrgkick_charging_current` - Current limit (6-32A)
- `number.nrgkick_energy_limit` - Energy limit (Wh)

### Examples

**Basic Automation** (pause during peak hours):

```yaml
automation:
  - alias: "NRGkick Peak Hour Pause"
    trigger:
      - platform: time
        at: "17:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.nrgkick_charge_pause
```

**Basic Dashboard Card**:

```yaml
type: entities
title: NRGkick
entities:
  - sensor.nrgkick_charging_status
  - binary_sensor.nrgkick_charging
  - sensor.nrgkick_total_active_power
  - switch.nrgkick_charge_pause
  - number.nrgkick_charging_current
```

**More Examples:**

- **Automations**: See [`examples/automations.yaml`](examples/automations.yaml) for solar charging, time-based control, notifications, temperature protection, and more
- **Dashboard Cards**: See [`examples/lovelace_cards.yaml`](examples/lovelace_cards.yaml) for status cards, gauges, graphs, mobile layouts, and custom cards

## Troubleshooting

### Connection Issues

- Verify IP address is correct (ping device)
- Ensure JSON API is enabled in NRGkick app
- Check Home Assistant and NRGkick are on same network/VLAN
- Check logs: **Settings** → **System** → **Logs**

### Authentication Errors

- Verify credentials match NRGkick app settings
- Ensure BasicAuth is enabled in app if using credentials
- Try without credentials if BasicAuth is disabled

### Data Not Updating

- Check logs for errors
- Reload integration: **Settings** → **Devices & Services** → **NRGkick** → **⋮** → **Reload**
- Verify device is powered and connected

### Missing or Unknown Sensors

- Per-phase sensors (L2, L3) only show data during multi-phase charging
- Temperature sensors may not be available on all connector types
- Download diagnostics: **Integration** → **⋮** → **Download diagnostics** to check `coordinator_last_update_success` and data structure

## Technical Details

### API

Uses NRGkick Gen2 Local REST JSON API (`http://{device_ip}`):

- `GET /info` - Device information
- `GET /values` - Real-time telemetry
- `GET /control` - Control parameters
- `GET /control?param=value` - Set parameters

### Update Mechanism

Polls device every 30 seconds (configurable 10-300s). Uses Home Assistant's `DataUpdateCoordinator` for efficient data fetching and automatic retry on failures.

## Development

### Project Structure

```
custom_components/nrgkick/
├── __init__.py           # Integration setup, coordinator
├── api.py                # REST API client
├── binary_sensor.py      # Binary sensor platform
├── config_flow.py        # UI configuration flow
├── const.py              # Constants, mappings
├── manifest.json         # Integration metadata
├── number.py             # Number entity controls
├── sensor.py             # Sensor platform (80+ sensors)
├── switch.py             # Switch platform
└── translations/         # Internationalization
    ├── en.json           # English translations
    └── de.json           # German translations
```

### Local Development

1. Clone repository
2. Copy `custom_components/nrgkick` to your HA config
3. Restart Home Assistant
4. Configure integration via UI
5. Check logs for any errors

### Contributing

Want to contribute? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development environment setup
- Code style guidelines
- Testing procedures
- Pull request process
- Release workflow

The project includes comprehensive tests and automated quality checks to ensure code quality.

### Technical Documentation

- **[INFO.md](INFO.md)**: Quick technical reference with entity overview, API endpoints, and configuration patterns.
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed technical architecture covering data flow, coordinator design, and implementation patterns.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/andijakl/nrgkick-homeassistant/issues)
- [GitHub Discussions](https://github.com/andijakl/nrgkick-homeassistant/discussions)

## Disclaimer

Unofficial integration, not affiliated with DiniTech GmbH. Use at your own risk.
