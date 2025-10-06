"""Diagnostics support for NRGkick."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import NRGkickDataUpdateCoordinator
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: NRGkickDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Get all data from coordinator
    data = coordinator.data

    # Redact sensitive information
    config_data = {
        "host": entry.data.get("host", "unknown"),
        "has_username": entry.data.get("username") is not None,
        "has_password": entry.data.get("password") is not None,
    }

    diagnostics_data = {
        "config": config_data,
        "coordinator_last_update_success": coordinator.last_update_success,
        "coordinator_update_interval": coordinator.update_interval.total_seconds(),
    }

    # Add data from coordinator if available
    if data:
        diagnostics_data["data"] = {
            "info": data.get("info", {}),
            "control": data.get("control", {}),
            "values": data.get("values", {}),
        }
    else:
        diagnostics_data["data"] = None
        diagnostics_data["note"] = "No data available from coordinator"

    return diagnostics_data
