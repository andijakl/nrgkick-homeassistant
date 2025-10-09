"""Number platform for NRGkick."""

from __future__ import annotations

import asyncio

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
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
    """Set up NRGkick number entities based on a config entry."""
    coordinator: NRGkickDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Get rated current from device info
    rated_current = (
        coordinator.data.get("info", {}).get("general", {}).get("rated_current", 32)
    )

    entities: list[NRGkickNumber] = [
        NRGkickNumber(
            coordinator,
            "current_set",
            "Charging Current",
            UnitOfElectricCurrent.AMPERE,
            6.0,
            float(rated_current),
            0.1,
            ["control", "current_set"],
            NumberMode.SLIDER,
        ),
        NRGkickNumber(
            coordinator,
            "energy_limit",
            "Energy Limit",
            "Wh",
            0,
            100000,
            100,
            ["control", "energy_limit"],
            NumberMode.BOX,
        ),
        NRGkickNumber(
            coordinator,
            "phase_count",
            "Phase Count",
            None,
            1,
            3,
            1,
            ["control", "phase_count"],
            NumberMode.SLIDER,
        ),
    ]

    async_add_entities(entities)


class NRGkickNumber(CoordinatorEntity, NumberEntity):  # pylint: disable=abstract-method
    """Representation of a NRGkick number entity."""

    def __init__(
        self,
        coordinator: NRGkickDataUpdateCoordinator,
        key: str,
        name: str,
        unit: str | None,
        min_value: float,
        max_value: float,
        step: float,
        value_path: list[str],
        mode: NumberMode = NumberMode.BOX,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = mode
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
        return self._key

    @property
    def native_value(self) -> float | None:
        """Return the value of the number entity."""
        data = self.coordinator.data
        for key in self._value_path:
            if data is None:
                return None
            data = data.get(key)
        return float(data) if data is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the number entity."""
        if self._key == "current_set":
            await self.coordinator.api.set_current(value)
        elif self._key == "energy_limit":
            await self.coordinator.api.set_energy_limit(int(value))
        elif self._key == "phase_count":
            await self.coordinator.api.set_phase_count(int(value))

        # Sleep 2 seconds to make sure the device status is updated
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
