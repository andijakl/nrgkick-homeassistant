"""The NRGkick integration."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    NRGkickAPI,
    NRGkickApiClientAuthenticationError,
    NRGkickApiClientCommunicationError,
)
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NRGkick from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = NRGkickAPI(
        host=entry.data["host"],
        username=entry.data.get("username"),
        password=entry.data.get("password"),
        session=async_get_clientsession(hass),
    )

    coordinator = NRGkickDataUpdateCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when it changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class NRGkickDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NRGkick data from the API."""

    def __init__(
        self, hass: HomeAssistant, api: NRGkickAPI, entry: ConfigEntry
    ) -> None:
        """Initialize."""
        self.api = api
        self.entry = entry

        # Get scan interval from options or use default
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            info = await self.api.get_info()
            control = await self.api.get_control()
            values = await self.api.get_values()

            return {
                "info": info,
                "control": control,
                "values": values,
            }
        except NRGkickApiClientAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except NRGkickApiClientCommunicationError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _async_execute_command_with_verification(
        self,
        command_func: Callable[[], Awaitable[dict[str, Any]]],
        expected_value: Any,
        control_key: str,
        error_message: str,
    ) -> None:
        """Execute a command and verify the state changed.

        Args:
            command_func: Async function to execute the command
            expected_value: Expected value after command execution
            control_key: Key in control data to verify (e.g., "charge_pause")
            error_message: Error message to show if verification fails
        """
        # Execute command and get response
        response = await command_func()

        # Check if response contains an error message
        if "Response" in response:
            raise NRGkickApiClientCommunicationError(
                f"{error_message} {response['Response']}"
            )

        # Check if response contains the expected key with the new value
        if control_key in response:
            actual_value = response[control_key]

            # Convert both values to float for comparison to handle type differences
            try:
                actual_float = float(actual_value) if actual_value is not None else None
                expected_float = (
                    float(expected_value) if expected_value is not None else None
                )
                if actual_float != expected_float:
                    raise NRGkickApiClientCommunicationError(
                        f"{error_message} Device returned unexpected value: "
                        f"{actual_value} (expected {expected_value})."
                    )
            except (ValueError, TypeError) as err:
                raise NRGkickApiClientCommunicationError(
                    f"{error_message} Device returned invalid value."
                ) from err

            # Update coordinator data immediately with the new value
            if "control" not in self.data:
                self.data["control"] = {}
            self.data["control"][control_key] = actual_value

            # Notify all entities that coordinator data has been updated
            self.async_set_updated_data(self.data)

        else:
            # Response doesn't contain expected key - refresh to get current state
            await asyncio.sleep(2)
            await self.async_request_refresh()

    async def async_set_current(self, current: float) -> None:
        """Set the charging current."""
        await self._async_execute_command_with_verification(
            lambda: self.api.set_current(current),
            current,
            "current_set",
            f"Failed to set charging current to {current}A.",
        )

    async def async_set_charge_pause(self, pause: bool) -> None:
        """Set the charge pause state."""
        expected_state = 1 if pause else 0
        await self._async_execute_command_with_verification(
            lambda: self.api.set_charge_pause(pause),
            expected_state,
            "charge_pause",
            f"Failed to {'pause' if pause else 'resume'} charging.",
        )

    async def async_set_energy_limit(self, energy_limit: int) -> None:
        """Set the energy limit."""
        await self._async_execute_command_with_verification(
            lambda: self.api.set_energy_limit(energy_limit),
            energy_limit,
            "energy_limit",
            f"Failed to set energy limit to {energy_limit}Wh.",
        )

    async def async_set_phase_count(self, phase_count: int) -> None:
        """Set the phase count."""
        await self._async_execute_command_with_verification(
            lambda: self.api.set_phase_count(phase_count),
            phase_count,
            "phase_count",
            f"Failed to set phase count to {phase_count}.",
        )


class NRGkickEntity(CoordinatorEntity):
    """Base class for NRGkick entities with common device info setup."""

    coordinator: NRGkickDataUpdateCoordinator

    def __init__(
        self, coordinator: NRGkickDataUpdateCoordinator, key: str, name: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"NRGkick {name}"
        self._attr_translation_key = f"nrgkick_{key}"
        self._setup_device_info()

    def _setup_device_info(self) -> None:
        """Set up device info and unique ID."""
        device_info = self.coordinator.data.get("info", {}).get("general", {})
        serial = device_info.get("serial_number", "unknown")

        self._attr_unique_id = f"{serial}_{self._key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": device_info.get("device_name", "NRGkick"),
            "manufacturer": "DiniTech",
            "model": device_info.get("model_type", "NRGkick Gen2"),
            "sw_version": self.coordinator.data.get("info", {})
            .get("versions", {})
            .get("sw_sm"),
        }
