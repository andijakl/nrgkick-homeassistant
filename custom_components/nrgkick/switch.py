"""Switch platform for NRGkick."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NRGkickDataUpdateCoordinator, NRGkickEntity
from .api import NRGkickApiClientError

_LOGGER = logging.getLogger(__name__)


PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NRGkick switches based on a config entry."""
    coordinator: NRGkickDataUpdateCoordinator = entry.runtime_data

    entities: list[NRGkickSwitch] = [
        NRGkickSwitch(
            coordinator,
            key="charge_pause",
            name="Charge Pause",
            icon="mdi:pause",
            value_path=["control", "charge_pause"],
        ),
    ]

    async_add_entities(entities)


class NRGkickSwitch(NRGkickEntity, SwitchEntity):
    """Representation of a NRGkick switch."""

    def __init__(
        self,
        coordinator: NRGkickDataUpdateCoordinator,
        *,
        key: str,
        name: str,
        icon: str,
        value_path: list[str],
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, key, name)
        self._attr_icon = icon
        self._value_path = value_path

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        data: Any = self.coordinator.data
        for key in self._value_path:
            if data is None:
                return None
            data = data.get(key)
        return bool(data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.async_set_charge_pause(True)
        except NRGkickApiClientError as err:
            raise HomeAssistantError(f"Unable to pause charging: {err}") from err

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.async_set_charge_pause(False)
        except NRGkickApiClientError as err:
            raise HomeAssistantError(f"Unable to resume charging: {err}") from err
