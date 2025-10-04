"""Constants for the NRGkick integration."""

from typing import Final

DOMAIN: Final = "nrgkick"

# Configuration
CONF_HOST: Final = "host"

# Default values
DEFAULT_SCAN_INTERVAL: Final = 30

# API Endpoints
ENDPOINT_INFO: Final = "/info"
ENDPOINT_CONTROL: Final = "/control"
ENDPOINT_VALUES: Final = "/values"

# Charging Status
STATUS_UNKNOWN: Final = 0
STATUS_STANDBY: Final = 1
STATUS_CONNECTED: Final = 2
STATUS_CHARGING: Final = 3
STATUS_ERROR: Final = 6
STATUS_WAKEUP: Final = 7

STATUS_MAP: Final = {
    0: "Unknown",
    1: "Standby",
    2: "Connected",
    3: "Charging",
    6: "Error",
    7: "Wakeup",
}

# Attributes
ATTR_STATUS: Final = "status"
ATTR_POWER: Final = "power"
ATTR_CURRENT: Final = "current"
ATTR_VOLTAGE: Final = "voltage"
ATTR_ENERGY: Final = "energy"
