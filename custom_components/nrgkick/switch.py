"""Switch platform for NRGkick."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NRGkickDataUpdateCoordinator, NRGkickEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NRGkick switches based on a config entry."""
    coordinator: NRGkickDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

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
        await self.coordinator.api.set_charge_pause(True)  # type: ignore[attr-defined]
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.api.set_charge_pause(False)  # type: ignore[attr-defined]
        # Sleep 2 seconds to make sure the device status is updated
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
