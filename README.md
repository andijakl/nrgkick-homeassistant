# NRGkick Home Assistant Integration

[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://hacs.xyz/docs/default_repositories)
[![GitHub Release](https://img.shields.io/github/release/andijakl/nrgkick-homeassistant.svg)](https://github.com/andijakl/nrgkick-homeassistant/releases)
[![License](https://img.shields.io/github/license/andijakl/nrgkick-homeassistant.svg)](https://github.com/andijakl/nrgkick-homeassistant/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/andijakl/nrgkick-homeassistant.svg)](https://github.com/andijakl/nrgkick-homeassistant/issues)
[![Validate](https://github.com/andijakl/nrgkick-homeassistant/actions/workflows/validate.yml/badge.svg)](https://github.com/andijakl/nrgkick-homeassistant/actions/workflows/validate.yml)
[![Test](https://github.com/andijakl/nrgkick-homeassistant/actions/workflows/test.yml/badge.svg)](https://github.com/andijakl/nrgkick-homeassistant/actions/workflows/test.yml)
[![HACS Validation](https://github.com/andijakl/nrgkick-homeassistant/actions/workflows/hacs.yml/badge.svg)](https://github.com/andijakl/nrgkick-homeassistant/actions/workflows/hacs.yml)

Home Assistant integration for the [NRGkick Gen2 EV mobile wallbox](https://www.nrgkick.com/en/) by [DiniTech GmbH](https://www.dinitech.at/en/) using the official local REST JSON API.

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
  28: - **Localization**: Fully translated entity names and error messages (English/German)

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

- Home Assistant 2025.10 or newer
- NRGkick Gen2 device with firmware >= SmartModule 4.0.0.0
- Local network access to your NRGkick device
- JSON API enabled in the NRGkick App (Extended → Local API)

## Supported Devices

- **NRGkick Gen2** (Smart Cable)
- **Firmware Requirement**: SmartModule firmware 4.0.0.0 or newer

_Note: NRGkick Gen1 (Bluetooth only) is not supported._

## Known Limitations

- **Polling Interval**: The minimum polling interval is 10 seconds to protect the device's internal flash memory and CPU.
- **Phase-Specific Sensors**: Sensors for Phase 2 and Phase 3 (voltage, current, power) only report data when a 3-phase source is connected and active.
- **Temperature Sensors**: Availability of specific temperature sensors (e.g., connector pins) depends on the attached connector attachment.
- **Cloud Independence**: This integration works entirely locally. It does not access the NRGkick Cloud and cannot control cloud-specific features (like cloud-based charging reports).

## ⚠️ Upgrading from v1.x to v2.0.0

**Version 2.0.0 contains breaking changes.** Entity IDs will change due to Home Assistant Silver quality tier compliance requirements. See [MIGRATION.md](MIGRATION.md) for detailed upgrade instructions.

**Note**: The exact new entity IDs depend on your Home Assistant configuration. Always verify the actual IDs in your system.

### Why This Change?

This update implements Home Assistant's Silver quality tier requirements:

- ✅ Uses modern `has_entity_name` pattern for better device/entity organization
- ✅ Uses `ConfigEntry.runtime_data` for improved performance and memory management
- ✅ Aligns with Home Assistant core integration standards

### Need Help?

If you encounter issues during migration:

- Check [GitHub Issues](https://github.com/andijakl/nrgkick-homeassistant/issues) for similar problems
- Create a new issue with details about your setup
- Include Home Assistant version and integration version

## Installation

### Via HACS (Recommended)

This integration is available in the default HACS repository:

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

## Removal

1. Go to **Settings** → **Devices & Services**
2. Select the **NRGkick** integration
3. Click the three dots menu (⋮) on the integration entry and select **Delete**

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

**Version 2.0.0+**: Entities use modern Home Assistant naming with automatic device context. The device name (e.g., "NRGkick") is automatically prefixed to entity names.

Entity ID pattern: `{domain}.{device_name}_{entity_name}` (auto-generated by Home Assistant)

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
- **Dashboard Cards**: See [`examples/dashboard.yaml`](examples/dashboard.yaml) for status cards, gauges, graphs, mobile layouts, and custom cards

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

Uses the official [NRGkick Gen2 Local REST JSON API](https://www.nrgkick.com/wp-content/uploads/2024/12/local_api_docu_simulate-1.html) (`http://{device_ip}`):

- `GET /info` - Device information
- `GET /values` - Real-time telemetry
- `GET /control` - Control parameters
- `GET /control?param=value` - Set parameters

### Update Mechanism

Polls device every 30 seconds (configurable 10-300s). Uses Home Assistant's `DataUpdateCoordinator` for efficient data fetching with automatic error recovery. The integration automatically retries failed connections up to 3 times with exponential backoff, ensuring reliable operation even with temporary network issues.

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
