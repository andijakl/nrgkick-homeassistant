# NRGkick Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/andijakl/nrgkick-homeassistant.svg)](https://github.com/andijakl/nrgkick-homeassistant/releases)
[![License](https://img.shields.io/github/license/andijakl/nrgkick-homeassistant.svg)](LICENSE)

A comprehensive Home Assistant integration for the **NRGkick Gen2** EV charging controller, providing local control and monitoring through the device's REST JSON API.

> **✨ Easy Setup**: UI-based configuration flow. No YAML editing required!

## Features

### 📊 Comprehensive Monitoring (80+ Sensors)

**Power & Energy**
- Total active/reactive/apparent power, power factor
- Total charged energy, session energy
- Per-phase power monitoring (L1, L2, L3)
- Peak power tracking

**Electrical Measurements**
- Voltage, current, frequency (total and per-phase)
- Neutral current monitoring
- Power factor per phase

**Device Status**
- Charging status (Standby/Connected/Charging/Error)
- Charging rate, relay state
- Charge count, RCD trigger status
- Warning and error codes

**Temperature Monitoring**
- Housing temperature
- Per-phase connector temperatures (L1, L2, L3)
- Domestic plug temperatures

**Network & Device Information**
- IP address, MAC address
- WiFi SSID and signal strength (RSSI)
- Connector details (type, serial, max current)
- Grid information (voltage, frequency, phases)
- Firmware versions

**Session Statistics**
- Vehicle connect time
- Vehicle charging time

### 🎛️ Controls

- **Charging Current** - Adjust from 6A to 32A (dynamic range based on device rating)
- **Charge Pause Switch** - Pause/resume charging instantly
- **Energy Limit** - Set session energy limit (0-100,000 Wh, 0 = unlimited)
- **Phase Count** - Switch between 1-3 phases (if supported by device)

### 🔌 Binary Sensors

- Charging active status
- Charge permitted indicator
- Charge pause status

## Requirements

- Home Assistant 2023.1 or newer
- NRGkick Gen2 device with firmware >= SmartModule 4.0.0.0
- Local network access to your NRGkick device
- JSON API enabled in the NRGkick App (Settings → API Settings)

## Installation

### Via HACS (Recommended)

Once this integration is available in HACS:

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click **Explore & Download Repositories**
4. Search for **NRGkick**
5. Click **Download**
6. Restart Home Assistant
7. Go to **Settings** → **Devices & Services** → **Add Integration** → **NRGkick**

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
        ├── strings.json
        ├── switch.py
        └── translations/
            ├── de.json
            └── en.json
```

## Configuration

### Prerequisites

**Enable JSON API on your NRGkick:**
1. Open the NRGkick mobile app
2. Go to **Settings** → **API Settings**
3. Enable **JSON API** (or "Native Web API")
4. (Optional) Enable **BasicAuth** and set username/password for security

**Find your NRGkick IP address:**
- Via NRGkick app: Settings → Network Information
- Via router: Check DHCP client list for device named "NRGkick"
- Via mDNS: Device advertises as `_nrgkick._tcp` (may be accessible as `nrgkick.local`)

**💡 Tip**: Set a static IP or DHCP reservation in your router for reliability

### Setup Steps

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for **NRGkick**
4. Enter device information:
   - **Host**: IP address or hostname (e.g., `192.168.1.100` or `nrgkick.local`)
   - **Username**: (Optional) Only if BasicAuth is enabled
   - **Password**: (Optional) Only if BasicAuth is enabled
5. Click **Submit**

The integration will verify the connection and automatically create all entities.

### Multiple Devices

To add multiple NRGkick devices, repeat the configuration steps for each device. Each will be identified by its unique serial number.

## Usage

### Entity Overview

All entities follow the naming pattern: `{domain}.nrgkick_{entity_name}`

**Key Entities:**
- `sensor.nrgkick_total_active_power` - Current power draw (W)
- `sensor.nrgkick_charged_energy` - Current session energy (Wh)
- `sensor.nrgkick_charging_status` - Status text
- `binary_sensor.nrgkick_charging` - Charging on/off
- `switch.nrgkick_charge_pause` - Pause/resume control
- `number.nrgkick_charging_current` - Current setting (6-32A)
- `number.nrgkick_energy_limit` - Energy limit (Wh)
- `number.nrgkick_phase_count` - Phase selection (1-3)

### Automation Examples

**Solar-powered charging:**
```yaml
automation:
  - alias: "NRGkick Solar Charging"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power
        above: 3000
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.nrgkick_charge_pause
      - service: number.set_value
        target:
          entity_id: number.nrgkick_charging_current
        data:
          value: 16
```

**Time-based charging (off-peak hours):**
```yaml
automation:
  - alias: "NRGkick Scheduled Charging"
    trigger:
      - platform: time
        at: "23:00:00"  # Start at 11 PM
    condition:
      - condition: state
        entity_id: binary_sensor.nrgkick_charging
        state: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.nrgkick_charge_pause
      - service: number.set_value
        target:
          entity_id: number.nrgkick_charging_current
        data:
          value: 16
```

**Pause during peak hours:**
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

**Charging complete notification:**
```yaml
automation:
  - alias: "NRGkick Charging Complete"
    trigger:
      - platform: state
        entity_id: binary_sensor.nrgkick_charging
        from: "on"
        to: "off"
    condition:
      - condition: numeric_state
        entity_id: sensor.nrgkick_charged_energy
        above: 1000
    action:
      - service: notify.mobile_app
        data:
          title: "Charging Complete"
          message: "EV charged {{ states('sensor.nrgkick_charged_energy') | float / 1000 | round(2) }} kWh"
```

**Dynamic current based on available power:**
```yaml
automation:
  - alias: "NRGkick Dynamic Current"
    trigger:
      - platform: state
        entity_id: sensor.available_power
    action:
      - service: number.set_value
        target:
          entity_id: number.nrgkick_charging_current
        data:
          value: >
            {% set available = states('sensor.available_power') | float %}
            {% set voltage = 230 %}
            {% set max_current = (available / voltage) | round(0, 'floor') %}
            {{ [6, [max_current, 32] | min] | max }}
```

### Dashboard Examples

**Status Card:**
```yaml
type: entities
title: NRGkick Status
entities:
  - entity: sensor.nrgkick_charging_status
    name: Status
  - entity: binary_sensor.nrgkick_charging
    name: Charging Active
  - entity: sensor.nrgkick_total_active_power
    name: Power
  - entity: sensor.nrgkick_charging_current
    name: Current
  - entity: sensor.nrgkick_charged_energy
    name: Session Energy
  - entity: sensor.nrgkick_housing_temperature
    name: Temperature
```

**Control Card:**
```yaml
type: entities
title: NRGkick Control
entities:
  - entity: switch.nrgkick_charge_pause
    name: Pause Charging
  - entity: number.nrgkick_charging_current
    name: Charging Current
  - entity: number.nrgkick_energy_limit
    name: Energy Limit
  - entity: number.nrgkick_phase_count
    name: Phase Count
```

**Gauge Card:**
```yaml
type: gauge
entity: sensor.nrgkick_total_active_power
name: Charging Power
min: 0
max: 22000
severity:
  green: 0
  yellow: 11000
  red: 18000
```

**Energy Bar Card:**
```yaml
type: custom:bar-card
entity: sensor.nrgkick_charged_energy
name: Session Energy
unit_of_measurement: Wh
max: 50000
positions:
  icon: outside
  indicator: inside
  name: inside
  value: inside
```

More examples available in [`examples/`](examples/) directory.

## Troubleshooting

### Cannot Connect Error

**Possible causes:**
- Wrong IP address
- Device not on same network
- JSON API not enabled
- Firewall blocking connection

**Solutions:**
1. Verify IP address (ping the device)
2. Check NRGkick app: JSON API is enabled
3. Ensure Home Assistant and NRGkick are on same network/VLAN
4. Check Home Assistant logs: **Settings** → **System** → **Logs**

### Invalid Authentication Error

**Solutions:**
1. Verify username/password in NRGkick app
2. Check BasicAuth is enabled in app
3. Try without credentials if BasicAuth is disabled

### Data Not Updating

**Solutions:**
1. Check logs for errors
2. Verify device is powered and connected
3. Reload integration: **Settings** → **Devices & Services** → **NRGkick** → **⋮** → **Reload**
4. Restart Home Assistant

### Some Sensors Show "Unknown"

**Normal behavior:**
- Per-phase sensors only show data during 3-phase charging
- Some values depend on device model and firmware version
- Temperature sensors may not be available on all connectors

## Technical Details

### API Information

The integration uses the NRGkick Gen2 Local REST JSON API:
- **Base URL**: `http://{device_ip}`
- **Endpoints**:
  - `GET /info` - Device information, network, hardware/software versions
  - `GET /control` - Charging control parameters
  - `GET /values` - Real-time telemetry data
  - `GET /control?param=value` - Set control parameters

### Update Interval

The integration polls the device every **30 seconds** to retrieve current data. This balances responsiveness with device load.

### Data Coordinator

Uses Home Assistant's `DataUpdateCoordinator` pattern:
- Efficient data fetching with single API call cycle
- Automatic retry on failures
- Shared data across all entities
- Built-in state management

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
├── strings.json          # UI strings
├── switch.py             # Switch platform
└── translations/         # Internationalization
    ├── de.json
    └── en.json
```

### Local Development

1. Clone repository
2. Copy `custom_components/nrgkick` to your HA config
3. Restart Home Assistant
4. Configure integration via UI
5. Check logs for any errors

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **DiniTech GmbH** - For creating the NRGkick Gen2 EV charger
- **Home Assistant Community** - For the excellent platform and documentation
- **Contributors** - For testing, feedback, and improvements

## Disclaimer

This is an unofficial integration and is not affiliated with, endorsed by, or supported by DiniTech GmbH. Use at your own risk.

## Support

- **Issues**: [GitHub Issues](https://github.com/andijakl/nrgkick-homeassistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/andijakl/nrgkick-homeassistant/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

---

**Made with ❤️ for the Home Assistant community**
