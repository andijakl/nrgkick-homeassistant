"""Constants for the NRGkick integration."""

from typing import Final

DOMAIN: Final = "nrgkick"

# Configuration
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Default values
DEFAULT_SCAN_INTERVAL: Final = 30
MIN_SCAN_INTERVAL: Final = 10
MAX_SCAN_INTERVAL: Final = 300

# API Endpoints
ENDPOINT_INFO: Final = "/info"
ENDPOINT_CONTROL: Final = "/control"
ENDPOINT_VALUES: Final = "/values"

# Charging Status Constants
# These map to the numeric values returned by the API's status field
STATUS_UNKNOWN: Final = 0
STATUS_STANDBY: Final = 1
STATUS_CONNECTED: Final = 2
STATUS_CHARGING: Final = 3
STATUS_ERROR: Final = 6
STATUS_WAKEUP: Final = 7

# Human-readable status mapping for the status sensor
STATUS_MAP: Final = {
    STATUS_UNKNOWN: "Unknown",
    STATUS_STANDBY: "Standby",
    STATUS_CONNECTED: "Connected",
    STATUS_CHARGING: "Charging",
    STATUS_ERROR: "Error",
    STATUS_WAKEUP: "Wakeup",
}
