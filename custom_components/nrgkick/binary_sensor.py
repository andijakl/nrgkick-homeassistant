"""Binary sensor platform for NRGkick."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NRGkickDataUpdateCoordinator
from .const import DOMAIN, STATUS_CHARGING


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NRGkick binary sensors based on a config entry."""
    coordinator: NRGkickDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NRGkickBinarySensor] = [
        NRGkickBinarySensor(
            coordinator,
            "charging",
            "Charging",
            BinarySensorDeviceClass.BATTERY_CHARGING,
            ["values", "general", "status"],
            value_fn=lambda x: (
                x == STATUS_CHARGING if isinstance(x, int) else x == "CHARGING"
            ),
        ),
        NRGkickBinarySensor(
            coordinator,
            "charge_permitted",
            "Charge Permitted",
            BinarySensorDeviceClass.POWER,
            ["values", "general", "charge_permitted"],
        ),
        NRGkickBinarySensor(
            coordinator,
            "charge_pause",
            "Charge Pause",
            None,
            ["control", "charge_pause"],
        ),
    ]

    async_add_entities(entities)


class NRGkickBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a NRGkick binary sensor."""

    def __init__(
        self,
        coordinator: NRGkickDataUpdateCoordinator,
        key: str,
        name: str,
        device_class: BinarySensorDeviceClass | None,
        value_path: list[str],
        value_fn: Any = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_device_class = device_class
        self._value_path = value_path
        self._value_fn = value_fn

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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        data = self.coordinator.data
        for key in self._value_path:
            if data is None:
                return None
            data = data.get(key)

        if self._value_fn and data is not None:
            return self._value_fn(data)
        return bool(data)
