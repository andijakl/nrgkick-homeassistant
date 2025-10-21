"""Switch platform for NRGkick."""

# pylint: disable=duplicate-code

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NRGkickDataUpdateCoordinator
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


class NRGkickSwitch(CoordinatorEntity, SwitchEntity):  # pylint: disable=abstract-method
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
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"NRGkick {name}"
        self._attr_icon = icon
        self._value_path = value_path

        # Device info
        device_info = coordinator.data.get("info", {}).get("general", {})
        self._attr_unique_id = f"{device_info.get('serial_number', 'unknown')}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info.get("serial_number", "unknown"))},
            "name": device_info.get("device_name", "NRGkick"),
            "manufacturer": "DiniTech",
            "model": device_info.get("model_type", "NRGkick Gen2"),
            "sw_version": coordinator.data.get("info", {})
            .get("versions", {})
            .get("sw_sm"),
        }

    @property
    def translation_key(self) -> str:
        """Return the translation key to translate the entity's name and states."""
        return f"nrgkick_{self._key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        data = self.coordinator.data
        for key in self._value_path:
            if data is None:
                return None
            data = data.get(key)
        return bool(data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.api.set_charge_pause(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.api.set_charge_pause(False)
        # Sleep 2 seconds to make sure the device status is updated
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
