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

from . import NRGkickDataUpdateCoordinator, NRGkickEntity
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
            key="charging",
            name="Charging",
            device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
            value_path=["values", "general", "status"],
            value_fn=lambda x: (
                x == STATUS_CHARGING if isinstance(x, int) else x == "CHARGING"
            ),
        ),
        NRGkickBinarySensor(
            coordinator,
            key="charge_permitted",
            name="Charge Permitted",
            device_class=BinarySensorDeviceClass.POWER,
            value_path=["values", "general", "charge_permitted"],
        ),
        NRGkickBinarySensor(
            coordinator,
            key="charge_pause",
            name="Charge Pause",
            device_class=None,
            value_path=["control", "charge_pause"],
        ),
    ]

    async_add_entities(entities)


class NRGkickBinarySensor(NRGkickEntity, BinarySensorEntity):
    """Representation of a NRGkick binary sensor."""

    def __init__(
        self,
        coordinator: NRGkickDataUpdateCoordinator,
        *,
        key: str,
        name: str,
        device_class: BinarySensorDeviceClass | None,
        value_path: list[str],
        value_fn: Any = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, key, name)
        self._attr_device_class = device_class
        self._value_path = value_path
        self._value_fn = value_fn

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        data: Any = self.coordinator.data
        for key in self._value_path:
            if data is None:
                return None
            data = data.get(key)

        if self._value_fn and data is not None:
            return self._value_fn(data)
        return bool(data)
