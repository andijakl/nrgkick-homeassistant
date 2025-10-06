"""The NRGkick integration."""

from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NRGkickAPI
from .const import DOMAIN

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

    def __init__(self, hass: HomeAssistant, api: NRGkickAPI, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = api
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
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
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                raise ConfigEntryAuthFailed(
                    "Authentication failed. Please reconfigure the integration with valid credentials."
                ) from err
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
